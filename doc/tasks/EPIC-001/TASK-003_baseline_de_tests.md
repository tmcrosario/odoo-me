# EPIC-001 / TASK-003 — Baseline de tests (inventario y gaps)

Estado: Done
Modo: M
Riesgo: bajo
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: N/A

## Objetivo

Completar `doc/project/me/tests_plan.md` (hoy stub) con el inventario real de tests de
`me`, su cobertura frente a las reglas activas y los gaps prioritarios.

## Contexto mínimo

El `_legacy_backlog.md` referencia tests por task (p.ej. `TestJurisdictionConditional012`).
Falta un mapa consolidado de qué cubre `me/tests/` hoy y dónde quedan huecos.

## Alcance

Incluye:

- inventariar `me/tests/` (clases, qué prueban);
- mapear cobertura contra las reglas activas de `business_rules.md` y los workflows;
- identificar gaps prioritarios (movimientos automáticos, poseedor, duplicados,
  bypass de fecha, reingreso institucional, permisos);
- confirmar disponibilidad de CI.

No incluye:

- escribir tests nuevos (se prioriza en tasks de implementación posteriores);
- correr la suite como criterio de cierre de esta task (es relevamiento).

## Acceptance criteria

- [x] `tests_plan.md` lista los tests existentes y qué reglas/workflows cubren (23 clases,
  201 métodos; tabla de inventario + mapa de cobertura contra `business_rules.md`).
- [x] Gaps priorizados registrados (5 gaps; el más alto: CI no corre los tests).
- [x] Estado de CI confirmado (`pipeline.yml` = build/Snyk/deploy; **no** corre tests).

## Plan técnico preliminar

Lectura de `me/tests/`. Opcionalmente correr la suite para confirmar que pasa
(evidencia user-run); no es bloqueante para el relevamiento.

## Riesgos

- Bajo. No modifica código.

## Tests evidenciados

- Estado: N/A + motivo — relevamiento de tests; no agrega ni modifica tests. Si se
  corre la suite para constatar estado, pegar evidencia acá.

## Estado / próximo paso

**Done.** `tests_plan.md` completado (inventario + cobertura + gaps + CI). Relevamiento
read-only, sin cambios de código. Los gaps quedan como insumo para tasks futuras (el de
CI es el más relevante; escribir tests nuevos no es parte de esta task).

## Resultado / cierre

Cerrada (Done) el 2026-06-19. Entregado en `doc/project/me/tests_plan.md`:
- Inventario: **23 clases, 201 métodos** (177 en `test_document_exp.py` + 24 en
  `test_document_movement.py`), con tabla clase→qué prueba→semilla.
- Mapa de cobertura contra las reglas activas de `business_rules.md` (mayoría ✅).
- **Gaps priorizados:** (1) ALTA — CI (`pipeline.yml`) no ejecuta la suite (solo
  build/Snyk/deploy); (2) MEDIA — aviso de duplicado de expediente sin test;
  (3-5) BAJA — multi-año, continuidad/append-only, camino negativo "ME inexistente".
- Estado de CI confirmado (no corre tests; verificación manual vía `me_test`).
