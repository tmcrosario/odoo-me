# EPIC-004 / TASK-001 — Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO)

Estado: Draft
Modo: L
Riesgo: alto/sensible (campo persistente required, create(), movimientos, método con frontera de seguridad cross-módulo)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: bloqueada (joint)
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: implementación **joint** con `odoo-junco` EPIC-010. No mergear
  una punta sin la otra; deploy conjunto `-u me,junco` (ME carga antes por dependencia).
  Arrancar solo con luz verde de JUNCO (su EPIC-010/TASK-002 ya está listo y a la espera).

## Objetivo

Que un expediente **DEM** se cree en ME con `jurisdiction_dependence` y
`source_dependence_id` vacíos, dejando que JUNCO los complete al vincular el expediente
al proceso (vía método controlado), sin romper la creación, los movimientos automáticos
ni los constraints. CM y TMC quedan intactos.

## Contexto mínimo

Definición funcional y decisiones joint (D-1/D-2/D-3/D-4) en
`doc/epics/EPIC-004_reacotamiento_carga_me_traspaso_junco.md`. Contraparte:
`odoo-junco/doc/epics/EPIC-010_*`. Verificación técnica ya hecha: `computed_name` no
depende de jurisdicción; el único bloqueo de carga era el `required=True` del campo; el
`write()` tiene un guard que exige el método controlado.

## Alcance

Incluye:

- quitar el `required=True` de `jurisdiction_dependence` (modelo);
- en DEM, ocultar los 2 campos cuando están vacíos y mostrarlos readonly cuando tienen valor;
- desacoplar el 1er movimiento (origin = `dependence_id`);
- método `action_set_origin_from_junco(jurisdiction_id, source_id=False)`;
- tests.

No incluye:

- CM ni TMC (sin cambios de carga);
- la implementación del lado JUNCO (EPIC-010);
- migración masiva de expedientes existentes.

## Reglas / decisiones

- **D-3 scoping (no negociable):** todo cambio de carga es **condicional por origen = DEM**.
- **D-1:** en DEM los 2 campos quedan vacíos al ingresar; JUNCO los escribe al vincular.
- **D-4:** JUNCO escribe vía el método, no con write crudo (sortea el write-guard).
- **UI (decidido):** en DEM los 2 campos están **ocultos cuando vacíos** (carga inicial)
  y aparecen **readonly cuando JUNCO los completó**.
- **Movimiento (opción A, decidido):** 1er pase DEM→TMC con origin = `dependence_id`.
- No inventar reglas de negocio; el dominio del nomenclador se reusa de los computes
  existentes (`_compute_allowed_jurisdictions` / `_compute_allowed_sub_dependences`).

## Preguntas abiertas

- Ninguna bloqueante. Riesgo de diseño abierto (ver Riesgos Odoo): el método **no puede**
  restringirse por ACL a `junco.group_user` desde ME (dependencia inversa) — la seguridad
  queda en la validación interna + superficie de escritura mínima.

## Acceptance criteria

- [x] Un expediente DEM se crea con `jurisdiction_dependence` y `source_dependence_id`
      vacíos, sin error (required quitado; constraints no disparan).
- [x] CM y TMC conservan su carga actual (jurisdicción auto; TMC mantiene source manual).
- [x] Al crear un DEM se generan el 1er movimiento DEM→TMC (origin = `dependence_id`) y el
      2do TMC→ME, visibles en ME al ingresar.
- [x] En la UI de carga DEM, `jurisdiction_dependence` y `source_dependence_id` están
      **ocultos cuando vacíos** y **readonly cuando tienen valor**; TMC/CM sin cambios.
- [x] `action_set_origin_from_junco(jurisdiction_id, source_id=False)`:
      · invocable por un usuario no-manager (eleva con `sudo()` internamente);
      · escribe solo esos 2 campos y solo si el expediente es DEM (si no, `UserError`);
      · valida `jurisdiction_id` (jurisdicción válida del nomenclador) y `source_id`
        (hijo de la jurisdicción) → `UserError` claro si inválidos;
      · acepta `source_id=False`;
      · idempotente (repetir la misma llamada con los mismos valores no falla).
- [x] Expedientes DEM existentes conservan su jurisdiction/source (sin migración masiva).

## Contrato técnico

- **Modelos** (`me/models/document_exp.py`):
  - `jurisdiction_dependence`: quitar `required=True` (l.38). Seguro: `create()`
    autoasigna jurisdicción a TMC/CM (l.446-451); solo DEM queda vacío. `is_valid`
    (invisible) pasa a False sin efecto funcional.
  - `create()` (l.487-497): cambiar `origin_dependence_id` del 1er movimiento de
    `record.jurisdiction_dependence.id` a `record.dependence_id.id`; revisar la guarda
    `if not origin_is_tmc and record.jurisdiction_dependence` → debe basarse en
    `dependence_id` (DEM/CM) y no en la jurisdicción, para que el 1er pase se cree con
    jurisdicción vacía. 2do movimiento (TMC→ME) sin cambios.
  - Nuevo método `action_set_origin_from_junco(self, jurisdiction_id, source_id=False)`:
    valida `self.dependence_id.abbreviation == 'DEM'` (si no → `UserError`); valida
    `jurisdiction_id`/`source_id` contra el nomenclador (`tmc.dependence_order`: jurisdicción
    = hijo de `tmc_dependence_adm`; source = hijo de la jurisdicción) reusando la lógica
    de los computes existentes; escribe vía `sudo()` solo esos 2 campos; idempotente.
