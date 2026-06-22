# Modelos — módulo `me` (Mesa de Entradas)

> Consolida los antiguos `docs/models.md` + `docs/model_registry.md` (que estaban
> casi duplicados). Es una descripción **conceptual + registro autoritativo** de
> modelos. El detalle de campos/métodos vive en [`architecture.md`](architecture.md);
> el código es la fuente de verdad final (`me/models/`).

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
- Campos, computed (`computed_name`, `is_origin_complete`/`is_valid`,
  `current_holder_id`, `current_location_dependence_id`, `has_reentry`…) y métodos: ver
  [`architecture.md`](architecture.md) y [`workflows.md`](workflows.md).
- `current_location_dependence_id` (EPIC-003): Many2one stored computed = oficina
  **interna** de destino del último movimiento (`is_internal=True`); False sin movimientos
  o si el expediente salió del Tribunal. Espejo de `current_holder_id`. Alimenta el filtro
  "Destination Office" de la vista de lista.
- **EPIC-004**: `jurisdiction_dependence` ya **no es required** (solo DEM queda vacío al
  ingresar; TMC/CM se autoasignan en `create()`). Para DEM, `jurisdiction_dependence` y
  `source_dependence_id` los completa **JUNCO** vía el método público
  `action_set_origin_from_junco(jurisdiction_id, source_id=False)` (valida DEM-only +
  nomenclador `tmc.dependence_order`, `sudo()` acotado, idempotente). Ver
  [`security.md`](security.md) (canal de escritura) y [`business_rules.md`](business_rules.md).

## `me.document_movement`

- Registra cada movimiento/transferencia del expediente entre dependencias. Es el
  modelo de trazabilidad.
- Cada movimiento referencia exactamente un expediente (`expediente_id`, required,
  `ondelete="cascade"`).
- Tiene `origin_dependence_id` / `destination_dependence_id` (→ `tmc.dependence`),
  `date`, `user_id`, `fojas`, `is_automatic`. Constraints e integridad
  (UNIQUE + checks de fecha): ver [`workflows.md`](workflows.md).

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
