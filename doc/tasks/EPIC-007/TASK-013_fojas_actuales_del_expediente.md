# EPIC-007 / TASK-013 — Fojas actuales del expediente

Estado: Draft
Modo: L
Riesgo: bajo-medio (campo nuevo calculado, no almacenado; cambia qué fojas muestra la vista)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: sin tomar
- Notas de coordinación: surge de una consulta de `demo-junco` (2026-11-17) sobre si el total de fojas sigue al
  pase. `odoo-me-8a` (junco) confirmó que no toca `me`; si el campo cambia de contrato (nombre, tipo,
  almacenado) hay que avisarles. Ellos lo mostrarían con un related de solo lectura, tarea propia en junco.

## Objetivo

Que el expediente muestre las **fojas actuales** (las del último pase) en lugar del valor de ingreso, que hoy
queda congelado aunque el expediente crezca en pases posteriores.

## Alcance

Incluye:

- campo `current_fojas` en `me.document_exp`: Integer, calculado, **no almacenado**, de solo lectura;
- valor = `fojas` del pase de **mayor id**; sin pases, cae al `fojas` de ingreso;
- vista: con el expediente guardado se muestra `current_fojas`; el `fojas` de ingreso se oculta (sigue
  visible al cargarlo, donde es obligatorio). El valor de ingreso queda visible en el 1er pase;
- traducción es_AR, tests y docs (`models.md`, `business_rules.md`, `tests_plan.md`).

No incluye:

- cambiar quién puede editar `fojas` de ingreso (→ TASK-014);
- historial de cambios (→ IDEA 14 del brainstorming, no se implementa);
- tocar `odoo-junco` (mostrarlo allá es tarea de junco);
- migrar ni reescribir datos.

## Reglas decididas (usuario, 2026-11-17)

- Nombre `current_fojas`, entero, no almacenado.
- Último pase = el de mayor id (igual que el poseedor y el default de `fojas` en un pase nuevo).
- Sin pases: vale el de ingreso.
- En la vista se muestran las fojas actuales; el valor de ingreso ya está en el 1er pase.

## Acceptance criteria

- [ ] `current_fojas` es la `fojas` del último pase (mayor id) del expediente.
- [ ] Al registrar un pase con más fojas, `current_fojas` pasa a ese valor sin tocar `fojas` de ingreso.
- [ ] Un expediente sin pases devuelve el `fojas` de ingreso.
- [ ] Corregir las fojas del último pase manual actualiza `current_fojas`.
- [ ] En el formulario con el expediente guardado se ve `current_fojas` (solo lectura) y no el `fojas` de
      ingreso; al crear sigue siendo obligatorio cargar `fojas`.
- [ ] El campo no se almacena (sin migración ni backfill).
- [ ] Suite `/me` verde, con evidencia (`... of N tests`, N > 0).
- [ ] Prueba manual de UI en `practica`: alta con fojas, pase con más fojas, el formulario muestra el nuevo
      total.
- [ ] Aviso a `odoo-me-8a` / `demo-junco` con el contrato final del campo.

## Riesgos y preguntas abiertas

- Si más adelante se quiere buscar o agrupar por fojas actuales habría que almacenarlo (migración y
  `depends` sobre los pases).
- Si la lista de expedientes muestra `fojas`, revisar qué columna conviene.

## Tests evidenciados

PENDIENTE USER-RUN.

## Estado / próximo paso

Draft. Falta el OK del usuario a los criterios y asignar la task antes de implementar. Sin código tocado.

## Resultado

(pendiente)
