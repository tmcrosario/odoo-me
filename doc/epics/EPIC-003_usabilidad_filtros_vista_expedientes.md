# EPIC-003 — Usabilidad y filtros de la vista de expedientes

Estado: Done (sobre develop; deploy a prod diferido)
Riesgo global: medio (una task toca un campo persistente nuevo)
Módulo: `me`
Owner: sin asignar

## Objetivo

Mejorar la usabilidad de la list/search view de expedientes (`me.document_exp`)
agregando filtros operativos. Primer lote: filtrar por **usuario poseedor** y por
**oficina (ubicación actual)** del expediente.

## Contexto

Pedido del usuario: poder ver qué expedientes tiene cada usuario y, sobre todo, qué
oficina los tiene actualmente, dado que una oficina interna de TMC puede tener más de
un usuario. Hoy la search view (`document_exp_view_search`) solo ofrece el filtro
"In My Possession" (poseedor = uid propio) y la searchpanel por `dependence_id`
(Origen). No hay forma de filtrar por poseedor arbitrario ni por ubicación actual.

Modelo relevante (AS-IS):

- `current_holder_id` — Many2one a `res.users`, **stored computed** = `user_id` del
  último movimiento. Es el poseedor actual.
- La **ubicación actual** = `destination_dependence_id` del último movimiento. **No
  existe** un campo stored equivalente a `current_holder_id` para la oficina; solo
  está el booleano `is_currently_internal`.

## Alcance

Incluye:

- filtro/group-by por usuario poseedor (`current_holder_id`);
- filtro por oficina = ubicación actual del expediente (requiere campo nuevo).

No incluye:

- filtro por historial de oficinas por las que pasó el expediente (solo ubicación
  actual);
- rediseño general de la vista ni otros filtros no pedidos.

## Módulos afectados

- Módulo principal: `me`
- Módulos secundarios afectados: N/A (consume `tmc.dependence`, sin cambios en `tmc`)
- Dependencias entre módulos: N/A

## Reglas / decisiones durables

- "Oficina" = ubicación actual (destino del último movimiento), no historial.
- Una "oficina de TMC" es un `tmc.dependence` interno (criterio `is_internal` a
  confirmar en TASK-002).
- Campo persistente nuevo → escala a L y exige contrato técnico antes de tocar código.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Filtro por usuario poseedor en la vista de lista | sin asignar | S | `me` | Done |
| TASK-002 | Filtro por oficina (ubicación actual) en la vista de lista | sin asignar | L | `me` | Done |

## Preguntas abiertas

Cerradas: UI = campo buscable + group-by (sin searchpanel); "oficina TMC" = `is_internal=True`;
el filtro lista solo internas (campo internal-only).

## Cierre de épica

Cerrada (Done) el 2026-06-19 sobre `develop`, con TASK-001 (filtro por poseedor) y
TASK-002 (filtro por oficina interna de destino) entregadas, suite `me` 201/0/0 y UI
verificada en me2. Deploy a producción diferido (usuario).
