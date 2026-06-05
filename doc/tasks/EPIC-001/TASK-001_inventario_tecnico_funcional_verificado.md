# EPIC-001 / TASK-001 — Inventario técnico-funcional verificado

Estado: Draft
Modo: L
Riesgo: medio
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: N/A

## Objetivo

Reconciliar la documentación consolidada de `me` (`architecture.md`, `workflows.md`,
`models.md`, `business_rules.md`) contra el código real, y cerrar las inconsistencias
(§7) y aspectos inciertos (§8) heredados del análisis original.

## Contexto mínimo

`architecture.md` es un snapshot del 2026-03-26 parcialmente histórico; `workflows.md`
es más reciente (#021–#030). El `_legacy_backlog.md` también está desfasado (p.ej.
#031 figura `[IDEA]` pero ya está commiteado). Fuente de verdad: `me/models/`,
`me/views/`, `me/security/`, `me/data/`.

## Alcance

Incluye:

- verificar modelos, campos, computed, métodos y constraints reales vs `models.md`/`architecture.md`;
- confirmar el comportamiento de los workflows reales vs `workflows.md`;
- resolver las inconsistencias §7 (ai-context inexistente, herencia `_inherits`,
  movimientos automáticos, append-only, etc.) y los aspectos §8;
- actualizar los docs `doc/project/me/*` con lo verificado y datar la vigencia.

No incluye:

- cambios de código (salvo que se decida abrir una task de fix aparte);
- baseline de seguridad (TASK-002) ni de tests (TASK-003).

## Acceptance criteria

- [ ] `architecture.md`, `workflows.md`, `models.md`, `business_rules.md`
  reflejan el estado **actual** del código, con marcas de vigencia.
- [ ] Cada inconsistencia §7 y aspecto incierto §8 queda: resuelto (con referencia a
  código) o reclasificado como pregunta/riesgo/`N/A` justificado.
- [ ] Estado real de #031 (y cualquier otro desfase del legacy) confirmado.
- [ ] Lista de deltas doc↔código registrada en la task card.

## Plan técnico preliminar

Lectura dirigida de `me/models/document_exp.py`, `document_movement.py`,
`dependence_ext.py`, vistas y `me/data/`. Sin modificar código.

## Riesgos

- Doc consolidada parcialmente histórica: no asumir sus afirmaciones como vigentes.
- No inventar reglas: lo ambiguo queda como pregunta abierta.

## Tests evidenciados

- Estado: N/A + motivo — task de relevamiento documental; no modifica código.

## Estado / próximo paso

Draft, sembrada en el bootstrap. Próximo paso: `/prepare-task` o `/product-spec` para
afinar criterios antes de relevar.

## Resultado / cierre

Pendiente.
