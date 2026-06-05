# Plan de migración — Framework SDD para odoo-me

> Documento de traspaso. Escrito desde el repo **odoo-junco** (que ya tiene el
> framework) para portarlo a **odoo-me** (mesa de entradas + raa).
> Es el alcance acordado; el chat nuevo lo ejecuta como primer task card de setup.

## Objetivo

Dar a odoo-me la **columna SDD** que hoy no tiene (entry point doctrinal + flujo
de epics/task-cards + slash commands), **reconciliando** la documentación que
odoo-me YA tiene (que es rica) en los slots del framework. No es copiar y pisar:
es mapear lo existente y agregar solo lo que falta.

## Decisión base (ya tomada)

- **Copia propia.** odoo-me tiene su propia instancia del framework, independiente
  de junco, aunque los módulos estén relacionados. No se consume una fuente
  compartida.

## Estado de partida

**odoo-junco (fuente del framework):**
`AGENTS.md` + `CLAUDE.md` (entry point) + `doc/framework/*` (14) +
`doc/skills/*` (4) + `doc/project/*` + `doc/tasks` (epics + templates) +
`doc/epics/*` + `.claude/commands/*` (9 slash commands).

**odoo-me (hoy, forma "vieja" estilo Cursor):**
`ai-rules/odoo/*.mdc` · `domain-rules/{me,raa}/*` · `docs/*` (14 archivos) ·
`skills/*` (4) · `prompts/*` · `.claude/settings.local.json` (sin commands) ·
módulos `me/` (mesa de entradas) + `raa/`.
**No tiene** `AGENTS.md`, `CLAUDE.md`, `doc/framework`, ni flujo epics/task-cards.

## Mapa de migración

### A. Columna del framework (se copia ~1:1 desde junco — genérica)
- `AGENTS.md`
- `doc/framework/*` (overview, delivery_modes, odoo_development_rules, git_policy,
  testing_policy, context_policy, documentation_policy, language_policy,
  antipatterns, workflow, project_config, etc.)
- `doc/skills/*` (bugfix_workflow, feature_development, code_review, close_gate)
- `doc/tasks/templates/*` (xs/s/m/full) + `doc/epics/templates/epic.md`
- `.claude/commands/*` (9 slash commands)

### B. Entry point (se REESCRIBE para odoo-me)
- `CLAUDE.md` — adaptar a odoo-me: módulos **`me` + `raa`** (junco es mono-módulo),
  comando de test por módulo, convención de branches/PR (confirmar destino de PR;
  junco usa `develop -> 19.0`, odoo-me está en `develop`).

### C. Verdad del proyecto (se SIEMBRA desde lo que odoo-me YA tiene)
| odoo-me (hoy) | → slot framework |
|---|---|
| `docs/rules_business.md` | `doc/project/business_rules.md` |
| `docs/model_registry.md` + `docs/models.md` | `doc/project/models.md` |
| `docs/system_overview.md` + `docs/me_architecture_analysis_report.md` | `doc/project/architecture.md` |
| `domain-rules/me/*`, `domain-rules/raa/*` | `doc/project/*` (ya es dominio) |
| `docs/coding_standards.md` | fusionar en `doc/framework/odoo_development_rules.md` |
| `docs/development_workflow.md` | contrastar con `doc/framework/workflow.md` |
| `docs/todo.md` + analysis report | semilla del primer EPIC real |
| `skills/architecture_analysis.md` (extra) | sumar a `doc/skills/` (unión, no duplicar) |
| `ai-rules/odoo/*.mdc` (Cursor) | convertir a `odoo_development_rules.md` y deprecar el `.mdc` |
| `prompts/*` | evaluar: la mayoría la reemplazan los slash commands |

## Decisiones de fondo pendientes (resolver en el chat nuevo)

1. ✅ Copia propia (resuelto).
2. **Copiar limpio, no la deuda.** La `doc/framework` de junco todavía arrastra el
   modelo OpenCode/dos-capas (deuda documental tolerada en junco por razón
   histórica). En odoo-me NO hay esa razón: es greenfield. Copiar la versión ya
   depurada single-tool y **no propagar la deuda** a un repo nuevo.
3. **Dos módulos (`me` + `raa`).** Definir si `doc/project` es compartido o por
   módulo. Recomendación: `doc/project/me/` + `doc/project/raa/`.
4. **`docs/` → `doc/`.** odoo-me usa `docs/` (plural); el framework usa `doc/`
   (singular). Unificar a `doc/` y retirar el viejo cuando esté migrado.
5. **Primer epic.** No arrancar de cero: `EPIC-001` = "reverse-engineering +
   baseline de mesa de entradas", sembrado con `docs/` + el analysis report.

## Primer paso en el chat nuevo

Un task card de **setup/init** (el `project_config.md` del framework):
1. Instala columna A + B (framework + entry point reescrito).
2. Ejecuta el mapeo C (reconcilia la doc existente).
3. Deja `doc/tasks/_index.md` + `EPIC-001` listos.

Riesgo: medio (mueve muchos archivos de doc). **No toca código** de `me/` ni `raa/`.

## Guardarraíles (heredados de la doctrina del repo)

- **Git seguro**: no commitear / pushear / mergear sin pedido explícito.
- No inventar reglas de negocio: lo no especificado queda como pregunta / riesgo / N/A.
- Single-tool: VS Code + Claude. Nada de OpenCode/Cursor en la columna nueva.
- Idioma: metodología y task cards en español rioplatense; reglas de código en
  inglés técnico.
