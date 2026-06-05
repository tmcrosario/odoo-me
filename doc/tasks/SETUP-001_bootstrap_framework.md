# SETUP-001 — Bootstrap del framework SDD en odoo-me

Estado: Done
Modo: L
Riesgo: medio (mueve mucha doc; **no toca** código de `me/` ni `raa/`)
Módulos: me + raa
Responsable: Ale Gallo
Branch: `chore/framework-migration`

> Task card de bootstrap, previo a las épicas. Registra el port del Odoo Agentic
> Delivery Framework desde odoo-junco a odoo-me como **copia propia e
> independiente**, reconciliando la documentación que odoo-me ya tenía.
> Plan de fondo: `MIGRATION_PLAN.md` (raíz del repo).

## Objetivo

Dar a odoo-me su columna SDD (entry point + framework + flujo epics/task-cards +
slash commands), reconciliando la doc existente en los slots `doc/`, y dejar
EPIC-001 listo. Sin tocar código de los módulos.

## Decisiones aplicadas

1. **Copia propia** independiente de junco.
2. **Reescritura single-tool**: se porta la versión depurada VS Code + Claude; no se
   propaga la deuda OpenCode/dos-capas (`.opencode`, `.cursor`, mirror de skills,
   comandos `/code-*-prompt`).
3. **`doc/project/me/` + `doc/project/raa/`**: verdad del proyecto por módulo; raa
   arranca como stub.
4. **`docs/` → `doc/`**: unificar a singular y retirar el viejo al final.
5. **EPIC-001 = reverse-engineering + baseline de `me`**; raa para un epic posterior.

## Alcance

Incluye:

- Columna A: framework genérico + slash commands + templates (depurados single-tool).
- Columna B: entry point reescrito (`AGENTS.md`, `CLAUDE.md`, `project_config.md`).
- Columna C: reconciliación de la doc existente en `doc/project/{me,raa}/` y
  retiro de `docs/`, `ai-rules/`, `prompts/`.
- Columna D: índices + EPIC-001.

No incluye:

- Cambios en código de `me/` ni `raa/`.
- Commits/push/merge sin pedido explícito.
- Implementación de las tasks de EPIC-001.

## Pasos de ejecución

### Paso A — Columna A (framework genérico + depuración) — DONE

- [x] Esqueleto `doc/{framework,skills,tasks/templates,epics/templates}` + `.claude/commands/`.
- [x] Copia de archivos limpios: `delivery_modes`, `git_policy`, `context_policy`,
  `documentation_policy`, `odoo_development_rules` (+ 2 fixes `code-aware`→`critical`).
- [x] 9 slash commands (`test-run` adaptado a módulos `me`/`raa`).
- [x] Templates de task (xs/s/m/full) + epic + `doc/tasks/README.md`.
- [x] Depuración single-tool: `overview`, `testing_policy`, `language_policy`,
  `workflow`, `handoff_policy`, `antipatterns`.
- [x] Reescritura single-tool: `tooling_layers`, `agents_and_artifacts`.
- [x] Skills depuradas: `feature_development`, `bugfix_workflow`, `code_review`,
  `close_gate`.
- [x] Verificación: sin referencias OpenCode/`.cursor`/`/code-*-prompt` en lo portado.

### Paso B — Columna B (entry point reescrito) — DONE

- [x] `AGENTS.md` adaptado single-tool, 2 módulos (reescrito: sin "Roles típicos"
  OpenCode ni "Capas de tooling" dos-capas).
- [x] `CLAUDE.md` de odoo-me (módulos me+raa, comando de test por módulo, branches/PR).
- [x] `doc/framework/project_config.md` sembrado para odoo-me (single-tool, multi-módulo).
- [x] **Decisión cerrada:** destino de PR `develop -> 19.0`, **gestionado por el
  usuario** (el framework no abre/mergea PRs).

### Paso C — Columna C (reconciliar doc → `doc/project/{me,raa}/`) — DONE

Decisiones aplicadas: deprecar docs meta (salvar substancia + borrar) ·
`tmc_base_system` → `doc/project/me/tmc_base_reference.md` · `raa` solo `architecture.md`.

