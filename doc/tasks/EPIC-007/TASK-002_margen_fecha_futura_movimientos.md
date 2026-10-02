# EPIC-007 / TASK-002 — Tolerar saltos de reloj en la fecha no futura de movimientos

Estado: Done
Modo: S
Riesgo: bajo (margen de 60 s en un constraint existente; sin campos ni datos)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done, retroactiva)
- Fecha de toma: 2026-09-15
- Notas de coordinación: reportado por la sesión de `odoo-junco`: su suite fallaba de forma
  intermitente con "Movement date cannot be in the future." Commit `04bbe54`.

## Objetivo

Que un movimiento con fecha "ahora" no falle por un salto del reloj de pared entre que se setea la
fecha y se valida el constraint.

## Alcance

Incluye:

- `_check_date_not_future` compara contra `now() + _FUTURE_DATE_TOLERANCE` (60 s, a nivel timestamp);
- 3 tests con `now()` congelado por `patch` (retroceso de reloj, borde de 60 s, 61 s);
- corregir `test_same_path_different_date_does_not_raise`, que usaba las 08:00/09:00 UTC de hoy y
  fallaba entre las 21 y las 06 (hora Argentina) con el mismo mensaje.

No incluye: comparar por día (descartado: aceptaría horas posteriores de hoy).

## Acceptance criteria

- [x] Un movimiento "ahora" con el reloj retrocedido unos segundos se acepta.
- [x] 60 s de adelanto se aceptan y 61 s se rechazan (el valor queda fijado por tests).
- [x] Una fecha de +1 día sigue rechazándose.
- [x] Suite `/me` verde con evidencia.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `doc/project/me/tests_plan.md`
- Fecha: 2026-09-15
- Resultado: **0 failed, 0 error(s) of 258 tests**. Sin el fix, el test del retroceso de reloj falla
  con el mismo `ValidationError`. Aplicado a me2 y junco_demo.

## Estado / próximo paso

**Done.** Push: usuario. **La causa raíz no se pudo reproducir con el reloj real** (25 s de medición
sin retrocesos); el fix cubre el caso que sí puede disparar el error. Si el intermitente reaparece, la
causa es otra.

## Resultado / cierre

Cerrada el 2026-09-15 sobre `develop`. Regla documentada en `business_rules.md` (Integridad de
movimientos) y `workflows.md`.
