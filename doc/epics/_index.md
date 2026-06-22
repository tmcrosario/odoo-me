# Índice de épicas — odoo-me

Las épicas agrupan capacidades o líneas funcionales. Las tasks viven bajo
`doc/tasks/EPIC-XXX/`.

| Épica | Título | Módulo | Estado | Notas |
| --- | --- | --- | --- | --- |
| EPIC-001 | Reverse-engineering + baseline de mesa de entradas | `me` | Done (develop) | 4/4 tasks Done; doc canónica verificada y datada vs código; §7/§8 reconciliados |
| EPIC-002 | Integración ME ↔ JUNCO (proceso licitatorio) | `me` (consumido por `junco`) | Gobernada en `odoo-junco` | Implementada/documentada en JUNCO. Acá: solo contrato de campos (input de EPIC-001) + decisión #4 (visibilidad ME) parkeada. No abrir tasks de integración acá |
| EPIC-003 | Usabilidad y filtros de la vista de expedientes | `me` | Done (develop) | Filtros por usuario (S) y por oficina interna de destino (L). Ambas tasks Done; suite 201/0/0; UI verificada. Deploy a prod diferido |
| EPIC-004 | Reacotamiento de la carga de ME: traspaso de clasificación a JUNCO | `me` (+ `junco`) | Done (develop) | DEM cede jurisdiction/source a JUNCO vía `action_set_origin_from_junco`; 1er movimiento DEM→TMC desacoplado. Validada end-to-end en me2 (`-u me,junco`); deploy a prod diferido. Contraparte junco EPIC-010 Done |
| EPIC-005 | Deuda técnica (limpieza post-baseline) | `me` | Draft | Follow-ups de EPIC-001/TASK-001: remover `allowed_dependence_ids` (8.6) + decidir declarar `raa` en manifest (8.8) |
