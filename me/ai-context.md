# ME Module – AI Context

This document provides a technical overview of the ME module for AI-assisted development.

Its purpose is to help AI agents quickly understand:

- the module structure and main entities
- architectural constraints and design decisions
- non-obvious behaviors that affect code proposals
- where to find the implementation


--------------------------------------------------
Module Overview
--------------------------------------------------

The **ME module (Mesa de Entradas)** manages administrative documents
entering the organization and tracks their internal routing.

Main responsibilities:

- register expedientes (administrative documents) in the intake system
- automatically link each expediente to the RAA registry
- track document movements between organizational units
- maintain complete traceability of document handling


--------------------------------------------------
Relationship with Base Document System
--------------------------------------------------

The ME module is built on top of an existing document system.

Base model: `tmc.document`

This model is provided by the `odoo-tmc` repository and is **not implemented here**.

The ME module extends this model using **delegation inheritance** (`_inherits`),
not extension inheritance (`_inherit`). This is a critical distinction:

- `_inherits`: creates TWO records in TWO separate tables
  (`me_document_exp` + `tmc_document`), linked by `document_id`
- `_inherit`: would extend a single table

When accessing fields from `tmc.document` via `me.document_exp`,
both records must exist. The `document_id` field is the link.

Implementation: `me/models/document_exp.py`, line 6:
```python
_inherits = {"tmc.document": "document_id"}
```


--------------------------------------------------
me.document_exp ≠ tmc.document_exp
--------------------------------------------------

IMPORTANT: the `tmc` module defines its own `tmc.document_exp` model,
which is a generic specialization of type EXP in the base system.

`me.document_exp` is a different model with a different `_name`,
its own table, and its own business logic (movements, RAA, jurisdiction).

Do not confuse these two models or propose inheritance from `tmc.document_exp`.


--------------------------------------------------
Core Models
--------------------------------------------------

**me.document_exp** (`me/models/document_exp.py`)

Represents an expediente managed by the Mesa de Entradas.
Uses `_inherits` over `tmc.document` via `document_id`.

Own fields (defined in `me.document_exp`):

| Field | Type | Required | Notes |
|---|---|---|---|
| `document_id` | Many2one(tmc.document) | Yes | delegation link, ondelete=cascade |
| `jurisdiction_dependence` | Many2one(tmc.dependence) | Yes | origin of first automatic movement |
| `intake_date` | Date | Yes | date of physical receipt at Mesa de Entradas; no default; future dates rejected |
| `external_key` | Char | No | identifier used by the Municipality |
| `fojas` | Yes (view) | Integer; number of pages; default=0; 0 is valid; required="1" in view only — Integer required=True at model level would reject 0 |
| `number` | Integer | Yes | inherited from tmc.document, required enforced here |
| `is_valid` | Boolean | No | computed: True when 5 fields complete (dependence_id, document_type_id, number, period, jurisdiction_dependence) |
| `is_origin_complete` | Boolean | No | computed: True when 3 fields complete (dependence_id, number, period); controls UI progression |
| `dependence_abbreviation` | Char | No | computed proxy: `dependence_id.abbreviation or ''`; declared `invisible="1"` in view; used in view invisible/readonly expressions (dot-notation on _inherits fields is not reliable client-side) |
| `computed_name` | Char | No | computed: format EXP-XXXXXX-ABR/YEAR; shown as soon as dependence_id + number + period are set |
| `source_dependence_id` | Many2one(tmc.dependence) | Conditional | required when `allowed_sub_dependence_ids` is non-empty AND dependence_id is not TMC or CM; enforced by `@api.constrains` + `required="allowed_sub_dependence_ids"` in view; cleared when `jurisdiction_dependence` changes; invisible in view when dependence_abbreviation == 'CM' |
| `allowed_sub_dependence_ids` | Many2many(tmc.dependence) | No | computed; depends on `jurisdiction_dependence`; queries `tmc.dependence_order` where `parent_id = jurisdiction_dependence.id`; provides domain for `source_dependence_id` |
| `allowed_dependence_ids` | Many2many(tmc.dependence) | No | computed, no declared dependencies; hardcoded to DEM/TMC/CM |
| `allowed_jurisdiction_ids` | Many2many(tmc.dependence) | No | computed, no declared dependencies; queries tmc.dependence_order children of tmc_dependence_adm (~21 first-level institutional bodies); declared `invisible="1"` in view; provides domain for `jurisdiction_dependence` |
| `document_movement_ids` | One2many(me.document_movement) | No | movement history |
| `has_reentry` | Boolean | No | stored computed: True when the expediente has at least one movement to an external dependence followed by a movement to an internal dependence (institutional reentry detection); depends on `document_movement_ids.destination_dependence_id.is_internal`; initialized to False for pre-existing rows when the column is first added — see upgrade note below |
| `main_topic_id` | Many2one(tmc.document_topic) | No | proxy compute+inverse over `main_topic_ids`; domain: root topics only, filtered to `allowed_exp_topic_ids`; cleared via `_onchange_main_topic_id` when changed |
| `secondary_topic_id` | Many2one(tmc.document_topic) | No | proxy compute+inverse over `secondary_topic_ids`; domain: children of `main_topic_id`; cleared via `_onchange_main_topic_id` when `main_topic_id` changes |
| `allowed_exp_topic_ids` | Many2many(tmc.document_topic) | No | computed; resolves Licitación and Nota by XML ID from tmc_data; independent of `dependence_id`; declared `invisible="1"` in view; provides domain for `main_topic_id` |

