# EPIC-007 / TASK-014 — El Responsable corrige las fojas de ingreso

Estado: Draft
Modo: L
Riesgo: medio-alto (cambia una regla de negocio: hoy `fojas` es de solo lectura al guardar, también para el Responsable; además reescribe pases automáticos)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: sin tomar
- Dependencia: conviene después de TASK-013 (`current_fojas`), porque la corrección se ve a través de ese campo.
- Notas de coordinación: ninguna con junco (no cambia contratos que ellos usen).

## Objetivo

Que si quien da de alta carga mal las fojas, un **Responsable de ME** (`me.group_manager`) pueda corregirlas, y
que la corrección se refleje en los pases automáticos del ingreso. Además, que un expediente **no pueda
ingresar con 0 fojas**.

## Alcance

Incluye:

- vista: con el expediente guardado, `fojas` de ingreso visible y editable **solo para `me.group_manager`**
  (para el resto sigue sin verse, ver TASK-013);
- backend: al escribir `fojas` en `me.document_exp`, se copia el nuevo valor a los **dos pases automáticos**
  del ingreso (origen → TMC y TMC → ME). Los pases manuales no se tocan;
- validación: `fojas` de ingreso debe ser mayor que 0, al crear y al corregir (en `create()`/`write()`, no
  `@api.constrains`, para que los expedientes ya cargados con 0 no fallen al editar otros campos);
- tests (corrección por Responsable, propagación a los dos pases automáticos, no propagación a pases manuales,
  el operativo sigue sin poder escribirlo) y docs (`business_rules.md` regla "Fojas — bloqueo
  post-creación", `security.md`, `workflows.md`, `tests_plan.md`).

No incluye:

- historial de cambios de fojas (→ IDEA 14 del brainstorming; **decisión del usuario: por ahora solo idea,
  no se implementa**);
- editar las fojas de los pases manuales (sigue la regla actual: el poseedor corrige el último);
- cambiar quién puede escribir por ORM (ya es solo el Responsable).

## Reglas decididas (usuario)

- 2026-11-18: un expediente no puede cargarse con 0 fojas (hallado probando TASK-013 en `practica`).
- Opción A: el Responsable puede cambiar la cantidad de fojas del expediente.
- La corrección baja a los **dos pases automáticos** del ingreso (confirmado), y no a los pases manuales.

## Acceptance criteria

- [ ] Un Responsable ve y edita `fojas` de ingreso con el expediente guardado.
- [ ] Un usuario sin rol Responsable no lo ve ni lo puede escribir (ORM/API incluidos).
- [ ] Al guardar un cambio de `fojas`, los dos pases automáticos quedan con el valor nuevo.
- [ ] Los pases manuales conservan su `fojas`.
- [ ] En un expediente con solo los pases automáticos, `current_fojas` muestra el valor corregido.
- [ ] Guardar sin cambiar `fojas` no reescribe pases.
- [ ] Crear un expediente con `fojas` 0 (o negativo) falla con un mensaje claro; corregir a 0 también.
- [ ] Un expediente ya cargado con 0 fojas sigue pudiéndose editar en otros campos.
- [ ] Suite `/me` verde, con evidencia (`... of N tests`, N > 0).
- [ ] Prueba manual de UI en `practica` con un usuario Responsable y uno operativo.
- [ ] Documentada la regla nueva (reemplaza el bloqueo post-creación para el Responsable).

## Riesgos y preguntas abiertas

- Crear sin `fojas` hoy toma el default 0: la validación rompe los tests y las cargas por script que no pasan
  `fojas` (ajustar fixtures de `me`; **verificar `odoo-junco`** y la migración, que crean expedientes por ORM; si
  alguno omite `fojas`, avisar a `demo-junco` / `odoo-me-8a` antes de implementar).
- Sin historial, la corrección no deja rastro de quién cambió qué (aceptado por el usuario por ahora).
- Los pases automáticos son de solo lectura en la vista: la propagación debe hacerse por backend, sin
  depender de la UI.

## Tests evidenciados

PENDIENTE USER-RUN.

## Estado / próximo paso

Draft. Falta el OK del usuario a los criterios y asignar la task antes de implementar. Sin código tocado.

## Resultado

(pendiente)
