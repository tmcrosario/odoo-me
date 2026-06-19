# EPIC-003 / TASK-002 — Filtro por oficina (ubicación actual) en la vista de lista

Estado: Done
Modo: L
Riesgo: alto/sensible (campo persistente nuevo)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: N/A

## Objetivo

Permitir filtrar expedientes por la **oficina donde están ubicados actualmente** (la
dependencia interna de TMC de destino del último movimiento), para ver el conjunto de
expedientes que tiene una oficina aunque ésta tenga más de un usuario.

## Contexto mínimo

La ubicación actual de un expediente = `destination_dependence_id` del último
movimiento (mayor `id`). Hoy **no existe** un campo stored para esto; solo está
`current_holder_id` (poseedor, stored computed análogo) y el booleano
`is_currently_internal`. Un filtro por dominio sobre `document_movement_ids` no sirve
porque "último movimiento" no se expresa en un domain de search view → hace falta un
campo stored computado.

## Alcance

Incluye:

- nuevo campo `current_location_dependence_id` (Many2one `tmc.dependence`), **stored
  computed**, = `destination_dependence_id` del último movimiento, con
  `@api.depends('document_movement_ids.destination_dependence_id')` (espejo de
  `_compute_current_holder_id`);
- exponer en `document_exp_view_search` un campo buscable (typeahead) sobre
  `current_location_dependence_id` con dominio `[('is_internal','=',True)]`;
- test del compute (paralelo al de `current_holder_id`).

No incluye:

- filtro por historial de oficinas (solo ubicación actual);
- filtro por usuario (TASK-001).

## Reglas / decisiones

- "Oficina" = ubicación actual (destino del último movimiento), no historial.
- **Oficina TMC = `tmc.dependence` con `is_internal=True`** (campo de `dependence_ext.py`,
  "belongs to the Tribunal"). Confirmado contra el sistema viejo (select "Oficina de
  destino" lista solo dependencias internas de TMC).
- **UI decidida:** campo **buscable (typeahead)** `current_location_dependence_id` con
  dominio `is_internal=True`. Sin searchpanel lateral (se descartó por los ~20 + duplicados).
- Nombre del campo: `current_location_dependence_id`.

## Preguntas abiertas

- Ninguna bloqueante (todas cerradas arriba). Resta solo la **limitación de datos** (no
  se arregla acá): ver Riesgos.

## Acceptance criteria

- [x] Existe `current_location_dependence_id` stored = oficina interna de destino del
  último movimiento; **False** si no hay movimientos o si salió del Tribunal (último
  destino no interno) → el group-by solo muestra oficinas internas.
- [x] La search view permite filtrar expedientes por esa oficina (campo buscable,
  dominio `is_internal=True`) + group-by por oficina.
- [x] El recompute es correcto al agregar un movimiento nuevo (cambia la ubicación).
- [x] Test que cubre el compute (con y sin movimientos, y tras nuevo movimiento).
- [x] Sin regresión de filtros existentes ni de `current_holder_id` (suite /me 201/0/0).

## Limitaciones conocidas

- El nomenclador tiene **dependencias internas duplicadas** (visto en el sistema viejo:
  Dir. de Asuntos Legales ×2, Dir. de Coordinación y Despacho ×2, variantes de "Tribunal
  Municipal de Cuentas"). El filtro las mostrará duplicadas. **No se sanea en esta task**
  (es problema de datos, territorio #033 / EPIC-001/TASK-004); se documenta como limitación.

## Contrato técnico

- **Modelos** (`me/models/document_exp.py`):
  - Nuevo `current_location_dependence_id = fields.Many2one('tmc.dependence', ...,
    compute='_compute_current_location_dependence_id', store=True)`, **espejo exacto** de
    `current_holder_id` (l.158-173).
  - `_compute_current_location_dependence_id` con
    `@api.depends('document_movement_ids.destination_dependence_id',
    'document_movement_ids.destination_dependence_id.is_internal')`: toma el destino del
    último movimiento (`sorted('id')[-1:]`) **solo si es interno** (`is_internal=True`);
    si no hay movimientos o el expediente salió del Tribunal (último destino no interno)
    → `False`. **Internal-only** para que el group-by no muestre oficinas externas.
  - Help describe la semántica internal-only.
- **Vistas** (`document_exp_view_search`, `me/views/document_exp_views.xml`):
  - `<field name="current_location_dependence_id" string="Destination Office"
    domain="[('is_internal','=',True)]"/>` (buscable/typeahead), junto a `current_holder_id`.
    Etiqueta "Destination Office" (= "Oficina de destino" del sistema viejo).
  - Group-by por oficina: **incluir** por simetría con `group_by_holder` (TASK-001):
    `<filter name="group_by_location" string="Destination Office" context="{'group_by': 'current_location_dependence_id'}"/>`.
    Separable si se prefiere alcance mínimo.
- **Seguridad:** sin nueva ACL (campo, no modelo). El campo hereda la visibilidad de
  `me.document_exp`; no expone datos nuevos sensibles.
- **Datos:** N/A.
- **Migraciones:** N/A manual. El campo `store=True` se **recomputa al `-u me`** para todos
  los expedientes existentes → validar que el recompute corre sin error y revisar
  performance del `depends` sobre `document_movement_ids` (mismo patrón que `current_holder_id`,
  ya en producción, así que el costo es comparable).
- **Tests** (`me/tests/test_document_exp.py`): ver Plan de tests (espejo de `TestCurrentHolder029`).

## Tests evidenciados

- Estado: OK
- Comando: `docker compose -f develop.yml exec -T odoo odoo -d me_test -u me --addons-path=<tmc,tmc-data,me,junco> --db_host=db --db_user=odoo --db_password=odoo --test-tags /me --stop-after-init --http-port=8169 --gevent-port=8173 --max-cron-threads=0 --log-level=test`
  (DB **dedicada no servida** `me_test`; sobre me1/me2 servidas recolecta 0 tests = verde falso)
- Fecha: 2026-06-19
- Resultado: **0 failed, 0 error(s) of 201 tests** (247 métodos), 5 tests nuevos `TestCurrentLocation`.
- Salida (resumen):

  ```text
  me: 247 tests 4.05s 10222 queries
  0 failed, 0 error(s) of 201 tests when loading database 'me_test'
  ```

Casos cubiertos (`TestCurrentLocation`):
- sin movimientos → False; destino interno → esa oficina; **salió del Tribunal (destino
  no interno) → False**; sigue el último movimiento no el primero; filtro por ubicación.
- UI verificada en me2 (group-by solo oficinas internas) tras apply + recompute forzado + restart.

## Docs canónicas

Actualizada: `doc/project/me/models.md` (campo `current_location_dependence_id`).
`architecture`/`business_rules`: N/A (campo análogo a `current_holder_id`, sin regla nueva).

## Estado / próximo paso

**Done.** Implementado (campo internal-only + vista buscable/group-by "Destination
Office"), suite `me_test` 201/0/0, UI verificada en me2. Push y deploy a prod: usuario.

## Resultado / cierre

Cerrada (Done) el 2026-06-19. Entregado: campo stored `current_location_dependence_id`
(oficina interna de destino del último movimiento; False si salió del Tribunal o sin
movimientos) + filtro buscable y group-by "Destination Office" (dominio `is_internal=True`)
en la search view. Limitación conocida: duplicados de dependencias internas en el
nomenclador (#033). Hallazgo registrado: `me` tiene dependencia implícita de `tmc_data`
(data) no declarada en el manifest — candidato a corregir en EPIC-001 con aprobación.
