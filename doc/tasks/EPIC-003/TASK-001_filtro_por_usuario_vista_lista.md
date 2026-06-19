# EPIC-003 / TASK-001 — Filtro por usuario poseedor en la vista de lista

Estado: Done
Modo: S
Riesgo: bajo
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: N/A

## Objetivo

Permitir filtrar y agrupar expedientes por su poseedor actual (`current_holder_id`) en
la search view, más allá del filtro existente "In My Possession" (que solo usa el uid
propio).

## Alcance

Incluye:

- en `document_exp_view_search` (`me/views/document_exp_views.xml`): exponer
  `current_holder_id` como campo buscable y agregar group-by por poseedor.

No incluye:

- filtro por oficina/ubicación (TASK-002);
- cualquier cambio de modelo o campo persistente (`current_holder_id` ya existe stored).

## Acceptance criteria

- [x] La search view permite buscar/filtrar expedientes por usuario poseedor
  (`current_holder_id`), no solo por el usuario propio (campo buscable "Holder").
- [x] Existe group-by "Holder" que agrupa los expedientes por `current_holder_id`.
- [x] Los filtros existentes ("In My Possession", reentry, tribunal, licitación,
  origen TMC) siguen funcionando (sin regresión).

## Validación

Manual (UI) verificada por el usuario: campo buscable + Group By por poseedor OK; filtros
existentes sin regresión. El módulo actualiza limpio (`-u me --stop-after-init` exit 0,
sin errores de validación de vista). Sin tests automatizados nuevos (cambio de vista).

## Preguntas abiertas

- Ninguna. **UI decidida:** campo buscable `current_holder_id` + Group By "Poseedor".
  **Sin** entrada en la searchpanel lateral (se descartó por no escalar con muchos usuarios).

## Estado / próximo paso

**Done.** Implementado en `document_exp_view_search` y verificado en UI.

## Resultado / cierre

Cerrada (Done) el 2026-06-19. Entregado: campo buscable `current_holder_id` ("Holder") +
filtro group-by por poseedor en la search view de expedientes, sin cambios de modelo ni
regresión de los filtros existentes.
