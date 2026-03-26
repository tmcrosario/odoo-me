# ME Models Documentation

This document describes the conceptual model of the **ME (Mesa de Entradas)** module.

Its purpose is to help developers and AI agents understand:

- the main models of the system
- their relationships
- the role of each model in the document handling process

The ME module is currently **under active development** and is being migrated
from **Odoo 14 to Odoo 19**.

Important:

This document currently represents a **conceptual description of the system**.

The exact behavior of the models must be verified against the actual
implementation located in:

```
me/models/
```

AI agents are encouraged to **analyze the implementation code** before
making architectural decisions or proposing modifications.


--------------------------------------------------
Base System Dependency
--------------------------------------------------

The ME module is built on top of an existing document management system.

Core model:

tmc.document

This model belongs to the base document system and is **not implemented in this repository**.

The ME module extends or interacts with this model to add
Mesa de Entradas specific behavior.

Important:

The ME module **does not replace the base document system**.
It extends it.


--------------------------------------------------
Core ME Models
--------------------------------------------------

The current implementation revolves around the following models:

- `document_exp`
- `document_movement`

The authoritative list of models can be found in:

```
docs/model_registry.md
```

AI agents must consult the registry before proposing new models.


--------------------------------------------------
Conceptual Model Overview
--------------------------------------------------

The ME system manages documents and tracks their movement
inside the organization.

Conceptually:

```
tmc.document
        │
        │ extension
        ▼
document_exp
        │
        │ movements
        ▼
document_movement
```

Documents originate in the base document system
and are extended in ME for intake and internal tracking.

Movements record how a document travels through the organization.


--------------------------------------------------
Model: document_exp
--------------------------------------------------

Description:

Represents an extension of the base document model (`tmc.document`)
used by the Mesa de Entradas module.

Purpose:

- store ME-specific metadata
- integrate documents with the intake workflow
- prepare documents for internal processing


Key responsibilities:

- associate a document with the ME workflow
- expose relevant fields for tracking and routing
- support document movements


Relationships:

```
document_exp
    └── document_movement (One2many)
```


Implementation reference:

```
me/models/document_exp.py
```


Important note:

This model extends a document that already exists in the base system,
so the ME module **does not introduce a new document model**.


--------------------------------------------------
Model: document_movement
--------------------------------------------------

Description:

Represents a movement or transfer of a document
between organizational actors or states.

Purpose:

- record traceability of document handling
- track document routing inside the organization


Typical movements may include:

- assignment to a unit
- transfer to another user
- workflow step transitions


Relationships:

```
document_movement
    └── document_exp (Many2one)
```


Implementation reference:

```
me/models/document_movement.py
```


Each movement must always reference a document.


--------------------------------------------------
External Models
--------------------------------------------------

The repository also contains the module:

RAA – Registro de Actos Administrativos

Example model:

```
registry_aa
```

Important:

The **RAA module is outside the scope of the ME development**.

AI agents must not propose structural modifications to the RAA module
unless explicitly requested.


--------------------------------------------------
Future Model Evolution
--------------------------------------------------

The ME module is still evolving.

Future versions of the system may introduce:

- additional metadata for documents
- workflow states
- integrations with other administrative modules
- new document routing rules

Any new model must be evaluated carefully and registered in:

```
docs/model_registry.md
```


--------------------------------------------------
Architecture Guardrails
--------------------------------------------------

To maintain consistency in the system:

Prefer:

- extending existing models
- adding fields
- adding relations

Avoid introducing new models unless the concept:

- has its own lifecycle
- represents a distinct entity
- cannot be modeled as a relation or field.


--------------------------------------------------
Documentation Consistency
--------------------------------------------------

If a model is modified (fields, relations or behaviors),
this document must be updated accordingly.

When updating this document:

1. Verify the model definition in `me/models/`
2. Ensure consistency with `docs/model_registry.md`
3. Update architecture diagrams if relationships change
4. Update business rules in `docs/rules_business.md` if necessary