Fields inherited from `tmc.document` (via delegation):

`name`, `dependence_id`, `document_type_id`, `period`, `date`,
`document_object`, `main_topic_ids`, `secondary_topic_ids`,
`document_topic_ids`, `related_document_ids`, `highlight_ids`

Commented fields (currently inactive):
- `asunto` (Char) — was removed, do not re-add without explicit request


**me.document_movement** (`me/models/document_movement.py`)

Records each routing event of an expediente between organizational units.

Fields:

| Field | Required | Notes |
|---|---|---|
| `expediente_id` | Yes | Many2one(me.document_exp), ondelete=cascade |
| `date` | Yes | Datetime, default=now(); cannot be future; cannot be before expediente.intake_date |
| `origin_dependence_id` | Yes | Many2one(tmc.dependence); pre-loaded via default_get() with the destination of the last movement (highest id) when default_expediente_id is in context; empty if no prior movements |
| `destination_dependence_id` | Yes | Many2one(tmc.dependence) |
| `fojas` | No | Integer, default=0; snapshot of expediente.fojas at the moment of the movement; auto-populated in automatic movements; pre-loaded via default_get() for manual movements using context default_expediente_id |
| `is_automatic` | No | Boolean, default=False; True when the movement was generated by me.document_exp.create(); readonly in view when True (fojas cannot be edited on automatic movements) |
| `user_id` | No | Odoo user responsible for the expediente at the destination of this movement (NOT who loaded it — that is `create_uid`); default=current user; readonly in view when `is_automatic=True` |
| `destination_abbreviation` | No | computed Char proxy: `destination_dependence_id.abbreviation or ''`; declared `invisible="1"` / `column_invisible="1"` in view; used in view invisible/required expressions for `legajo_number` |
| `legajo_number` | Conditional | Char; required and visible only when `destination_abbreviation == 'LEG'` (destination = Adjunto a Legajo); enforced at model level via `@api.constrains`; invisible in view for all other destinations |

Constraints:
- `_unique_movement` (models.Constraint): UNIQUE(expediente_id, origin_dependence_id, destination_dependence_id, date) — prevents exact duplicates at DB level
- `_check_date_not_future`: date cannot be after now()
- `_check_date_not_before_intake`: date.date() cannot be before expediente_id.intake_date

Note: In Odoo 19, use `models.Constraint(...)` as a class attribute — NOT `_sql_constraints`.
`_sql_constraints` is deprecated and has no effect. See `docs/coding_standards.md`.

Commented fields (currently inactive):
- `notes` (Text) — was removed, do not re-add without explicit request


--------------------------------------------------
Automatic Behavior in create()
--------------------------------------------------

IMPORTANT: when a `me.document_exp` is created, the system automatically:

1. Creates a `tmc.document` record via the `_inherits` delegation mechanism.
   Odoo handles this automatically in `super().create()` — the base fields
   (dependence_id, document_type_id, number, period, date, document_object)
   are passed through transparently.
   Do NOT create tmc.document manually before calling super() — it breaks _inherits.

2. Creates a `raa.registry_aa` record linked to that tmc.document.

