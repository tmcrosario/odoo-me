# EPIC-007 / TASK-003 — Formato Odoo 19 de las traducciones `es_AR` de `me` y `raa`

Estado: Done
Modo: S
Riesgo: bajo (solo archivos `.po`; sin lógica)
Módulo: `me` / `raa`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done, retroactiva)
- Fecha de toma: 2026-09-17
- Notas de coordinación: la sesión de `odoo-junco` no pudo activar `es_AR` en me2/junco_demo.
  Commits `37d9175`, `ea94551`, `bf32327`.

## Objetivo

Que `es_AR` cargue y que los mensajes de error de `me` y `raa` salgan en español.

## Alcance

Incluye:

- `me/i18n/es_AR.po`: una entrada sin `#. module: me` hacía fallar `--load-language=es_AR`
  (`AttributeError ... 'groups'`, `translate.py`) y revertía la carga completa;
- `#. odoo-python` en las 31 entradas de código Python (20 de `me`, 11 de `raa`); sin esa marca
  Odoo 19 las ignora en silencio;
- typo "expecificaron" → "especificaron" en `raa`;
- documentar el formato en el framework (`odoo_development_rules.md` → *Translations (i18n)*).

No incluye: los 56 mensajes Python sin marcar de `junco` (repo de junco).

## Acceptance criteria

- [x] `--load-language=es_AR` termina sin error y deja el idioma activo.
- [x] Odoo sirve las 31 traducciones Python (20/20 y 11/11).
- [x] Ningún `msgstr` con placeholders distintos de su `msgid`.
- [x] Suite `/me` verde con evidencia.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `doc/project/me/tests_plan.md` + `odoo shell` (`code_translations`)
- Fecha: 2026-09-17
- Resultado: **0 failed, 0 error(s) of 258 tests**. Mensajes reales verificados en `es_AR`,
  incluido uno con `%(intake)s`.

## Estado / próximo paso

**Done.** Push: usuario. Al cargar `es_AR` en una DB hay que reiniciar Odoo (las traducciones de
código se cachean por proceso). Activar `es_AR` en producción sigue pendiente (usuario).

## Resultado / cierre

Cerrada el 2026-09-17 sobre `develop`. Formato documentado; los chequeos quedan en el framework.
