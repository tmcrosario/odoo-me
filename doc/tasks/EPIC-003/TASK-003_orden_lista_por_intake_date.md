# EPIC-003 / TASK-003 — Orden de la lista de expedientes por fecha de ingreso

Estado: Done
Modo: XS
Riesgo: bajo (default sort del modelo; sin datos ni ACL)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-07-30

## Cambio

La lista de expedientes ordena por **`intake_date` descendente** (ingreso más reciente
primero), con **`id desc`** de desempate (`intake_date` es un `Date` → muchos comparten día).
Se implementa con `_order = "intake_date desc, id desc"` en el modelo `me.document_exp`:
es el **default de todas las vistas de lista** (el `<list>` de Odoo no lleva orden propio en
el arch). El usuario puede reordenar clickeando columnas; esto es solo el orden inicial.

## Validación

- Test `test_list_default_order_by_intake_desc` (crea dos, verifica que el de ingreso más
  reciente viene primero).
- Suite `/me`: **0 failed, 0 error(s) of 236 tests** (2026-07-30). UI verificada en me2.

## Cierre

Cerrada (Done) el 2026-07-30 sobre `develop`. Push: usuario. Deploy a prod: diferido.
