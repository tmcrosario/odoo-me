# Feature Development Workflow

Design and implement a new feature in the **odoo-me** project in a controlled,
consistent, and maintainable way.

--------------------------------------------------
## Description
--------------------------------------------------

Use this skill whenever a new feature, enhancement, field, model,
report, workflow change, or business rule change is requested.

The goal is to prevent low-quality "vibe coding" by forcing the agent to:

- analyze before coding
- detect impacted models and views
- check business rules consistency
- check Odoo 19 compatibility
- detect documentation updates
- suggest tests when appropriate
- keep the system coherent as it grows

--------------------------------------------------
## Project context
--------------------------------------------------

The repository contains two modules:

- `me` → Mesa de Entradas
- `raa` → Registro de Actos Administrativos

Current development focus is the **ME module**.

RAA must **not be modified unless explicitly requested**.

The system depends on a base document system providing:

tmc.document

The ME module extends this base model.

Core models currently used in ME:

- `document_exp`
- `document_movement`

Always review system documentation before implementing changes.

Relevant documents:

docs/system_overview.md  
docs/models.md  
docs/model_registry.md  
docs/rules_business.md  
domain-rules/me/me_architecture.md  
me/ai-context.md  

--------------------------------------------------
## Instructions
--------------------------------------------------

Follow these steps in order.

### 1. Understand the request

Restate the request in clear technical terms.

Identify what type of change it is:

- new field
- new model
- new relation
- view change
- workflow change
- business rule change
- automation
- report
- refactor
- bugfix with functional impact

If something is unclear, ask for clarification before generating code.

--------------------------------------------------

### 2. Detect impact

Identify all impacted areas.

Analyze at least:

- models
- fields
- views
- menus
- actions
- security
- computed fields
- business rules
- documentation
- tests

Always specify:

- which models are affected
- which files are affected
- whether the feature changes functional behavior

Also consider database impact:

- relational fields (Many2one / One2many / Many2many)
- computed field dependencies
- migration requirements
- possible circular dependencies

--------------------------------------------------

### 3. Check model registry

Before introducing a new model, consult:

docs/model_registry.md

Verify whether the concept can be implemented as:

- a new field
- a relation
- an extension of an existing model

Only propose a new model if the concept has its own lifecycle
and cannot be represented by extending an existing model.

--------------------------------------------------

### 4. Check business rule consistency

Before writing code, consult:

docs/rules_business.md

Verify whether the feature affects:

- document lifecycle
- document movements
- document traceability
- routing or assignment logic

If business rules are impacted, explicitly state that:

rules_business.md must be updated.

--------------------------------------------------

### 5. Check documentation impact

Before coding, determine whether documentation must change.

Update **docs/models.md** if:

- a new model is introduced
- a field is added or modified
- relationships change
- computed fields are added

Update **docs/rules_business.md** if:

- workflow rules change
- document lifecycle rules change
- validation logic changes

Documentation must remain synchronized with implementation.

--------------------------------------------------

### 6. Propose implementation plan

Before generating code, provide a short plan including:

- objective
- affected models
- affected files
- view changes
- security changes
- documentation updates
- test suggestions

--------------------------------------------------

### 7. Generate code

After the plan is clear, generate code.

Requirements:

- fully compatible with Odoo 19
- follow coding_standards.md
- avoid deprecated view patterns
- keep code simple and maintainable
- avoid unnecessary abstraction

View rules for Odoo 19:

- use `<list>` instead of `<tree>`
- avoid deprecated attributes (`attrs`, `states`)
- ensure fields used in views exist in models

--------------------------------------------------

### 8. Close with integrity checklist

Always finish with:

- impacted files
- affected models
- documentation updates required
- tests recommended
- migration considerations
- possible regressions