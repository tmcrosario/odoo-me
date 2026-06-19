# EPIC-001 / TASK-002 — Baseline de seguridad (ACL/grupos/record rules)

Estado: Done
Modo: M
Riesgo: medio (toca lectura de security; sin cambios)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: N/A

## Objetivo

Completar `doc/project/me/security.md` (hoy stub) con el baseline real de seguridad
del módulo `me`: grupos, ACL (`ir.model.access.csv`), record rules y reglas de
poseedor enforced en backend.

## Contexto mínimo

`security.md` recogió lo conocido de `system_narrative` y de #018/#027/#028. Falta
verificar el contenido real de `me/security/*` y mapear permisos por grupo. El
análisis original (§8.5) dudaba de la existencia de `ir.model.access.csv`; la
narrativa (2026-03-31) afirma que existe para `me.document_exp` y
`me.document_movement`. A confirmar contra el código.

## Alcance

Incluye:

- inventariar `me/security/*` (CSV, record rules, grupos XML);
- mapear permisos CRUD por grupo y modelo (#018 matriz de permisos);
- documentar las reglas de poseedor en `write()` (#027/#028/#029);
- confirmar si `tmc`/`raa` proveen ACL para modelos usados por `me`.

No incluye:

- cambios de permisos o de código;
- tests (se cubren en TASK-003).

## Acceptance criteria

- [x] `security.md` lista grupos (con `implied_ids`), ACL y record rules reales con ref a
  archivo. Record rules: **no hay `ir.rule`** → la seguridad de fila/operación es por guards.
- [x] Matriz permisos CRUD × grupo × modelo completa (2 modelos × 3 grupos).
- [x] Caminos negativos sensibles identificados (mapeados a tests de `tests_plan.md`).
- [x] Dudas §8.5 resueltas: `ir.model.access.csv` **existe** y se documentó su contenido.

## Plan técnico preliminar

Lectura de `me/security/`, grupos en XML y guards en `me/models/*.py`. Sin modificar.

## Riesgos

- Security es área sensible: no proponer cambios en esta task; solo documentar AS-IS.

## Tests evidenciados

- Estado: N/A + motivo — relevamiento de seguridad; no modifica código.

## Estado / próximo paso

**Done.** `security.md` completado con el baseline verificado. Relevamiento read-only, sin
cambios de permisos ni código.

## Resultado / cierre

Cerrada (Done) el 2026-06-19. Entregado en `doc/project/me/security.md`:
- **Grupos** (`me_groups.xml`): `group_user` (⇒ `tmc.group_user`), `group_manager`
  (⇒ user + `tmc.group_manager`; `implied_by base.group_erp_manager`), `group_read_only`.
- **Matriz ACL** real (`ir.model.access.csv`): 2 modelos × 3 grupos; user sin unlink,
  read_only solo lectura. §8.5 resuelto (el CSV existe).
- **Record rules:** no hay `ir.rule` → la seguridad de fila/operación se hace por **guards
  imperativos** en `write()` (de ahí el insight: el CSV es permisivo, el código restringe).
- **Guards documentados:** `me.document_exp.write()` (#027/#029 + canal EPIC-004),
  `me.document_movement.write()` (#028: último movimiento + poseedor + campos editables).
- **`sudo()`** como fronteras deliberadas (RAA, campos delegados `tmc.document`, canal JUNCO).
- Caminos negativos mapeados a tests; ACL de modelos externos (`tmc`/`raa`) aclarada.
