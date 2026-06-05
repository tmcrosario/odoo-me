# Índice global de tasks — odoo-me

Las tasks viven agrupadas por épica bajo `doc/tasks/EPIC-XXX/`. Cada épica tiene su
`_index.md`. El bootstrap del framework se registra en `SETUP-001` (fuera de épica).

Nomenclatura:

- Épica: `EPIC-001` · Task: `TASK-004` · Referencia: `EPIC-001/TASK-004`
- Archivo: `doc/tasks/EPIC-001/TASK-004_titulo_corto.md`

| Referencia | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| SETUP-001 | Bootstrap del framework SDD en odoo-me | Ale Gallo | L | In progress | Port del framework; ver task card |
| EPIC-001/TASK-001 | Inventario técnico-funcional verificado | sin asignar | L | Draft | Reconciliar doc ↔ código |
| EPIC-001/TASK-002 | Baseline de seguridad (ACL/grupos/record rules) | sin asignar | M | Draft | Completa `security.md` |
| EPIC-001/TASK-003 | Baseline de tests (inventario y gaps) | sin asignar | M | Draft | Completa `tests_plan.md` |
| EPIC-001/TASK-004 | Investigación: filtrado de jurisdicciones del DEM (#033) | sin asignar | M | Draft | Diagnóstico (datos/lógica/intencional) |

> EPIC-002 (Integración ME ↔ JUNCO) está en Draft **sin tasks aún**: requiere
> `/product-spec` para cerrar decisiones abiertas antes de abrir una task.