3. Creates automatic movements depending on `dependence_id`:

   **DEM (and any non-TMC origin):**
   - Movement 1: jurisdiction_dependence → TMC  (snapshot fojas, is_automatic=True)
   - Movement 2: TMC → Mesa de Entradas         (snapshot fojas, is_automatic=True)

   **TMC origin:**
   - Movement 1 is SKIPPED — it would be TMC→TMC, which has no functional meaning.
   - Only movement TMC → Mesa de Entradas is created.

   **CM origin:**
   - jurisdiction_dependence is auto-assigned to the CM record in create() (backup
     for API calls; the onchange handles the UI case).
   - Movement 1: CM → TMC   (snapshot fojas, is_automatic=True)
   - Movement 2: TMC → Mesa de Entradas   (snapshot fojas, is_automatic=True)

   In all cases, movements are only created if both dependences (TMC, ME) exist
   in the database. If they do not, the movements are silently skipped.

The user does NOT create the tmc.document separately first.
The document is created inside me.document_exp.create() via _inherits.

Implementation: `me/models/document_exp.py`, method `create()`.


--------------------------------------------------
RAA Integration
--------------------------------------------------

The `raa` module is outside the scope of ME development
and must NOT be modified.

However, `me.document_exp.create()` automatically creates a
`raa.registry_aa` record linked to the new tmc.document.

This coupling exists in the code even though `raa` is not declared
as a dependency in `me/__manifest__.py`.

Do not propose code that creates raa.registry_aa a second time,
and do not assume this integration is missing — it is already implemented.


--------------------------------------------------
Business Rules and Constraints
--------------------------------------------------

**Dependence filter (hardcoded)**

`dependence_id` is restricted to dependences with abbreviations:
`['DEM', 'TMC', 'CM']`

This filter is enforced both in the computed field `allowed_dependence_ids`
and in the view domain. It is static — not configurable.

Do not propose changes to this list without explicit requirement.

Implementation: `document_exp.py:66`, `document_exp_views.xml:41`


**Jurisdiction domain (jurisdiction_dependence)**

`jurisdiction_dependence` is restricted to the ~21 first-level institutional bodies
of the nomenclator (codes 1.XX.00 — Secretarías, CM, DEM, TMC, etc.).

These are computed by `allowed_jurisdiction_ids`, which queries `tmc.dependence_order`
where `parent_id = tmc_dependence_adm` and maps `.dependence_id`. The view applies this
as a domain filter. Sub-dependences (2nd level and deeper) do NOT appear here.

Do not hardcode a domain on `jurisdiction_dependence` in the view — use
`allowed_jurisdiction_ids` as the source of truth.

Conditional behavior by origin:
- DEM: operator selects from the ~21 jurisdictions; field is required.
- TMC: auto-assigned to TMC record via `_onchange_dependence`; field is readonly in view.
- CM: auto-assigned to CM record via `_onchange_dependence` (and `create()` backup for API
  calls); field is invisible in view — operator never sees or edits it.

`_check_source_dependence_required` constraint exempts both CM and TMC:
condition is `dependence_id.abbreviation not in ('CM', 'TMC')`.


**Sub-dependence domain (source_dependence_id)**

`source_dependence_id` is filtered to the children of `jurisdiction_dependence`
in the nomenclator. The allowed values are computed by `allowed_sub_dependence_ids`,
which queries `tmc.dependence_order` where `parent_id = jurisdiction_dependence.id`
and maps `.dependence_id`. The view applies this as a domain filter.

When `jurisdiction_dependence` changes, `_onchange_jurisdiction_dependence()` clears
`source_dependence_id` to prevent stale values. The field is conditionally required:
mandatory when the selected jurisdiction has sub-dependences in `tmc.dependence_order`
AND `dependence_id` is not CM or TMC; otherwise optional.

For CM origin: field is invisible in view; `source_dependence_id` remains empty.

Do not hardcode a domain on `source_dependence_id` in the view — use the computed
field `allowed_sub_dependence_ids` as the source of truth.


**Topic filtering for EXP documents**

`main_topic_id` shows only root topics allowed for EXP documents: Licitación and Nota.
These are resolved by XML external ID from the tmc_data module
(`tmc_data.tmc_document_topic_licitacion`, `tmc_data.tmc_document_topic_nota`),
NOT filtered by `dependence_id`. The allowed set is the same regardless of which
origin dependence (DEM, TMC, CM) the expediente has.

