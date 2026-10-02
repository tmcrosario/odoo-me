# EPIC-006 — Usabilidad del formulario de expedientes

Estado: En progreso (sobre develop) — TASK-001 y TASK-002 Done
Riesgo global: bajo (UX/cosmético; sin campos persistentes, ACL ni JS propio. TASK-002 suma un computed **no-stored** al modelo)
Módulo: `me`
Owner: sin asignar

## Objetivo

Agrupar mejoras de **usabilidad del formulario** de `me.document_exp` (a diferencia de
EPIC-003, que fue usabilidad de la **vista lista**: filtros/group-by). Cambios chicos,
mayormente cosméticos, que hacen más obvias las acciones para el usuario operativo.

## Contexto

Primera task viene de un patrón portado de `odoo-junco` (`junco:EPIC-008/TASK-004`): un
botón "Save" textual en el header, visible solo cuando el registro está dirty, para
usuarios operativos a los que la nube/check del breadcrumb de Odoo 19 les cuesta encontrar.
La idea se registró antes en `brainstorming.md` (IDEA 3) y acá se formaliza y cierra.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Botón "Save" textual visible solo en dirty (form de expediente) | Ale Gallo | S | `me` | Done |
| TASK-002 | Indicador "En Legajo Nº X" en el form + filtro "Adjuntos a Legajo" | Ale Gallo | S | `me` | Done |

## Reglas / decisiones durables

- **Primer asset de frontend de `me`.** La adopción introdujo `me/static/src/scss/` y la
  sección `assets` (`web.assets_backend`) en el manifest — antes inexistentes. Los siguientes
  assets backend de `me` cuelgan de acá.
- **Patrón portado, no compartido.** El repo dueño del patrón es `odoo-junco`; en `me` se
  reimplementa con clase propia (`o_me_form_save_button`) para no acoplar assets entre repos.
- **Zero-JS.** La visibilidad depende solo de la clase `o_form_dirty` que el renderer de Odoo
  ya pone; nada de overrides de JS ni del ORM.

## Preguntas abiertas

- ¿Esparcir el botón a otros forms (movimiento, `raa`)? Hoy solo `document_exp`. Se evalúa
  caso por caso con el usuario antes de abrir nuevas tasks (ver IDEA 3 en `brainstorming.md`).

## Cierre de épica

Abierta. TASK-001 (2026-07-27, suite 209/0/0) y TASK-002 (2026-08-05, suite 246/0/0) Done sobre
`develop`, con UI verificada en me2. Deploy a prod: diferido (usuario). La épica queda abierta por
si se suman mejoras de form.
