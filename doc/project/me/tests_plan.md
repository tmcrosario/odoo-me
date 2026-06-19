# Plan de tests — módulo `me` (Mesa de Entradas)

Baseline de tests relevado en EPIC-001/TASK-003. Estado al 2026-06-19: **23 clases,
201 métodos de test**, suite verde (`0 failed, 0 error(s)`).

## Comando canónico

Los tests deben correrse sobre una **DB de test dedicada y NO servida** (`me_test`); sobre
una DB que la instancia ya sirve (me1/me2) el runner recolecta **0 tests** (verde falso).
Desde la raíz del stack `odoo-docker-stack/`:

```bash
# Crear me_test una vez (me arrastra tmc_data por dependencia)
docker compose -f develop.yml exec -T odoo odoo -d me_test -i me,raa \
  --addons-path=/mnt/extra-addons/odoo-tmc,/mnt/extra-addons/odoo-tmc-data,/mnt/extra-addons/odoo-me,/mnt/extra-addons/odoo-junco \
  --db_host=db --db_user=odoo --db_password=odoo --stop-after-init \
  --http-port=8169 --gevent-port=8173 --max-cron-threads=0 --log-level=warn

# Correr la suite
docker compose -f develop.yml exec -T odoo odoo -d me_test -u me \
  --addons-path=/mnt/extra-addons/odoo-tmc,/mnt/extra-addons/odoo-tmc-data,/mnt/extra-addons/odoo-me,/mnt/extra-addons/odoo-junco \
  --db_host=db --db_user=odoo --db_password=odoo --test-tags /me --stop-after-init \
  --http-port=8169 --gevent-port=8173 --max-cron-threads=0 --log-level=test
```

Verificar `... of N tests` con **N > 0** y `0 failed, 0 error(s)`. `--addons-path` siempre
explícito (sin él corre 0 tests). Fallback de evidencia: `docker compose run --rm` (también
recolecta > 0). Framework de test: `odoo.tests.common.TransactionCase`, tags
`('post_install', '-at_install')`.

## Inventario de tests (`me/tests/`)

### `test_document_exp.py` — 177 métodos

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestDocumentExp` | 30 | create básico, movimientos automáticos (DEM/TMC/CM), RAA, unlink/cascade, `is_valid`, **EPIC-004** (create DEM sin jurisdicción + `action_set_origin_from_junco`: happy/UserError/idempotencia/no-manager) | varias |
| `TestSourceDependence` | 4 | `source_dependence_id` / `allowed_sub_dependence_ids` | #012 |
| `TestSecondaryTopics` | 5 | `secondary_topic_id` (subtema) | — |
| `TestTopicProxyFields` | 8 | proxies `main_topic_id` / `secondary_topic_id` sobre `tmc.document` | — |
| `TestRequiredFields017` | 8 | campos obligatorios Fase 2; fecha required; jurisdicción DEM; `computed_name` | #017 |
| `TestDocumentTopicsTMC` | 5 | topics/clasificación TMC | — |
| `TestFojasLock` | 21 | matriz de permisos + bloqueo de `fojas` post-creación | #018 |
| `TestJurisdictionConditional012` | 8 | jurisdicción condicional por origen (TMC/CM auto, DEM) | #012 |
| `TestHasReentry021` | 7 | reingreso institucional (`is_internal` / `has_reentry`) | #021 |
| `TestSearchFilters022023024` | 11 | filtros de búsqueda de expedientes | #022/#023/#024 |
| `TestArchivoDependence025` | 6 | "Archivo" como destino de movimiento | #025 |
| `TestLegajoDependence026` | 9 | movimiento a Legajo + `legajo_number` | #026 |
| `TestMovementDefaultGet` | 4 | `default_get` de `me.document_movement` | — |
| `TestMovementPoseedor027` | 6 | solo el poseedor registra nuevos pases desde UI | #027 |
| `TestMovementCorrection028` | 19 | corrección del último movimiento manual (campos editables) | #028 |
| `TestCurrentHolder029` | 6 | `current_holder_id` (poseedor = último movimiento) | #029 |
| `TestCurrentLocation` | 5 | `current_location_dependence_id` (ubicación interna actual) | EPIC-003 |
| `TestNumberRange032` | 8 | rango de número 1–999999 | #032 |
| `TestDefaultResponsible030` | 7 | `default_responsible_id` onchange en destino | #030 |

### `test_document_movement.py` — 24 métodos

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestDocumentMovement` | 8 | integridad: origen/destino obligatorios, fecha (no futura/anterior), duplicado exacto | — |
| `TestFojasMovimiento` | 7 | campo `fojas` en el movimiento (default/explícito/automático) | #015 |
| `TestResponsibleUser011` | 4 | `user_id` como responsable operativo en destino | #011 |
| `TestAutoOriginPreload020` | 5 | pre-carga de `origin_dependence_id` en `default_get()` | #020 |

