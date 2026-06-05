# Architecture Analysis Workflow

Use this skill to perform a **deep architectural analysis**
of an Odoo module before modifying or extending it.

This workflow is especially useful for:

- legacy modules
- migrations between Odoo versions
- poorly documented systems
- preparing AI-assisted development


--------------------------------------------------
## Purpose
--------------------------------------------------

The goal of this workflow is to understand how the module
actually works **based on the existing code**, not assumptions.

The analysis should identify:

- models
- relationships
- workflows
- business rules
- architectural constraints
- integration points with other modules


--------------------------------------------------
## Project context
--------------------------------------------------

The repository contains two main modules:

me → Mesa de Entradas  
raa → Registro de Actos Administrativos

The current development focus is **ME**.

The system depends on an external document system providing:

tmc.document

ME extends this base model.

Core ME models typically include:

- document_exp
- document_movement

RAA exists in the repository but is outside the current
development scope and should not be modified.


--------------------------------------------------
## Files to analyze
--------------------------------------------------

Primary analysis targets:

me/models  
me/views  
me/security  
me/wizards  

Secondary context:

raa/models  
doc/project/me/architecture.md  
doc/project/me/models.md  
doc/project/me/business_rules.md  
doc/project/me/workflows.md  
doc/project/me/tmc_base_reference.md  


--------------------------------------------------
## Analysis steps
--------------------------------------------------

Follow these steps in order.


### 1. Identify models

List all models defined in the module.

For each model determine:

- model name
- file location
- purpose
- main responsibilities


### 2. Identify inheritance

Detect model inheritance patterns.

Pay special attention to:

tmc.document

Identify which models extend or depend on it.


### 3. Identify relationships

Detect relationships between models:

- Many2one
- One2many
- Many2many

Explain how the entities interact.


### 4. Detect business logic

Search for important logic in:

- compute methods
- constraints
- overridden methods
- action methods
- workflow logic


### 5. Detect workflow patterns

Attempt to identify:

- document lifecycle
- routing logic
- movement logic
- traceability mechanisms

If the workflow is unclear, mark it as:

"uncertain"


### 6. Detect architectural constraints

Identify important design assumptions, such as:

- documents must originate from the base system
- movements always reference a document
- traceability must be preserved


### 7. Detect migration risks

Because the module originates from **Odoo 14**, detect patterns
that may cause migration issues in **Odoo 19**, such as:

- deprecated XML view attributes
- outdated ORM patterns
- legacy APIs


--------------------------------------------------
## Expected output
--------------------------------------------------

Produce a structured analysis report with the following sections:

1. Module Purpose  
2. Models Detected  
3. Model Relationships  
4. Inferred Workflow  
5. Business Logic Locations  
6. Architectural Constraints  
7. Uncertain Areas  
8. Migration Risks


--------------------------------------------------
## Important rules
--------------------------------------------------

- Do not invent behavior not present in the code.
- Do not propose refactors in this step.
- Mark unclear areas as **uncertain**.
- Treat documentation as helpful context, but use **code as source of truth**.


--------------------------------------------------
## Outcome
--------------------------------------------------

The results of this analysis will be used to update the canonical project docs:

doc/project/me/architecture.md  
doc/project/me/models.md  
doc/project/me/business_rules.md  
doc/project/me/workflows.md