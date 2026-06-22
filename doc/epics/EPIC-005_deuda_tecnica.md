# EPIC-005 — Deuda técnica (limpieza post-baseline)

Estado: Done (sobre develop)
Riesgo global: bajo/medio (uno toca el manifest = dependencia de módulo)
Módulo: `me`
Owner: sin asignar

## Objetivo

Agrupar follow-ups de **código** derivados del baseline de EPIC-001 (inventario): limpiezas
y decisiones técnicas chicas que no eran parte del relevamiento doc-only.

## Contexto

Salidos de la reconciliación §8 en EPIC-001/TASK-001 (2026-06-19). Son cambios de código
(no doc), por eso se sacan de EPIC-001 (que es baseline documental) a este epic.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Remover campo muerto `allowed_dependence_ids` | sin asignar | XS | `me` | Done |
| TASK-002 | Decidir/declarar dependencia `raa` en el manifest | sin asignar | S | `me` | Done |

## Detalle de los follow-ups

- **TASK-001 (8.6):** `allowed_dependence_ids` (Many2many computed `@api.depends()` vacío)
  no se referencia en ninguna vista ni código; la vista usa un domain hardcodeado
  `[('abbreviation','in',['DEM','TMC','CM'])]`. Es artefacto muerto → `[REM]`. Verificar
  que ningún XML/heredado lo use antes de remover.
- **TASK-002 (8.8):** `me/__manifest__.py` declara `["tmc", "tmc_data"]` pero **no `raa`**,
  y `create()` siempre crea `raa.registry_aa` (vía `sudo()`). El acoplamiento se dejó
  deliberado ("acoplamiento implícito" en el comentario). **Decisión requerida:** ¿declarar
  `raa` en `depends` (como se hizo con `tmc_data`) o mantener el acoplamiento blando? Toca
  dependencias de módulo → requiere aprobación explícita del usuario.

## Reglas / decisiones durables

- Cambios de dependencia (`depends`) requieren aprobación explícita (TASK-002).
- No remover `allowed_dependence_ids` sin confirmar que no hay referencias (TASK-001).

## Preguntas abiertas

Ninguna. (TASK-002 resuelta: `raa` no se declara — sería circular; acoplamiento implícito
documentado.)

## Cierre de épica

Cerrada (Done) el 2026-06-22 sobre `develop`. TASK-001 (`[REM]` campo muerto
`allowed_dependence_ids`, suite 201/0/0) y TASK-002 (decisión `raa`: no declarable por ciclo
`raa→me`, documentado en `models.md`). Deploy a prod: N/A.
