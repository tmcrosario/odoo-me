# EPIC-007 / TASK-001 — Gobernar por ACL la escritura de fecha de GD por SQL crudo

Estado: Done
Modo: L
Riesgo: medio (security/ACL; el alta del operativo corre por el mismo camino)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done, retroactiva)
- Fecha de toma: 2026-08-14
- Notas de coordinación: pedido de la sesión de `odoo-junco` (deuda detectada por la auditoría de
  `junco:EPIC-015`). Commit `4d53975`.

## Objetivo

`_update_document_date()` actualiza `tmc.document.date` con SQL crudo, que saltea `ir.model.access` y
las record rules: la escritura de esa fecha no estaba gobernada. Re-imponer el ACL **sin quitar el
SQL**, que existe para escapar de la regla año == período de `tmc.document`.

## Alcance

Incluye:

- `self.document_id.check_access('write')` justo antes del `cr.execute`;
- `record.sudo()._update_document_date()` en `create()`: el seteo de fecha es parte de la creación
  elevada del padre (EPIC-015); sin el `sudo` el check cortaba el alta del operativo, que solo lee
  `tmc.document`;
- test de regresión y documentación en `security.md`.

No incluye: quitar el SQL, ni cambiar la regla de período.

## Acceptance criteria

- [x] Usuario con `write` sobre `tmc.document`: comportamiento idéntico.
- [x] Usuario sin `write` que llega a `_update_document_date()`: `AccessError` (antes pasaba en silencio).
- [x] El alta del operativo sigue funcionando (`test_me_user_can_create_expediente`).
- [x] Suite `/me` verde con evidencia.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `doc/project/me/tests_plan.md` (`me_test`, `--addons-path` completo)
- Fecha: 2026-08-14
- Resultado: **0 failed, 0 error(s) of 255 tests**. Test nuevo
  `TestMeSecurity.test_gd_read_only_cannot_update_document_date` (asserta que el corte viene de
  `tmc.document`). Aplicado a me2 + restart.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido. Docs actualizadas: `security.md` (bypass
gobernado + fila de `sudo()`), `tests_plan.md`, `epics/_index.md`.

## Resultado / cierre

Cerrada el 2026-08-14 sobre `develop`. La escritura de la fecha queda gobernada: el camino por ACL
real es `write()` (solo managers, sin `sudo`); el alta corre elevada como el resto de la creación.
Confirmado con junco, que no toca el check ni el tipo de excepción.
