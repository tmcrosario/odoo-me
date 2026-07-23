# EPIC-004 — Reacotamiento de la carga de ME: traspaso de clasificación a JUNCO

Estado: Done (sobre develop; deploy a prod diferido)
Riesgo global: alto/sensible (campos persistentes hoy required, workflow de movimientos, create(), validaciones, migración de datos, contrato cross-módulo)
Módulo: `me` (contraparte en `junco`, repo `odoo-junco`)
Owner: sin asignar

## Objetivo

Redefinir el alcance funcional del ingreso de expedientes en ME: dejar de cargar desde
ME los campos clasificatorios/funcionales que pasarán a completarse desde JUNCO, y
rediseñar la lógica de movimientos automáticos en consecuencia. ME queda acotado como
**sistema de ingreso y trazabilidad**; JUNCO pasa a completar parte de la información
funcional/clasificatoria.

> **Épica cerrada (Done, 2026-06-17).** Este documento arrancó como definición funcional;
> la implementación se hizo en TASK-001 y se validó end-to-end con JUNCO. Se conserva el
> texto de definición abajo como memoria de las decisiones. Ver "Cierre de épica".

## Contexto

Hasta ahora ME funcionaba con una carga más completa del expediente. El cambio mueve a
JUNCO la responsabilidad de **dos campos de origen/jurisdicción**, pero **solo en el
flujo DEM compras** (ver D-3): CM no cede nada y TMC queda intacto. ME conserva además
los campos de clasificación temática y el objeto del expediente.
El cambio impacta el contrato de campos que JUNCO ya consume de `me.document_exp`
(ver EPIC-002): hoy JUNCO **lee** `jurisdiction_dependence`; con este cambio pasa a
**escribirlo** (inversión de la dirección del dato). La contraparte JUNCO está en
**EPIC-010 de `odoo-junco`** (`EPIC-010_contraparte_jurisdiccion_origen_dem_cm.md`).

## Decisiones joint cerradas con JUNCO (contrato)

Cerradas con el usuario, valen para las dos puntas (espejo de EPIC-010):

- **D-1 — Momento de completado:** JUNCO escribe `jurisdiction_dependence` y
  `source_dependence_id` sobre `me.document_exp` **al vincular el expediente al proceso**
  (en su `_set_current_expediente_id`, único punto de escritura). ⇒ Para ME: en el flujo
  DEM estos campos quedan **vacíos al ingresar** y los completa JUNCO después.
- **D-2 — JUNCO escribe en ME (acotado):** se deroga la regla "JUNCO no escribe en ME"
  (era D-005 de la EPIC-002 de junco). JUNCO escribe **solo esos 2 campos y solo en DEM**,
  vía ORM. Se eligió así porque la lógica de ME depende de la jurisdicción; ver
  **Verificación técnica (D-2)** abajo.
- **D-3 — Alcance solo DEM:** el traspaso aplica únicamente a **DEM**. **CM no cede nada**
  (su jurisdicción ya es auto `= dependence_id` y no usa source) y **TMC queda intacto**.
  Esto cierra la pregunta abierta "¿qué cede CM?": nada.

## Verificación técnica (D-2) — ¿puede `jurisdiction_dependence` quedar vacío en DEM?

Revisado en `me/models/document_exp.py` (responde el punto que JUNCO marcó como el más
sensible de este lado):

| Punto | Impacto si `jurisdiction_dependence` está vacío (DEM) | Veredicto |
| --- | --- | --- |
| `computed_name` (`_compute_name`, l.345) | depende de `dependence_id`/`number`/`period`, **NO de jurisdiction** | ✅ no se rompe |
| `is_origin_complete` (l.321) | depende de `dependence_id`/`number`/`period` | ✅ no se rompe |
| `is_valid` (l.333) | pasa a `False`, pero el campo es `invisible="1"` en la vista → no gatea nada | ✅ sin efecto funcional |
| Constraints (l.313, l.360) | el de source/jurisdiction no se dispara si jurisdiction vacío (sin `allowed_sub_dependence_ids`) | ✅ no bloquea |
| `create()` — campo `required=True` (l.38) | **bloquea**: ORM rechaza crear sin jurisdiction | ❌ **hay que quitar/condicionar el `required=True`** |
| Movimiento 1 auto (`create()`, l.487-497) | el 1er movimiento usa `jurisdiction_dependence` como **origen** y está guardado por `and record.jurisdiction_dependence` → **si vacío, el movimiento NO se crea** (no rompe, se omite) | ⚠️ el 1er pase no se genera al ingresar |

**Conclusión:** `jurisdiction_dependence` puede quedar vacío en DEM sin romper nada,
con **una condición obligatoria** (quitar/condicionar el `required=True`) y **una
consecuencia de diseño**: el movimiento del 1er pase hoy se deriva de la jurisdicción en
`create()`, así que sin ella no se genera al ingresar (resuelto con opción A).

## D-4 — Write-guard y método de escritura JUNCO→ME (prerequisito joint)

