# Coding Standards

This document defines the coding standards for the ME project.

Its goal is to keep the codebase:

- consistent
- maintainable
- easy to review
- easy to evolve with AI-assisted development

---

## General Principles

- Prefer clarity over cleverness
- Keep modules small and focused
- Avoid duplicated logic
- Reuse Odoo conventions whenever possible
- Do not introduce architectural complexity without clear need

---

## Odoo Conventions

- Follow standard Odoo module structure:
  - `models/`
  - `views/`
  - `security/`
  - `wizards/`
  - `data/`
  - `tests/`
- Use Odoo ORM conventions consistently
- Prefer explicit model relationships over implicit logic
- Keep business logic in models, not in views
- Use views only for presentation and interaction flow
- Avoid putting business rules only in domains or onchange methods
- If a rule is important, validate it in backend too

---

## Python Style

- Use clear and descriptive names
- Keep methods short and focused
- Avoid deeply nested logic when possible
- Prefer helper methods when logic becomes repetitive
- Use comments only when the intention is not obvious from the code
- Do not leave dead code commented out unless there is a temporary and justified reason
- Remove debug prints before closing a task

---

## XML / Views Style

- Keep views readable and well organized
- Use meaningful XML ids
- Avoid unnecessary duplication in views
- Prefer simple and explicit domains
- Keep form views aligned with the real workflow of the model
- Do not encode important business rules only in the UI

---

## Naming Conventions

Use English for all technical artifacts.

This includes:

- model names
- field names
- method names
- variable names
- XML ids
- Python comments
- test class names
- test method names
- internal technical constants

Examples:

- `document_movement`
- `current_dependence_id`
- `action_create_process`
- `test_create_expediente_generates_movements` ❌
- `test_create_expediente_generates_movements` should be avoided because it mixes languages
- `test_create_record_generates_movements` ✅

---

## Language Rules

All technical code artifacts must be written in English.

This includes:

- Python code
- model names
- field names
- method names
- variable names
- XML ids
- technical comments
- test names

User-facing strings in models and views should also be written in English
and wrapped in `_()` so they can be translated through Odoo i18n.

Do not mix Spanish and English in the same string.

Use Spanish only in:

- functional documentation
- backlog descriptions
- business notes
- translation files (`i18n/*.po`)
- user-facing translated text when required by the system

---

## Business Logic Rules

- Important rules must live in backend code
- Do not rely only on `onchange` for critical validations
- Do not rely only on view domains for data integrity
- If a value must be restricted, validate it in the model
- Prefer explicit constraints for integrity rules
- If behavior depends on another module, document that dependency clearly

---

## Tests

- Every important functional change should include tests
- Tests must live in `tests/`
- Prefer focused tests with minimal setup
- Test names must describe behavior clearly
- Cover:
  - expected behavior
  - validation errors
  - important side effects
- Do not close an implementation task without validating whether tests are needed

---

## Documentation Alignment

Whenever a change affects behavior, evaluate whether these files must be updated:

- `docs/system_overview.md`
- `docs/system_narrative.md`
- `docs/models.md`
- `docs/model_registry.md`
- `docs/rules_business.md`
- `domain-rules/me/workflows.md`
- `me/ai-context.md`

Code is the final source of truth, but documentation must be kept aligned.

---

## Security and Access

- Do not assume UI restrictions are enough
- Validate permissions in backend when needed
- If access rules are important for a feature, review:
  - `security/ir.model.access.csv`
  - related security XML files
- If a feature changes who can read/write/create/delete, document it

---

## Commits

The AI must not execute commits.

It should only suggest:

- commit name
- short description

Allowed labels:

- `[IMP]` – Improvements and enhancements
- `[FIX]` – Bug fixes
- `[ADD]` – Add new features or modules
- `[REM]` – Remove features or code
- `[REF]` – Refactoring (no functional changes)
- `[MIG]` – Migration between Odoo versions
- `[UPD]` – Updates to documentation or configurations
- `[WIP]` – Work in progress (avoid in main branch)

Always choose the label that best represents the main purpose of the change.

---

## AI-Assisted Development

Before proposing code changes, review available project context:

- `me/ai-context.md`
- `docs/system_overview.md`
- `docs/system_narrative.md`
- `docs/architecture_diagram.md`
- `docs/me_architecture_analysis_report.md`
- `domain-rules/me/workflows.md`
- `todo.md`

Rules for AI-assisted work:

- Do not invent behavior not supported by code or documentation
- If something is unclear, mark it as `Uncertain / pending definition`
- If backlog decisions are still open, do not jump directly to implementation
- Prefer backlog → definition → implementation → tests → review

---

## Final Rule

Readable code, explicit logic, aligned documentation, and validated behavior
are always more important than writing code quickly.