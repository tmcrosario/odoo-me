# EPIC-007 / TASK-006 — Regla de poseedor también al crear un movimiento directo

Estado: Done
Modo: L
Riesgo: medio/alto (seguridad: regla de quién puede registrar un pase)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-10-26
- Notas de coordinación: decisión del usuario (opción a) a `brainstorming.md` IDEA 8. JUNCO no crea
  movimientos directamente (revisado); su suite no cambió por esto.

## Objetivo

Que un usuario que no es el poseedor del expediente no pueda registrar un pase por ORM/RPC. Antes lo
aceptaba el ACL (`create=1`) y lo convertía en poseedor sin pase.

## Alcance

Incluye:

- `me.document_movement.create()` aplica el mismo chequeo de poseedor que el guard de
  `me.document_exp.write()`;
- reemplazar el test que afirmaba lo contrario y agregar tests de los casos permitidos y rechazados;
- documentar en `security.md`, `business_rules.md`, `workflows.md`, `tests_plan.md`.

No incluye: cambiar el ACL del CSV, la UI, ni el guard de `write()` del expediente.

## Acceptance criteria

- [x] Un usuario ME no poseedor no puede crear un movimiento por ORM: `AccessError`.
- [x] El poseedor y los managers sí pueden.
- [x] El alta del expediente (movimientos automáticos, `me_create_in_progress`) no cambia.
- [x] El camino del formulario sigue funcionando.
- [x] Un no-manager no puede registrar más de un pase por expediente en un mismo guardado
      (`ValidationError`); un manager sí. Hallado en la prueba de UI del 2026-10-26 (EXP-016557-DEM/2026).
- [x] Si el expediente no tiene movimientos, cualquier usuario ME puede crear el primero.
- [x] `test_operator_can_create_new_movement` se reemplaza por `test_operator_holder_can_create_new_movement`.

## Tests evidenciados

- Nuevos en `TestMovementPoseedor027`: no poseedor rechazado, poseedor permitido, manager permitido,
  sin movimientos permitido, varios pases en un guardado (rechazado para no-manager, permitido para manager).
- Suite `/me` en `me_test`: `0 failed, 0 error(s) of 265 tests`.
- Suite `/junco` (solo lectura): `0 failed, 3 error(s) of 721 tests`; los 3 son `KeyError` de
  traducciones `es_AR` (idioma no cargado en `me_test`), ajenos a este cambio.

## Estado / próximo paso

Cerrada. UI verificada por el usuario (2026-10-26) en `practica`. Sin pendientes.

## Resultado

La regla de poseedor vale en el modelo, no solo en el formulario.
