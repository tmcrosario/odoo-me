# Odoo Development Rules

## Baseline

This framework assumes **Odoo 19 or newer**.

When a rule changes in a future Odoo version, update this file or document the exception in the task card.

## General Principles

- Prefer simple and explicit solutions.
- Do not add new models unless the specification or technical contract justifies them.
- Do not duplicate business logic across models.
- Business rules belong in backend Python, not only in views.
- UI rules must not be the only security barrier.
- Keep changes small and cohesive within the task scope.

## Models

- Follow Odoo model naming conventions.
- Use descriptive and globally unique technical names.
- Define `_description` for new models.
- Avoid new models when an existing concept can be extended without forcing the design.
- Every new persistent model requires ACL and record-rule analysis.

## Fields

- Use descriptive `snake_case` names.
- Avoid vague names such as `data`, `value`, `info`, or `flag` unless the meaning is obvious from context.
- Define `string`, `help`, `required`, and `default` when they add clarity.
- User-visible Python strings must be translatable with `_()`; XML strings should be ready for i18n.

## Relations

- Relations must be explicit.
- Define `ondelete` for `Many2one` fields when data integrity matters.
- `One2many` fields must declare the correct inverse field.
- Avoid unnecessary `Many2many` relations.
- Before adding relations, review data impact and migration risk.

## Computed Fields

- Every computed field must declare dependencies with `@api.depends`.
- Use `store=True` only with a concrete reason: searches, reports, performance, or business semantics.
- Avoid circular dependencies.
- Keep compute methods batch-friendly; avoid per-record queries when precomputation is possible.

## Constraints And Validations

- Use `@api.constrains` for business rules.
- For uniqueness and simple DB-level validations in **Odoo 19**, use
  `models.Constraint(...)` as a class attribute. The legacy `_sql_constraints` list is
  **deprecated and has no effect in Odoo 19** — do not use it.

  ```python
  # Odoo 19:
  _unique_movement = models.Constraint(
      'UNIQUE(expediente_id, origin_dependence_id, destination_dependence_id, date)',
      'A movement with the same origin, destination and date already exists.',
  )
  ```

  The attribute name must start with `_`; the DB constraint name becomes
  `{model._table}_{name_without_leading_underscore}`; the message is shown on violation.
- Business errors should use explicit exceptions (`ValidationError`, `UserError`) with translatable messages.
- Do not rely only on `onchange` for validations; backend code must enforce the rule.

## States And Workflow

- State fields should be clear `Selection` fields and documented when they affect behavior.
- State transitions should live in explicit `action_*` methods.
- Avoid scattered direct state changes in `write()` unless the reason is documented.
- Sensitive workflows escalate to L/XL mode and require critical verification.

## Security

- Every new persistent model requires an entry in `security/ir.model.access.csv` or an explicit N/A reason.
- Sensitive `create`, `write`, and `unlink` permissions should be granted through explicit groups.
- Prefer default-deny for sensitive operations.
- Avoid `sudo()` unless there is a strong technical reason and it is documented.
- Permission changes should include or recommend negative-path tests (`with_user` + `AccessError`) when practical.
- Readonly/invisible UI attributes do not replace ACLs, record rules, or backend validations.

## Performance

- Avoid N+1 queries.
- Prefer batch operations and prefetch-friendly code.
- Use `read_group` for aggregations when appropriate.
- Do not perform heavy searches inside loops when the data can be prefetched or grouped.

## XML And Views For Odoo 19+

- In Odoo 19+, use `<list>`, not `<tree>`.
- Do not use `attrs`.
- Do not use `states` in views/fields.
- Do not use `statusbar_colors`.
- Use explicit attributes with expressions:
  - `invisible`
  - `readonly`
  - `required`
  - `widget`
  - `options`
- Example:

```xml
<field name="date_done" invisible="state != 'done'"/>
```

- Do not put business rules only in XML.
- Verify that widgets exist and are compatible with the target Odoo version.

## OWL And Frontend

- Prefer existing widgets and components before adding custom frontend code.
- Keep frontend logic minimal.
- If JS, tour, or portal behavior changes, document expected tests or N/A with reason.

## Server Actions And Cron

- Server actions should follow standard Odoo structure.
- Cron jobs should be defined with `ir.cron` and call a clear model method.
- Avoid complex logic embedded directly in XML server actions; prefer Python model methods.

## Module Structure

Expected Odoo module structure:

```text
models/
views/
security/
data/
static/
tests/
```

Each relevant model usually needs:

- a Python file in `models/`;
- a view/action/menu when applicable;
- ACL when persistent;
- tests or N/A with reason when behavior changes.

## Tests

Tests are expected, or explicitly N/A with reason, for:

- business rules;
- workflow/state changes;
- security/permissions;
- persistent models/fields;
- migrations/existing data;
- bugfixes with regression risk.

Never report tests as `OK` without evidence.

## Migrations

If a change affects existing data, persistent fields, constraints, or relations:

- escalate to L/XL mode;
- document migration risk in the task;
- define migration script/strategy when applicable;
- request critical review.

## Future Compatibility

- Avoid legacy patterns from older Odoo versions unless explicitly verified.
- If an exception is needed for compatibility, document it in the task card and contract.
- When upgrading Odoo versions, review this file as part of the framework update.
