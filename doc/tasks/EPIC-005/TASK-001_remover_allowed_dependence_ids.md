# EPIC-005 / TASK-001 — Remover campo muerto `allowed_dependence_ids`

Estado: Done
Modo: XS
Riesgo: bajo (campo computed no-stored, sin referencias)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
- Notas: follow-up de EPIC-001/TASK-001 (§8.6).

## Objetivo

Remover `allowed_dependence_ids` de `me.document_exp`: campo Many2many computed
(`@api.depends()` vacío) **sin uso real** — la vista filtra `dependence_id` con un domain
hardcodeado `[('abbreviation','in',['DEM','TMC','CM'])]`, no con este campo.

## Alcance

- Remover el campo (`document_exp.py` l.17) y su compute `_compute_allowed_dependencies`.
- Corregir `me/ai-context.md` (afirmaba erróneamente que el campo "enforces" el filtro).

No incluye: el domain hardcodeado de la vista (se mantiene; es el que realmente filtra).

## Verificación previa (sin referencias)

`grep` en todos los addons (`odoo-me`, `odoo-junco`, `odoo-tmc`, `odoo-tmc-data`, todo tipo
de archivo): **cero referencias de código/XML** fuera de la definición + el compute. El
resto eran menciones en documentación.

## Acceptance criteria

- [x] Campo + compute removidos de `document_exp.py`.
- [x] Sin referencias rotas (verificado en todos los addons).
- [x] Suite `/me` verde tras la remoción.
- [x] `ai-context.md` corregido.

## Tests evidenciados

- Estado: OK
- Comando: `... exec -T odoo odoo -d me_test -u me --addons-path=<...> --test-tags /me --stop-after-init ...`
- Fecha: 2026-06-22
- Resultado: **0 failed, 0 error(s) of 201 tests** (247 métodos) sobre `me_test`.
- Aplicado a me2 (`-u me`) + restart odoo; sin superficie de UI (campo era invisible/sin uso).

## Estado / próximo paso

**Done.** Push: usuario.

## Resultado / cierre

Cerrada (Done) el 2026-06-22. Removido el campo muerto + su compute; `ai-context.md`
corregido. Suite verde. El domain hardcodeado de la vista (el que filtra de verdad) intacto.