Do NOT use `document_topic_ids` for the domain of `main_topic_id` — that field
filters by `dependence_id` and returns empty for non-TMC expedientes.

`secondary_topic_id` is filtered to children of the selected `main_topic_id`.
`_onchange_main_topic_id` clears `secondary_topic_id` when `main_topic_id` changes.

The auxiliary field `allowed_exp_topic_ids` (declared `invisible="1"` in the view)
is the source of truth — reference it in the domain, do not hardcode topic IDs.

Implementation: `document_exp.py`, `_compute_allowed_exp_topic_ids()`, `_EXP_ROOT_TOPIC_XMLIDS`


**Duplicate validation (warning only)**

When `dependence_id + document_type_id + number + period` matches
an existing tmc.document, a UI warning is shown.

This does NOT block saving. There is no backend constraint preventing
duplicate records from being created.


**Document type auto-assignment**

When `dependence_id` is selected, `document_type_id` is automatically
set to the type with `abbreviation='EXP'`. The user cannot freely choose
a different document type.


**Fojas lock after creation**

`fojas` (page count) can be set freely during creation. After the record is saved,
only a manager (`me.group_manager`) can modify it. Regular operators receive an
AccessError if they attempt to change `fojas` post-creation.

This is enforced in `write()` in `me.document_exp`. The constraint is intentional:
fojas variations after creation must be traced through document movements, not by
editing the original value directly. Managers can correct data entry errors.

Do not propose removing or bypassing this check without explicit requirement.

Implementation: `document_exp.py`, `write()` method.


**Date update via direct SQL**

`write()` updates the `date` field using a raw SQL query
to bypass the `_check_date_not_future` constraint in `tmc.document`.

Do not propose using the ORM to update the date field directly —
it will fail due to base model constraints.

Implementation: `document_exp.py`, `_update_document_date()`, lines 163–180.


**Progressive visibility in UI**

The form view shows fields progressively based on `is_origin_complete` (not `is_valid`):

Phase 1 — always visible: `dependence_id`, `document_type_id` (auto, readonly, visible once
dependence_id is set), `number`, `period`

Phase 2 — visible when `is_origin_complete = True` (dependence_id + number + period complete):
`jurisdiction_dependence` (hidden for CM), `source_dependence_id` (hidden for CM; required when
jurisdiction has non-TMC/CM children), `intake_date`, `main_topic_id` (optional),
`secondary_topic_id` (visible when main_topic_id set), `document_object`, `date` (required),
`external_key`, `fojas` (required in view, 0 is valid)

Conditional behavior by origin dependence (controlled via `dependence_abbreviation`):
- DEM: all Phase 2 fields visible; operator selects jurisdiction from ~21 mother bodies
- TMC: `jurisdiction_dependence` auto-assigned to TMC and readonly; `source_dependence_id`
  not required even if TMC has children in the nomenclator
- CM: `jurisdiction_dependence` and `source_dependence_id` hidden (auto-assigned CM internally);
  `intake_date` and all other fields remain visible

View invisible/readonly conditions use `dependence_abbreviation` (a computed Char proxy field),
NOT `dependence_id.abbreviation` — the latter is not reliably loaded client-side for _inherits fields.

- `is_valid` is still computed and exists in the model (controls functional completeness),
  but it is NOT the UI visibility control — do not use it for that purpose
- `computed_name` appears in the header as soon as Phase 1 is complete (3 fields),
  not after all 5 fields
- record not yet saved (no id): movements tab hidden

The "Documentos Relacionados" tab is always invisible (hardcoded).


--------------------------------------------------
Conceptual Relationship
--------------------------------------------------

```
tmc.document  (base, odoo-tmc repository)
    │
    │ _inherits (delegation via document_id)
    ▼
me.document_exp
    │                          │
    │ One2many                 │ auto-created in create()
    ▼                          ▼
me.document_movement       raa.registry_aa
    │
    │ Many2one (origin / destination)
    ▼
tmc.dependence  ← extended by me via _inherit: adds is_internal (Boolean)
                  Internal dependences: TMC, ME, VOC, FC, DAL, DAT, DCD, DAF, DIC, AFC, ARCH, LEG
                  All others (DEM, CM, jurisdictions) are external (is_internal=False)
```


