# Migration Notes — odoo-me (14.0 → 19.0)

Two modules: `me` (Mesa de Entrada) and `raa` (Registro de Actos Administrativos,
depends on `me`).

This repo had a **pre-existing, partially-migrated `19.0` branch**. Most
model/view/security work was already done there (the `raa` wizards `entry.py` /
`number_range.py` were heavily refactored, the security was already migrated to the 19.0
`res.groups.privilege` pattern). This round finished the one remaining deprecation and
added OCA tooling. The `18.0` branch did not exist for this repo.

## Summary of changes by category

### Models / wizards

- No source changes required. `raa/models/registry_aa.py`, `raa/wizards/entry.py`,
  `raa/wizards/number_range.py` already use the modern API (verified: no `name_get`,
  `fields_view_get`, `_translate`, `xmlid_to_res_id`, `read_group`, `_cr/_uid/_context`,
  single-record `create`).

### Views / reports

- `raa/reports/missing_raa_template.xml`: converted all 6 QWeb `t-esc="..."` →
  `t-out="..."` (16.0/17.0). These are simple value outputs; `t-out` HTML-escapes by
  default like the old `t-esc`, so behavior is preserved.
- No `<tree>`, `attrs`, `states`, `view_mode` tree, or `tree_view_ref` remained (already
  converted on the pre-existing branch).

### Security

- **Already correct for 19.0** — no change needed. `me/security/me_groups.xml` and
  `raa/security/raa_groups.xml` already use the new 19.0 model: a `res.groups.privilege`
  record (whose `category_id` points to `ir.module.category`) and `res.groups` records
  referencing it via the new `privilege_id` field. This is the canonical 19.0 security
  pattern for this codebase.

### Manifests

- `me`: `version` `19.0.1.0.0`, `license` `AGPL-3`, `depends` `["tmc"]`, `installable`
  True — all correct.
- `raa`: `version` `19.0.1.0.0`, `license` `AGPL-3`, `depends` `["tmc", "me"]`,
  `installable` True — all correct.

## 18.0 branch

- Did not exist. The `19.0` branch is the pre-existing partial migration; continued on
  top of it.

## Removed dependencies

- None.

## Dependencies to verify before push

- `tmc` / `me` are internal (migrated in this batch) — confirm installable at 19.0.

## attrs conversions to review

- None (none remained).

## Autosave / onchange → constrains conversions

- None required (no `@api.onchange` raising exceptions found).

## Tooling note — ruff.toml removed (adopt OCA stack)

- The repo had a stray untracked `ruff.toml` (pre-existing WIP). Per the migration
  decision to standardize ALL repos on the canonical OCA 19.0 stack (which is itself
  ruff-based, configured via `pyproject.toml`), the stray `ruff.toml` was removed so it
  cannot conflict with the OCA ruff config. The pre-existing tree was stashed before
  migrating and restored afterward; on restore the `ruff.toml` was deleted (it is
  untracked, so it appears in neither commit). The OCA `pyproject.toml` provides the
  authoritative ruff configuration.

## Items left for human review

- None specific. (Security already on the 19.0 privilege pattern; nothing ambiguous was
  changed.)

## Lint findings

- Captured in the `[ADD]` tooling commit. Non-blocking reporters only.

## Translations

- Translation regeneration deferred to a later stage.
