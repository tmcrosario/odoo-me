# EPIC-004 / TASK-006 — Tema requerido al alta + filtro "Sin clasificar"

Estado: Done
Modo: XS
Riesgo: bajo (required de vista + filtro de búsqueda; sin backend constraint)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-08-07
- Notas: surge de una duda del usuario al cerrar TASK-005.

## Objetivo

Que **una compra sin tema no quede invisible para JUNCO**. JUNCO filtra los expedientes
elegibles por **tema principal** (licitación/concurso/directa); un expediente **sin tema** no
aparece en su selector → si el operativo se olvida el tema, la compra queda colgada sin aviso.
Se cierra por dos lados: **tema requerido al alta** (para el operativo) + **filtro "Sin
clasificar"** (para pescar los que entren por ORM/import o los viejos).

## Alcance

- **Vista:** `main_topic_id required="not id and is_origin_complete"` — requerido para expedientes
  **nuevos** (no rompe los viejos sin tema); condicionado a `is_origin_complete` para no exigirlo
  sobre un campo aún invisible.
- **Vista (search):** filtro `Unclassified` (`domain=[('main_topic_ids','=',False)]`) + traducción
  `es_AR` "Sin clasificar".

**Decisión de diseño:** el tema requerido es **solo de vista** (no `@api.constrains`), a diferencia
del subtema (TASK-005). Por qué: el tema requerido sería **global** (todo expediente) → un
constraint en `create()` rompería decenas de creates por ORM/tests, y **JUNCO ya gatea por tema**
(el enforcement duro está de su lado). El riesgo real es el **operativo que se olvida** → lo cubre
el required de vista; los caminos ORM/import/legacy los cubre el filtro.

No incluye: backend constraint del tema; se decidió a propósito (ver arriba).

## Reglas conocidas (validado con el usuario, 2026-08-07)

- **Todo expediente encaja en uno de los 4 temas** (compras = licitación/concurso/directa;
  no-compras = Nota) → requerir el tema no fuerza clasificaciones incorrectas.
- **Datos existentes:** 2 DEM sin tema en me2 (probablemente de prueba) → required solo para
  nuevas; el filtro los encuentra.
- **Confirmado por junco (verificado en su código, 2026-08-07):** un expediente de compra **sin
  tema simplemente no aparece** en su selector (el domain filtra por `main_topic_ids in
  [licitación, concurso, directa]`), **sin error** — la premisa de esta task es correcta. El
  error solo se da por **link ORM directo**, no por UI. Junco **parkeó** el micro-ajuste de un
  constraint en su link table para "licitación sin subtema por ORM directo": con el enforcement
  upstream de ME + sus capas, el único hueco es un write crudo por ORM/migración (marginal); lo
  reabren solo si aparece un ingestor ORM real.

## Acceptance criteria

- [x] Expediente nuevo: **tema obligatorio** (no se puede guardar sin tema).
- [x] Expediente viejo sin tema: **editable** (required solo para nuevas).
- [x] Filtro "Sin clasificar" (es_AR) deja solo los expedientes sin tema.
- [x] Suite `/me` verde + UI verificada en me2.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md`.
- Fecha: 2026-08-07
- Resultado: **0 failed, 0 error(s) of 254 tests** (stats 308). Test nuevo
  `test_unclassified_filter_finds_topicless` (el domain del filtro encuentra los sin tema). El
  required de vista es UI → USER-RUN (verificado en me2). Aplicado a me2 + restart.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido (+ recordar `es_AR` para "Sin clasificar").

## Resultado / cierre

Cerrada (Done) el 2026-08-07 sobre `develop`. Tema requerido al alta (vista, solo nuevas) +
filtro "Sin clasificar", para que ninguna compra quede invisible para JUNCO por falta de
clasificación. Enforcement duro del tema queda del lado de JUNCO (gate de elegibilidad).