- [x] `doc/project/me/`: `architecture.md` (backbone = analysis report + diagrama +
  principios, con nota de **vigencia**: snapshot 2026-03-26, reconciliar en EPIC-001),
  `workflows.md` (el más actual), `models.md` (dedup models+registry, corrige
  `_inherits`), `business_rules.md` (rules + narrative), `security.md` (stub),
  `tests_plan.md` (stub), `tmc_base_reference.md` (recortada).
- [x] `doc/project/raa/architecture.md` (stub boundary).
- [x] Skill `architecture_analysis` → `doc/skills/` (rutas actualizadas).
- [x] Fusión Odoo 19 `models.Constraint()` en `odoo_development_rules.md`
  (reconcilia contradicción con la línea de `_sql_constraints`).
- [x] Deprecados y borrados: `docs/*` (excepto `todo.md`), `ai-rules/`, `prompts/`,
  `domain-rules/`, `skills/`.
- [x] `docs/todo.md` **se conserva** (semilla de EPIC-001, Paso D).
- Nota: `architecture.md` §7/§10 conservan referencias a rutas viejas como parte del
  snapshot histórico; su reconciliación es trabajo de EPIC-001 (cubierto por la nota
  de vigencia).

### Paso D — EPIC-001 + índices — DONE

Decisiones aplicadas: archivar `todo.md` como legacy read-only · #007 → EPIC-002 ·
EPIC-001 con 3 tasks baseline + #033 como TASK-004.

- [x] `doc/epics/_index.md`, `doc/tasks/_index.md`, `doc/tasks/EPIC-001/_index.md`.
- [x] `EPIC-001_baseline_mesa_de_entradas.md` + TASK-001 (inventario verificado),
  TASK-002 (seguridad), TASK-003 (tests), TASK-004 (#033 jurisdicciones DEM).
- [x] `EPIC-002_integracion_me_junco.md` (Draft, decisiones #007 abiertas, sin tasks).
- [x] `docs/todo.md` archivado en `doc/project/me/_legacy_backlog.md` (con banner
  legacy); `docs/` ya no existe.

## Acceptance criteria

- [x] Existen `AGENTS.md` + `CLAUDE.md` adaptados a odoo-me, single-tool, 2 módulos.
- [x] `doc/framework/*` portado y depurado (cero referencias OpenCode/`.cursor`/
  `.opencode`/mirror/`/code-*-prompt`).
- [x] `doc/skills/*` y plantillas de task/epic presentes.
- [x] `.claude/commands/*` (9) presentes y consistentes con single-tool.
- [x] `doc/project/me/` + `doc/project/raa/` sembrados; huérfanos resueltos.
- [x] `doc/tasks/_index.md`, `doc/epics/_index.md` y `EPIC-001` creados; `docs/`,
  `ai-rules/`, `prompts/`, `domain-rules/`, `skills/` retirados (`todo.md` archivado
  como legacy).
- [x] `me/` y `raa/` (código) sin cambios — `git diff develop..HEAD -- me raa` vacío.

## Tests evidenciados

- Estado: N/A + motivo — cambio puramente documental/tooling, sin código Odoo.

## Verifier / close gate

- Implementación: OK — pasos A–D completos y commiteados (`a101b4c`, `6670764`,
  `2d571f1`, `dbdad15`).
- Acceptance criteria: OK — todos satisfechos.
- Seguridad: N/A — no se tocó security ni código del módulo.
- Tests evidenciados: N/A + motivo (doc/tooling, sin código).
- Verificación: revisión liviana (verifier-lite) — modo L pero **doc-only**, no
  corresponde verifier crítico de código. Chequeos hechos: sin deuda
  OpenCode/`.cursor`/`/code-*-prompt` en lo portado; `git diff` no toca `me/`/`raa/`;
  sin directorios vacíos remanentes; refs a rutas viejas solo en el snapshot
  histórico de `architecture.md` (cubierto por su nota de vigencia).
- Decisión de cierre: **Ready**.

## Cierre

**Done (cierre documental).** Bootstrap del framework SDD completado y portado a
odoo-me como copia propia single-tool. Docs canónicas: los slots `doc/project/me/*`
quedan **sembrados**; su verificación contra código real es trabajo de EPIC-001 (no
es deuda de esta task). Índices actualizados. El desarrollo del módulo `me` continúa
en EPIC-001 sobre `develop` una vez integrada esta branch.
