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
| EPIC-001/TASK-002 | Baseline de seguridad (ACL/grupos/record rules) | sin asignar | M | Done | `security.md` completo: grupos, matriz ACL, sin record rules (seguridad por guards), sudo |
| EPIC-001/TASK-003 | Baseline de tests (inventario y gaps) | sin asignar | M | Done | `tests_plan.md` completo: 23 clases/201 métodos, cobertura, 5 gaps (CI no corre tests) |
| EPIC-001/TASK-004 | Investigación: filtrado de jurisdicciones del DEM (#033) | sin asignar | M | Done | Causa: dato (falta nomenclador 2025) + intencional (multi-año). No es bug de me. Fix en tmc_data (externo), anotado en business_rules |
| EPIC-003/TASK-001 | Filtro por usuario poseedor en la vista de lista | sin asignar | S | Done | UI sobre `current_holder_id`; buscable + group-by. Verificada en UI |
| EPIC-003/TASK-002 | Filtro por oficina (ubicación actual) en la vista de lista | sin asignar | L | Done | Campo `current_location_dependence_id` (internal-only) + filtro/group-by "Destination Office". Suite 201/0/0 |
| EPIC-004/TASK-001 | Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO) | sin asignar | L | Done (develop) | Validada end-to-end en me2; deploy a prod diferido (usuario). JUNCO EPIC-010 Done |

> EPIC-002 (Integración ME ↔ JUNCO) está gobernada en `odoo-junco` (puntero local,
> sin tasks de integración acá).
