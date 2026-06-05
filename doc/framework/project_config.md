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
- Dependencias Odoo: pendiente de relevar
- Dependencias custom: pendiente de relevar (stack TMC compartido)
- Integraciones externas: ninguna confirmada por ahora
- Estado: base en Odoo 19; `me` con documentación rica previa, `raa` mínimo (stub)

## Operación

- Entorno único: VS Code + Claude (operador único; sin OpenCode ni Cursor)
- Fases como compuertas de disciplina (ver `doc/framework/tooling_layers.md`)
- Los agentes pueden modificar código Odoo: no por defecto; solo en paso de
  implementación con instrucción explícita y acceptance criteria claros
- Los agentes pueden correr Docker / tests: con permiso explícito o task de validación

## Tests

- Suite real de tests: pendiente de confirmar por módulo
- Ubicación de planes de test: `doc/project/me/tests_plan.md`, `doc/project/raa/tests_plan.md`
- Comando de tests por módulo (desde la raíz del stack `odoo-docker-stack/`):
  - `me`: `docker compose -f develop.yml run --rm odoo odoo -d <TEST_DB> -u me --test-tags /me --stop-after-init --log-level=test`
  - `raa`: `docker compose -f develop.yml run --rm odoo odoo -d <TEST_DB> -u raa --test-tags /raa --stop-after-init --log-level=test`
- Docker disponible: sí
- CI disponible: pendiente
- Política default de tests: user-run (default)
- Evidencia suficiente: salida pegada / link CI / log resumido / captura

## Git y entrega

- Rama de integración: `develop`
- Estilo de commit: `[TYPE] resumen imperativo breve` (mensaje = solo título;
  comentario descriptivo aparte para GitHub). Sin atribución AI.
- Naming de branches: `<tipo>/EPIC-XXX-TASK-YYY-slug`
- El agente puede commitear bajo pedido explícito: sí
- El agente puede pushear bajo pedido explícito: no autorizado por default
- Workflow de PR: `develop -> 19.0`. **Los PR los gestiona el usuario**; el framework
  no abre ni mergea PRs.
- Checks / hooks obligatorios: pendiente / no confirmados

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

## Épicas iniciales

- EPIC-001 — Reverse-engineering + baseline de mesa de entradas (`me`)

## Estado de inicialización

- Estado: parcial (bootstrap del framework en curso — `doc/tasks/SETUP-001_bootstrap_framework.md`)
- Inicializado por: VS Code + Claude
- Fecha: 2026-06-05
- Configuración pendiente: confirmar suites de test por módulo, dependencias,
  CI, hooks/checks obligatorios; baseline de `raa`.
