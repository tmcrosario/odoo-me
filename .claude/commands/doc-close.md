---
description: Cierra documentación de una task (marca Done) cuando hay evidencia suficiente
argument-hint: [EPIC-XXX/TASK-YYY]
---

Cerrá la documentación de una task cuando hay evidencia suficiente. Esta es la única ruta válida para marcar `Done`.

Referencia: $ARGUMENTS

## Requisitos

- Acceptance criteria OK o N/A justificado.
- Tests OK, pendiente explícito o N/A justificado.
- Verifier OK si el modo lo exige.
- Docs canónicas actualizadas, diferidas o N/A: `doc/project/business_rules.md`, `models.md`, `architecture.md`, `security.md`, `tests_plan.md`.
- Índices actualizados: `doc/epics/_index.md`, epic card, `doc/tasks/_index.md` y `doc/tasks/EPIC-XXX/_index.md` cuando corresponda.
- Bloque **Estado / próximo paso** de la task card actualizado a cierre.

## Reglas

- No modificar código Odoo durante el cierre documental.
- El cierre documental es un paso separado del commit.
