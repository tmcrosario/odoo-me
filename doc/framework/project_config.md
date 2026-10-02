# Project config

Configuración persistente del proyecto odoo-me.

## Identidad del proyecto

- Nombre del proyecto: odoo-me
- Dominio funcional: Mesa de entradas (gestión de expedientes) + RAA
- Módulos Odoo principales: `me`, `raa`
- Versión Odoo: 19
- Layout repositorio: dos addons custom dentro de carpeta de addons compartida
- Idioma de documentación interna: español rioplatense
- Idioma visible al usuario final: inglés + i18n `es_AR`

## Módulos Odoo

- Módulo custom principal: `me` (mesa de entradas)
- Módulos custom adicionales: `raa`
- Cantidad total de módulos custom: 2
- Layout `doc/project/`: **por módulo** (`doc/project/me/`, `doc/project/raa/`)
- Dependencias (de los manifests): `me` → `tmc`, `tmc_data`; `raa` → `tmc`, `me`. `tmc` (repo
  `odoo-tmc`) → `web_tree_many2one_clickable` y `remove_odoo_enterprise` (OCA); `tmc_data` (repo
  `odoo-tmc-data`) → `tmc` y `auditlog` (OCA `server-tools`). `me` crea registros de `raa` sin
  declararlo (ciclo): ver `doc/project/me/models.md`.
- Integraciones externas: ninguna confirmada por ahora
- Estado: base en Odoo 19; `me` con documentación rica previa, `raa` mínimo (stub)

## Operación

- Entorno único: VS Code + Claude (operador único; sin OpenCode ni Cursor)
- Fases como compuertas de disciplina (ver `doc/framework/tooling_layers.md`)
- Los agentes pueden modificar código Odoo: no por defecto; solo en paso de
  implementación con instrucción explícita y acceptance criteria claros
- Los agentes pueden correr Docker / tests: con permiso explícito o task de validación

## Tests

- Suite real de tests: `me` relevada (ver `tests_plan.md`); `raa` **sin suite** (no tiene `tests/`)
- Ubicación de planes de test: `doc/project/me/tests_plan.md` (`raa` no tiene plan: sin suite)
- Comando de tests: **no se duplica acá**. El canónico y sus trampas viven en
  [`doc/project/me/tests_plan.md`](../project/me/tests_plan.md) → sección "Comando canónico".
  Lo que no se negocia: DB de test **dedicada y no servida** (`me_test`), `--addons-path`
  explícito **y completo** (las 9 rutas, incluidas las 5 de OCA) y verificar la línea de
  resultado `... of N tests` con **N > 0**. Sin eso el runner recolecta **0 tests** (verde falso).
- Docker disponible: sí
- CI: `.github/workflows/pipeline.yml` (build y push de la imagen Docker, escaneo Snyk y deploy);
  dispara solo en push a la rama `14.0` y **no corre la suite de tests**. Para `develop` y `19.0` no
  corre nada.
- Política default de tests: user-run (default)
- Evidencia suficiente: salida pegada / link CI / log resumido / captura

## Git y entrega

- Rama de integración: `develop`
- Estilo de commit: `[TYPE] resumen imperativo breve` (mensaje = solo título;
  comentario descriptivo aparte para GitHub). Sin atribución AI.
- Naming de branches: `<tipo>/EPIC-XXX-TASK-YYY-slug` (en la práctica se trabaja directo sobre `develop`)
- El agente puede commitear bajo pedido explícito: sí
- El agente puede pushear bajo pedido explícito: no autorizado por default
- Workflow de PR: `develop -> 19.0`. **Los PR los gestiona el usuario**; el framework
  no abre ni mergea PRs.
- Checks / hooks obligatorios: ninguno (no hay hooks ni `.pre-commit-config`; el único check automático es
  el CI de arriba)

## Reglas de riesgo

Áreas sensibles por default (escalan a L/XL automáticamente):

- modelos y campos persistentes;
- security, ACL, grupos y record rules;
- workflow, estados y trazabilidad;
- datos XML/CSV, migraciones y datos existentes;
- evidencia de auditoría / compliance;
- integraciones externas;
- reglas de negocio ambiguas.

Áreas sensibles específicas del proyecto:

- modelos de expediente, numeración/secuencias, estados del trámite, jurisdicción
  (DEM/CM), permisos y record rules de mesa de entradas, datos XML/CSV.

## Épicas

Al bootstrap solo existía EPIC-001 (reverse-engineering + baseline de `me`). El listado vigente está
en [`doc/epics/_index.md`](../epics/_index.md).

## Estado de inicialización

- Estado: bootstrap del framework completo (`doc/tasks/SETUP-001_bootstrap_framework.md`, Done)
- Inicializado por: VS Code + Claude
- Fecha: 2026-06-05
- Configuración pendiente: tests de CI para `develop`/`19.0` y baseline de `raa` (hoy solo
  `architecture.md`, sin suite de tests).
