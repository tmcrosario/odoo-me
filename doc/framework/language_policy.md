# Política de idioma

## Regla general

El framework usa dos registros de idioma según audiencia:

- **Español rioplatense** para la interfaz humana y metodológica.
- **Inglés técnico** para las reglas de código y la implementación Odoo.

La idea es que el equipo entienda fácil el proceso, pero que las instrucciones que
operan sobre código queden compactas y alineadas al vocabulario técnico de
Odoo/Python/XML.

## Español rioplatense

Usar español rioplatense en:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/commands/*.md`
- `doc/framework/*.md` (metodología: workflow, delivery_modes, agents_and_artifacts,
  testing_policy, git_policy, documentation_policy, etc.)
- `doc/epics/templates/*.md`
- `doc/tasks/templates/*.md`
- `doc/project/**/*.md`

Estos archivos sirven para operar el framework, coordinar, registrar decisiones y
cerrar documentación.

## Inglés técnico

Usar inglés técnico en:

- `doc/framework/odoo_development_rules.md`

Son las reglas que se consumen al implementar y revisar código Odoo.

## Tasks y docs del proyecto

El idioma de las task cards y docs del proyecto se fija en el bootstrap y queda
registrado en `doc/framework/project_config.md`.

Default para odoo-me:

- task cards y epic cards: español rioplatense;
- execution reports: español rioplatense;
- user-visible Odoo strings: inglés + i18n `es_AR` (política por módulo).

## Por qué no todo en español

El inglés técnico suele ser más corto y preciso para instrucciones sobre código:

- `computed fields`
- `constraints`
- `record rules`
- `onchange`
- `server actions`
- `ACL`
- `migrations`

Traducir todo puede aumentar tokens y ambigüedad sin mejorar la implementación.
Los términos técnicos Odoo/Python pueden quedar en inglés aunque el texto esté en
español (`recordset`, `domain`, `cron`, `model`, `environment`, etc.).
