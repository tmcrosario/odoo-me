# Reglas de negocio — módulo `me` (Mesa de Entradas)

> Consolida `docs/rules_business.md` (invariantes conceptuales) y la sección "Reglas
> de negocio activas" de `docs/system_narrative.md` (v1.0, 2026-03-31, la más
> reciente). Las reglas marcadas como **principio sin enforcement** o **limitación**
> NO deben asumirse como cerradas por su enunciado: el estado real se verificó contra
> código en EPIC-001 (Done, 2026-06-19) y se revalida en cada cambio. El comportamiento
> operativo detallado vive en [`workflows.md`](workflows.md). La **procedencia normativa** de
las reglas de ENTRADA (PRO-11, Ord. 7.767) y el contrato DEM/CM↔JUNCO (BR-021) están en
[`entrada_expediente.md`](entrada_expediente.md).

## Invariantes del sistema (deben cumplirse siempre)

1. Todo movimiento pertenece a exactamente un expediente; no hay movimiento sin
   documento.
2. Los expedientes deben permanecer trazables a través de su historial de movimientos.
3. ME **extiende** el sistema documental base (`tmc.document`), no lo reemplaza. ME no
   crea documentos standalone: todo expediente origina en el sistema base.

Cualquier feature que viole estos invariantes debe rechazarse o redefinir
explícitamente las reglas.

## Reglas activas (observadas en código)

