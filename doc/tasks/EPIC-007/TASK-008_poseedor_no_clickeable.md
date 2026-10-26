# EPIC-007 / TASK-008 — Poseedor no clickeable en la grilla de movimientos

Estado: Done
Modo: XS
Riesgo: bajo (opción nativa de la vista; sin lógica, campos ni ACL)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-10-26
- Notas de coordinación: pedido del usuario (`brainstorming.md` IDEA 9).

## Objetivo

Que en la solapa Movements del expediente el poseedor (`user_id`) no se pueda abrir como link al usuario.

## Alcance

Incluye: `options="{'no_open': True}"` en `user_id`, en la lista y en el popup de movimiento de
`document_exp_views.xml`. El campo sigue siendo seleccionable.

No incluye: `movement_views.xml` (sin menú ni acción), ni cambios de lógica.

## Acceptance criteria

- [x] El poseedor se muestra como texto en la lista y en el popup, sin link al usuario.
- [x] Prueba manual de UI (OK del usuario, 2026-10-26).

## Tests evidenciados

Cambio solo de vista (opción nativa de Odoo). Suite `/me`: `0 failed, 0 error(s) of 265 tests`.

## Estado / próximo paso

Cerrada. Sin pendientes.

## Resultado

El poseedor se ve como texto en la grilla y en el popup de movimientos.
