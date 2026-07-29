# EPIC-004 / TASK-002 — Carga de jurisdicción/origen en ME para expedientes DEM con tema Nota

Estado: Done
Modo: L
Riesgo: medio (enmienda una regla de EPIC-004; campo persistente nuevo; toca el punto de
entrada de la integración con JUNCO)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-07-28
- Notas de coordinación: contrato confirmado con `odoo-junco` (ver "Coordinación con JUNCO").

## Objetivo

Que un expediente **DEM cuyo tema es "Nota"** pueda cargar **jurisdicción y repartición
desde ME al ingreso**. EPIC-004 cedió esos campos a JUNCO para **todo** DEM, asumiendo que
todo DEM termina en un proceso de compras; las Notas (ej. "nota que eleva informe") no van a
JUNCO, así que hoy esos campos quedan **huérfanos**: ni los carga ME ni los completa JUNCO.

## Alcance

Incluye:

- Campo `is_nota` (Boolean, computed **stored**), resuelto por XML ID
  `tmc_data.tmc_document_topic_nota` — calcado de `is_licitacion`.
- **Vista**: subir el bloque de asunto/subtema **arriba** del bloque de jurisdicción (el tema
  pasa a gobernar la editabilidad de campos que hoy están por encima de él).
- **Vista**: en DEM + Nota, jurisdicción y repartición **visibles y editables al crear**;
  jurisdicción **required**. Tras guardar, vuelven a readonly (decisión: carga solo al ingreso).
- **Backend**: `@api.constrains` que exige jurisdicción en DEM + Nota (la UI no reemplaza la
  validación backend).
- **Guarda defensiva** en `action_set_origin_from_junco`: rechaza escribir el origen si el
  expediente tiene tema Nota.
- Tests de la matriz completa + no-regresión de EPIC-004.

No incluye:

- **Abrir el guard de `write()`** (decisión del usuario: carga solo al ingreso; corregir
  después queda para un Responsable, como hoy con `fojas`).
- Cambios en TMC/CM (jurisdicción automática) ni en el flujo de compras.
- Cambios en `odoo-junco` (no hacen falta) ni en `tmc_data`.
- Hacer obligatorio el **tema** en sí (hoy `main_topic_id` no es required; sigue igual).

## Reglas conocidas (verificadas en código, no asumidas)

