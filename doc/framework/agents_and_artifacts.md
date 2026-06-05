# Agentes y artifacts

Documento canónico que reúne en un solo lugar:

- **Quién hace qué** (modos de trabajo y comandos);
- **Qué archivos puede tocar cada paso** y cuáles no;
- **Cuándo usar cada uno**;
- **Mapa de artifacts** (carpetas, archivos clave, propósito).

> odoo-me se opera con **VS Code + Claude** (un solo operador). Los "agentes" son
> **modos internos** de la misma sesión, expuestos como slash commands en
> `.claude/commands/`. No hay capas separadas de herramientas: las fases son
> compuertas de disciplina (ver `doc/framework/tooling_layers.md`).

## Modos y comandos

| Modo / comando | Qué hace | Puede tocar | NO puede tocar | Cuándo usarlo |
| --- | --- | --- | --- | --- |
| `/flow` | Clasifica el pedido y propone el siguiente paso; sin pedido concreto, analiza estados/prioridades | `doc/epics/`, `doc/tasks/`, `doc/framework/project_config.md` | Código Odoo (`models/`, `views/`, `security/`, `data/`, `tests/`) | Al inicio de cada pedido o al retomar sin recordar el estado |
| Setup (bootstrap) | Configura identidad, módulos, herramientas, tests, git, riesgos | `doc/framework/project_config.md`, `doc/project/**`, `doc/epics/_index.md` | Código Odoo | Primer uso del framework |
| `/new-idea` | Decide si una idea abre épica o entra en una existente | `doc/epics/_index.md`, epic cards puntuales | Tasks sueltas (toda task pertenece a una épica) | Cuando aparece una capacidad nueva |
| `/new-task` | Crea task card con el template más chico compatible con el riesgo | `doc/tasks/EPIC-XXX/` | Código Odoo | Al abrir una unidad de trabajo |
| `/product-spec` | Aclara objetivo, alcance, reglas, criterios | Task card, `doc/project/<modulo>/business_rules.md` (lectura) | Código Odoo | Para cerrar definición funcional |
| `/prepare-task` | Confirma readiness: asignación, riesgos, modo, próximo paso | Task card | Código Odoo | Antes de contrato o implementación |
| `/contract-draft` | Fija el plan/contrato técnico (diseño) antes de implementar | Task card, docs aplicables (lectura mínima) | Implementación | Modo M/L/XL o áreas sensibles |
| Implementación | Modifica código Odoo siguiendo el contrato | `models/`, `views/`, `security/`, `data/`, `tests/` | Cierre documental `Done` | Cuando hay que tocar código con criterios claros |
| Verificación | Revisión crítica diff-first: criterios, security, riesgos, tests | Código, diffs, task card, docs (lectura) | Marcar `Done` documental | Después de implementación sensible |
| `/test-run` | Coordina evidencia de tests | `doc/project/<modulo>/tests_plan.md`, task card | Declarar OK sin evidencia | Validación user-run |
| `/doc-close` | Cierra documentación con evidencia | Task card, `_index.md`, docs canónicas (solo al cierre) | Código Odoo | Cuando hay evidencia suficiente |
| `/commit-ready` | Prepara o ejecuta commits seguros | `git status`, `git diff`, `git log` | Push sin pedido, commit sin confirmación | Antes/después de implementar, bajo pedido |

## Skills

Las skills viven en `doc/skills/` y son la fuente de las prácticas. Se aplican como
guía dentro de la sesión VS Code + Claude:

| Skill | Rol | Cuándo usarlo |
| --- | --- | --- |
| `feature_development` | Flujo de implementación de features | Nueva funcionalidad |
| `bugfix_workflow` | Flujo de fix de bugs | Corrección de errores |
| `code_review` | Checklist de revisión crítica | Revisión de cambios |
| `close_gate` | Check final: implementación/security/tests/docs | Antes de `/doc-close` |
| `architecture_analysis` | Relevamiento y análisis arquitectónico | Reverse-engineering / baseline |

## Tabla de transiciones de estado

Ver `doc/framework/workflow.md` (sección **Tabla de transiciones**) para el detalle
de quién puede hacer cada transición y qué precondiciones aplican.

Resumen rápido:

- `Draft → Ready`: modo `product-spec` o `contract-draft`.
- `Ready → Implemented`: implementación.
- `Implemented → Verified`: verificación.
- `Verified → Done`: **solo** `/doc-close`.

## Paso a paso operativo

