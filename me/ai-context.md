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
| `external_key` | Char | No | identifier used by the Municipality |
| `fojas` | Integer | No | number of pages |
| `number` | Integer | Yes | inherited from tmc.document, required enforced here |
| `is_valid` | Boolean | No | computed: True when all 5 key fields are complete |
| `computed_name` | Char | No | computed: format EXP-XXXXXX-ABR/YEAR |
| `allowed_dependence_ids` | Many2many(tmc.dependence) | No | computed, no declared dependencies |
| `document_movement_ids` | One2many(me.document_movement) | No | movement history |

Fields inherited from `tmc.document` (via delegation):

`name`, `dependence_id`, `document_type_id`, `period`, `date`,
`document_object`, `main_topic_ids`, `secondary_topic_ids`,
`document_topic_ids`, `related_document_ids`, `highlight_ids`

Commented fields (currently inactive):
- `asunto` (Char) — was removed, do not re-add without explicit request


**me.document_movement** (`me/models/document_movement.py`)

Records each routing event of an expediente between organizational units.
No inheritance, no methods, no constraints — pure audit record.

Fields: `expediente_id`, `date`, `origin_dependence_id`,
`destination_dependence_id`, `user_id`

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

2. Creates a `raa.registry_aa` record linked to that tmc.document

3. Creates movement 1: jurisdiction_dependence → TMC
   (only if a tmc.dependence with abbreviation='TMC' exists)

4. Creates movement 2: TMC → Mesa de Entradas
   (only if a tmc.dependence with name ilike 'Mesa de Entradas' exists)

The user does NOT create the tmc.document separately first.
The document is created inside me.document_exp.create() via _inherits.

If the searched dependences do not exist in the database,
the movements are silently skipped — no error, no warning.

Implementation: `me/models/document_exp.py`, lines 133–162.


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


**Duplicate validation (warning only)**

When `dependence_id + document_type_id + number + period` matches
an existing tmc.document, a UI warning is shown.

This does NOT block saving. There is no backend constraint preventing
duplicate records from being created.


**Document type auto-assignment**

When `dependence_id` is selected, `document_type_id` is automatically
set to the type with `abbreviation='EXP'`. The user cannot freely choose
a different document type.


**Date update via direct SQL**

`write()` updates the `date` field using a raw SQL query
to bypass the `_check_date_not_future` constraint in `tmc.document`.

Do not propose using the ORM to update the date field directly —
it will fail due to base model constraints.

Implementation: `document_exp.py`, `_update_document_date()`, lines 163–180.


**Progressive visibility in UI**

The form view shows fields progressively based on `is_valid`:

- is_valid = False: only basic fields visible (dependence, jurisdiction, type, number, period)
- is_valid = True: also shows topics, reference, date, external_key, fojas
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
tmc.dependence
```


--------------------------------------------------
Design Constraints
--------------------------------------------------

- ME extends `tmc.document` via `_inherits`, not `_inherit`
- `me.document_exp.create()` always creates tmc.document + raa.registry_aa + up to 2 movements
- document movements must always reference an expediente (ondelete=cascade)
- the dependence filter ['DEM', 'TMC', 'CM'] is hardcoded and intentional
- do not update `date` via ORM — use the existing _update_document_date() method
- do not re-add commented fields (notes, asunto) without explicit requirement


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
