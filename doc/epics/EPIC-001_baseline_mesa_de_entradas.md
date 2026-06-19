# EPIC-001 — Reverse-engineering + baseline de mesa de entradas

Estado: Draft
Riesgo global: medio
Módulo: `me`
Owner: sin asignar

## Objetivo

Fijar el AS-IS **verificado** del módulo `me`: reconciliar la documentación
consolidada (`doc/project/me/*`) contra el código real, cerrar los aspectos
inciertos y las inconsistencias detectadas en el análisis, y completar los stubs de
seguridad y tests. El resultado es un baseline confiable sobre el cual construir.

## Contexto

`me` viene de una base Odoo 14 migrada a 19, con ~30 task entregadas (#001–#030,
#032 en `doc/project/me/_legacy_backlog.md`). La documentación se consolidó durante
el bootstrap del framework (ver `doc/tasks/SETUP-001_bootstrap_framework.md`), pero:

- `architecture.md` es un snapshot del 2026-03-26 **parcialmente histórico**;
  `workflows.md` lo supera en varios puntos.
- El análisis original dejó **inconsistencias doc↔código** (§7) y **aspectos
  inciertos** (§8) sin cerrar.
- `security.md` y `tests_plan.md` son **stubs**.
- El `_legacy_backlog.md` está desfasado respecto del código (p.ej. #031 figura
  `[IDEA]` pero ya está commiteado).

Antes de cualquier cambio funcional conviene fijar el baseline documental verificado.

## Alcance

Incluye:

- verificación del inventario técnico-funcional contra el código real;
- cierre de inconsistencias (§7) y aspectos inciertos (§8) del análisis;
- baseline de seguridad (ACL, grupos, record rules reales);
- baseline de tests (qué existe, cobertura, gaps);
- investigación del filtrado de jurisdicciones del DEM (#033).

No incluye:

- nuevas capacidades funcionales;
- la integración ME↔JUNCO (ver EPIC-002);
- refactors o cambios de comportamiento (salvo que una task lo defina con criterios).

## Módulos afectados

- Módulo principal: `me`
- Módulos secundarios afectados: lectura de contexto de `tmc` (base) y `raa`
  (acoplamiento implícito); sin modificarlos.
- Dependencias entre módulos: `me` extiende `tmc.document`; instancia `raa.registry_aa`.

## Reglas / decisiones durables

- No inventar reglas de negocio: lo no cerrado queda como pregunta/riesgo/`N/A`.
- El código es la fuente de verdad; la doc consolidada se corrige contra él.
- Donde `architecture.md` y `workflows.md` discrepen, `workflows.md` es más reciente.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Inventario técnico-funcional verificado | sin asignar | L | `me` | Draft |
| TASK-002 | Baseline de seguridad (ACL/grupos/record rules) | sin asignar | M | `me` | Draft |
| TASK-003 | Baseline de tests (inventario y gaps) | sin asignar | M | `me` | Done |
| TASK-004 | Investigación: filtrado de jurisdicciones del DEM (#033) | sin asignar | M | `me` | Done |

## Preguntas abiertas

- ¿Cuáles de los aspectos §8 (estados, append-only, jurisdiction vs dependence,
  comportamiento sin "Mesa de Entradas", etc.) son decisiones pendientes y cuáles
  ya quedaron resueltos en #021–#032?
- ¿El bypass SQL de fecha (`_update_document_date`) es regla de negocio intencional
  o deuda técnica a remediar?
- ¿Declarar `raa` como dependencia formal en `me/__manifest__.py`?

## Cierre de épica

Pendiente.
