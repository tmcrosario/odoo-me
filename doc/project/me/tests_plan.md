# Plan de tests — módulo `me` (Mesa de Entradas)

Baseline de tests relevado en EPIC-001/TASK-003; revalidado tras `junco:EPIC-011`,
`junco:EPIC-015`, `EPIC-006/TASK-001/002`, `EPIC-004/TASK-002/003/004` + `EPIC-003/TASK-003`.
**Estado al 2026-08-05: 27 clases, 246 métodos de test**, suite verde.

**Convención de métrica (importante — hay dos números y ambos son correctos):**

| Métrica | Valor | De dónde sale |
| --- | ---: | --- |
| **Línea de resultado** (la que usamos) | **246** | `odoo.tests.result: 0 failed, 0 error(s) of 246 tests`. Coincide con contar `def test_` en el fuente |
| `stats` | 300 | `odoo.tests.stats: me: 300 tests` — cuenta distinto |

Citar siempre **la línea de resultado** y decir qué métrica es. Las cifras históricas de ME
en la doc de junco se bajaron a esta convención.

## Comando canónico

Los tests deben correrse sobre una **DB de test dedicada y NO servida** (`me_test`); sobre
una DB que la instancia ya sirve (me1/me2) el runner recolecta **0 tests** (verde falso).
Desde la raíz del stack `odoo-docker-stack/`:

```bash
# Crear me_test una vez (me arrastra tmc_data por dependencia)
docker compose -f develop.yml exec -T odoo odoo -d me_test -i me,raa \
  --addons-path=/mnt/extra-addons/odoo-tmc,/mnt/extra-addons/odoo-tmc-data,/mnt/extra-addons/odoo-me,/mnt/extra-addons/odoo-junco,/mnt/addons/oca/server-tools,/mnt/addons/oca/web,/mnt/addons/oca/server-brand,/mnt/addons/oca/server-ux,/mnt/addons/oca/partner-contact \
  --db_host=db --db_user=odoo --db_password=odoo --stop-after-init \
  --http-port=8169 --gevent-port=8173 --max-cron-threads=0 --log-level=warn

# Correr la suite
docker compose -f develop.yml exec -T odoo odoo -d me_test -u me \
  --addons-path=/mnt/extra-addons/odoo-tmc,/mnt/extra-addons/odoo-tmc-data,/mnt/extra-addons/odoo-me,/mnt/extra-addons/odoo-junco,/mnt/addons/oca/server-tools,/mnt/addons/oca/web,/mnt/addons/oca/server-brand,/mnt/addons/oca/server-ux,/mnt/addons/oca/partner-contact \
  --db_host=db --db_user=odoo --db_password=odoo --test-tags /me --stop-after-init \
  --http-port=8169 --gevent-port=8173 --max-cron-threads=0 --log-level=test
```

Verificar la **línea de resultado**: `... of N tests` con **N > 0** y `0 failed, 0 error(s)`.
`--addons-path` siempre explícito (sin él corre 0 tests = **verde falso**) **y completo**:
desde la **tmc 19.0 (2026-07-23)** `tmc` depende de módulos OCA
(`web_tree_many2one_clickable` de OCA/web, `remove_odoo_enterprise` de OCA/server-brand) →
**sin las rutas `/mnt/addons/oca/*` tmc no carga y todo el grafo (`me`/`junco`/`raa`) se
saltea**. Síntomas: `KeyError: 'tmc.dependence_order'` en `odoo shell`; "Some modules are not
loaded ['junco','me','raa','tmc','tmc_data']" en el server. Si el módulo OCA falta en la
**imagen**: `docker compose -f develop.yml build --no-cache --pull` (re-clona los repos OCA).
Si la **DB de test es anterior al salto** (p.ej. `me_test`), correr **una vez** `-u tmc,me`:
actualizar `tmc` instala sus deps OCA nuevas — `-u me` solo **no** lo hace (carga el grafo sin
instalar deps ajenas) y el síntoma es el mismo `0 tests of 0` **aun con el path completo**.
Copiar el path del `command:` de `develop.yml`. Para una clase puntual:
`--test-tags "/me:TestMeSecurity"`. Fallback de evidencia: `docker compose run --rm` (también
recolecta > 0). Framework: `odoo.tests.common.TransactionCase`, tags
`('post_install', '-at_install')`.

