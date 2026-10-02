# Referencia: sistema documental base TMC

> **Referencia de contexto transversal.** Describe el sistema documental base
> `tmc.*` que `me` extiende. **Vive en otro repo (`odoo-tmc`), no se implementa ni
> se modifica acá**; se documenta para entender la arquitectura de `me`
> (ver [`architecture.md`](architecture.md)). Las convenciones de commit canónicas
> son las del framework (`CLAUDE.md` + `doc/framework/git_policy.md`), no las de este
> archivo.

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


The ME module extends this model through **delegation inheritance** (`_inherits`):

`me.document_exp`

Do not confuse it with `tmc.document_exp`, a **different model** of the base module (its own table
and purpose). See [`models.md`](models.md).


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
      ↓ extended by (_inherits)
me.document_exp
      ↓ tracked through
me.document_movement
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
Validaciones de `tmc.document` que afectan a `me`
--------------------------------------------------

Verificadas en `odoo-tmc/tmc/models/document.py` (2026-10-02). Como `me.document_exp` delega en
`tmc.document` (`_inherits`), el alta de un expediente crea el documento padre y **estas validaciones
corren también sobre él**, salvo donde `me` las esquiva a propósito.

| Validación en `tmc.document` | Efecto sobre un expediente |
|---|---|
| `UNIQUE(name)` ("Document already exists"); `name` = tipo + número + dependencia + período | Un expediente duplicado no se puede guardar (ver `business_rules.md`) |
| `create()`/`write()`: el año de `date` debe coincidir con `period`, salvo tipo `CONV` ("Date does not match with period") | **Es la razón del SQL de `_update_document_date`** en `me`: permite archivar un documento viejo en un expediente del período actual (`workflows.md`, Workflow 7) |
| `_check_date_not_future`: `date` > hoy (fecha UTC del servidor) → "Date cannot be in the future." | `me` la esquiva con el SQL y la **reimplementa** en `_update_document_date`, contra la fecha del usuario (`context_today`) |
| `_check_document_object_length`: el objeto no puede superar **125 caracteres**, salvo tipo `DIC` (el campo admite 250, pero el constraint corta en 125) | Rige para el "Reference" del expediente: 125 pasa y 126 se rechaza (probado) |
| `_check_period`: 1000 ≤ período ≤ año actual, y no antes de 1948 | El período de un expediente no puede ser anterior a 1948 |
| `_check_number`: 0 es inválido (salvo tipo `ACT`); máximo 999999 para EXP/ACT/CONV/NTA/NJC y para CM/HCM/CONC, 9999 para DHH y 6000 en el resto | Para un EXP coincide con el rango 1–999999 que valida `me` (`_validate_number`) |

--------------------------------------------------
`tmc.dependence_order` (jerarquía de dependencias)
--------------------------------------------------

Modelo del base (`_order = "code"`) que ordena las dependencias en árbol: cada registro tiene `code`,
la `dependence_id` que representa, su padre (`parent_id`, otra `tmc.dependence`) y los nomencladores
(`institutional_classifier_ids`) en los que figura. **De él depende todo el filtrado de origen de `me`:**

- **Jurisdicciones** ofrecidas (`allowed_jurisdiction_ids`): las dependencias hijas de `adm`
  (`tmc_dependence_adm`), de **todos** los nomencladores cargados (multi-año, a propósito).
- **Reparticiones** ofrecidas (`allowed_sub_dependence_ids`): las dependencias cuyo `parent_id` es la
  jurisdicción elegida.
- `action_set_origin_from_junco` valida jurisdicción y repartición contra este mismo árbol.

