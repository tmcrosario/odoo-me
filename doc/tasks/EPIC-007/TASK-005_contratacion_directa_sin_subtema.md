# EPIC-007 / TASK-005 — Contratación Directa no ofrece subtemas

Estado: Done
Modo: S
Riesgo: bajo (solo el dominio del subtema en la vista; sin campos, datos ni ACL)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: tomada
- Fecha de toma: 2026-10-26
- Notas de coordinación: decisión del usuario (opción 1) a la pregunta abierta de la auditoría de
  documentación. JUNCO no se toca: `_derive_process_type_from_exp` ya ignora el subtema de
  Contratación Directa.

## Objetivo

Que el formulario de expedientes no ofrezca, para Contratación Directa, sus 4 hijos del nomenclador
(Concejo Municipal, Excepciones Ordenanzas, Inmueble, Otros): son subtemas documentales de GD que
JUNCO no consume.

## Alcance

Incluye:

- `_compute_allowed_secondary_topic_ids` devuelve vacío para Contratación Directa, y la vista oculta
  el subtema (ya oculta cuando no hay subtemas permitidos);
- test que fija que no se ofrecen aunque `tmc_data` conserve los hijos;
- actualizar `business_rules.md` y `workflows.md`.

No incluye: tocar `tmc_data`, agregar un constrains (los expedientes que ya tengan un subtema cargado
lo conservan), ni cambios en JUNCO.

## Acceptance criteria

- [x] Al elegir Contratación Directa, `allowed_secondary_topic_ids` queda vacío.
- [x] Licitación (2 subtipos), Nota (hijos) y Concurso (vacío) no cambian.
- [x] Los hijos siguen colgando de Contratación Directa en `tmc_data`.
- [x] Prueba manual de UI: el subtema no aparece al elegir Contratación Directa (OK del usuario, 2026-10-26).

## Tests evidenciados

- `test_contratacion_directa_offers_no_subtema` (`me/tests/test_licitacion_subtopic.py`).
- Suite `/me` en `me_test` reconstruida: `0 failed, 0 error(s) of 259 tests`.

## Estado / próximo paso

Cerrada. Sin pendientes.

## Resultado

Contratación Directa deja de ofrecer sus 4 subtemas; el resto de los temas no cambia.
