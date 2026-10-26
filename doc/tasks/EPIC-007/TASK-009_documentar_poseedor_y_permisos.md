# EPIC-007 / TASK-009 — Documentar que ser poseedor no da permisos

Estado: Done
Modo: XS
Riesgo: bajo (solo documentación)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada
- Fecha de toma: 2026-10-26
- Notas de coordinación: surgió de la prueba en `practica`: dos usuarios con solo ME / Read Only figuraban
  como poseedores y no veían "Add a line". El usuario decidió **no cambiar el código**.

## Objetivo

Dejar escrito el funcionamiento acordado del poseedor, para que no se lea como un defecto.

## Alcance

Incluye: notas en `security.md`, `workflows.md` y `business_rules.md`:

- el poseedor se elige entre todos los usuarios, sin filtro por grupo (lo elige el manager que carga el pase);
- ser poseedor no da permisos: el usuario del área de destino debe tener ME / User; es una condición de alta de
  usuarios, no de código;
- un destino externo deja el pase sin poseedor y el reingreso lo carga un manager.

No incluye: filtro de dominio en `user_id` / `default_responsible_id`, validación backend ni elevación de
permisos por ser poseedor (opciones descartadas por el usuario).

## Acceptance criteria

- [x] La regla queda escrita en las tres canónicas.
- [x] Sin cambios de código.

## Tests evidenciados

N/A: sin cambios de código.

## Resultado

El comportamiento queda documentado como decisión. Si más adelante molesta elegir a un usuario sin permiso,
la opción abierta es un aviso no bloqueante en la pantalla.
