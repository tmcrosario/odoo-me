# EPIC-003 / TASK-001 — Filtro por usuario poseedor en la vista de lista

Estado: Draft
Modo: S
Riesgo: bajo
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
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

- [ ] La search view permite buscar/filtrar expedientes por usuario poseedor
  (`current_holder_id`), no solo por el usuario propio.
- [ ] Existe group-by "Poseedor" que agrupa los expedientes por `current_holder_id`.
- [ ] Los filtros existentes ("In My Possession", reentry, tribunal, licitación,
  origen TMC) siguen funcionando (sin regresión).

## Validación

Manual (UI): cargar expedientes con distintos poseedores y verificar filtro + group-by.
Sin tests automatizados nuevos (cambio de vista, sin lógica).

## Preguntas abiertas

- UI: ¿alcanza con campo buscable + group-by, o se quiere también entrada en la
  searchpanel lateral? (definir en `/prepare-task`).

## Estado / próximo paso

Draft, creada desde idea de backlog del usuario. Próximo paso: `/prepare-task` para
cerrar la UI exacta y pasar a implementación.

## Resultado / cierre

Pendiente.