**Hallazgo:** `write()` de `me.document_exp` (l.534-576) tiene un guard de seguridad:
si el usuario no es `me.group_manager` y no hay contexto `me_create_in_progress`, lo
único permitido son comandos de `document_movement_ids`; **cualquier otro write lanza
`AccessError`** ("Existing expedientes can only be modified by an Intake Register
manager."). Un `exp.sudo().write({jurisdiction, source})` desde JUNCO chocaría con esto
(el superusuario no está confiablemente en `me.group_manager`).

**Decisión (acordada con JUNCO):** ME expone un método controlado que JUNCO llama desde
su `_set_current_expediente_id` (en vez de write crudo). ME es dueño de la frontera y la
elevación de privilegio ocurre dentro del método.

Firma propuesta: `action_set_origin_from_junco(jurisdiction_id, source_id=False)`.

Requisitos del método (pedidos por JUNCO, defensa en profundidad):

1. **Llamable por `junco.group_user`**: JUNCO lo invoca como el usuario actual; el
   `sudo()` / elevación lo hace ME adentro.
2. **Valida y lanza `UserError` claro** si: el expediente no es DEM, o jurisdiction/source
   no son válidos según el dominio del nomenclador (`tmc.dependence_order`). Surface en UI.
3. **`source_id` opcional (acepta `False`)**: para jurisdicciones DEM sin sub-dependencias.
   La obligatoriedad condicional la chequean ambos lados.
4. **Idempotente**: se llama en el inverse en cada save; llamarlo 2 veces con los mismos
   valores no debe fallar.

> Solo escribe `jurisdiction_dependence` y `source_dependence_id`, solo en DEM. No abre
> el guard general: es un punto de entrada único y validado.

## Orden de merge (acordado)

**(a) Misma ventana/deploy.** Cada repo se pushea por separado y en la instancia se corre
`-u me,junco` en la misma corrida (ME carga antes por dependencia). JUNCO-primero queda
**descartado** (su llamada necesita el método de ME). Fallback **(b) ME-primero, JUNCO
inmediatamente después** (los cambios de ME son backward-compatible con la versión actual
de JUNCO, que solo lee jurisdicción). Sin flag. La derogación formal de D-005 (EPIC-002
de junco) la hace JUNCO al implementar.

## Alcance por tipo de origen (clave)

Por D-3, el traspaso de carga aplica **únicamente a DEM compras**. JUNCO igualmente solo
ve expedientes DEM/CM compras, pero **CM no cede campos** (su jurisdicción ya es auto) y
**TMC ni siquiera entra en JUNCO** y conserva toda su carga (incluida `source_dependence_id`).

Comportamiento actual por origen (`_onchange_dependence`, ~líneas 371-395):

| Origen | `jurisdiction_dependence` | `source_dependence_id` | Visible en JUNCO | ¿Cede carga? |
| --- | --- | --- | --- | --- |
| **DEM** (else) | manual (queda `False` hasta cargar) | manual; required si hay sub-dependencias (constraint ~línea 360) | Sí (compra) | **Sí** |
| **CM** | auto `= dependence_id` (línea 385) | se limpia (`False`), no se usa | Sí (compra) | No (ya es auto) |
| **TMC** | auto `= dependence_id` (línea 383) | manual, **se conserva** (no required) | No | No |

## Campos afectados (AS-IS, grounded en `me/models/document_exp.py`)

ME **deja de cargar — solo para expedientes DEM** (los completa JUNCO al vincular, D-1):

| Campo | Estado actual | Cambio propuesto |
| --- | --- | --- |
| `jurisdiction_dependence` | Many2one, **required=True** (l.38); en DEM es manual; alimenta `_compute_allowed_*` (domain de sub-deps), `is_valid` (invisible) y el **origen del 1er movimiento auto** en `create()`. **No** alimenta `computed_name` (corrección) | dejar de cargarse en ME para DEM → lo escribe JUNCO; **quitar/condicionar el `required=True`** |
| `source_dependence_id` | Many2one; en DEM es manual; en CM no se usa; **en TMC se conserva** | dejar de cargarse en ME solo en DEM; **intacto para CM/TMC** |

ME **conserva** (siguen cargándose en ME — corrección sobre la versión inicial):

| Campo | Nombre funcional | Estado actual | Nota |
| --- | --- | --- | --- |
| `main_topic_id` | subject (tema) | proxy compute/inverse sobre `main_topic_ids` (tmc.document) | ej. "Licitación" |
| `secondary_topic_id` | specification (subtema) | proxy sobre topics secundarios, domain por `main_topic_id` | ej. "Privada"/"Pública" |
| `document_object` | reference (objeto) | **required=True** (~línea 100); la UI ya lo etiqueta "Reference" | ej. "Compra de Equipamiento Informático". **Candidato a reutilizarse en JUNCO como objeto de la compra/contratación** (JUNCO lo leería; sin inversión, ME sigue siendo fuente) |

> UX: estos tres se quieren mostrar con etiquetas Subject / Specification / Reference,
> no como "Tema/Subtema/Objeto" (relabel menor en la vista de carga; `main_topic_id` y
> `secondary_topic_id` no tienen `string` propio hoy).

## Cambio en movimientos automáticos

Flujo objetivo:

- **1er pase:** DEM → TMC
- **2do pase:** TMC → ME

AS-IS (grounded en `create()`, l.479-508): el **2do pase (TMC→ME)** se crea siempre. El
**1er pase** se crea solo si `record.jurisdiction_dependence` existe, y usa **la
jurisdicción como origen** (`origin_dependence_id = record.jurisdiction_dependence`,
l.492), no el `dependence_id` DEM literal. Si la jurisdicción queda vacía al ingresar
(nuevo flujo DEM), el 1er movimiento simplemente **no se genera** (el guard ya lo omite).

Opciones para el origen del 1er pase en DEM:

- **A) ✅ DECIDIDA (usuario):** cambiar el origen del 1er movimiento de
  `jurisdiction_dependence` a `dependence_id` (DEM), que **sí está presente al ingresar** →
  el 1er pase **DEM→TMC se crea y se ve en Mesa de Entradas al ingresar**, independiente
  de si JUNCO carga la jurisdicción después. Es lo que se maneja por ahora.
