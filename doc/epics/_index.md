# Índice de épicas — odoo-me

Las épicas agrupan capacidades o líneas funcionales. Las tasks viven bajo
`doc/tasks/EPIC-XXX/`.

| Épica | Título | Módulo | Estado | Notas |
| --- | --- | --- | --- | --- |
| EPIC-001 | Reverse-engineering + baseline de mesa de entradas | `me` | Draft | AS-IS verificado; cierra inconsistencias e inciertos del análisis |
| EPIC-002 | Integración ME ↔ JUNCO (proceso licitatorio) | `me` (consumido por `junco`) | Gobernada en `odoo-junco` | Implementada/documentada en JUNCO. Acá: solo contrato de campos (input de EPIC-001) + decisión #4 (visibilidad ME) parkeada. No abrir tasks de integración acá |
| EPIC-003 | Usabilidad y filtros de la vista de expedientes | `me` | Draft | Filtros por usuario (S) y por oficina/ubicación actual (L, campo persistente nuevo) |
