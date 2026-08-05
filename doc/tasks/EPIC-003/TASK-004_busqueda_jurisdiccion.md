# EPIC-003 / TASK-004 — Búsqueda y group-by por Jurisdicción en la lista

Estado: Done
Modo: XS
Riesgo: bajo (campo buscable + group-by en la search view; sin lógica)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-08-05
- Notas: cierra IDEA 1 (`brainstorming.md`).

## Cambio

En la lista de expedientes se puede **buscar** por `jurisdiction_dependence` (campo buscable en
la barra: se tipea y autocompleta) y **agrupar** por Jurisdicción (group-by con contadores).

## Por qué así (decisión, revisada)

Se descartó el **searchpanel** (panel izquierdo, como "Origen") porque la jurisdicción tiene
**muchos valores que crecen** con el uso → una lista permanente larga, con el grupo "Sin
especificar" (compras) siempre a la vista. El **campo buscable + group-by** escala a cualquier
cantidad sin ocupar espacio fijo, y el group-by cubre "ver todas agrupadas" **on-demand**. El
searchpanel queda para categorías pocas y estables (Origen = DEM/TMC/CM).

- El campo buscable va **sin `string=`**: usa el label del campo (`Jurisdiction`), que ya se
  traduce por `field_description` → se traduce solo. Al group-by (que sí lleva `string`) se le
  sumó la referencia de la search view a la entrada "Jurisdiction" del `.po`.

## Salvedad de negocio (de IDEA 1)

Para **compras** la jurisdicción la completa **JUNCO** (vacía en ME hasta entonces) → el filtro
sirve recién cuando está cargada, y esos expedientes caen en el grupo **None** del group-by.
Para **Notas** es dato de ME desde el ingreso (EPIC-004/TASK-002).

## Validación

- Suite `/me`: **0 failed, 0 error(s) of 246 tests** (2026-08-05). Cambio de vista → sin tests
  nuevos. UI verificada en me2 (buscar por jurisdicción + agrupar).

## Cierre

Cerrada (Done) el 2026-08-05 sobre `develop`. Push: usuario. Deploy a prod: diferido. Cierra
IDEA 1. (Nota de deploy: el label español "Jurisdicción" requiere `es_AR` activo en prod.)