**Upgrade note — is_internal and has_reentry on existing databases**

`me/data/dependence_data.xml` uses `<odoo noupdate="1">`. On a fresh install
(`-i me`) the `is_internal` values are written correctly. On an upgrade
(`-u me`) over an existing database the records are already present in
`ir_model_data` and Odoo skips them — `is_internal` stays NULL (False) for all
pre-existing dependences.

Separately, `has_reentry` is `store=True`. When the column is added to an existing
table Odoo sets the column default (False) for all rows. Because `is_internal` was
never corrected, no `@api.depends` trigger fires and the stored values are never
recomputed for historical expedientes.

Both corrections are required before the "With Institutional Reentry" filter
returns results on upgraded installations: (1) apply `is_internal=True` to the
internal dependences, and (2) run an explicit recompute of `has_reentry` for all
existing expedientes. Neither correction is needed on a clean install.


--------------------------------------------------
Design Constraints
--------------------------------------------------

- ME extends `tmc.document` via `_inherits`, not `_inherit`
- `me.document_exp.create()` always creates tmc.document + raa.registry_aa + up to 2 movements
- document movements must always reference an expediente (ondelete=cascade)
- movement origin and destination are required — do not propose optional M2one for these fields
- movement date cannot be future and cannot be before expediente.intake_date
- the dependence filter ['DEM', 'TMC', 'CM'] is hardcoded and intentional
- do not update `date` via ORM — use the existing _update_document_date() method
- do not re-add commented fields (notes, asunto) without explicit requirement
- `_onchange_jurisdiction_dependence()` clears `source_dependence_id` — do not bypass this behavior


--------------------------------------------------
Development Status
--------------------------------------------------

The ME module:

- originates from an Odoo 14 implementation
- has been migrated to Odoo 19
- views use `<list>` syntax and inline visibility (`invisible="not field"`)
- remains under active development
- workflow states (open/closed/archived) are not yet defined


--------------------------------------------------
Related Documentation
--------------------------------------------------

docs/models.md
docs/model_registry.md
docs/rules_business.md
domain-rules/me/me_architecture.md
docs/me_architecture_analysis_report.md  ← full architectural analysis

AI agents should consult these files before proposing
structural changes to the module.


--------------------------------------------------
Module Boundaries
--------------------------------------------------

The repository also contains:

- **RAA** – Registro de Actos Administrativos:
  outside scope of ME development, must not be modified.
  It IS used implicitly by me.document_exp.create().

- **tmc** (odoo-tmc repository):
  provides the base document system. Read for context,
  do not modify.



--------------------------------------------------
Grupos y política de permisos
--------------------------------------------------

Los grupos de ME usan `res.groups.privilege` (patrón Odoo 19), definidos en
`me/security/me_groups.xml`. Las reglas de acceso están en
`me/security/ir.model.access.csv`.

Grupos:

  me.group_user (operador): R_C_ en document_exp y document_movement.
    Registra ingresos y pases. No puede editar ni eliminar registros existentes.
    implied_ids: tmc.group_user (necesario para crear tmc.document via _inherits).

  me.group_manager (gestor): RWCU en document_exp y document_movement.
    Supervisa y corrige. Puede modificar fojas post-creación (excepción operativa).
    implied_ids: me.group_user + tmc.group_manager (necesario para write en tmc.document).

  me.group_read_only: R___ en ambos modelos.

Cadena de implicación:
  me.group_manager → me.group_user → tmc.group_user → base.group_user
  me.group_manager → tmc.group_manager → tmc.group_user

Dependencia con TMC:
  me.document_exp usa _inherits sobre tmc.document. Cualquier write() sobre
  campos delegados (dependence_id, number, period, document_object, etc.)
  requiere perm_write=1 en tmc.document. Solo tmc.group_manager lo tiene.
  Por eso me.group_manager implica tmc.group_manager vía implied_ids.
  me.group_user implica tmc.group_user, que tiene perm_create=1 en tmc.document
  (necesario para que el operador pueda crear expedientes via _inherits).

Restricción de fojas:
  write() en me.document_exp verifica has_group('me.group_manager').
  me.group_user no tiene perm_write en me.document_exp → recibe AccessError
  antes de llegar al check. El check protege contra me.group_manager que
  intente modificar fojas accidentalmente vía API; el gestor puede corregirlo
  cuando es un error operativo real.