## Inventario de tests (`me/tests/`)

### `test_document_exp.py` — 192 métodos

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestDocumentExp` | 40 | create básico, movimientos automáticos (DEM/TMC/CM), RAA, unlink/cascade, `is_valid`, **EPIC-004** (create DEM sin jurisdicción + `action_set_origin_from_junco`: happy/UserError/idempotencia/no-manager), **junco:EPIC-011** (`test_allowed_exp_root_topics`: los 4 temas raíz), **EPIC-004/TASK-002 fechas** (8: `date`/`intake_date` no futuras, `intake >= period` asimétrica, `intake >= date`, incl. en `write` y por el SQL directo), **EPIC-003/TASK-003** (`test_list_default_order_by_intake_desc`) | varias |
| `TestSourceDependence` | 4 | `source_dependence_id` / `allowed_sub_dependence_ids` | #012 |
| `TestSecondaryTopics` | 5 | `secondary_topic_id` (subtema) | — |
| `TestTopicProxyFields` | 8 | proxies `main_topic_id` / `secondary_topic_id` sobre `tmc.document`; 2 de los 8 cubren `allowed_exp_topic_ids` | — |
| `TestRequiredFields017` | 8 | campos obligatorios Fase 2; fecha required; jurisdicción DEM; `computed_name` | #017 |
| `TestDocumentTopicsTMC` | 5 | topics/clasificación TMC | — |
| `TestFojasLock` | 21 | matriz de permisos + bloqueo de `fojas` post-creación | #018 |
| `TestJurisdictionConditional012` | 8 | jurisdicción condicional por origen (TMC/CM auto, DEM) | #012 |
| `TestHasReentry021` | 7 | reingreso institucional (`is_internal` / `has_reentry`) | #021 |
| `TestSearchFilters022023024` | 11 | filtros de búsqueda de expedientes | #022/#023/#024 |
| `TestArchivoDependence025` | 6 | "Archivo" como destino de movimiento | #025 |
| `TestLegajoDependence026` | 14 | movimiento a Legajo + `legajo_number`; **EPIC-006/TASK-002**: `current_legajo_number` (indicador "En Legajo Nº X" del último movimiento — en legajo/se movió/varios/sin legajo) + domain del filtro "Adjuntos a Legajo" | #026 |
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

### `test_security.py` — 5 métodos (junco:EPIC-015)

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestMeSecurity` | 5 | Permisos cross-sistema ME↔GD: el operativo hereda `tmc.group_read_only` y **no** `tmc.group_user`; **puede** crear expedientes (el `tmc.document` padre se crea con el `create` elevado — protege la regresión que rompería quitar el `sudo`); **lee** `tmc.document` pero no lo escribe ni lo crea; un **lector no puede crear expedientes**; y el **orden de la escalera del privilegio ME** (`test_me_privilege_ladder_order`) | junco:EPIC-015 (+ /TASK-004) |

### `test_save_button.py` — 2 métodos (EPIC-006)

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestSaveButton` | 2 | Botón "Save" dirty-only del form de expediente: (1) el arch tiene `special="save"` con la clase outline `o_me_form_save_button` (nunca la variante `btn-primary`); (2) el SCSS está registrado en `web.assets_backend` del manifest (guard del acople botón↔asset). La **visibilidad** por dirty vive en el SCSS y necesita navegador → es USER-RUN | EPIC-006 |

> Nota: `test_save_button.py` no prueba la visibilidad real (dirty→muestra, limpio→oculta):
> eso es CSS y requiere un tour/browser. El guard del asset evita el falso verde de borrar el
> bloque `assets` del manifest dejando el arch intacto. Evidencia de comportamiento: USER-RUN
> en me2 (EPIC-006/TASK-001).

### `test_nota_origin.py` — 18 métodos (EPIC-004/TASK-002 + TASK-003)

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestNotaOrigin` | 18 | DEM + tema Nota carga jurisdicción/origen en ME: `is_nota` (m2m del padre **y** el proxy `main_topic_id`, para que reaccione antes de guardar); carga y obligatoriedad backend; **no-regresión de EPIC-004** (temas de compra siguen cediendo a JUNCO, `action_set_origin_from_junco` sigue OK para compras); **guarda defensiva** (rechaza Nota, no pisa lo cargado); **tema cambiado post-alta** (poner Nota exige jurisdicción; sacarla la libera; editar algo ajeno al tema no bloquea); aviso de duplicado no se autodetecta; el operativo **no** puede tocar el origen post-alta; dato viejo (Nota sin jurisdicción) **sobrevive al recompute** de `-u`; **TASK-003:** el 1er movimiento de una Nota sale de la **jurisdicción** y el de compras de `dependence_id` | EPIC-004/TASK-002 + TASK-003 |

