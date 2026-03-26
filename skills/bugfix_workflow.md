# Bugfix Workflow

Use this skill when fixing a bug in the **odoo-me** project.

--------------------------------------------------
## 1. Understand and reproduce
--------------------------------------------------

Confirm the exact symptom:

- error message
- incorrect behavior
- incorrect data

Reproduce the issue in a controlled environment.

Identify affected components:

- models (for example `document_exp`, `document_movement`)
- views
- menus
- actions
- security rules

--------------------------------------------------
## 2. Locate the source
--------------------------------------------------

Search in:

models/
views/
security/
wizards/

Check for:

- compute methods
- constraints
- overridden methods (`create`, `write`, `unlink`)
- domain filters
- visibility rules in views

--------------------------------------------------
## 3. Check documentation
--------------------------------------------------

Verify the expected behavior using:

docs/rules_business.md  
docs/models.md  
docs/model_registry.md  
domain-rules/me/me_architecture.md  
me/ai-context.md  

Determine whether:

- the code is incorrect
- or the documentation is outdated.

--------------------------------------------------
## 4. Implement the fix
--------------------------------------------------

Prefer the **minimal change** that:

- fixes the bug
- preserves architecture
- avoids unintended side effects

Business logic must live in models, not views.

--------------------------------------------------
## 5. Update documentation if needed
--------------------------------------------------

Update documentation when:

- behavior changes
- validation rules change
- relationships change

Possible updates:

docs/models.md  
docs/rules_business.md  
docs/model_registry.md  

--------------------------------------------------
## 6. Validate and check regressions
--------------------------------------------------

Verify that:

- the original bug is fixed
- document lifecycle still works
- document movements remain consistent
- no access errors appear

When appropriate, suggest or add a test for the bug scenario.