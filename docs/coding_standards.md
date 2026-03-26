# Project Coding Standards

These rules define how code must be written in generic tmc projects.

They apply to:

- Python code
- Odoo models
- business logic
- error handling
- commits
- development workflow

The goal is to keep the system maintainable, consistent, and predictable as it grows.


--------------------------------------------------
Project Context
--------------------------------------------------

Project: Odoo-based administrative systems
Platform: Odoo 19
Python Version: 3.12


The system must remain consistent and maintainable as the codebase grows and AI-assisted development is used.


--------------------------------------------------
General Development Principles
--------------------------------------------------

1. Prefer simple solutions over complex architectures.

2. Avoid introducing new models unless clearly justified.

3. Avoid duplicating business logic across models.

4. Prefer explicit logic over hidden side effects.

5. The code must always reflect the documented business rules.

6. Business rules must not be hidden in UI logic.


--------------------------------------------------
Commit Style
--------------------------------------------------

Commits must follow the Odoo Git guidelines.

Reference:
https://www.odoo.com/documentation/19.0/contributing/development/git_guidelines.html


Format:

[TYPE] Short description

- Detailed change 1
- Detailed change 2
- Detailed change 3


Allowed types:

ADD – new feature  
IMP – improvement  
FIX – bug fix  
REF – refactor without functional change  
REM – remove code or feature  
MIG – migration between Odoo versions  
UPD – documentation or configuration changes  


Rules:

- Use imperative form.
- Keep the first line under ~72 characters.
- One logical change per commit.
- Do not include AI attribution in commits.


Example:

[ADD] Document review model

- Added SLA computation logic
- Implemented deadline comparison
- Added computed SLA status field


--------------------------------------------------
Python Style
--------------------------------------------------

Follow PEP 8.

Key rules:

- 4 spaces indentation
- No tabs
- Maximum line length: 100 characters
- Use descriptive variable names
- Avoid unnecessary abbreviations


Imports order:

1. standard library
2. third-party libraries
3. odoo modules
4. local modules


Example:

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


--------------------------------------------------
Error Handling
--------------------------------------------------

Use explicit exceptions for business logic errors.

ValidationError

Used for validation rules.

Example:

raise ValidationError(_("Deadline must be in the future."))


UserError

Used when the user must correct an action.


Logging

Use Python logging when needed.

Example:

import logging
_logger = logging.getLogger(__name__)


--------------------------------------------------
Performance Principles
--------------------------------------------------

Avoid N+1 queries.

Prefer:

- read_group for aggregations
- batch operations
- prefetching relations

Avoid loops performing database queries.

Compute fields should use store=True only when necessary.


--------------------------------------------------
Testing
--------------------------------------------------

Tests are strongly recommended for:

- complex business rules
- workflow transitions
- computed fields
- data integrity constraints
- integrations with other modules
- run the relevant Odoo test suite


--------------------------------------------------
Development Workflow
--------------------------------------------------

When implementing changes:

1. Analyze the request
2. Identify impacted models
3. Check business rule consistency
4. Check documentation impact
5. Implement the change
6. Validate behavior


Large features should follow the feature_development skill workflow.


--------------------------------------------------
Documentation Synchronization
--------------------------------------------------

Code changes must remain consistent with the documentation in:

doc/models.md  
doc/rules_business.md

When a change affects:

- models
- fields
- relationships
- workflows
- business rules

The documentation must be updated accordingly.


--------------------------------------------------
Complexity Control
--------------------------------------------------

To prevent system degradation:

- avoid unnecessary abstractions
- avoid premature optimization
- avoid hidden dependencies

If a feature introduces significant complexity, consider:

- refactoring
- simplifying workflows
- documenting architectural decisions

--------------------------------------------------
Documentation Synchronization Rules
--------------------------------------------------

Documentation must always remain synchronized with the codebase.

When a developer or AI agent introduces changes affecting:

- new models
- new fields
- new relationships
- model removals
- changes to state machines
- new business entities

the following documents MUST be updated in the same change:

doc/models.md  
doc/rules_business.md


Required updates when modifying models:

If a new model is introduced:
- add the model to doc/models.md
- document its relationships
- update the Mermaid diagram if necessary
- update the conceptual model overview

If a model gains important fields:
- update the "Key Fields" section

If relationships change:
- update the relationship section and diagram


Changes must be committed in the same commit as the code modification.

Example commit:

[ADD] WorkOrderReview model

- Added model sigop.work_order.review
- Added relation to work orders
- Updated models.md documentation
- Updated model diagram

Language rules

All source code must be written in English.

This includes:

- model names
- field names
- method names
- variable names
- XML ids
- user-visible strings in models and views
- validation messages
- help texts
- labels

Use the Odoo translation system for other languages.

User-facing strings must always be wrapped in _() for translation.

Do not mix Spanish and English in the same string.

Example (correct):

raise ValidationError(_('The dossier number must be greater than zero.'))

Example (incorrect):

raise ValidationError(_('El número de expediente must be greater than zero.'))



--------------------------------------------------
System evolution checklist (AI & developers)
--------------------------------------------------

Whenever you introduce one of the following:

- a new **model**
- a new **field** that affects business behavior
- a new **state** or a change in state transitions
- a new **cron** or automation

you must explicitly check:

- **Business rules**:
  - Does this change affect workflow rules or business constraints?
  - If yes, update `doc/rules_business.md`.
- **Documentation of models**:
  - If models or important fields/relations change, update:
    - `doc/models.md`
    - `doc/model_registry.md`
- **Security**:
  - For new models, ensure entries exist in `security/ir.model.access.csv`
    and record rules if needed.
- **Odoo 19 compatibility**:
  - Verify views and ORM usage against `odoo_common.mdc` and `odoo19.mdc`.

Changes are considered incomplete if code, business rules and documentation
are not kept in sync.