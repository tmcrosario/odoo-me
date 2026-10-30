# EPIC-007 / TASK-010 — Secretaría de Vocalía y Contadores Fiscales como dependencias internas

Estado: En progreso (implementado; falta el commit)
Modo: L
Riesgo: medio (datos XML + script de migración; cambia qué expedientes figuran con reingreso)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-10-30
- Notas de coordinación: reportado desde la base `migracion` (otra sesión), que no se modificó a la espera
  de este fix. Hallazgo: `has_reentry` daba verdadero para expedientes que nunca salieron del Tribunal.

## Objetivo

Que un pase por Secretaría de Vocalía (SEC) o Contadores Fiscales (CF) no cuente como salida del Tribunal.

## Contexto mínimo

`me/data/dependence_data.xml` marca `is_internal=True` en 12 dependencias del Tribunal y omitía
`tmc_data.tmc_dependence_sec`. `_compute_has_reentry` trata toda dependencia no interna como "fuera del
Tribunal": un pase DCD → SEC contaba como salida y el siguiente pase a Vocalía o a Mesa de Entradas, como
reingreso. En `migracion` (instalación limpia) quedaban con reingreso falso EXP-009762/2026 y EXP-012295/2022.

## Alcance

Incluye:

- agregar SEC y CF a `dependence_data.xml`;
- `me/migrations/19.0.1.0.1/post-migration.py` (versión de `me` 19.0.1.0.0 → 19.0.1.0.1): el archivo de datos
  es `noupdate` y un `-u` no marca las bases que ya tienen `me` instalado (verificado: `is_internal` quedó
  NULL tras `-u me`); el script marca SEC y CF solo si no estaban internas;
- 3 tests en `TestHasReentry021`;
- docs (`workflows.md`, `tests_plan.md`).

No incluye: `tmc_dependence_tmc_sub` (nodo 1.13.01 sin abreviatura), ni modificar la base `migracion`.

## Acceptance criteria

- [x] SEC queda `is_internal=True` en una instalación nueva.
- [x] Un pase DCD → SEC → VOC da `has_reentry = False`.
- [x] En una base ya instalada, `-u me` marca SEC (migración) y recalcula `has_reentry`: un expediente de
      prueba DCD → SEC → VOC pasó de `True` a `False` sin recompute manual.
- [x] Suite `/me` verde con evidencia.
- [x] Contadores Fiscales (CF) es interna (decisión del usuario, 2026-10-30).

## Revisión del nomenclador

Las dependencias del Tribunal son las del código 1.13.xx. Solo faltaban **SEC** y **CF — Contadores Fiscales**
(1.13.84); el usuario confirmó que CF es interna. El nodo `tmc_dependence_tmc_sub` (1.13.01, sin abreviatura)
no se marcó.

## Tests evidenciados

- Reproducción previa en `me_test`: con SEC sin marcar, DCD → SEC → VOC daba `has_reentry = True`.
- `-u me` sobre `me_test` (aplica la migración): SEC `is_internal = t`, el expediente de prueba `has_reentry = f`.
- Suite `/me` en `me_test` (con la migración corriendo en la misma pasada): `0 failed, 0 error(s) of 268 tests`.
- Aplicado con `-u me` en `practica` y `junco_demo` (SEC interna en ambas). `migracion` no se tocó.

## Estado / próximo paso

Falta el commit (a pedido). Para `migracion` basta un `-u me` con esta versión.

## Resultado

Pendiente.
