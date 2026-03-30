--------------------------------------------------
System Architecture Overview
--------------------------------------------------

Three distinct layers interact in this system.
The ME module consumes the base document system and implicitly
creates entries in the RAA module at document creation time.

    ┌─────────────────────────────────────┐
    │   Base Document System (odoo-tmc)   │
    │                                     │
    │         tmc.document                │
    │         tmc.dependence              │
    │         tmc.document_type           │
    └──────────────────┬──────────────────┘
                       │ _inherits (delegation)
                       │ document_id → tmc.document
                       ▼
    ┌─────────────────────────────────────┐
    │         ME Module (odoo-me)         │
    │                                     │
    │         me.document_exp             │
    │              │                      │
    │              │ One2many             │
    │              ▼                      │
    │         me.document_movement        │
    └──────────────────┬──────────────────┘
                       │ auto-created in create()
                       │ document_id → tmc.document
                       ▼
    ┌─────────────────────────────────────┐
    │        RAA Module (odoo-me)         │
    │                                     │
    │         raa.registry_aa             │
    │   (read-only from ME perspective)   │
    └─────────────────────────────────────┘


--------------------------------------------------
Model Relationship Diagram
--------------------------------------------------

All relationships observed directly in code.

    tmc.document  (odoo-tmc/tmc/models/document.py)
        │
        │ _inherits via document_id (delegation inheritance)
        │ Two records in two tables: me_document_exp + tmc_document
        │ me/models/document_exp.py:6
        ▼
    me.document_exp  (me/models/document_exp.py)
        │
        ├── One2many: document_movement_ids
        │       │  me/models/document_exp.py:57
        │       ▼
        │   me.document_movement  (me/models/document_movement.py)
        │       ├── Many2one: expediente_id → me.document_exp  (required, cascade)
        │       ├── Many2one: origin_dependence_id → tmc.dependence
        │       └── Many2one: destination_dependence_id → tmc.dependence
        │
        ├── Many2one: jurisdiction_dependence → tmc.dependence  (required)
        │       me/models/document_exp.py:28
        │
        └── [Inferred] auto-created inside create()
                │  me/models/document_exp.py:138
                │  raa not declared in me/__manifest__.py
                ▼
            raa.registry_aa  (raa/models/registry_aa.py)
                └── Many2one: document_id → tmc.document  (required, unique)


    tmc.dependence  (odoo-tmc — read-only from ME)
        ▲
        │ Many2one from: me.document_movement (origin + destination)
        │ Many2one from: me.document_exp (jurisdiction_dependence)
        │ Many2one from: tmc.document (dependence_id, inherited by me.document_exp)


--------------------------------------------------
Module Boundaries
--------------------------------------------------

ME (me/)
    Manages the intake of administrative documents (expedientes).
    Owns: me.document_exp, me.document_movement
    Depends on: tmc.document, tmc.dependence, tmc.document_type
    Implicitly uses: raa.registry_aa (not declared in __manifest__.py)
    Does NOT declare raa as a formal dependency — see ai-context.md.

RAA (raa/)
    Manages the formal registry of administrative acts.
    Owns: raa.registry_aa
    Read from ME at creation time; must not be modified from ME.
    raa.registry_aa has a UNIQUE constraint on document_id.
    raa/models/registry_aa.py:52

    IMPORTANT — implicit coupling:
    me.document_exp.create() calls self.env["raa.registry_aa"].create(...)
    but raa is NOT declared as a dependency in me/__manifest__.py.
    If raa is not installed, create() will raise an error at runtime.
    This may introduce deployment or migration risks.
    Observed in code: me/models/document_exp.py:138

Base Document System (odoo-tmc — external repository)
    Provides tmc.document, tmc.dependence, tmc.document_type.
    Defines the _check_date_not_future constraint that
    me.document_exp bypasses via raw SQL in _update_document_date().
    Read for context; must not be modified.
