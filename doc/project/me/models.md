# Modelos — módulo `me` (Mesa de Entradas)

> Consolida los antiguos `docs/models.md` + `docs/model_registry.md` (que estaban
> casi duplicados). Es una descripción **conceptual + registro autoritativo** de
> modelos, con el **inventario vigente de campos** propios (extraído del registro de Odoo el
> 2026-10-02). [`architecture.md`](architecture.md) es un snapshot histórico; el código es la
> fuente de verdad final (`me/models/`).

## Dependencia del sistema base

`me` se construye sobre el sistema documental base `tmc.document` (repo `odoo-tmc`,
**no implementado en este repo**). ME **extiende, no reemplaza** ese modelo. Ver
[`tmc_base_reference.md`](tmc_base_reference.md).

`depends`: `["tmc", "tmc_data"]`. `tmc_data` es necesario porque
`me/data/dependence_data.xml` referencia registros del nomenclador definidos en ese
módulo (ej. `tmc_data.tmc_dependence_tmc`); sin declararlo, una instalación fresca de
`me` falla por orden de carga (Odoo no respeta el orden del `-i`, usa los `depends`).

## Registro autoritativo de modelos de `me`

Lista de modelos `_name` propios del módulo. **Antes de introducir un modelo nuevo**,
verificar si el concepto puede resolverse con un campo, una relación o la extensión
de un modelo existente. Un modelo nuevo solo se justifica si el concepto tiene ciclo
de vida propio, representa una entidad distinta y no puede modelarse de otra forma.

| Modelo | Tipo | Rol |
|---|---|---|
| `me.document_exp` | Entidad de negocio (hereda `tmc.document`) | El expediente de la Mesa de Entradas |
| `me.document_movement` | Entidad de trazabilidad | Registro de cada movimiento del expediente |

