# ME Business Rules

This document defines the functional rules of the **ME (Mesa de Entradas)** module.

These rules describe how the system must behave from a business perspective.

They are independent from the technical implementation.

The ME module is currently **under development** and some rules may still
be refined as the system evolves.


--------------------------------------------------
Core Concepts
--------------------------------------------------

The ME module manages administrative documents and tracks their movement
inside the organization.

The system focuses on:

- documents
- document movements
- document traceability


--------------------------------------------------
Documents
--------------------------------------------------

Documents originate in the base document management system.

The ME module extends these documents through the model:

`me.document_exp`


Documents managed in ME must always originate from the base document system.

ME does not create standalone document entities.


--------------------------------------------------
Document Movements
--------------------------------------------------

Document movements represent the transfer or routing of a document
between actors in the organization.

Model:

`me.document_movement`

Examples of movements include:

- assignment to an internal unit
- transfer to another user
- routing to a different department


Each movement must reference exactly one document.


--------------------------------------------------
Movement Integrity
--------------------------------------------------

The following conditions must always hold:

1. A document movement must reference exactly one document.
2. Movements cannot exist without a document.
3. Movements must preserve the chronological traceability of the document.


--------------------------------------------------
Document Traceability
--------------------------------------------------

The system must maintain a clear history of how a document moves
through the organization.

This history is represented by the sequence of document movements.

Movements should never remove previous traceability information.

Movements should behave as **append-only records**, meaning that
historical movements should not be modified retroactively.


--------------------------------------------------
Document Editing
--------------------------------------------------

Rules regarding document editing are partially inherited
from the base document system (`tmc.document`).

The ME module may add additional restrictions depending on workflow
requirements.

Detailed editing rules may evolve during development.


--------------------------------------------------
Future Workflow Rules
--------------------------------------------------

The document workflow is still evolving.

Future versions of the system may introduce rules regarding:

- workflow states
- routing restrictions
- document locking
- automated assignments


These rules will be defined progressively as the system design evolves.


--------------------------------------------------
Relationship with RAA
--------------------------------------------------

Some documents may eventually be associated with administrative acts
registered in the RAA module.

Example model:

`raa.registry_aa`

However:

- the RAA module is outside the scope of ME development
- ME must treat RAA as an external integration point


--------------------------------------------------
System Invariants
--------------------------------------------------

The following conditions must always remain true:

1. Every movement must belong to a document.
2. Documents must remain traceable through their movement history.
3. ME must extend the base document system rather than replacing it.


Any feature that violates these invariants must be rejected
or explicitly redefine the business rules.


--------------------------------------------------
Implementation Reference
--------------------------------------------------

Current implementation:

me/models/document_exp.py  
me/models/document_movement.py