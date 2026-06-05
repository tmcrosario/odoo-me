# Framework overview

Odoo Agentic Delivery Framework (OADF) es una metodología liviana para coordinar
trabajo con IA en proyectos Odoo. En odoo-me se opera con un único entorno:
**VS Code + Claude**. Un solo operador recorre todas las fases en la misma sesión;
las fases valen como **compuertas de disciplina**, no como límites entre
herramientas (ver `doc/framework/tooling_layers.md`).

Busca equilibrar:

- velocidad de cambios pequeños;
- seguridad en cambios sensibles;
- trazabilidad útil;
- bajo contexto;
- handoff claro entre análisis, implementación y verificación.

## Capas documentales

1. **Framework**: reglas metodológicas, comandos y templates (`doc/framework/`,
   `.claude/commands/`, `doc/tasks/templates/`, `doc/epics/templates/`).
2. **Proyecto**: arquitectura, reglas de negocio, modelos, seguridad y plan de
   tests, por módulo (`doc/project/me/`, `doc/project/raa/`).
3. **Tareas**: unidades de trabajo con intensidad proporcional al riesgo
   (`doc/epics/`, `doc/tasks/EPIC-XXX/`).

Ver también `doc/framework/agents_and_artifacts.md` para saber qué vive dónde.

## Resultado esperado

Antes del primer cambio, el proyecto debería quedar inicializado en
`doc/framework/project_config.md` (bootstrap del framework).

Cada cambio debe dejar evidencia mínima de:

- objetivo;
- alcance;
- criterios de aceptación;
- validación;
- estado final.

El commit es guiado por `git_policy.md` y `/commit-ready`, pero no reemplaza
validación ni cierre documental.

La cantidad de detalle depende del modo de entrega.
