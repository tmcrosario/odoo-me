# EPIC-007 / TASK-014 — El Responsable corrige las fojas de ingreso

Estado: Done
Modo: L
Riesgo: medio-alto (cambia una regla de negocio: hoy `fojas` es de solo lectura al guardar, también para el Responsable; además reescribe pases automáticos)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-11-18
- Dependencia: conviene después de TASK-013 (`current_fojas`), porque la corrección se ve a través de ese campo.
- Notas de coordinación: ninguna con junco (no cambia contratos que ellos usen).

## Objetivo

Que si quien da de alta carga mal las fojas, un **Responsable de ME** (`me.group_manager`) pueda corregirlas, y
que la corrección se refleje en los pases automáticos del ingreso.

## Alcance

Incluye:

- vista: con el expediente guardado, `fojas` de ingreso visible y editable **solo para `me.group_manager`**
  (para el resto sigue sin verse, ver TASK-013);
- backend: al escribir `fojas` en `me.document_exp`, se copia el nuevo valor a los **dos pases automáticos**
  del ingreso (origen → TMC y TMC → ME). Los pases manuales no se tocan;
- tests (corrección por Responsable, propagación a los dos pases automáticos, no propagación a pases manuales,
  el operativo sigue sin poder escribirlo) y docs (`business_rules.md` regla "Fojas — bloqueo
  post-creación", `security.md`, `workflows.md`, `tests_plan.md`).

No incluye:

- rechazar el ingreso con 0 fojas (→ IDEA 15 del brainstorming, decisión del usuario: por ahora solo idea);
- historial de cambios de fojas (→ IDEA 14 del brainstorming; **decisión del usuario: por ahora solo idea,
  no se implementa**);
- editar las fojas de los pases manuales (sigue la regla actual: el poseedor corrige el último);
- cambiar quién puede escribir por ORM (ya es solo el Responsable).

## Reglas decididas (usuario)

- Opción A: el Responsable puede cambiar la cantidad de fojas del expediente.
- La corrección baja a los **dos pases automáticos** del ingreso (confirmado), y no a los pases manuales.

## Acceptance criteria

- [x] Un Responsable ve y edita `fojas` de ingreso con el expediente guardado.
- [x] Un usuario sin rol Responsable no lo ve ni lo puede escribir (ORM/API incluidos).
- [x] Al guardar un cambio de `fojas`, los dos pases automáticos quedan con el valor nuevo.
- [x] Los pases manuales conservan su `fojas`.
- [x] En un expediente con solo los pases automáticos, `current_fojas` muestra el valor corregido.
- [x] Guardar sin cambiar `fojas` no reescribe pases.
- [x] Suite `/me` verde, con evidencia (`... of N tests`, N > 0).
- [x] Prueba manual de UI en `practica` con un usuario Responsable y uno operativo (OK del usuario, 2026-11-18).
- [x] Documentada la regla nueva (reemplaza el bloqueo post-creación para el Responsable).

## Riesgos y preguntas abiertas

- Sin historial, la corrección no deja rastro de quién cambió qué (aceptado por el usuario por ahora).
- Los pases automáticos son de solo lectura en la vista: la propagación debe hacerse por backend, sin
  depender de la UI.

## Tests evidenciados

- Suite `/me` en `me_test`: `0 failed, 0 error(s) of 293 tests` (288 previos + 5 nuevos en `TestFojasLock`).
- Aplicado a `practica` (`-u me --i18n-overwrite` + restart). Prueba manual de UI: OK del usuario (2026-11-18).

## Estado / próximo paso

Cerrada. Sin pendientes.

## Resultado

El Responsable corrige las fojas de ingreso y el valor se copia a los dos pases automáticos; el operativo sigue sin acceso.
