# Base Document System (TMC)

This document describes the **base document management system**
used by modules such as **ME (Mesa de Entradas)**.

The base system provides the core document models and functionality
on top of which the ME module is built.

The ME module **extends this system but does not replace it**.

Important:

The models described in this document **are not implemented in this repository**.
They belong to the base document management system used by the institution.

The implementation of the base document system lives
in a separate repository: `odoo-tmc`.

This document exists to help developers and AI agents understand
how extensions such as the ME module interact with the base system.


--------------------------------------------------
System Role
--------------------------------------------------

The base system provides:

- document storage
- document metadata
- document classification
- organizational structure
- topic categorization

The **ME module builds on top of this system** to implement:

- Mesa de Entradas workflows
- document routing
- document traceability.


--------------------------------------------------
Core Model: tmc.document
--------------------------------------------------

The main document model that tracks all documents in the system.

This is the **central entity of the document management system**.

Key responsibilities:

- store document metadata
- connect documents to organizational units
- categorize documents by topics
- support relationships between documents


Important fields include:

- `dependence_id` → organizational unit
- `document_type_id` → document type
- `number` → document number
- `period` → year
- `date` → document date
- `document_object` → description
- `main_topic_ids` → main topics
- `secondary_topic_ids` → secondary topics


The ME module extends this model through:

`document_exp`


--------------------------------------------------
Organizational Structure
--------------------------------------------------

Model:

`tmc.dependence`

Represents organizational units inside the institution.

Used to classify documents according to their origin
or responsible department.


--------------------------------------------------
Document Types
--------------------------------------------------

Model:

`tmc.document_type`

Defines the different types of documents
that can exist in the system.

Examples may include:

- resolutions
- reports
- official communications


--------------------------------------------------
Topic Classification
--------------------------------------------------

Model:

`tmc.document_topic`

Provides hierarchical categorization of document subjects.

Topics may be organized using parent-child relationships.


--------------------------------------------------
Institutional Classifier
--------------------------------------------------

Model:

`tmc.institutional_classifier`

Represents the official nomenclator used
to organize institutional dependencies by period.


--------------------------------------------------
Relationship with ME Module
--------------------------------------------------

The ME module extends this base system.

Conceptually:

```
tmc.document
      ↓ extended by
document_exp
      ↓ tracked through
document_movement
```

Important:

ME **does not create independent documents**.

All documents originate from the **base document system**.


--------------------------------------------------
Design Constraints
--------------------------------------------------

The ME module must always treat `tmc.document`
as the **source of truth** for document entities.

ME may:

- extend the model
- add fields
- add relationships
- add workflow logic

ME must **not replace the document model**.


--------------------------------------------------
Extension Guidelines
--------------------------------------------------

Modules that extend the TMC document system
(such as the ME module) should follow these principles.

Prefer:

- extending existing models
- adding fields
- adding relations
- implementing additional workflows outside the base model

Avoid:

- redefining core document models
- duplicating document entities
- bypassing the base document system.


--------------------------------------------------
Commit Guidelines for TMC-based Systems
--------------------------------------------------

Modules that extend the base document system (such as `me`)
must follow the commit conventions used in the TMC Odoo repositories.

These conventions follow the official Odoo Git Guidelines:
https://www.odoo.com/documentation/19.0/contributing/development/git_guidelines.html


--------------------------------------------------
Commit Message Format
--------------------------------------------------

```
[TYPE] Short description

- Detail of the change
- Additional explanation if needed
```

Rules:

- Use **imperative mood** ("Add feature" not "Added feature")
- Keep the first line concise (preferably under 72 characters)
- Describe **why the change exists**, not only what changed
- Use bullet points for relevant implementation details
- Each commit should represent **one logical change**
- Avoid mixing unrelated changes in the same commit


--------------------------------------------------
Commit Types
--------------------------------------------------

[ADD]  
Add new functionality or modules.

Example:
```
[ADD] Implement document movement tracking
```


[IMP]  
Improvement to existing functionality.

Example:
```
[IMP] Improve document routing logic
```


[FIX]  
Bug fix.

Example:
```
[FIX] Prevent creation of invalid document movements
```


[REM]  
Removal of obsolete code or features.

Example:
```
[REM] Remove deprecated document workflow
```


[REF]  
Refactoring without changing functional behavior.

Example:
```
[REF] Simplify document movement validation logic
```


[MIG]  
Migration related changes (for example adapting code between Odoo versions).

Example:
```
[MIG] Adapt ME module views for Odoo 19
```


[UPD]  
Documentation or configuration updates.

Example:
```
[UPD] Update ME architecture documentation
```


[WIP]  
Work in progress commits.

Important:
Avoid using `[WIP]` in stable branches.


--------------------------------------------------
Traceability Rule
--------------------------------------------------

If a commit modifies behavior related to the document system
(for example document lifecycle, routing, or movements),
developers should review the related documentation:

- docs/models.md
- docs/rules_business.md
- domain-rules/me/me_architecture.md

This ensures that implementation and architecture documentation
remain aligned.


--------------------------------------------------
Important Rule
--------------------------------------------------

Commit messages must **not include AI attribution**.

Do not add lines such as:

- "Generated with Claude"
- "Co-authored-by: Claude"