- `is_origin_complete` = origen + número + período; **no** incluye el tema
  ([`document_exp.py:339-344`](../../../me/models/document_exp.py#L339)).
- `_onchange_dependence` fuerza `jurisdiction=False` en DEM (rama `else`, l.459-460).
- Constrains existente: la **repartición** ya es obligatoria si la jurisdicción tiene
  sub-dependencias y el origen no es CM/TMC (l.378-387) → **no hay que agregar nada** para eso.
- `action_set_origin_from_junco` valida **solo** que sea DEM; no mira el tema (l.401).
- Precedente de "editable solo al crear": `fojas` usa `readonly="id"` en la vista.
- Precedente de campo por XML ID: `is_licitacion` (`store=True`, `@api.depends('main_topic_ids')`
  sobre un campo delegado por `_inherits`).

## Coordinación con JUNCO (cerrada, 2026-07-28)

Consultado y **confirmado por el chat de `odoo-junco`** (verificado contra su código,
`develop-ale` `e78cd10`):

- Excluir "nota" de los temas elegibles es **intencional y se mantiene** (BR-005: el
  `process_type` se **deriva** del tema; una compra necesita un expediente de compras).
  `_get_eligible_main_topic_ids()` = licitación, concurso de precios, contratación directa.
  Caveat honesto de ellos: la lista **puede crecer**, pero siempre hacia **otros tipos de
  compra**, nunca hacia "nota" → la guarda es segura frente a eso.
- **No existe hoy** ningún flujo que vincule expediente o llame al método sin pasar por el
  domain de la vista: `action_set_origin_from_junco` se llama desde un solo lugar
  (`_persist_dem_origin`), bajo `is_dem_origin AND current_expediente_id AND
  dem_jurisdiction_id`. Sin wizards, sin data XML, sin import/migración. **Ningún test de
  junco dispararía el UserError.**
- Confirmaron el diagnóstico: hoy la elegibilidad la sostiene **solo un domain de vista**; un
  vínculo por ORM/import/API de una Nota con `dem_jurisdiction_id` **pisaría en silencio** la
  jurisdicción cargada por Mesa. La guarda de ME tapa ese agujero **del lado del dato**.
- Ellos agendaron la **defensa simétrica** en su repo (`junco:EPIC-010/TASK-003`: constraint
  backend de elegibilidad). **No nos bloquea ni nos pide cambios.**

## Acceptance criteria

- [x] **DEM + Nota (nuevo)**: jurisdicción y repartición visibles y editables; no se puede
      guardar sin jurisdicción (validado en pantalla **y** en backend).
- [x] **DEM + Nota**: elegida la jurisdicción, si tiene reparticiones, la repartición es
      obligatoria (comportamiento existente, sin regresión).
- [x] **DEM + Nota (guardado)**: el operativo **no** puede modificar esos campos después
      (guard de `write()` intacto — `test_operator_cannot_change_nota_origin_after_save`).
- [x] **DEM + compras**: comportamiento **idéntico** al actual — ocultos si vacíos, readonly
      si cargados por JUNCO. EPIC-004 intacto.
- [x] **TMC / CM**: sin cambios (jurisdicción automática).
- [x] **DEM sin tema**: jurisdicción no editable (no se habilita).
- [x] `action_set_origin_from_junco` **rechaza** un expediente con tema Nota (UserError).
- [x] Orden del form: asunto/subtema por encima de jurisdicción.
- [x] Suite `/me` verde + UI verificada en me2.

## Alcance adicional que apareció en la verificación de UI

- **Bugs latentes destapados** al permitir editar el origen post-alta: (a) el aviso de
  duplicado se **autodetectaba** en un expediente ya guardado → se excluye `_origin.document_id`;
  (b) `date` (campo delegado) volvía **`False`** tras el `UPDATE` SQL porque solo se invalidaba
  el caché del padre → se invalida también el del expediente.
- **Trampa de diseño (documentada en la vista):** el `readonly` de jurisdicción/source **no**
  se condiciona al valor en edición (el cliente lo evalúa contra lo que se está tipeando →
  bloquea la carga y Odoo no envía el campo). El "solo al ingreso" lo hace el guard de `write()`.
- **Validaciones de fecha** (semántica confirmada con junco): `date`/`intake_date` no futuras,
  `intake >= period` (asimétrica), `intake >= date`. Las de `date` van en `_update_document_date`
  (el SQL directo no dispara `@api.constrains`). **No** se exige `año(date)==period` (decisión
  del usuario). Detalle en `business_rules.md`.
- **UI/i18n:** label `date` "Document Date" → **"Procedure Start Date"** (inglés) + traducción
  `es_AR` "Fecha de inicio del trámite" en `me/i18n/es_AR.po` (regla de `language_policy.md`:
  string inglés + i18n). Mensaje de la constrains Nota **sin** referencia a JUNCO.

## Nota de deploy (idioma)

me2 corre **solo en `en_US`** (ningún `es_AR` activo, todos los usuarios `en_US`) → la UI se ve
en inglés. El usuario confirmó que **producción debe correr en `es_AR`**. **Acción del usuario
en deploy:** activar `es_AR` en prod para que se vean las traducciones (todas ya cargadas en el
`.po`). No es cambio de código.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md` (`-u me`, `--addons-path` completo con las 5 rutas OCA,
  `--test-tags /me`, `me_test`).
- Fecha: 2026-07-29
- Resultado: **0 failed, 0 error(s) of 233 tests** (stats `me: 285`). Antes 209 → **+24**
  (`test_nota_origin.py` 16 + 8 de fecha en `test_document_exp.py`). Aplicado a me2 (`-u me`) +
  restart. **UI verificada por el usuario** en me2 (carga Nota, fechas, no-regresión compras/TMC/CM).

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido (+ activar `es_AR`, ver Nota de deploy).

## Resultado / cierre

Cerrada (Done) el 2026-07-29 sobre `develop`. Enmienda a EPIC-004: los DEM con tema **Nota**
cargan jurisdicción/origen en ME al ingreso (obligatorio, guard de `write()` para el "solo al
ingreso"), los de compra siguen cediendo a JUNCO, con guarda defensiva en el punto de entrada.
En el camino se saldaron 2 bugs latentes (duplicado propio, caché de `date`) y se sumaron las
validaciones de fecha del expediente + el renombre/traducción del label. Coordinado y confirmado
con `odoo-junco` (no requirió cambios de su lado; agendaron `junco:EPIC-010/TASK-003`). Suite
233/0/0, UI verificada en me2.