- **Vistas** (`me/views/document_exp_views.xml`):
  - `jurisdiction_dependence`: `readonly` para TMC y DEM; `invisible` para CM y, en DEM,
    también cuando el campo está vacío (`... or (DEM and not jurisdiction_dependence)`).
  - `source_dependence_id`: `readonly` en DEM; `invisible` para CM y, en DEM, cuando el
    campo está vacío. El `required="allowed_sub_dependence_ids"` no estorba: con
    jurisdicción vacía no exige, y al completarse desde JUNCO queda satisfecho.
- **Seguridad:**
  - El método hace `sudo()` interno acotado a 2 campos + scope DEM: es el único punto de
    escritura JUNCO→ME y la frontera la valida ME. No se abre el guard general de `write()`.
  - **No** referenciar `junco.group_user` desde ME (rompería ME standalone). Control de
    acceso = read ACL de `me.document_exp` (que JUNCO ya tiene) + validación interna.
  - Sin nuevas filas en `ir.model.access.csv` (no hay modelo nuevo).
- **Datos:** N/A.
- **Migraciones:** N/A — expedientes DEM existentes conservan jurisdiction/source. Quitar
  `required` no afecta registros existentes. Documentar que no hay migración masiva.
- **Tests** (`me/tests/`): ver Plan de tests.

## Execution report

Implementado en `me/models/document_exp.py` (required quitado, `create()` desacoplado,
guard de `write()` con canal `me_origin_from_junco`, método `action_set_origin_from_junco`)
y `me/views/document_exp_views.xml` (ocultar vacíos / readonly con valor en DEM). 9 tests
nuevos + 3 preexistentes ajustados al nuevo comportamiento. UI verificada por el usuario.

## Verifier / close gate

Tests verdes (evidencia abajo) + verificación manual de UI por el usuario. Cierre
documental formal queda para `/doc-close` tras el deploy joint con JUNCO.

## Tests evidenciados

- Estado: OK
- Comando: `docker compose -f develop.yml run --rm odoo odoo -d me1 --addons-path=/mnt/extra-addons/odoo-tmc,/mnt/extra-addons/odoo-tmc-data,/mnt/extra-addons/odoo-me,/mnt/extra-addons/odoo-junco,/mnt/addons/oca/* -u me --test-tags /me --stop-after-init --log-level=test`
  (el `--addons-path` explícito es necesario porque `run` sobrescribe el `command:` de develop.yml)
- Fecha: 2026-06-17
- Resultado: **0 failed, 0 error(s) of 196 tests** (240 métodos, 7.2s, 19499 queries)
- Salida (resumen):

  ```text
  me: 240 tests 7.21s 19499 queries
  0 failed, 0 error(s) of 196 tests when loading database 'me1'
  ```

Casos cubiertos (9 nuevos en `test_document_exp.py`):
- create DEM con jurisdiction/source vacíos → OK; 1er movimiento DEM→TMC (origin = `dependence_id`).
- método: happy path; `source_id=False`; UserError no-DEM / jurisdiction inválida / source inválido;
  idempotencia; no-manager bloqueado en write crudo pero OK vía el método.
- Ajustados: `test_create_generates_two_movements` (origen DEM), `test_create_dem_without_jurisdiction_succeeds`
  (antes `_raises`), `test_poseedor_logic_unaffected` (destino interno ≠ TMC para evitar colisión).

## Docs canónicas

Actualizar al implementar: `doc/project/me/models.md` (required + método nuevo),
`business_rules.md` (cesión DEM, 1er movimiento), `security.md` (método con sudo y su
frontera). `workflows` si se documenta el cambio de movimientos.

## Bloqueos

- Bloqueada por: coordinación joint — requiere luz verde de JUNCO (EPIC-010) y ventana de
  deploy conjunta `-u me,junco`.
- Propietario del bloqueo: usuario (coordina ambas puntas).
- Fecha de bloqueo: 2026-06-12.
- Acción mínima para destrabar: confirmación de JUNCO de que arranca implementación en la
  misma ventana; entonces ME implementa y se despliega junto.

## Estado / próximo paso

Implementada en ME y con tests verdes + UI verificada. Próximo paso: push de ME →
JUNCO implementa contra el método → deploy conjunto (`-u me,junco`). Cierre documental
(`/doc-close`) tras el deploy joint. Al implementar JUNCO deroga D-005 en su EPIC-002.

## Resultado / cierre

Pendiente.