- **B)** (descartada por ahora) diferir la creación hasta que JUNCO escriba la jurisdicción.

> Pendiente futuro (no ahora): evaluar si los movimientos se gestionan también desde una
> pestaña en JUNCO. Por ahora la trazabilidad de movimientos vive en ME.

## Alcance

Incluye (a precisar en spec):

- tratamiento de los dos campos cedidos (`jurisdiction_dependence`, `source_dependence_id`):
  ocultar / quitar de la fase de carga / dejar de ser required / pasar a readonly desde JUNCO;
- relabel UX de los campos conservados (subject/specification/reference);
- rediseño de la lógica de movimientos automáticos y de la determinación del origen;
- impacto en `create()`, validaciones/constraints, fases del formulario, tests y docs;
- reparto de responsabilidad ME↔JUNCO (fuente de verdad y momento de completado);
- tratamiento de expedientes ya existentes (migración / convivencia).

No incluye:

- la implementación (se abre como tasks recién tras el spec);
- la lógica interna de JUNCO ajena a estos campos.

## Módulos afectados

- Módulo principal: `me`
- Módulos secundarios afectados: `junco` (repo `odoo-junco`) — debe asumir la carga de
  los campos cedidos.
- Dependencias entre módulos: `junco` depende de `me`; `me` no puede depender de
  `junco`. La inversión del flujo de `jurisdiction_dependence` debe resolverse sin
  introducir dependencia circular.

## Reglas / decisiones durables

- No inventar reglas de negocio: el tratamiento de cada campo, la determinación del
  origen del 1er pase y la migración se deciden con el usuario en el spec.
- Cambios sobre campos persistentes required, workflow y create() escalan a L/XL y
  exigen contrato técnico antes de tocar código.
- Contraparte JUNCO: EPIC-010 de `odoo-junco`. El contrato cambia de dirección y se
  deroga "JUNCO no escribe en ME" (D-2) — acotado a 2 campos y solo DEM.
- **Scoping por origen (no negociable, D-3):** el traspaso de carga aplica solo a
  expedientes **DEM** compras. CM no cede (jurisdicción auto) y TMC queda intacto
  (incluida `source_dependence_id`). Cualquier cambio de carga es condicional por origen.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO) | sin asignar | L | `me` | Done (sobre develop) |

## Preguntas abiertas

**Cerradas** (ver Decisiones joint): momento de completado y fuente de verdad → JUNCO al
vincular (D-1/D-2); alcance → solo DEM, CM no cede (D-3).

**ME-interno — todas RESUELTAS en TASK-001 (Done):**

1. ~~Tratamiento de los 2 campos cedidos en DEM~~ **RESUELTA:** `required=True` quitado; en
   la UI de carga DEM quedan **ocultos si vacíos / readonly si tienen valor**.
2. ~~Origen del 1er pase en DEM~~ **RESUELTA (opción A):** el 1er movimiento DEM→TMC se
   crea al ingresar con origen = `dependence_id`, sin esperar a JUNCO.
3. ~~¿ME muestra los 2 campos en readonly u ocultos?~~ **RESUELTA:** ocultos si vacíos,
   readonly si con valor (ídem #1).
4. ~~Migración de DEM existentes~~ **RESUELTA:** se respetan (sin migración masiva).

**Cross con JUNCO (parkeada, no bloqueante):**

5. `document_object` como objeto compartido: JUNCO evalúa reutilizarlo como objeto de la
   compra/contratación (JUNCO lector, ME fuente). TASK-001 la excluyó explícitamente del
   alcance; sigue parkeada del lado JUNCO.

## Cierre de épica

Cerrada (Done) el 2026-06-17 sobre `develop`, con TASK-001 entregada y la integración
ME↔JUNCO validada end-to-end en `me2` (deploy conjunto `-u me,junco`). Contraparte
`odoo-junco` EPIC-010 cerrada (Done), D-005 derogada en su EPIC-002. **Deploy a
producción diferido** (lo gestiona el usuario, `-u me,junco` conjunto cuando corresponda).
