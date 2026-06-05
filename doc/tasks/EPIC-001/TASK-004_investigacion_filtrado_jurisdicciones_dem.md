# EPIC-001 / TASK-004 — Investigación: filtrado de jurisdicciones del DEM (#033)

Estado: Draft
Modo: M
Riesgo: medio (puede derivar en fix de datos o de lógica)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: N/A

## Objetivo

Determinar por qué, al cargar un expediente del DEM, el campo `jurisdiction_dependence`
no muestra todas las secretarías esperadas del nomenclador, y clasificar la causa:
bug de código, dato faltante o comportamiento intencional no documentado.

## Contexto mínimo

Semilla: #033 (`doc/project/me/_legacy_backlog.md`). El dominio de opciones lo calcula
`_compute_allowed_jurisdictions` (`me/models/document_exp.py`, ~línea 270) buscando
hijos directos de `tmc_data.tmc_dependence_adm` en `tmc.dependence_order`. Si una
secretaría no tiene entrada con `parent_id = adm`, no aparece.

## Alcance

Incluye:

- confirmar qué secretarías debería ver el operador (nomenclador oficial);
- comparar contra lo que retorna `_compute_allowed_jurisdictions` (query directa);
- diagnosticar causa (hipótesis A datos / B referencia adm / C jerarquía no plana /
  D inconsistencia `tmc.dependence` vs `tmc.dependence_order`);
- determinar si el fix es de datos (`tmc_data`) o de lógica (`me/models`).

No incluye:

- aplicar el fix (esta task es de diagnóstico; el fix se abre como task aparte con
  criterios, posiblemente en `tmc_data` fuera de `me`).

## Acceptance criteria

- [ ] Diferencia entre jurisdicciones esperadas y mostradas, documentada con evidencia
  (resultado de la query).
- [ ] Causa clasificada (A/B/C/D) con referencia a código/datos.
- [ ] Recomendación de fix: dato vs lógica vs "intencional → documentar", con alcance
  estimado.

## Plan técnico preliminar

Query de diagnóstico sobre `tmc_dependence` / `tmc_dependence_order`; lectura de
`_compute_allowed_jurisdictions` y de `tmc_data`. Punto de partida de test:
`TestJurisdictionConditional012`.

## Riesgos

- El fix puede caer en `tmc_data` (repo/dominio distinto de `me`): coordinar alcance.
- No tocar lógica de jurisdicción sin confirmar la causa (área sensible: afecta carga
  de expedientes).

## Tests evidenciados

- Estado: N/A + motivo — task de diagnóstico; no modifica código. La query de
  diagnóstico y su salida se registran en el resultado, no como suite de tests.

## Estado / próximo paso

Draft, sembrada en el bootstrap (desde #033). Próximo paso: `/prepare-task`.

## Resultado / cierre

Pendiente.
