# EPIC-001 / TASK-004 — Investigación: filtrado de jurisdicciones del DEM (#033)

Estado: Done (diagnóstico)
Modo: M
Riesgo: bajo (fue read-only; el fix queda fuera, en `tmc_data`)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
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

- [x] Diferencia entre jurisdicciones esperadas y mostradas, documentada con evidencia
  (resultado de la query) — ver Resultado.
- [x] Causa clasificada (A/B/C/D) con referencia a código/datos — A (datos faltantes) + D
  (intencional, multi-año).
- [x] Recomendación de fix: dato vs lógica vs "intencional → documentar" — documentar la
  regla multi-año (hecho en `business_rules.md`) + cargar nomenclador 2025 en `tmc_data`.

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

**Done.** Diagnóstico completo; no requiere cambios en `me`. El único accionable (cargar
nomenclador 2025) vive en `tmc_data` (repo externo, gestionado aparte) y quedó anotado en
`business_rules.md` → "Limitaciones conocidas".

## Resultado / cierre

Cerrada (Done, diagnóstico) el 2026-06-19.

**Estructura del nomenclador (entendida, read-only sobre seed `tmc_data` + queries me2):**
- `tmc.dependence` = catálogo maestro de nombres (acumulativo entre años/versiones).
- `tmc.dependence_order` = árbol jerárquico con `code` `X.YY.ZZ` (`1.00.00` raíz =
  `tmc_dependence_adm` "ADMINISTRACIÓN CENTRAL"; `1.YY.00` = jurisdicciones/secretarías,
  hijas de adm; `1.YY.ZZ` = sub-dependencias/source) y `institutional_classifier_ids` = años.
- `_compute_allowed_jurisdictions` = hijos de `adm`, **sin filtrar por año** (intencional).

**Evidencia (me2):** muestra 21 jurisdicciones (árbol 2020). Faltan 6 secretarías 2025 en
MAYÚSCULAS (Género y DDHH, Modernización y Cercanía, Desarrollo Humano y Hábitat, Desarrollo
Económico y Empleo, Movilidad, Deporte y Turismo): existen en el catálogo pero `en_order=0`
o cuelgan de otro padre. Además ~20 duplicados case-variant (Tipo-Oración), sueltos de adm.

**Causa:** A (datos faltantes — está cargado el nomenclador 2020, falta el 2025) + D
(comportamiento intencional — el no-filtrar-por-año es a propósito, para soportar documentos
generados en estructuras anteriores con secretarías que ya no existen). **No es bug de `me`**;
el compute es correcto. La ref a `adm` es correcta (descarta B).

**Recomendación:** (1) documentar la regla multi-año → **hecho** en `business_rules.md`.
(2) Cargar el nomenclador **2025 de forma aditiva** (sin quitar el 2020) en **`odoo-tmc-data`**
(repo externo, no se toca desde este flujo) → anotado en `business_rules.md` "Limitaciones
conocidas". (3) Higiene de datos: deduplicar los registros case-variant al cargar el 2025.
