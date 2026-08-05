# Índice global de tasks — odoo-me

Las tasks viven agrupadas por épica bajo `doc/tasks/EPIC-XXX/`. Cada épica tiene su
`_index.md`. El bootstrap del framework se registra en `SETUP-001` (fuera de épica).

Nomenclatura:

- Épica: `EPIC-001` · Task: `TASK-004` · Referencia: `EPIC-001/TASK-004`
- Archivo: `doc/tasks/EPIC-001/TASK-004_titulo_corto.md`

| Referencia | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| SETUP-001 | Bootstrap del framework SDD en odoo-me | Ale Gallo | L | Done | Port del framework completo (pasos A–D) |
| EPIC-001/TASK-001 | Inventario técnico-funcional verificado | sin asignar | L | Done | §7/§8 reconciliados; architecture datado; workflows corregido; #031 confirmado |
| EPIC-001/TASK-002 | Baseline de seguridad (ACL/grupos/record rules) | sin asignar | M | Done | `security.md` completo: grupos, matriz ACL, sin record rules (seguridad por guards), sudo |
| EPIC-001/TASK-003 | Baseline de tests (inventario y gaps) | sin asignar | M | Done | `tests_plan.md` completo: 23 clases/201 métodos, cobertura, 5 gaps (CI no corre tests) |
| EPIC-001/TASK-004 | Investigación: filtrado de jurisdicciones del DEM (#033) | sin asignar | M | Done | Causa: dato (falta nomenclador 2025) + intencional (multi-año). No es bug de me. Fix en tmc_data (externo), anotado en business_rules |
| EPIC-003/TASK-001 | Filtro por usuario poseedor en la vista de lista | sin asignar | S | Done | UI sobre `current_holder_id`; buscable + group-by. Verificada en UI |
| EPIC-003/TASK-002 | Filtro por oficina (ubicación actual) en la vista de lista | sin asignar | L | Done | Campo `current_location_dependence_id` (internal-only) + filtro/group-by "Destination Office". Suite 201/0/0 |
| EPIC-004/TASK-001 | Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO) | sin asignar | L | Done (develop) | Validada end-to-end en me2; deploy a prod diferido (usuario). JUNCO EPIC-010 Done |
| EPIC-004/TASK-002 | Carga de jurisdicción/origen en DEM con tema Nota | Ale Gallo | L | Done (develop) | Excepción a TASK-001: las Notas no van a JUNCO → ME carga al ingreso. + validaciones de fecha + label i18n. Suite 233/0/0; UI verificada en me2 |
| EPIC-004/TASK-003 | 1er movimiento de una Nota: origen = jurisdicción | Ale Gallo | S | Done (develop) | Habilitada por TASK-002. Compras intactas; el origen es snapshot al crear. Suite 236/0/0; UI verificada |
| EPIC-004/TASK-004 | Acotar el subtema de Licitación a Privada/Pública (+ ocultar sin hijos) | Ale Gallo | S | Done (develop) | Domain de vista en ME (no toca `tmc_data`); alinea con lo que JUNCO consume (confirmado). Suite 241/0/0; UI verificada |
| EPIC-003/TASK-003 | Orden de la lista por fecha de ingreso (más reciente primero) | Ale Gallo | XS | Done (develop) | `_order = "intake_date desc, id desc"`. Suite 236/0/0; UI verificada |
| EPIC-003/TASK-004 | Búsqueda y group-by por Jurisdicción en la lista | Ale Gallo | XS | Done (develop) | Cierra IDEA 1. Campo buscable + group-by (searchpanel descartado por cardinalidad). Suite 246/0/0; UI verificada |
| EPIC-005/TASK-001 | Remover campo muerto `allowed_dependence_ids` | sin asignar | XS | Done | Removido; sin referencias; suite 201/0/0 |
| EPIC-005/TASK-002 | Decidir/declarar dependencia `raa` en el manifest | sin asignar | S | Done | No declarable (circular `raa→me`); acoplamiento implícito documentado |
| EPIC-006/TASK-001 | Botón "Save" textual visible solo en dirty (form de expediente) | Ale Gallo | S | Done | Portado de `junco:EPIC-008/TASK-004`; primer asset frontend de `me`; suite 209/0/0; UI verificada en me2 |
| EPIC-006/TASK-002 | Indicador "En Legajo Nº X" en el form + filtro "Adjuntos a Legajo" | Ale Gallo | S | Done | Computed del último movimiento a LEG + filtro de lista; strings inglés + i18n; suite 246/0/0; UI verificada |

> EPIC-002 (Integración ME ↔ JUNCO) está gobernada en `odoo-junco` (puntero local,
> sin tasks de integración acá).
>
> **`junco:EPIC-011` y `junco:EPIC-015`** también están gobernadas en `odoo-junco` (repo dueño) y
> aterrizaron **código** en `me` sin card local — es correcto: no se abren cards espejo. Ver las
> filas-puntero en [`../epics/_index.md`](../epics/_index.md) y la verdad durable en las canónicas
> (`security.md`, `business_rules.md`, `models.md`, `tests_plan.md`).
