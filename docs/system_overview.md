# Odoo ME – System Overview

This document provides a high-level overview of the **Mesa de Entradas (ME) system**.

Its purpose is to help developers and AI agents understand:

- the role of the ME module
- its relationship with the base document system
- how documents and movements are handled

This document intentionally focuses only on **ME**.

The **RAA module exists in the repository but is considered external to the
current development scope and should not be modified.**


--------------------------------------------------
System Purpose
--------------------------------------------------

The ME module manages administrative document intake and tracking.

Its main responsibilities are:

- registering documents entering the organization
- tracking movements of documents between units or users
- managing document workflow within the institution
- preparing documents for potential administrative registration


--------------------------------------------------
Dependency on Base Document System
--------------------------------------------------

The ME module is built on top of an existing document management system.

The base document model is:

tmc.document

The ME module **extends this model** rather than replacing it.

This means:

- document metadata may come from the base system
- ME-specific behavior is implemented through model extensions
- naming conventions may reflect this inheritance


--------------------------------------------------
Core Concepts
--------------------------------------------------

Document Extension

Documents managed by Mesa de Entradas are represented by
extensions of the base document model.

These extensions store additional metadata or behavior needed
for the intake and tracking process.


Document Movements

Documents can move between:

- organizational units
- users
- workflow states

These movements are tracked to maintain traceability
of the document's path inside the organization.


--------------------------------------------------
Relationship with RAA
--------------------------------------------------

The repository also contains the module:

RAA – Registro de Actos Administrativos

This module manages the formal registry of administrative acts.

However:

- the RAA module is **not part of the current development scope**
- no structural modifications should be proposed for RAA
- ME development should treat RAA as an **external integration point**


--------------------------------------------------
Development Scope
--------------------------------------------------

Current development efforts should focus on:

ME module

The following components should not be modified unless explicitly requested:

- RAA module
- base document system


--------------------------------------------------
AI Development Guidance
--------------------------------------------------

Before proposing architectural changes, consult:

- docs/model_registry.md
- domain-rules/me/
- ai-rules/

This helps prevent:

- duplicate models
- inconsistent domain logic
- unnecessary architectural complexity.





--------------------------------------------------
Functional Scenarios
--------------------------------------------------

This section describes how the system is used in practice.

The goal is to provide a clear functional understanding
of user interactions with the ME module.


--------------------------------------------------
Ingreso de expediente en Mesa de Entradas
--------------------------------------------------

Cuando un usuario registra un nuevo expediente en Mesa de Entradas:

1. El usuario crea un nuevo registro en el sistema.
2. El sistema muestra una vista tipo formulario (`form view`).
3. El usuario completa los datos del expediente.

Campo: origen (`dependence_id`)

- Representa la dependencia de origen del expediente.
- El usuario solo puede seleccionar entre un conjunto limitado de dependencias.
- Este conjunto está restringido mediante un filtro en la vista (domain).

Comportamiento esperado:

- No se deben permitir dependencias fuera del conjunto definido.
- El expediente debe tener un origen válido para poder ser procesado.


--------------------------------------------------
Movimiento de expediente (conceptual)
--------------------------------------------------

Un expediente puede ser transferido entre diferentes actores del sistema.

Ejemplos:

- asignación a una dependencia
- derivación a otro usuario
- cambio de estado (si aplica)

Cada movimiento:

- debe estar asociado a un expediente
- debe registrarse para mantener trazabilidad

Nota:

Los detalles del workflow aún están en evolución.