> ⚠️ Varios de estos tests documentan **por qué NO** cierta forma más simple: la validación
> vive en `create()`/`write()` y **no** en `@api.constrains('is_nota')` (al ser stored,
> recomputarlo dispararía la constraint sobre TODOS los registros en cada `-u me` y abortaría
> el update sobre las Notas viejas legítimamente vacías). No relajar.

### `test_licitacion_subtopic.py` — 5 métodos (EPIC-004/TASK-004)

| Clase | # | Qué prueba | Semilla |
| --- | ---: | --- | --- |
| `TestLicitacionSubtopic` | 5 | El subtema de Licitación se acota a Privada/Pública vía `allowed_secondary_topic_ids`: solo esos 2 (no los 25 de GD); una "etapa" **no** se ofrece **pero sigue colgando de Licitación** en `tmc_data` (guardrail junco); reacciona al proxy `main_topic_id` antes de guardar; no-regresión (otros temas → hijos del tema); Concurso de Precios (sin hijos) → subtema vacío/oculto | EPIC-004/TASK-004 |

> ⚠️ **`test_me_privilege_ladder_order` asserta el orden `[Read Only, User, Manager]` Y que los
> ranks sean estrictamente crecientes — las dos cosas, a propósito.** El assert de ranks es el que
> exige que el orden venga de la **cadena real** (`user` implica `read_only`): sin él, el test pasa
> con la opción descartada (`sequence`), que deja los ranks empatados y el orden sostenido por el
> desempate por `id`. **No relajarlo a "están los 3 grupos"**: eso pasa siempre y no prueba nada.
> Este test existe porque el defecto **no lo detectó ninguna suite** — lo encontró un humano
> mirando un dropdown (junco:EPIC-015/TASK-004).

> ⚠️ **`test_me_read_only_cannot_create_expediente` asserta el modelo citado en el mensaje del
> `AccessError` A PROPÓSITO — no simplificar a un `assertRaises(AccessError)` pelado.** Un
> `assertRaises` pelado **pasa igual sin el fix**: el error llega enmascarado desde
> `me.document_movement` (el ACL de movimientos bloquea de rebote) en vez de venir del ACL de
> `me.document_exp`. Ese falso positivo ya ocurrió: el test pasaba antes **y** después del fix,
> y no probaba nada. Si se simplifica, la regresión vuelve y **ninguna suite la ve**.

## Cobertura de las reglas activas (`business_rules.md`)

| Regla activa | Tests | Estado |
| --- | --- | --- |
| Tipo de documento automático | `TestJurisdictionConditional012` (onchange) | ✅ (indirecto) |
| Origen permitido DEM/TMC/CM | `TestJurisdictionConditional012`, `TestDocumentExp` | ✅ |
| Nombre generado (`computed_name`) | `TestRequiredFields017` (`test_computed_name_*`) | ✅ |
| **Temas raíz del expediente** (junco:EPIC-011) | `TestDocumentExp.test_allowed_exp_root_topics`; `TestTopicProxyFields` (2 tests de `allowed_exp_topic_ids`) | ✅ (el `domain`; el gating no tiene enforcement backend — ver `business_rules.md`) |
| **Permisos cross-sistema (ME ↔ GD)** → `security.md` | `TestMeSecurity` (5, incluye el orden de la escalera de grupos) | ✅ |
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
