# EPIC-003 — Índice de tasks

Épica: `doc/epics/EPIC-003_usabilidad_filtros_vista_expedientes.md`

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Filtro por usuario poseedor en la vista de lista | sin asignar | S | Done | UI sobre `current_holder_id` (ya stored); buscable + group-by. Verificada en UI |
| TASK-002 | Filtro por oficina (ubicación actual) en la vista de lista | sin asignar | L | Done | Campo `current_location_dependence_id` (internal-only) + filtro/group-by "Destination Office". Suite 201/0/0, UI verificada |
| TASK-003 | Orden de la lista por fecha de ingreso (más reciente primero) | Ale Gallo | XS | Done | `_order = "intake_date desc, id desc"`. Suite 236/0/0; UI verificada |
| TASK-004 | Búsqueda y group-by por Jurisdicción en la lista | Ale Gallo | XS | Done | Cierra IDEA 1. Campo buscable + group-by (se descartó searchpanel por cardinalidad). Suite 246/0/0; UI verificada |
