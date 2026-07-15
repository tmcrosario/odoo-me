# CLAUDE.md — odoo-me

> Claude Code no carga `AGENTS.md` solo. Este es el punto de entrada.
> **Antes de tocar nada, leé `AGENTS.md`** (doctrina del framework).

## Qué es odoo-me

Repo de dos módulos custom Odoo 19:

- **`me`** — mesa de entradas (módulo principal).
- **`raa`** — registro/área asociada (módulo secundario).

No tocar código de `me/` ni `raa/` salvo en un paso explícito de implementación con
acceptance criteria claros.

## Cómo se trabaja acá

Único entorno: **VS Code + Claude**. No hay OpenCode ni Cursor. Vos recorrés el
flujo completo —preparar, implementar, verificar y cerrar— en una sola sesión. Las
fases del framework valen como **compuertas de disciplina**, no como límites entre
herramientas. Si encontrás referencias a comandos OpenCode (`/setup-project`,
`/code-*-prompt`, etc.), no existen acá.

## La memoria vive en el repo, no en el chat

Entre sesiones no sobrevive contexto salvo lo que esté escrito:

- **Estado de trabajo** → `doc/tasks/EPIC-XXX/TASK-YYY_*.md` + `doc/tasks/_index.md`.
  Toda task lleva un bloque **Estado / próximo paso** actualizado. Al retomar, leé
  la task card antes de re-derivar nada.
- **Verdad del proyecto** → `doc/project/me/*` y `doc/project/raa/*` (architecture,
  models, business_rules, security, tests_plan). Actualizalos cuando un cambio sea
  durable.
- **Ideas sueltas / brainstorming** → `doc/project/me/brainstorming.md` (documento vivo,
  **no canónico**: ideas, dudas y posibles tareas). No reemplaza épicas/specs/task cards;
  cuando una idea se cierra, se mueve a épica/task y queda acá solo como referencia.

## Leé según la tarea

- `AGENTS.md` — principios, escalamiento, prohibiciones (siempre).
- `doc/framework/odoo_development_rules.md` — reglas Odoo 19+ (toda edición de código).
- `doc/framework/delivery_modes.md` — modos XS/S/M/L/XL.
- `doc/skills/*` — feature, bugfix, code review, close gate, architecture analysis.
- `doc/project/<modulo>/*` — arquitectura, modelos, reglas y seguridad del módulo.

## Reglas que no se negocian

- **No inventes reglas de negocio.** Lo no especificado queda como pregunta abierta,
  riesgo o `N/A` justificado.
- **Escalá a L/XL y revisá críticamente** si tocás: modelos/campos persistentes,
  security/ACL/record rules, workflow/estados, datos XML/CSV, migraciones,
  integraciones externas o reglas de negocio ambiguas.
- **Criterios antes de código**: sin acceptance criteria claros, no implementás.
- **Odoo 19+ en vistas**: `<list>` (no `<tree>`); nada de `attrs`, `states` ni
  `statusbar_colors`; usá `invisible`/`readonly`/`required` con expresiones.
- **Seguridad**: todo modelo persistente nuevo requiere entrada en
  `security/ir.model.access.csv` o `N/A` con motivo. UI readonly/invisible no
  reemplaza ACL ni validación backend.
- **Tests con evidencia**: nunca declares tests `OK` sin salida. Default
  `PENDIENTE USER-RUN`.
- **Git**: no commitees ni pushees sin pedido explícito. Un commit no es `Done`; el
  cierre documental es un paso aparte.

## Comandos

El stack Docker vive en la raíz `odoo-docker-stack/` (no usa archivo `.conf`: pasa
flags directos en `develop.yml`). El servicio Odoo se llama `odoo`.

Tests: **el comando canónico y sus trampas están en
[`doc/project/me/tests_plan.md`](doc/project/me/tests_plan.md)** — leelo antes de correr la suite.
Resumen de lo que NO se negocia:

- **DB de test dedicada y NO servida** (`me_test`). Sobre una DB que la instancia ya sirve
  (me1/me2) el runner recolecta **0 tests** → **verde falso**.
- **`--addons-path` siempre explícito.** Sin él corre **0 tests en silencio**.
- Verificar la **línea de resultado** (`... of N tests`) con **N > 0** y `0 failed, 0 error(s)`.
  `0 tests of 0` **no es evidencia**.

```bash
# Mesa de entradas (desde la raíz del stack) — ver tests_plan.md para el comando completo
docker compose -f develop.yml exec -T odoo odoo -d me_test -u me \
  --addons-path=/mnt/extra-addons/odoo-tmc,/mnt/extra-addons/odoo-tmc-data,/mnt/extra-addons/odoo-me,/mnt/extra-addons/odoo-junco \
  --db_host=db --db_user=odoo --db_password=odoo --test-tags /me --stop-after-init \
  --http-port=8169 --gevent-port=8173 --max-cron-threads=0 --log-level=test
```

Después de un `-u` sobre la DB donde prueba el usuario (`me2`), **reiniciar odoo**
(`docker compose -f develop.yml restart odoo`) o los cambios de vista no se ven.

- Commit: `[TYPE] resumen imperativo breve` (`[ADD]`/`[IMP]`/`[FIX]`/`[REF]`/
  `[REM]`/`[MIG]`/`[DOC]`/`[TEST]`/`[CHORE]`). Sin atribución AI. El mensaje de
  commit es solo el título; el comentario descriptivo va aparte (para pegar en
  GitHub).
- Branches: `<tipo>/EPIC-XXX-TASK-YYY-slug`. Rama de integración: `develop`.
- PR: `develop -> 19.0`. **Los PR los gestiona el usuario**; el framework no abre ni
  mergea PRs.

## Idioma

Metodología y task cards en español rioplatense; reglas de código en inglés técnico.
Detalle en `doc/framework/language_policy.md`.
