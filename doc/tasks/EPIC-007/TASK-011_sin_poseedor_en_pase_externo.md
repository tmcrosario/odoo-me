# EPIC-007 / TASK-011 — Un pase a una oficina externa no lleva poseedor

Estado: Done
Modo: L
Riesgo: medio (regla de negocio que vacía `user_id` al guardar; cambia el poseedor calculado)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-10-30
- Notas de coordinación: decisión del usuario (opción b). Se avisó a la sesión de `demo-junco`. JUNCO no
  crea movimientos de ME fuera de sus tests (`test_origin_filters.py`, que sigue pasando).

## Objetivo

Que un pase hacia una dependencia no interna no tenga poseedor, ni por la pantalla ni por ORM/RPC.

## Alcance

Incluye:

- campo relacionado `destination_is_internal` (no almacenado) en `me.document_movement`;
- vista: `user_id` de solo lectura cuando el destino no es interno (lista y popup del expediente);
- backend: `create()` y `write()` vacían `user_id` si el destino es externo, venga o no la clave (sin ella, el
  default del campo lo llenaría con el usuario de sesión);
- 5 tests nuevos en `TestMovementPoseedor027` y fixtures de 6 tests existentes que usaban un destino externo
  con poseedor;
- traducción del campo nuevo, docs (`security.md`, `workflows.md`, `models.md`, `business_rules.md`).

No incluye: tocar los pases ya cargados, ni la regla del reingreso (lo carga un manager, ya documentado).

## Acceptance criteria

- [x] Crear un pase a un destino externo con `user_id` lo deja vacío.
- [x] Escribir un destino externo (o un poseedor en un pase externo) lo deja vacío.
- [x] Un pase a un destino interno conserva su poseedor.
- [x] Suite `/me` verde con evidencia.
- [x] Prueba manual de UI: en un pase externo el poseedor queda vacío al guardar (OK del usuario, 2026-10-30).
- [x] Un pase externo que llega sin `user_id` (campo readonly, no viaja en el guardado) no recibe el default del
      usuario de sesión. Hallado en la prueba de UI (proceso 20 de `practica`).

## Tests evidenciados

- Suite `/me` en `me_test`: `0 failed, 0 error(s) of 273 tests`.
- Suite `/junco` (solo lectura): `0 failed, 4 error(s) of 765 tests`; los 4 son errores de traducciones `es_AR`
  (idioma no cargado en `me_test`), ajenos a este cambio.

## Estado / próximo paso

Cerrada. Sin pendientes.

## Resultado

Un pase a una oficina externa queda sin poseedor, por pantalla y por ORM/RPC.
