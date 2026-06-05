# EPIC-001 / TASK-002 — Baseline de seguridad (ACL/grupos/record rules)

Estado: Draft
Modo: M
Riesgo: medio (toca lectura de security; sin cambios)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
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

- [ ] `security.md` lista grupos, ACL y record rules reales con referencia a archivo.
- [ ] Matriz permisos CRUD × grupo × modelo completa.
- [ ] Caminos negativos sensibles identificados (con o sin test — se deriva a TASK-003).
- [ ] Dudas §8.5 resueltas (existe/qué contiene `ir.model.access.csv`).

## Plan técnico preliminar

Lectura de `me/security/`, grupos en XML y guards en `me/models/*.py`. Sin modificar.

## Riesgos

- Security es área sensible: no proponer cambios en esta task; solo documentar AS-IS.

## Tests evidenciados

- Estado: N/A + motivo — relevamiento de seguridad; no modifica código.

## Estado / próximo paso

Draft, sembrada en el bootstrap. Próximo paso: `/prepare-task`.

## Resultado / cierre

Pendiente.
