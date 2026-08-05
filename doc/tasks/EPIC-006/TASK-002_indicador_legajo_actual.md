# EPIC-006 / TASK-002 — Indicador "En Legajo Nº X" + filtro "Adjuntos a Legajo"

Estado: Done
Modo: S
Riesgo: bajo (computed no-stored + label de vista + filtro de búsqueda)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-08-05
- Notas: viene de IDEA 5 (`brainstorming.md`). Precursor: el `[FIX] no perder legajo_number`
  (`1547b8a`) — sin él el número no se cargaba bien.

## Objetivo

Que un expediente adjunto a un legajo **muestre visiblemente "En Legajo Nº XXXX"** en el form
(sin habilitar columnas), y que la lista pueda **filtrarse por "Adjuntos a Legajo"** (antes solo
se podía agrupar por ese criterio, no filtrar).

## Alcance

- Campo computed `current_legajo_number` (Char, **no-stored**, solo display), calcado del patrón
  "último movimiento" (`current_location_dependence_id`): toma el `legajo_number` del **último**
  movimiento **si su destino es Legajo (LEG)**; vacío si no. **Estado actual** → resuelve solo
  los casos "varios legajos" (muestra el del último pase) y "se movió después" (deja de mostrar).
- **Vista (form):** label bajo el nombre del expediente, visible solo con `current_legajo_number`.
  Texto **en inglés en el arch** ("In Legajo No.") + traducción `es_AR` ("En Legajo Nº") en
  `me/i18n/es_AR.po` (política de idioma).
- **Vista (search):** filtro `Attached to Legajo` (`domain=[('current_location_dependence_id.
  abbreviation','=','LEG')]`) + traducción `es_AR` ("Adjuntos a Legajo").

No incluye: columna de legajo en la lista (se decidió solo label en el form); hacer
`current_legajo_number` stored (no hace falta: el filtro usa `current_location_dependence_id`,
que ya es stored).

## Decisiones (usuario, 2026-08-05)

- **Cuándo:** estado actual (último movimiento), no histórico.
- **Dónde:** label en el form, bajo el nombre (se probó arriba a la derecha y se volvió atrás).
- **Idioma:** inglés en el arch + i18n `es_AR` (me2 corre en_US → se ve en inglés; prod es_AR → español).

## Acceptance criteria

- [x] Expediente en legajo → muestra "In Legajo No. XXXX" (es_AR: "En Legajo Nº") en el form.
- [x] Si tras Legajo se mueve a otro lado → el label desaparece (estado actual).
- [x] Varios pases a Legajo → muestra el del último.
- [x] Filtro "Attached to Legajo" en la lista deja solo los que están actualmente en legajo.
- [x] Strings en inglés en el arch + traducción `es_AR` en el `.po`.
- [x] Suite `/me` verde + UI verificada en me2.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md` (`-u me`, path OCA completo, `--test-tags /me`, `me_test`).
- Fecha: 2026-08-05
- Resultado: **0 failed, 0 error(s) of 246 tests** (stats 300). 5 tests nuevos en
  `TestLegajoDependence026`: `current_legajo_number` (en legajo → nro; se mueve → vacío; varios →
  último; sin legajo → vacío) + el domain del filtro. Aplicado a me2 + restart. UI verificada.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido (+ recordar activar `es_AR` para el texto español).

## Resultado / cierre

Cerrada (Done) el 2026-08-05 sobre `develop`. Indicador "En Legajo Nº X" (computed del último
movimiento, no-stored) + filtro "Adjuntos a Legajo" en la lista, ambos con string inglés + i18n.
IDEA 5 (`brainstorming.md`) marcada implementada.