| Regla | Descripción |
|---|---|
| Tipo de documento automático | Al elegir la dependencia de origen, el tipo `EXP` se asigna sin intervención del usuario. |
| Dependencias de origen permitidas | Solo DEM, TMC o CM (filtro hardcodeado `['DEM','TMC','CM']`). |
| Nombre generado | Formato `EXP-XXXXXX-ORIGEN/AÑO` (ej. `EXP-000042-DEM/2025`), calculado en tiempo real. |
| Movimientos iniciales automáticos | Al crear: DEM → 2 movimientos (**DEM→TMC**, TMC→ME); TMC → 1 (TMC→ME, omite TMC→TMC); CM → 2 (CM→TMC, TMC→ME). El 1er movimiento usa `dependence_id` como origen (EPIC-004), no la jurisdicción, así existe aunque la jurisdicción esté vacía. **Excepción Nota (EPIC-004/TASK-003):** en DEM+Nota el 1er movimiento sale de la **jurisdicción** (secretaría real), no de `dependence_id` — la jurisdicción está siempre cargada y estable (JUNCO no toca Notas). El origen es un **snapshot al crear** (no sigue cambios posteriores de la jurisdicción; en compras eso genera el desfase jurisdicción≠origen cuando JUNCO la completa después). |
| Orden de la lista de expedientes (EPIC-003/TASK-003) | Default sort por `intake_date` desc (ingreso más reciente primero), desempate `id desc` → `_order` del modelo. El usuario puede reordenar por columna; es solo el orden inicial. |
| Carga de jurisdicción/origen en DEM (EPIC-004) | En **DEM**, `jurisdiction_dependence` y `source_dependence_id` ya **no se cargan en ME** (campo no required): quedan vacíos al ingresar y los completa **JUNCO** al vincular el expediente a un proceso, vía `action_set_origin_from_junco()`. En la UI de carga DEM se ocultan si vacíos y readonly si tienen valor. **CM** (jurisdicción auto = origen) y **TMC** (jurisdicción auto, source manual) **no cambian**. |
| Excepción DEM + tema Nota (EPIC-004/TASK-002) | EPIC-004 asumió que **todo** DEM va a un proceso de compras; no es así: las **Notas** (ej. "nota que eleva informe") no llegan a JUNCO. Por eso, en **DEM con tema `Nota`** (`is_nota`, computed stored por XML ID `tmc_data.tmc_document_topic_nota`), ME **sí** carga jurisdicción y repartición, **editables al ingreso** y con **jurisdicción obligatoria** (vista `required` + `@api.constrains` backend — llamado desde `create()` y `write()`, **no** vía `@api.constrains('is_nota')` porque al recomputarse rompería el `-u`). El "solo al ingreso" lo garantiza el **guard de `write()`** (el operativo no puede tocar el origen ya guardado; el Responsable sí), **no** la vista (condicionar el readonly al valor en edición bloquea la carga y Odoo no envía el campo → se pierde). Al cambiar el tema **a** Nota o **desde** Nota, el origen se limpia/valida acorde. **Guarda defensiva:** `action_set_origin_from_junco` **rechaza** un expediente con tema Nota (hoy JUNCO no llega por su domain de elegibilidad, confirmado con junco; la guarda cubre ORM/import). Los temas de compra **no cambian** (siguen cediendo a JUNCO). |
| Jurisdicción DEM — multi-año (intencional) | El dropdown de `jurisdiction_dependence` ofrece **todas** las jurisdicciones de **todos** los nomencladores cargados (hijos de `tmc_dependence_adm` en `tmc.dependence_order`), **sin filtrar por año/`institutional_classifier`**, **a propósito**: un documento puede llegar hoy pero haberse generado en una estructura anterior con una secretaría que ya no existe o cambió de nombre, y el expediente debe poder referenciar la jurisdicción vigente en su momento. Por eso `_compute_allowed_jurisdictions` no filtra por año — **no es un bug** (#033). |
| Temas raíz del expediente (junco:EPIC-011) | El asunto (`main_topic_id`) se ofrece acotado a **4 temas raíz** resueltos por XML ID contra `tmc_data` (`_EXP_ROOT_TOPIC_XMLIDS`): licitación, nota, contratación directa, concurso de precios. Los 2 últimos se sumaron para que JUNCO pueda derivar su `process_type`. **Hoy el acote es solo el `domain` de la vista** (no hay `@api.constrains`): una escritura por ORM/API puede fijar otro tema — ver Limitaciones conocidas. |
| Subtema acotado al tema | `secondary_topic_id` ("Specification") se ofrece filtrado por el computed `allowed_secondary_topic_ids` (`domain=[('id','in', allowed_secondary_topic_ids)]`, `document_exp.py`): por defecto los **hijos directos del tema**; para **Licitación**, acotado a los **2 subtipos reales — Privada/Pública** (EPIC-004/TASK-004), no los 25 subtemas documentales de GD (JUNCO deriva su `process_type` del subtema — ver `brainstorming.md` IDEA 2). Se **oculta** hasta elegir tema **y** si el tema no tiene subtemas permitidos (`invisible="not main_topic_id or not allowed_secondary_topic_ids"` → caso Concurso de Precios, sin hijos). Se **limpia al cambiar el tema** (`_onchange_main_topic_id`). **Solo `domain` de vista, sin `@api.constrains`** (JUNCO tiene el enforcement duro de su lado). **No se toca `tmc_data`**: las 23 "etapas" siguen colgando de Licitación (guardrail — `junco.process_event` las usa vía `licitacion.child_ids`). |
| Clasificación requerida (EPIC-004/TASK-005/006) | El **subtema** es **obligatorio para Licitación** (JUNCO deriva el subtipo Pública/Privada de ahí): `required` de vista + validación backend en `create()`/`write()` (no `@api.constrains` sobre `is_licitacion` stored → no rompe el `-u` ni el dato viejo). Concurso/directa no llevan subtema. El **tema** es **obligatorio al alta** — **solo de vista** (no backend: sería global y rompería ORM/tests, y **JUNCO ya gatea por tema**), para que una compra sin tema no quede invisible para JUNCO. Ambos **required solo para nuevas** (`not id`) → el dato viejo sin subtema/tema queda editable. Filtro **"Sin clasificar"** (`main_topic_ids = False`) para pescar los sin tema (ORM/import/legacy). |
| Permisos cross-sistema (ME ↔ GD) | **Ver [`security.md`](security.md)** (postura, grupos y elevaciones). La regla del **stack** es **BR-016, gobernada en `odoo-junco`**; acá no se duplica. |
| Registro automático en RAA | Todo expediente queda registrado en `raa.registry_aa` al crearse. |
| Fojas — bloqueo post-creación | El número de fojas no se modifica una vez guardado, excepto por un Responsable de Mesa de Entradas; las variaciones se registran vía movimientos. |
| Aviso de duplicado | Si existe un expediente con igual origen+número+período, el sistema **avisa pero no bloquea** el guardado. El onchange **se excluye a sí mismo** (`_origin.document_id`): en un expediente ya guardado se detectaba como duplicado propio (se hizo visible al permitir editar el origen post-alta — EPIC-004/TASK-002). |
| Fechas del expediente — semántica (confirmada con junco) | `date` ("Procedure Start Date" / *Fecha de inicio del trámite* en `es_AR`) = **fecha de creación del expediente = la de la carátula**; el nº y el `period` se estampan en ese mismo momento. `intake_date` = **ingreso físico** al Tribunal, cargado a mano en Mesa. `period` = **año** de la carátula. JUNCO no valida sobre estas fechas, pero **desde 2026-07-29 JUNCO LEE `intake_date`** (lo muestra en la carátula del proceso, antes lo derivaba del 1er movimiento). **Contrato:** no renombrar ni cambiar la semántica de `intake_date` sin avisar a `odoo-junco`. |
| Fechas del expediente — validaciones (EPIC-004/TASK-002) | (1) `intake_date` no futura; (2) `intake_date` **no anterior al `period`** (no puede entrar antes de existir su año; **asimétrica**: un ingreso **posterior** al período **sí** es válido — el expediente del período anterior puede llegar después); (3) `date` **no futura**; (4) `intake_date >= date` (no puede ingresar a Mesa antes de existir el documento). Las de `date` se validan dentro de `_update_document_date` (embudo único de escritura de esa fecha) porque el **bypass SQL no dispara `@api.constrains`** — ver `architecture.md`. **NO** se exige `año(date) == period` (decisión del usuario, 2026-07-29): sería solo un control anti-error de tipeo, no una regla de negocio; se deja disponible por si se quiere activar. `date` **sí** puede ser de un año distinto/pasado respecto del período (motivo original del bypass). |
| Integridad de movimientos | Origen y destino obligatorios; fecha no futura ni anterior al ingreso; no se permiten movimientos duplicados exactos (expediente+origen+destino+fecha). |
| Poseedor actual | Solo el `user_id` del último movimiento puede registrar un pase nuevo desde la UI (managers sin restricción) — #027/#028/#029. |
| Salida / reingreso institucional | Derivado de `is_internal` por dependencia; `has_reentry` marca reingreso tras una salida previa — #021/#030. |
| Indicador de legajo actual (EPIC-006/TASK-002) | `current_legajo_number` (computed no-stored, del **último** movimiento cuando su destino es Legajo `LEG`) muestra "En Legajo Nº X" en el form (label bajo el nombre, visible solo en legajo). **Estado actual**: si el expediente se mueve después de Legajo, deja de mostrarse; con varios pases a Legajo muestra el del último. La lista se filtra con **"Adjuntos a Legajo"** (`current_location_dependence_id.abbreviation == 'LEG'`). Strings en inglés + i18n `es_AR`. |

## Append-only (principio, sin enforcement técnico)

El diseño establece que los movimientos son **append-only** (no modificables ni
eliminables retroactivamente). **Es un principio declarativo**: a la fecha del
análisis no hay constraint/override que lo enforce más allá de los permisos de grupo.
Verificado en EPIC-001 (Done): sigue sin enforcement técnico; el ACL (el operativo no
tiene `unlink`) y el guard de `write()` lo acotan en la práctica, pero un manager no está
limitado. Formalizarlo sigue siendo un ítem de backlog.

## Limitaciones conocidas (no implementado)

- **Sin estados de expediente** (no hay ciclo de vida abierto/en proceso/cerrado).
- **Sin validación de continuidad** entre movimientos (el destino de uno no se valida
  contra el origen del siguiente; orden cronológico no enforced).
- **Sin documentos relacionados** (tab deshabilitado).
- **Fragilidad**: el movimiento automático a "Mesa de Entradas" depende de encontrar
  la dependencia por nombre/abreviatura; si no existe, se omite sin aviso.
- **Nomenclador 2025 no cargado** (#033, dato externo): el seed de `tmc_data` en este
  stack es el nomenclador **2020** (`institutional_classifier` 2016–2020). Faltan las
  secretarías del **2025** (ej. Género y DDHH, Modernización y Cercanía, Desarrollo
  Humano y Hábitat, Desarrollo Económico y Empleo, Movilidad, Deporte y Turismo): existen
  en el catálogo `tmc.dependence` pero no cuelgan de `adm` en `dependence_order`, así que
  no aparecen en el dropdown ni se pueden setear (tampoco por el camino JUNCO de EPIC-004).
  **Fix pendiente = cargar el nomenclador 2025 de forma aditiva** (sin quitar el 2020, por
  la regla multi-año) **en `odoo-tmc-data`**, repo externo gestionado aparte (no se toca
  desde este flujo). Diagnóstico completo en EPIC-001/TASK-004.
- Higiene de datos: el catálogo `tmc.dependence` tiene **duplicados por variante de
  mayúsculas/acentos** (MAYÚSCULAS vs Tipo-Oración); no afectan el dropdown (los
  Tipo-Oración no cuelgan de `adm`), pero conviene tenerlos en cuenta al cargar el 2025.
- **Temas raíz sin enforcement backend** (junco:EPIC-011): el acote a los 4 temas raíz es
  **solo el `domain` de la vista** — no hay `@api.constrains`. Una escritura por ORM/API
  puede fijar un tema fuera de lista. **Hoy es ayuda de carga, no regla dura**, y no rompe
  a JUNCO (si el tema no está en lista, `process_type` simplemente no deriva).
  **Pregunta abierta** (decisión del usuario, no se asume): ¿endurecerlo con un constrains?
  Un constrains podría bloquear cargas legítimas (importaciones, datos viejos).
- **Subtema de Licitación — RESUELTO (EPIC-004/TASK-004).** Antes, al elegir `Licitación` el
  subtema ofrecía **25 hijos**. Encuadre corregido: esos 25 **no** son un dato mal modelado ni
  eventos de JUNCO — son la **taxonomía documental de GD** (clasifica resoluciones/decretos/
  convenios; `tmc.document_topic` tiene 62 raíces/201 temas). ME reusaba ese subtema-de-documento
  como subtipo del expediente. Resuelto **del lado de ME** (domain de vista): Licitación se acota
  a Privada/Pública (los que JUNCO consume); Concurso de Precios oculta el subtema vacío. **No se
  tocó `tmc_data`** (guardrail: `junco.process_event` usa `licitacion.child_ids`). Ver regla
  "Subtema acotado al tema" y `brainstorming.md` IDEA 2.

> Nota: la **ubicación interna actual** ya está implementada (EPIC-003): campo
> `current_location_dependence_id` (oficina interna de destino del último movimiento).

## Relación con RAA

Algunos expedientes quedan asociados a actos administrativos en `raa.registry_aa`.
RAA es un **punto de integración externo**: fuera del scope de ME, no se modifica sin
pedido explícito.
