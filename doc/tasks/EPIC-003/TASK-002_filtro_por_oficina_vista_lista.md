# EPIC-003 / TASK-002 — Filtro por oficina (ubicación actual) en la vista de lista

Estado: Draft
Modo: L
Riesgo: alto/sensible (campo persistente nuevo)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
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
- exponer el filtro en `document_exp_view_search` (filtro/searchpanel/group-by),
  preferentemente acotado a oficinas internas de TMC;
- test del compute (paralelo al de `current_holder_id`).

No incluye:

- filtro por historial de oficinas (solo ubicación actual);
- filtro por usuario (TASK-001).

## Reglas / decisiones

- "Oficina" = ubicación actual, no historial (decisión del usuario).
- No introducir reglas de negocio nuevas sobre qué cuenta como "oficina" sin confirmar
  el criterio (`is_internal`).

## Preguntas abiertas

- Criterio de "oficina TMC": ¿`is_internal = True` en `tmc.dependence`? (confirmar).
- ¿El filtro ofrece solo dependencias internas o cualquier destino?
- Nombre definitivo del campo (`current_location_dependence_id` propuesto).
- UI: filtro de barra vs searchpanel lateral vs group-by.

## Acceptance criteria

- [ ] Existe `current_location_dependence_id` stored, que refleja la dependencia de
  destino del último movimiento (False si no hay movimientos).
- [ ] La search view permite filtrar expedientes por esa oficina/ubicación actual.
- [ ] El recompute es correcto al agregar un movimiento nuevo (cambia la ubicación).
- [ ] Test que cubre el compute (con y sin movimientos, y tras nuevo movimiento).
- [ ] Sin regresión de filtros existentes ni de `current_holder_id`.

## Contrato técnico

- Modelos: `me.document_exp` — nuevo campo computed stored `current_location_dependence_id`.
- Vistas: `document_exp_view_search` (`me/views/document_exp_views.xml`).
- Seguridad: sin nueva ACL (campo, no modelo); verificar visibilidad por grupos.
- Datos: N/A.
- Migraciones: N/A manual; el campo stored se recomputa al actualizar el módulo
  (documentar el recompute, validar performance del depends sobre movimientos).
- Tests: nuevo test del compute en `me/tests`.

## Tests evidenciados

- Estado: PENDIENTE USER-RUN
- Comando: `docker compose -f develop.yml run --rm odoo odoo -d <TEST_DB> -u me --test-tags /me --stop-after-init --log-level=test`
- Fecha: N/A
- Resultado: N/A
- Salida (resumen): N/A — pendiente de implementación

## Docs canónicas

Diferir: al implementar, actualizar `doc/project/me/models.md` (nuevo campo) y, si
aplica, `architecture`/`business_rules`.

## Estado / próximo paso

Draft, creada desde idea de backlog del usuario. Toca campo persistente → **no
implementar sin contrato**. Próximo paso: `/contract-draft`.

## Resultado / cierre

Pendiente.