| Fase | Comando / acción | Output / decisión |
| --- | --- | --- |
| Clasificar | `/flow` | Próximo paso recomendado y modo probable |
| Ubicar idea | `/new-idea` | Nueva épica o épica existente |
| Crear task | `/new-task` | Task card bajo `doc/tasks/EPIC-XXX/` con asignación inicial |
| Definir producto | `/product-spec` | Objetivo, alcance, no-alcance, reglas conocidas y acceptance criteria |
| Preparar handoff | `/prepare-task` | Readiness: asignación, riesgos, modo y próximo paso |
| Contrato técnico | `/contract-draft` | Plan técnico, riesgos y contexto consolidado en la task card |
| Implementar | Paso de implementación | Cambios Odoo y execution report; no cierre documental |
| Evidenciar tests | `/test-run` | Evidencia de tests o `PENDIENTE USER-RUN` / `N/A + motivo` |
| Verificar | Paso de verificación | Close gate `Ready` / `Blocked`; no cierre documental |
| Cerrar docs | `/doc-close` | Task `Done` y docs canónicas actualizadas/diferidas/N/A |
| Commit | `/commit-ready` | Commit preparado o ejecutado solo bajo pedido explícito |

### Ruta típica

```text
/flow
→ /new-idea si no hay épica clara
→ /new-task
→ /product-spec si falta definición funcional
→ /prepare-task
→ /contract-draft si el cambio es M/L/XL o sensible
→ implementación
→ /test-run
→ verificación (crítica en L/XL)
→ /doc-close
→ /commit-ready solo si el usuario pide commit
```

### Regla de fases

Definir y consolidar contexto antes de implementar. La implementación lee código y
toca `models/`, `views/`, `security/`, `data/`, `tests/`; los pasos documentales no.
Los enganches entre fases no dependen del historial de chat: contrato técnico,
execution report, close gate, evidencia de tests y bloqueos se persisten en la task
card (ver `doc/framework/handoff_policy.md`).

## Mapa de artifacts del framework

| Artifact | Ubicación | Para qué sirve |
| --- | --- | --- |
| Punto de entrada | `CLAUDE.md` | Entry point para Claude; remite a `AGENTS.md` |
| Reglas globales | `AGENTS.md` | Contrato general / doctrina |
| Metodología | `doc/framework/` | Flujo, modos, políticas y handoff |
| Configuración del proyecto | `doc/framework/project_config.md` | Identidad, módulos, herramientas, tests, git y riesgos |
| Política de idioma | `doc/framework/language_policy.md` | Español rioplatense vs inglés técnico |
| Reglas Odoo 19+ | `doc/framework/odoo_development_rules.md` | Reglas técnicas para implementar y revisar código |
| Comandos | `.claude/commands/` | Forma operativa de usar el framework |
| Skills | `doc/skills/` | Prácticas reutilizables (feature, bugfix, review, close gate, analysis) |
| Política Git | `doc/framework/git_policy.md` | Commit seguro guiado |
| Antipatrones | `doc/framework/antipatterns.md` | Errores típicos a evitar |
| Licencia | `LICENSE` | LGPL-3.0 |

## Mapa de artifacts del proyecto

| Artifact | Ubicación | Para qué sirve |
| --- | --- | --- |
| Épicas | `doc/epics/` | Capacidades o líneas funcionales |
| Tasks | `doc/tasks/EPIC-XXX/` | Unidades de trabajo dentro de una épica |
| Plantillas de task | `doc/tasks/templates/` | XS/S/M/FULL según intensidad |
| Plantillas de épica | `doc/epics/templates/` | Estructura de epic card |
| Docs canónicas por módulo | `doc/project/me/`, `doc/project/raa/` | Arquitectura, reglas, modelos, seguridad y tests de cada módulo |
| Hotfix log | `doc/tasks/_hotfix_log.md` | Registro de hotfixes ad-hoc |
| Migraciones | `doc/project/<modulo>/migrations.md` | Histórico cronológico de migraciones |

## Reglas de acceso a archivos

- **Toda task vive dentro de una épica**: `doc/tasks/EPIC-XXX/TASK-YYY_*.md`.
- **No hay backlog plano** tipo `todo.md`. Si algo no pertenece claramente a una
  épica, usar `/new-idea`.
- **Los pasos documentales no tocan** `models/`, `views/`, `security/`, `data/` ni
  `tests/`, salvo lectura puntual.
- **`/doc-close` es la única ruta válida** para marcar `Done` documental.

## Cuándo actualizar docs canónicas

- **Durante implementación/fix**: la verdad operativa vive en la task card y en los
  índices (`_index.md`).
- **En `/doc-close`** (cuando hay evidencia suficiente y la regla es durable):
  - `doc/project/<modulo>/business_rules.md`
  - `doc/project/<modulo>/models.md`
  - `doc/project/<modulo>/architecture.md`
  - `doc/project/<modulo>/security.md`
  - `doc/project/<modulo>/tests_plan.md`
- **N/A con motivo**: si el cambio es puramente local y sin ambigüedad documental.
- **Diferidas**: registrar en la task card como **Docs canónicas pendientes de
  consolidación**. No tienen SLA estricto por defecto; se revisan on-demand.
