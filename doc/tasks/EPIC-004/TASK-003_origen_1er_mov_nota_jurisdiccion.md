# EPIC-004 / TASK-003 — 1er movimiento de una Nota: origen = jurisdicción

Estado: Done
Modo: S
Riesgo: bajo (cambio acotado en el bloque de movimientos automáticos; sin campos nuevos)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-07-30
- Notas: viene de IDEA 4 (`brainstorming.md`), habilitada por EPIC-004/TASK-002.

## Objetivo

Que el **1er movimiento automático** de un expediente **DEM con tema Nota** salga de la
**jurisdicción real** (la secretaría de origen) en vez del genérico `dependence_id`
("Departamento Ejecutivo"). Antes de EPIC-004 el origen era la jurisdicción para todos;
EPIC-004 lo pasó a `dependence_id` para que exista aunque la jurisdicción esté vacía
(compras). En Notas la jurisdicción **siempre está** (obligatoria al ingreso), así que se
recupera el origen preciso, acotado a Notas.

## Alcance

- En `create()` (bloque de movimientos automáticos): si `is_nota and jurisdiction_dependence`,
  el origen del 1er movimiento (→ TMC) es la jurisdicción; si no, `dependence_id` (defensivo).
- Compras / no-Notas: **sin cambios** (siguen con `dependence_id`).

No incluye: migrar dato viejo (el origen es un snapshot al crear; los expedientes previos no
cambian — en prod los nuevos ya salen consistentes).

## Reglas conocidas (verificadas en dato real, 2026-07-29)

- El origen del 1er movimiento es un **snapshot al crear**; no sigue cambios posteriores de la
  jurisdicción. En me2 hubo corte temporal: pre-EPIC-004 (hasta 06-11) origen = jurisdicción;
  desde EPIC-004 (06-17+) origen = `dependence_id`.
- **Seguro para Notas:** el desfase jurisdicción≠origen que se veía (ej. EXP-039310) es un
  fenómeno de **compras + JUNCO** (JUNCO setea la jurisdicción DESPUÉS del alta, sin tocar el
  movimiento). Las Notas cargan la jurisdicción al ingreso y **JUNCO nunca las toca** → el
  snapshot queda consistente. **JUNCO no escribe movimientos de ME** (verificado por grep).
- Ningún `@api.constrains` del movimiento restringe el origen; nada computa sobre
  `origin.is_internal` (el rastreo interno mira el destino) → sin efecto colateral.

## Acceptance criteria

- [x] DEM + Nota: 1er movimiento sale de la **jurisdicción** (→ TMC).
- [x] DEM + compras / sin tema: 1er movimiento sigue saliendo de `dependence_id`.
- [x] Defensivo: Nota sin jurisdicción (no debería) cae a `dependence_id`.
- [x] Suite `/me` verde + UI verificada en me2.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md` (`-u me`, path OCA completo, `--test-tags /me`, `me_test`).
- Fecha: 2026-07-30
- Resultado: **0 failed, 0 error(s) of 236 tests** (stats 288). Tests:
  `test_nota_first_movement_origin_is_jurisdiction`,
  `test_purchase_first_movement_origin_is_dependence`. Aplicado a me2 + restart. UI verificada.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido.

## Resultado / cierre

Cerrada (Done) el 2026-07-30 sobre `develop`. El 1er movimiento de una Nota refleja la
secretaría real de origen; compras intactas. IDEA 4 (`brainstorming.md`) marcada implementada.