Modelos extendidos por `me` vía `_inherit` (no son `_name` propios): `tmc.dependence`
(agrega `is_internal`, `default_responsible_id` — ver `workflows.md` #021/#030).

## `me.document_exp`

- Representa un expediente administrativo en la Mesa de Entradas.
- **Herencia por delegación**: `_inherits = {"tmc.document": "document_id"}`. Esto es
  `_inherits` (delegación), **no** `_inherit` (extensión): se crean **dos registros
  en dos tablas** (`me_document_exp` + `tmc_document`) vinculados por `document_id`.
  Esta distinción es técnicamente significativa para queries y constraints.
- **No** es lo mismo que `tmc.document_exp` (modelo distinto del módulo base, con
  otra tabla y otro propósito).
- Relación principal: `document_movement_ids` (One2many → `me.document_movement`).
- Orden por defecto: `_order = "intake_date desc, id desc"` (EPIC-003/TASK-003).
- Campos propios: ver la tabla de abajo. Métodos y comportamiento: [`workflows.md`](workflows.md)
  (vigente); [`architecture.md`](architecture.md) es un snapshot histórico.
- `current_location_dependence_id` (EPIC-003): Many2one stored computed = oficina
  **interna** de destino del último movimiento (`is_internal=True`); False sin movimientos
  o si el expediente salió del Tribunal. Espejo de `current_holder_id`. Alimenta el filtro
  "Destination Office" de la vista de lista.
- **EPIC-004**: `jurisdiction_dependence` ya **no es required** (solo DEM queda vacío al
  ingresar; TMC/CM se autoasignan en `create()`). Para DEM de compras, `jurisdiction_dependence` y
  `source_dependence_id` los completa **JUNCO** vía el método público
  `action_set_origin_from_junco(jurisdiction_id, source_id=False)` (valida DEM-only +
  nomenclador `tmc.dependence_order`, `sudo()` acotado, idempotente). **Excepción: DEM con tema
  Nota** (TASK-002): una Nota no va a JUNCO, así que ME carga jurisdicción (obligatoria) y
  repartición al ingreso, y `action_set_origin_from_junco` **rechaza** las Notas con `UserError`.
  Ver [`security.md`](security.md) (canal de escritura) y [`business_rules.md`](business_rules.md).
- **Temas raíz del expediente (junco:EPIC-011)**: `_EXP_ROOT_TOPIC_XMLIDS` fija **por código**
  los 4 temas raíz admitidos para EXP, resueltos **por XML ID** contra `tmc_data` (licitación,
  nota, contratación directa, concurso de precios). El computed `allowed_exp_topic_ids` los
  resuelve (`raise_if_not_found=False`: un xmlid ausente se omite en silencio) y alimenta el
  `domain` de `main_topic_id`. `main_topic_id` / `secondary_topic_id` son **proxies**
  (compute+inverse) sobre los Many2many `main_topic_ids` / `secondary_topic_ids` de
  `tmc.document`, para selección única en UI sin tocar el modelo base. El tema tiene **tres
  consumos funcionales** dentro de ME: `is_licitacion` e `is_nota` (stored computed, derivados de
  `main_topic_ids` y del proxy `main_topic_id` para reaccionar antes de guardar) gobiernan los
  `required` de vista y las validaciones de `create()`/`write()` (`_validate_licitacion_subtopic`,
  `_validate_nota_jurisdiction`); y `allowed_secondary_topic_ids` acota el subtema. **El acote de
  `main_topic_id` a los 4 temas raíz es solo el `domain` de la vista** (sin `@api.constrains`) —
  ver `business_rules.md` → Limitaciones conocidas.
- **`create()` — semántica de permisos (junco:EPIC-015)**: el `super()` corre **elevado**
  (`.with_context(me_create_in_progress=True).sudo()`) porque el `_inherits` crea el
  `tmc.document` padre y el operativo de ME ya **solo lee GD**; se des-eleva de inmediato
  (`records.sudo(self.env.su)`). Como la elevación saltearía el ACL de `me.document_exp`, el
  método valida antes con `self.check_access('create')`. Detalle en [`security.md`](security.md).

## `me.document_movement`

- Registra cada movimiento/transferencia del expediente entre dependencias. Es el
  modelo de trazabilidad.
- Cada movimiento referencia exactamente un expediente (`expediente_id`, required,
  `ondelete="cascade"`).
- Campos propios: ver la tabla de abajo. `_order = "id"` (el "último movimiento" se toma por `id`,
  no por `date`). Constraints e integridad (UNIQUE, fecha no futura con margen de 60 s, fecha no
  anterior al ingreso, `legajo_number` obligatorio si el destino es Legajo): ver
  [`business_rules.md`](business_rules.md) y [`workflows.md`](workflows.md).

## Inventario vigente de campos propios

Extraído del registro de Odoo (`me_test`, 2026-10-02): solo los campos **definidos por `me`**, no los
delegados por `_inherits` desde `tmc.document` (`name`, `dependence_id`, `document_type_id`, `number`,
`period`, `date`, `document_object`, `main_topic_ids`, `secondary_topic_ids`…). "Stored" = `store=True`.

### `me.document_exp`

| Campo | Tipo | Stored | Req. | Para qué |
|---|---|---|---|---|
| `document_id` | M2o `tmc.document` | sí | sí | Enlace de delegación (`_inherits`) |
| `intake_date` | Date | sí | sí | Ingreso físico al Tribunal; clave del `_order` |
| `fojas` | Integer | sí | no | Páginas; bloqueo post-creación (ver `business_rules.md`) |
| `external_key` | Char | sí | no | Clave externa de la Municipalidad |
| `jurisdiction_dependence` | M2o `tmc.dependence` | sí | no | Jurisdicción. TMC/CM la autoasignan; DEM de compras la completa JUNCO; DEM+Nota la carga ME |
| `source_dependence_id` | M2o `tmc.dependence` | sí | no | Repartición dentro de la jurisdicción; obligatoria si la jurisdicción tiene reparticiones (salvo CM/TMC) |
| `main_topic_id` | M2o `tmc.document_topic` | no | no | Proxy (compute+inverse) sobre `main_topic_ids`; selección única de tema |
| `secondary_topic_id` | M2o `tmc.document_topic` | no | no | Proxy sobre `secondary_topic_ids`; subtema (obligatorio para Licitación) |
| `document_movement_ids` | O2m `me.document_movement` | sí | no | Historial de movimientos |
| `computed_name` | Char | no | no | `EXP-XXXXXX-ORIGEN/AÑO` en tiempo real. **No es buscable** (sin `search`) |
| `is_nota` | Boolean | sí | no | El tema es Nota (por XML ID `tmc_data.tmc_document_topic_nota`) |
| `is_licitacion` | Boolean | sí | no | El tema es Licitación |
| `current_holder_id` | M2o `res.users` | sí | no | `user_id` del último movimiento (poseedor) |
| `current_location_dependence_id` | M2o `tmc.dependence` | sí | no | Oficina **interna** de destino del último movimiento (EPIC-003) |
| `current_legajo_number` | Char | no | no | `legajo_number` del último movimiento, solo si su destino es Legajo (EPIC-006/TASK-002) |
| `is_currently_internal` | Boolean | sí | no | El último movimiento deja el expediente en una dependencia interna |
| `has_reentry` | Boolean | sí | no | Hubo una salida del Tribunal seguida de un reingreso (#021/#030) |
| `is_origin_complete` | Boolean | no | no | Origen + número + período completos: gobierna la visibilidad progresiva del form |
| `is_valid` | Boolean | no | no | Campos básicos completos (incluye jurisdicción). Legado: la vista lo declara `invisible` pero ninguna condición depende de él (lo reemplazó `is_origin_complete`) |
| `dependence_abbreviation` | Char | no | no | Abreviatura del origen, para condiciones `invisible`/`readonly`/`required` de la vista |
| `allowed_exp_topic_ids` | M2m `tmc.document_topic` | no | no | Los 4 temas raíz admitidos (domain de `main_topic_id`) |
| `allowed_secondary_topic_ids` | M2m `tmc.document_topic` | no | no | Subtemas ofrecidos: Licitación → Privada/Pública; el resto → los hijos del tema |
| `allowed_jurisdiction_ids` | M2m `tmc.dependence` | no | no | Jurisdicciones ofrecidas (todos los nomencladores cargados) |
| `allowed_sub_dependence_ids` | M2m `tmc.dependence` | no | no | Reparticiones hijas de la jurisdicción (`tmc.dependence_order`) |

### `me.document_movement`

| Campo | Tipo | Stored | Req. | Para qué |
|---|---|---|---|---|
| `expediente_id` | M2o `me.document_exp` | sí | sí | Expediente (`ondelete="cascade"`) |
| `date` | Datetime | sí | sí | Fecha del pase; default ahora |
| `origin_dependence_id` | M2o `tmc.dependence` | sí | sí | Origen del pase |
| `destination_dependence_id` | M2o `tmc.dependence` | sí | sí | Destino del pase |
| `user_id` | M2o `res.users` | sí | no | Responsable en el destino (poseedor tras el pase) |
| `fojas` | Integer | sí | no | Snapshot de fojas en ese pase |
| `is_automatic` | Boolean | sí | no | Movimiento generado al crear el expediente |
| `legajo_number` | Char | sí | no | Nº de legajo; obligatorio si el destino es Legajo (`LEG`) |
| `destination_abbreviation` | Char | no | no | Abreviatura del destino, para condiciones de vista |

### `tmc.dependence` (extensión por `_inherit`)

| Campo | Tipo | Stored | Para qué |
|---|---|---|---|
| `is_internal` | Boolean | sí | La dependencia es una oficina interna del Tribunal |
| `default_responsible_id` | M2o `res.users` | sí | Responsable por defecto al elegirla como destino (#030) |

## Modelo externo: `raa.registry_aa`

Pertenece al módulo `raa` (fuera de scope de ME). Se crea automáticamente desde
`me.document_exp.create()` (vía `sudo()`). **No proponer cambios estructurales** salvo
pedido explícito. Ver [`../raa/architecture.md`](../raa/architecture.md).

**Acoplamiento implícito (no se declara en el manifest — a propósito):** `me` crea
registros de `raa.registry_aa`, pero **`raa` depende de `me`** (`raa/__manifest__.py`:
`depends = ["tmc", "me"]`). Declarar `raa` en los `depends` de `me` crearía una
**dependencia circular** `me ↔ raa` que rompe la carga. Por eso el acoplamiento queda
implícito (decisión EPIC-005/TASK-002, §8.8). **Consecuencia:** `me` asume que `raa` está
co-instalado; si se instalara `me` sin `raa`, `create()` fallaría al crear el registro RAA.
En este stack siempre se co-instalan (`-i me,raa`).

## Guardrails de arquitectura

Preferir extender modelos existentes, agregar campos o relaciones. Evitar modelos
nuevos salvo que el concepto tenga ciclo de vida propio, sea una entidad distinta y
no pueda modelarse como relación o campo. Si dos modelos parecen representar el mismo
concepto, revisar la arquitectura antes de agregar más.
