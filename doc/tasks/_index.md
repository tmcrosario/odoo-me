# Índice global de tasks — odoo-me

Las tasks viven agrupadas por épica bajo `doc/tasks/EPIC-XXX/`. Cada épica tiene su
`_index.md`. El bootstrap del framework se registra en `SETUP-001` (fuera de épica).

Nomenclatura:

- Épica: `EPIC-001` · Task: `TASK-004` · Referencia: `EPIC-001/TASK-004`
- Archivo: `doc/tasks/EPIC-001/TASK-004_titulo_corto.md`

| Referencia | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| SETUP-001 | Bootstrap del framework SDD en odoo-me | Ale Gallo | L | Done | Port del framework completo (pasos A–D) |
| EPIC-001/TASK-001 | Inventario técnico-funcional verificado | sin asignar | L | Draft | Reconciliar doc ↔ código |
| EPIC-001/TASK-002 | Baseline de seguridad (ACL/grupos/record rules) | sin asignar | M | Draft | Completa `security.md` |
| EPIC-001/TASK-003 | Baseline de tests (inventario y gaps) | sin asignar | M | Draft | Completa `tests_plan.md` |
| EPIC-001/TASK-004 | Investigación: filtrado de jurisdicciones del DEM (#033) | sin asignar | M | Draft | Diagnóstico (datos/lógica/intencional) |
| EPIC-003/TASK-001 | Filtro por usuario poseedor en la vista de lista | sin asignar | S | Draft | UI sobre `current_holder_id`; sin cambios de modelo |
| EPIC-003/TASK-002 | Filtro por oficina (ubicación actual) en la vista de lista | sin asignar | L | Draft | Campo persistente nuevo; contrato previo |
| EPIC-004/TASK-001 | Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO) | sin asignar | L | Implementada (tests OK) | Pendiente push ME + deploy joint con odoo-junco EPIC-010 (`-u me,junco`) |

> EPIC-002 (Integración ME ↔ JUNCO) está gobernada en `odoo-junco` (puntero local,
> sin tasks de integración acá).
