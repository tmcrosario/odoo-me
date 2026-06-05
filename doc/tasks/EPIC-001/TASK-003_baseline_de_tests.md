# EPIC-001 / TASK-003 — Baseline de tests (inventario y gaps)

Estado: Draft
Modo: M
Riesgo: bajo
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
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

- [ ] `tests_plan.md` lista los tests existentes y qué reglas/workflows cubren.
- [ ] Gaps priorizados registrados.
- [ ] Estado de CI confirmado.

## Plan técnico preliminar

Lectura de `me/tests/`. Opcionalmente correr la suite para confirmar que pasa
(evidencia user-run); no es bloqueante para el relevamiento.

## Riesgos

- Bajo. No modifica código.

## Tests evidenciados

- Estado: N/A + motivo — relevamiento de tests; no agrega ni modifica tests. Si se
  corre la suite para constatar estado, pegar evidencia acá.

## Estado / próximo paso

Draft, sembrada en el bootstrap. Próximo paso: `/prepare-task`.

## Resultado / cierre

Pendiente.
