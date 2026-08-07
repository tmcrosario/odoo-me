# EPIC-004 / TASK-005 — Subtema de Licitación requerido (upstream de JUNCO)

Estado: Done
Modo: S
Riesgo: bajo (required condicional + validación backend; sin campos nuevos)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-08-07
- Notas: pedido de coordinación de `odoo-junco`. Sigue a EPIC-004/TASK-004 (que acotó el
  subtema de licitación a Privada/Pública).

## Objetivo

Una **Licitación no puede quedar sin subtema**: JUNCO deriva el subtipo del proceso
(`public_tender`/`private_tender`) del subtema (Pública/Privada) y **no puede cerrar upstream**
el caso "licitación sin subtema" (la licitación pasa su elegibilidad, pero sin subtema el tipo
queda ambiguo). Concurso de precios y contratación directa **no llevan subtema** → no se exigen.

## Alcance

- `is_licitacion` reacciona en vivo al proxy `main_topic_id` (added a `@api.depends`), para que
  el `required` de la vista se active al elegir el tema.
- **Vista:** `secondary_topic_id required="is_licitacion and not id"` (nuevas).
- **Backend:** `_validate_licitacion_subtopic()` llamado en `create()` y en `write()` cuando se
  toca tema/subtema (cubre reclasificar a licitación y quitarle el subtema). **NO**
  `@api.constrains('is_licitacion')` — al ser stored, recomputarlo dispararía la constraint sobre
  TODAS las licitaciones en cada `-u` y rompería las viejas sin subtema.
- Concurso/directa: intactos (no son licitación → no se validan).

No incluye: backfill del dato viejo (ver caveats); required global del tema (es TASK-006).

## Caveats validados (no inventados)

- **Datos existentes:** había **1 licitación cargada sin subtema** en me2 → **required solo para
  nuevas** (decisión del usuario): la vieja queda editable, el `-u` no la rompe (validación en
  create/write, no en constraint sobre el stored). Verificado: me2 actualizó sin abortar.
- **Momento:** Pública/Privada **se conoce al alta** (desde la carátula, decisión del usuario) →
  el required va al alta.

## Acceptance criteria

- [x] Licitación nueva sin subtema: **no se puede crear/guardar** (vista + backend).
- [x] Reclasificar a Licitación sin subtema / quitarle el subtema: **rechazado** (write).
- [x] Concurso / contratación directa: **sin cambios** (no exigen subtema).
- [x] Licitación vieja sin subtema: **editable** (required solo nuevas) y **sobrevive al `-u`**.
- [x] Suite `/me` verde + UI verificada en me2.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md` (`-u me`, path OCA completo, `--test-tags /me`, `me_test`).
- Fecha: 2026-08-07
- Resultado: **0 failed, 0 error(s) of 254 tests** (stats 308). 7 tests nuevos en
  `TestLicitacionSubtopic` (sin subtema→raise, con subtema→ok, concurso/directa→ok, reclasificar,
  quitar subtema, **legacy sobrevive al recompute + editable**). Además se **corrigieron 6 tests
  pre-existentes** que creaban licitaciones sin subtema (dato ahora inválido) → usan tema neutro
  (contratación directa) o subtema válido. Aplicado a me2 (`-u me`) + restart. UI verificada.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido.

## Resultado / cierre

Cerrada (Done) el 2026-08-07 sobre `develop`. El subtema de una Licitación es obligatorio
(patrón de la Nota: required condicional + validación en create/write, no en `@api.constrains`
sobre el stored, para no romper el dato viejo). Alinea la carga de ME con lo que JUNCO ya exige
al vincular (rechazo por clasificación). Coordinado con `odoo-junco`.
