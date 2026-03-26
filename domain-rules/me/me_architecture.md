# ME System Architecture

This document describes the architecture of the **ME (Mesa de Entradas)** module.

Its purpose is to help developers and AI agents understand:

- the core entities of the system
- how they relate to each other
- architectural principles
- boundaries of the module

The goal is to maintain architectural consistency while the system evolves.


--------------------------------------------------
System Overview
--------------------------------------------------

ME (Mesa de Entradas) is an Odoo module designed to manage
administrative document intake and traceability inside an organization.

Its main responsibilities include:

- registering documents in the intake system
- tracking document movements inside the organization
- maintaining document traceability

The module operates on top of an existing document management system.


--------------------------------------------------
Dependency on Base Document System
--------------------------------------------------

The ME module depends on an external document management system.

Core base model:

tmc.document

This model represents the canonical document entity in the system.

The ME module does **not replace this model**.

Instead, it extends it through ME-specific models
that integrate documents into the Mesa de Entradas workflow.


--------------------------------------------------
Core Entities
--------------------------------------------------

The ME system currently revolves around the following entities.


tmc.document

Represents a document managed by the base document system.


document_exp

Represents a document that is handled within the Mesa de Entradas module.

This model extends or references the base document
to integrate it into the ME workflow.


document_movement

Represents the movement or routing of a document
inside the organization.


--------------------------------------------------
Conceptual Structure
--------------------------------------------------

High-level structure of the system:

Document (tmc.document)
        │
        │ integration with ME
        ▼
document_exp
        │
        │ movement history
        ▼
document_movement


This structure allows the system to maintain a full trace
of how documents move through the organization.


--------------------------------------------------
Document Movement Model
--------------------------------------------------

The movement model provides traceability.

Each movement represents an event in the document lifecycle.

Examples of movements may include:

- assignment to a unit
- transfer between users
- routing to another department
- internal processing steps


Each movement must reference a document.


--------------------------------------------------
Traceability Principle
--------------------------------------------------

Traceability is a central principle of the system.

Documents must preserve their movement history.

Operations must not remove historical movements
unless explicitly required by domain rules.


--------------------------------------------------
Design Principles
--------------------------------------------------

The ME architecture follows these principles.


Single Source of Truth

Each domain concept should have one canonical representation.


Extension over duplication

The ME module extends the base document system
instead of creating duplicate document models.


Separation of concerns

- models contain business logic
- views define the UI
- documentation describes the domain rules


Predictable behavior

Document routing and traceability must behave consistently.


--------------------------------------------------
Architectural Boundaries
--------------------------------------------------

The ME module focuses on document intake and movement tracking.

Other modules may exist in the repository,
but they may fall outside the scope of this module.

Example:

RAA – Registro de Actos Administrativos


Important rule:

The architecture of external modules such as RAA
must not be modified unless explicitly requested.


--------------------------------------------------
Architecture Evolution
--------------------------------------------------

The ME module is currently under active development.

The system originates from an implementation in Odoo 14
and is being migrated to Odoo 19.

Some domain rules and workflows may evolve during development.


--------------------------------------------------
Documentation as Architecture Reference
--------------------------------------------------

The following documents define the system specification.

docs/models.md  
docs/rules_business.md  
docs/model_registry.md


When the architecture changes, these documents must be updated.


--------------------------------------------------
Model Registry
--------------------------------------------------

The authoritative list of models in the system is defined in:

docs/model_registry.md


Before introducing a new model, developers and AI agents must verify
whether the concept can be represented by:

- a field
- a relation
- an extension of an existing model


A new model should only be introduced if the concept:

- has its own lifecycle
- represents a distinct entity
- cannot be represented through existing models.


--------------------------------------------------
AI Development Safety
--------------------------------------------------

When AI agents generate code for this module, they must:

- inspect existing models first
- extend existing architecture
- avoid introducing duplicate entities

If domain behavior is unclear, mark it as:

pending definition

instead of inventing functionality.