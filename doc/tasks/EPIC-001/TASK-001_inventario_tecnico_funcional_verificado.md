# EPIC-001 / TASK-001 — Inventario técnico-funcional verificado

Estado: Done
Modo: L
Riesgo: medio
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
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

- [x] `architecture.md` (datada: §1–6 snapshot histórico, fuente de verdad = docs hermanos),
  `workflows.md` (verificada/datada, Workflow 4 corregido), `models.md`/`business_rules.md`/
  `security.md`/`tests_plan.md` (actualizados en EPIC-003/004 + TASK-002/003/004).
- [x] Cada §7 (8) y §8 (8) resuelto/obsoleto/reclasificado, con referencia a código.
- [x] #031 confirmado: searchpanel **implementado** (commit cf3951c, en la vista); `[IDEA]`
  del legacy es etiqueta vieja (el header del legacy ya lo flagea).
- [x] Deltas doc↔código registrados (abajo).

## Plan técnico preliminar

Lectura dirigida de `me/models/document_exp.py`, `document_movement.py`,
`dependence_ext.py`, vistas y `me/data/`. Sin modificar código.

## Riesgos

- Doc consolidada parcialmente histórica: no asumir sus afirmaciones como vigentes.
- No inventar reglas: lo ambiguo queda como pregunta abierta.

## Tests evidenciados

- Estado: N/A + motivo — task de relevamiento documental; no modifica código.

## Estado / próximo paso

**Done** el 2026-06-19. Las 5 pasadas completas (relevamiento read-only, sin cambios de código).

Pasadas: 1 §7 ✅ · 2 §8 ✅ · 3 cuerpo architecture.md (§1–6 datado) ✅ · 4 workflows.md
(verificado, Workflow 4 corregido) ✅ · 5 legacy (#031 confirmado) + cierre ✅.

**Follow-ups detectados (tasks de código aparte, NO en esta task doc-only):**
- 8.6 — `allowed_dependence_ids` es artefacto muerto → candidato a remoción (`[REM]`).
- 8.8 — `raa` dependencia implícita no declarada en el manifest → evaluar declararla
  (como se hizo con `tmc_data`); requiere aprobación de deps.

## Deltas doc↔código (acumulado)

**§7 Inconsistencias (pasada 1):**
- 7.1 `ai-context.md` "no existe" → **obsoleta**: ahora existe (creado post-snapshot).
- 7.2 RAA `[IDEA]` → **resuelta**: implementada (`create()` l.560 / `unlink()` l.711),
  documentada en `business_rules.md`; `docs/todo.md` migró a `_legacy_backlog`.
- 7.3 movimientos automáticos no documentados → **resuelta** (`business_rules.md`).
- 7.4 append-only sin enforcement → **reclasificada**: ACL (user sin unlink) + guard
  `write()` (#028) lo acotan; principio declarativo documentado (`business_rules`/`security`).
- 7.5 / 7.6 herencia no especificada → **resueltas**: `_inherits` explícito en `models.md`.
- 7.7 `document_topic_ids` invisible → **obsoleta**: removido de la vista post-snapshot.
- 7.8 tab Documentos Relacionados invisible → **documentada**: ahora "Related Documents"
  (l.115), invisible; limitación conocida en `business_rules.md`.

**§8 Aspectos inciertos (pasada 2):**
- 8.1 estados del expediente → **reclasificado**: sin `state`, limitación conocida (no incierto).
- 8.2 edición por estado → **reclasificado**: `N/A` mientras no haya estados (atado a 8.1).
- 8.3 `jurisdiction_dependence` vs `dependence_id` → **resuelto**: origen vs jurisdicción,
  documentado (`business_rules.md`, EPIC-004, multi-año).
- 8.4 "Mesa de Entradas" inexistente → **resuelto/documentado**: omite sin aviso; limitación
  conocida + gap de test.
- 8.5 `ir.model.access.csv` → **resuelto**: existe (TASK-002, `security.md`).
- 8.6 `allowed_dependence_ids` → **resuelto**: artefacto muerto (sin uso) → follow-up de remoción.
- 8.7 routing de movimientos posteriores → **reclasificado**: quién=resuelto (#027/#028); routing/continuidad=limitación conocida.
- 8.8 `raa` no declarada en manifest → **riesgo abierto**: dependencia implícita → follow-up.

**§1–6 / workflows / legacy (pasadas 3–5):**
- `architecture.md` §1–6: snapshot 2026-03-26 **datado como histórico**; nota de Vigencia
  ampliada apuntando a los docs hermanos como fuente de verdad (deltas EPIC-003/004).
- `workflows.md`: **Workflow 4 corregido** (1er movimiento usa `dependence_id`, EPIC-004);
  nota de vigencia con deltas EPIC-003/004.
- Legacy: #031 (searchpanel) confirmado implementado; `[IDEA]` stale ya flageado en el header.

## Resultado / cierre

Cerrada (Done) el 2026-06-19. Reconciliación documental completa de `me` (read-only): §7
(8) e §8 (8) cerrados, `architecture.md` datado como histórico con fuente de verdad en los
docs hermanos, `workflows.md` verificado y corregido (Workflow 4), #031 confirmado.
**Cierra EPIC-001** (4/4 tasks Done). Dos follow-ups de **código** quedaron registrados en
EPIC-005 (deuda técnica): remover `allowed_dependence_ids` (8.6) y decidir la declaración
de `raa` en el manifest (8.8).
