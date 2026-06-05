# Antipatrones del framework

Top-8 errores típicos a evitar al usar el OADF. Si una PR cae en uno de estos, la
verificación debe rechazarla salvo override documentado.

Cada antipatrón lleva: **descripción**, **por qué pasa**, **consecuencia**,
**corrección concreta** y **ejemplo**. Cuando reabras una task con dudas, leé esta
sección antes de buscar más contexto.

---

## 1. Marcar `Done` sin pegar salida de tests

**Descripción.** La task pasa a `Done` y la sección "Tests evidenciados" dice `OK`
sin comando, sin fecha y sin salida.

**Por qué pasa.** Apuro de cierre, "OK" inferido del contexto, dev que corrió tests
pero olvidó pegar el resultado.

**Consecuencia.** Pérdida total de trazabilidad. En la próxima regresión nadie sabe
si los tests realmente pasaron.

**Corrección.** En M/L/XL, el bloque "Tests evidenciados" es **obligatorio**. El
validador rechaza `/doc-close` si está vacío. Aceptado `Estado: PENDIENTE USER-RUN`
con comando sugerido cuando el dev no pudo correrlos todavía.

**Ejemplo correcto:**

```md
## Tests evidenciados
- Estado: OK
- Comando: docker compose -f develop.yml run --rm odoo odoo -d test_db -u me --test-tags /me --stop-after-init --log-level=test
- Fecha: 2026-05-04
- Resultado: 47 passed, 0 failed
- Salida (resumen):
  ```text
  test_priority_field ... ok
  test_priority_default ... ok
  Ran 47 tests in 12.3s
  OK
  ```
```

---

## 2. Crear backlog plano tipo `todo.md`

**Descripción.** Se acumula trabajo en un único archivo `TODO.md` o equivalente,
sin estructura de épicas y tasks.

**Por qué pasa.** Costumbre histórica del equipo, percepción de que crear épica es
overhead.

**Consecuencia.** Pierde visibilidad por capacidad funcional, imposibilita
asignación clara, rompe el principio "toda task vive bajo una épica".

**Corrección.** Si una idea no encaja en una épica existente, usá `/new-idea` para
decidir si abre una nueva o entra en una existente. Las tasks viven en
`doc/tasks/EPIC-XXX/TASK-YYY_*.md`. El framework no soporta backlog plano.

---

## 3. Implementar sin verificar `estado de toma`

**Descripción.** Dev A toma una task que dev B ya estaba trabajando. Conflictos de
merge y trabajo duplicado.

**Por qué pasa.** Saltarse el check de "Asignación" → "Estado de toma" antes de
abrir la branch.

**Consecuencia.** Conflictos de código, repetición de esfuerzo, fricción humana.

**Corrección.** Antes de tomar una task:

1. Leer la sección "Asignación" en la task card.
2. Si `Estado de toma: tomada` y el responsable no soy yo, no implementar.
   Coordinar con el responsable.
3. Si la task pasa a `tomada`, registrar `Responsable:` y `Fecha de toma:`.

---

## 4. Inventar reglas de negocio cuando la spec calla

**Descripción.** Se asume comportamiento sin que esté documentado en spec, business
rules o backlog.

**Por qué pasa.** Por completar acceptance criteria o cerrar definición sin
cuestionar lo no escrito.

**Consecuencia.** Reglas implícitas que entran al código sin trazabilidad. La
próxima persona no sabe si la regla es decisión del cliente o invento.

**Corrección.** Lo no especificado queda como **pregunta abierta** en la task card
o como `N/A + riesgo` documentado. El modo `product-spec` (`/product-spec`) y la
skill `feature_development` lo enforzan. Regla: si dudás, no inventes — preguntá.

---

## 5. Tocar código Odoo en un paso documental o de definición

**Descripción.** Durante un paso de spec, contrato, verificación o cierre documental
se editan `models/`, `views/`, `security/`, `data/` o `tests/`.

**Por qué pasa.** Mezclar fases en la misma sesión; "ya que estoy, lo arreglo".

**Consecuencia.** El cambio Odoo entra sin pasar por la compuerta de implementación
ni por verificación crítica. Se pierde la disciplina de fases y el diff queda
contaminado.

**Corrección.** Las fases son compuertas, aunque las recorra un solo operador.
Definir, contratar, verificar y cerrar **no editan código**. Para tocar código,
pasar explícitamente al paso de implementación con criterios claros. Ver
`doc/framework/agents_and_artifacts.md`.

---

## 6. Cerrar `Done` o tocar docs canónicas fuera de `/doc-close`

**Descripción.** Se marca la task como `Done` o se actualiza
`doc/project/<modulo>/business_rules.md` durante la implementación o la
verificación, sin pasar por el cierre documental.

**Por qué pasa.** "Cierro todo" tras implementar; falta de claridad de que
`/doc-close` es la única ruta a `Done`.

**Consecuencia.** Cierres prematuros sin evidencia consolidada, docs canónicas
desactualizadas o inconsistentes con la verdad operativa.

**Corrección.** La implementación devuelve **execution report**; la verificación
devuelve **close gate `Ready/Blocked`**. El cierre documental final se hace con
`/doc-close`. Si un paso "cierra Done" por su cuenta, pará y revisá el routing.

---

## 7. Implementar sin acceptance criteria definidos

**Descripción.** La task pasa a `Implemented` sin que la sección "Acceptance
criteria" tenga ítems verificables, o los ítems son vagos ("que ande bien").

**Por qué pasa.** Saltar el paso de definición por presión de tiempo; falta de spec
compartida.

**Consecuencia.** Rompe la **regla de determinismo**: dos implementadores razonables
podrían entregar cosas distintas. La task no se puede verificar.

**Corrección.** Antes de pasar `Draft → Ready`, los acceptance criteria deben ser
observables: "campo `priority` visible en form view de `me.expediente`", "el botón
`Cerrar` solo aparece si el user pertenece al grupo `me_manager`", etc. Si quedan
vagos, volver a definición o contrato.

---

## 8. Subdocumentar un cambio L sensible

**Descripción.** Cambio que toca modelos, ACL, workflow, datos, migraciones o
auditoría se trata como M (sin contrato técnico, sin verifier crítico).

**Por qué pasa.** Subestimación de impacto; querer cerrar rápido.

**Consecuencia.** Cambios sensibles que entran a producción sin red. Bugs de
seguridad, datos inconsistentes, auditoría fallida.

**Corrección.** `delivery_modes.md` enumera las áreas que **escalan automáticamente
a L/XL**: modelos persistentes, security/ACL/record rules, datos durables, workflow
de estados, contabilidad/permisos/auditoría, migraciones, integraciones externas.
Si el cambio toca cualquiera, el modo es L mínimo, requiere `task_full.md`, contrato
técnico y verifier crítico obligatorio.

---

## Cómo se aplica esta lista

- Antes de abrir una PR: relé la lista. Si la PR rompe alguno, marcalo en la
  descripción y resolvelo.
- En la skill `code_review`, declarar explícitamente que ningún antipatrón aplica
  antes de cerrar gate `Ready`.
- En `/doc-close`, si quedó un antipatrón sin resolver, el cierre devuelve
  `Blocked`.
- Esta lista vive y crece: cuando aparece un nuevo error típico, agregalo (modo S
  contra `antipatterns.md`).
