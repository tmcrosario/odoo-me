# Code Review Workflow

Use this skill when reviewing code changes in the **odoo-me** project.

--------------------------------------------------
## 1. Understand the change
--------------------------------------------------

Identify:

- which models are affected
- which views are modified
- whether the change affects business logic or presentation only.

Typical ME models include:

- `document_exp`
- `document_movement`

--------------------------------------------------
## 2. Architecture consistency
--------------------------------------------------

Verify consistency with:

domain-rules/me/me_architecture.md

Key architectural principles:

- ME extends the base document system
- document_exp represents documents inside ME
- document_movement records document traceability
- movements must always reference a document

Avoid introducing duplicate core entities.

--------------------------------------------------
## 3. Business rule consistency
--------------------------------------------------

Compare the implementation with:

docs/rules_business.md

Verify that changes do not violate:

- document traceability rules
- movement integrity
- document lifecycle assumptions

Flag:

- missing validations
- undocumented new rules
- forbidden transitions made possible

--------------------------------------------------
## 4. Odoo 19 compatibility
--------------------------------------------------

Verify compliance with:

ai-rules/odoo/odoo_common.mdc  
ai-rules/odoo/odoo19.mdc  

Checklist:

- modern ORM API
- no deprecated XML attributes
- views use `<list>` instead of `<tree>`
- no legacy API usage

--------------------------------------------------
## 5. Documentation and security
--------------------------------------------------

Documentation:

Check whether changes require updates to:

docs/models.md  
docs/model_registry.md  
docs/rules_business.md  

Security:

Verify that:

- new models have access rules
- security groups remain coherent
- no unintended permission escalation occurs.

--------------------------------------------------
## 6. Risk analysis
--------------------------------------------------

Identify risks such as:

- regressions in document movement logic
- traceability inconsistencies
- performance problems
- excessive complexity

Recommend tests when business rules are affected.

--------------------------------------------------
## 7. Review summary
--------------------------------------------------

Summarize:

- models affected
- files changed
- documentation updates required
- possible regressions
- recommendations.