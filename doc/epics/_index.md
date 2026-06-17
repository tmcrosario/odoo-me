# Índice de épicas — odoo-me

Las épicas agrupan capacidades o líneas funcionales. Las tasks viven bajo
`doc/tasks/EPIC-XXX/`.

| Épica | Título | Módulo | Estado | Notas |
| --- | --- | --- | --- | --- |
| EPIC-001 | Reverse-engineering + baseline de mesa de entradas | `me` | Draft | AS-IS verificado; cierra inconsistencias e inciertos del análisis |
| EPIC-002 | Integración ME ↔ JUNCO (proceso licitatorio) | `me` (consumido por `junco`) | Gobernada en `odoo-junco` | Implementada/documentada en JUNCO. Acá: solo contrato de campos (input de EPIC-001) + decisión #4 (visibilidad ME) parkeada. No abrir tasks de integración acá |
| EPIC-003 | Usabilidad y filtros de la vista de expedientes | `me` | Draft | Filtros por usuario (S) y por oficina/ubicación actual (L, campo persistente nuevo) |
| EPIC-004 | Reacotamiento de la carga de ME: traspaso de clasificación a JUNCO | `me` (+ `junco`) | Done (develop) | DEM cede jurisdiction/source a JUNCO vía `action_set_origin_from_junco`; 1er movimiento DEM→TMC desacoplado. Validada end-to-end en me2 (`-u me,junco`); deploy a prod diferido. Contraparte junco EPIC-010 Done |