## Cobertura de las reglas activas (`business_rules.md`)

| Regla activa | Tests | Estado |
| --- | --- | --- |
| Tipo de documento automático | `TestJurisdictionConditional012` (onchange) | ✅ (indirecto) |
| Origen permitido DEM/TMC/CM | `TestJurisdictionConditional012`, `TestDocumentExp` | ✅ |
| Nombre generado (`computed_name`) | `TestRequiredFields017` (`test_computed_name_*`) | ✅ |
| Movimientos iniciales automáticos | `TestDocumentExp` (two/tmc/cm), `TestAutoOriginPreload020` | ✅ |
| Carga jurisdicción/origen DEM (EPIC-004) | `TestDocumentExp` (bloque EPIC-004) | ✅ |
| **Jurisdicción multi-año (intencional)** | — | ❌ **gap (bajo)** |
| Registro automático en RAA | `TestDocumentExp` (`registers_in_raa`) | ✅ |
| Fojas — bloqueo post-creación | `TestFojasLock`, `TestFojasMovimiento` | ✅ |
| **Aviso de duplicado (origen+número+período)** | — (solo duplicado de *movimiento*) | ❌ **gap (medio)** |
| Fecha del documento (pasadas / bypass SQL) | `TestRequiredFields017`, `TestDocumentMovement` | ✅ |
| Integridad de movimientos | `TestDocumentMovement` | ✅ |
| Poseedor actual (#027/#028/#029) | `TestMovementPoseedor027`, `TestMovementCorrection028`, `TestCurrentHolder029` | ✅ (fuerte) |
| Salida / reingreso institucional (#021/#030) | `TestHasReentry021`, `TestDefaultResponsible030` | ✅ |
| Ubicación interna actual (EPIC-003) | `TestCurrentLocation` | ✅ |

## Gaps priorizados

1. **ALTA — CI no ejecuta los tests.** El pipeline (`.github/workflows/pipeline.yml`) solo
   construye/pushea la imagen Docker, corre **Snyk** (seguridad) y despliega; **no corre la
   suite `/me`**. Los tests no están gateados → regresiones pueden llegar a deploy sin red.
   *Recomendación:* agregar un job que levante Postgres y corra la suite sobre `me_test`
   antes del build/deploy.
2. **MEDIA — Aviso de duplicado de expediente** (origen+número+período, "avisa pero no
   bloquea"): sin test. *Recomendación:* test del onchange que verifique el warning sin
   bloqueo. (El duplicado de *movimiento* sí está cubierto.)
3. **BAJA — Jurisdicción multi-año**: el comportamiento intencional de no filtrar por año
   no tiene test directo. *Recomendación:* test que confirme que el dominio incluye
   jurisdicciones de más de un nomenclador cargado.
4. **BAJA — Continuidad / append-only de movimientos**: no implementado y sin test (coincide
   con "Limitaciones conocidas"). Si se implementa el enforcement, agregar tests.
5. **BAJA — Camino negativo "Mesa de Entradas" inexistente**: el movimiento automático a ME
   se omite sin aviso si no encuentra la dependencia; no hay test del caso.

## Estado de CI

`.github/workflows/pipeline.yml` — **Deployment Pipeline** (`on: push`):
build & push de imagen Docker (DockerHub) → Snyk security scan de la imagen → deploy por
SSH al stack (`docker compose up web --scale web=4`). **No incluye ejecución de tests.**
La verificación de tests es **manual** (ver "Comando canónico" y el workflow `me_test`).

## Política

- Tests user-run por default. No declarar `OK` sin salida pegada.
- En M/L/XL, el bloque "Tests evidenciados" de la task card es obligatorio.
- Áreas que requieren test (o `N/A + motivo`): reglas de negocio, workflow/movimientos,
  security/permisos, modelos/campos persistentes, migraciones, bugfixes con riesgo de
  regresión. Ver `doc/framework/odoo_development_rules.md` y `doc/framework/testing_policy.md`.
