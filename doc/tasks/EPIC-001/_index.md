# EPIC-001 — Índice de tasks

Épica: `doc/epics/EPIC-001_baseline_mesa_de_entradas.md`

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Inventario técnico-funcional verificado | sin asignar | L | Draft | Reconciliar `architecture`/`workflows`/`models`/`business_rules` ↔ código; §7/§8 |
| TASK-002 | Baseline de seguridad (ACL/grupos/record rules) | sin asignar | M | Done | `security.md` completo: grupos, matriz ACL, sin record rules (seguridad por guards), sudo |
| TASK-003 | Baseline de tests (inventario y gaps) | sin asignar | M | Done | `tests_plan.md` completo: 23 clases/201 métodos, cobertura, 5 gaps (CI no corre tests) |
| TASK-004 | Investigación: filtrado de jurisdicciones del DEM (#033) | sin asignar | M | Done | Causa: dato (falta nomenclador 2025) + intencional (multi-año). Fix en tmc_data (externo) |
