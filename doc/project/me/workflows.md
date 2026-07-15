# Módulo ME — Workflows

> Consolidado desde `domain-rules/me/workflows.md`. Es la descripción de
> comportamiento **más actual** del módulo (incorpora cambios hasta #021–#030):
> ante discrepancias con [`architecture.md`](architecture.md), **este doc manda**.
>
> **Verificado contra código vigente — EPIC-001/TASK-001 (2026-06-19).** Deltas posteriores
> a #030 incorporados: **EPIC-004** (en DEM, `jurisdiction_dependence`/`source_dependence_id`
> ya no se cargan en ME — los completa JUNCO vía `action_set_origin_from_junco()`; el 1er
> movimiento automático usa `dependence_id` como origen — ver Workflow 4 y `business_rules.md`);
> **EPIC-003** (campo `current_location_dependence_id` = oficina interna actual, + filtros
> por poseedor y por oficina de destino en la search view).

Este archivo documenta los workflows principales del módulo Mesa de Entradas
basándose en el comportamiento real del código.

Cada paso está clasificado como:

- **Observed in code** — comportamiento explícito en el código fuente
- **Inferred** — consecuencia indirecta observable, no declarada explícitamente
- **Uncertain / pending definition** — no está definido en el código actual


--------------------------------------------------

## 1. Creación de expediente (flujo principal)

El usuario crea un nuevo `me.document_exp` desde la vista formulario.
Este workflow incluye los sub-pasos 2, 3 y 4, que ocurren en el mismo
`create()` de forma atómica, sin intervención del usuario.

### Pasos

**Fase 1 (siempre visible):**

1. El usuario abre el formulario de nuevo expediente.
2. Completa `dependence_id` (origen del expediente).
3. Al seleccionar `dependence_id`, el sistema auto-asigna `document_type_id = 'EXP'`
   (vía `default_get` y `_onchange_dependence`). El campo es readonly.
4. El usuario completa `number` y `period`.
5. Al completar los 3 campos de Fase 1, `is_origin_complete` se vuelve `True`
   y el sistema muestra en tiempo real `computed_name` (ej. `EXP-000001-DEM/2025`).

**Fase 2 (visible cuando `is_origin_complete = True`):**

6. El usuario completa `intake_date` (obligatorio).
   Según la dependencia de origen elegida en Fase 1:
   - **DEM** (EPIC-004): el operador **NO carga** `jurisdiction_dependence` ni
     `source_dependence_id`. En la vista están **readonly** y **ocultos si vacíos**
     (`document_exp_views.xml`): quedan vacíos al ingresar y los completa **JUNCO** al
     vincular el expediente a un proceso, vía `action_set_origin_from_junco()`.
   - **TMC**: `jurisdiction_dependence` se auto-asigna a TMC y es readonly.
     `source_dependence_id` no es requerido.
   - **CM**: `jurisdiction_dependence` y `source_dependence_id` no se muestran.
     El sistema los completa internamente (jurisdiction = CM, source = vacío).
   Al cambiar `jurisdiction_dependence`, `source_dependence_id` se limpia automáticamente.
7. Si los 5 campos básicos están completos y existe un expediente con los mismos datos,
   el sistema emite un **warning** (no bloquea).
8. El usuario guarda el formulario → se ejecuta `create()`.
9. El sistema ejecuta los sub-pasos 2, 3 y 4 automáticamente.
10. El formulario muestra el expediente creado con su nombre generado.

### Evidence

**Observed in code:**
- Auto-asignación de `document_type_id`: `me/models/document_exp.py:93–108` (`_onchange_dependence`)
- Filtro de `dependence_id` restringido a `['DEM', 'TMC', 'CM']`: `me/views/document_exp_views.xml:41`
- Warning de duplicado en tiempo real: `me/models/document_exp.py:110–127` (`_onchange_document_data`)
- Warning no bloquea — retorna `warning` dict, no `raise`: `me/models/document_exp.py:122–127`
- `computed_name` visible desde el primer campo: `me/views/document_exp_views.xml:30–36`
- `source_dependence_id` opcional, domain dinámico vía `allowed_sub_dependence_ids`: `me/views/document_exp_views.xml:53–55`
- Limpieza de `source_dependence_id` al cambiar jurisdicción: `me/models/document_exp.py:155–158` (`_onchange_jurisdiction_dependence`)

**Inferred:**
- El formulario se muestra progresivamente: ver Workflow 6.

**Uncertain / pending definition:**
- No existe validación que bloquee la creación si el expediente duplicado ya existe.
  El warning es informativo. No está definido si esto es intencional o un gap.


--------------------------------------------------

## 2. Creación automática del documento base (sub-paso de Workflow 1)

Ocurre dentro de `me.document_exp.create()` al llamar a `super().create()`.
No es un workflow independiente — forma parte del Workflow 1.

### Pasos

0. **(junco:EPIC-015)** Antes de elevar, `create()` valida el ACL del llamador con
   `self.check_access('create')` — la elevación del paso siguiente saltearía el ACL de
   `me.document_exp` (`ir.model.access.check` corta por `env.su`).
1. `super().create(vals_list)` es invocado **elevado** (`.with_context(me_create_in_progress=True).sudo()`)
   con los campos del expediente en `vals`: el operativo de ME **solo lee GD**, y el padre
   `tmc.document` se crea dentro de este `super()`. Se **des-eleva de inmediato** después
   (`records.sudo(self.env.su)`) para que movimientos y demás corran con los permisos del usuario.
2. El mecanismo `_inherits` de Odoo detecta los campos del padre
   (`dependence_id`, `document_type_id`, `number`, `period`, `date`, `document_object`)
   y crea automáticamente el registro `tmc.document`.
3. Odoo asigna el `document_id` resultante al registro `me.document_exp`.
4. El registro `me.document_exp` queda creado y vinculado al `tmc.document`.

### Evidence

**Observed in code:**
- `check_access('create')` + `super().create()` elevado + des-elevación:
  `me/models/document_exp.py`, `create()` (~l.546-550)
- Mecanismo `_inherits`: `me/models/document_exp.py:6`
- Postura de permisos y elevaciones: [`security.md`](security.md)

**Inferred:**
- Si la creación de `tmc.document` falla (ej. constraint de unicidad de nombre),
  el `create()` completo falla y no se crea ningún registro.
  No hay manejo de error explícito en el código.

**Uncertain / pending definition:**
- No está definido qué campos adicionales del documento base
  (ej. `highlight_ids`, `main_topic_ids`) se inicializan en la creación.
  Solo se pasan los campos presentes en `vals` al momento de llamar a `super()`.


--------------------------------------------------

## 3. Registro automático en RAA (sub-paso de Workflow 1)

Ocurre dentro de `me.document_exp.create()` inmediatamente después de crear
el registro ME. No es un workflow independiente.

### Pasos

1. Después de `super().create(vals)`, el sistema crea un registro `raa.registry_aa`
   con el `document_id` del `tmc.document` recién creado.
2. El registro RAA vincula el acto administrativo al documento base.

### Evidence

**Observed in code:**
- Creación de `raa.registry_aa` con `sudo()` (efecto interno; el operador no necesita ACL
  en `raa`): `me/models/document_exp.py`, `create()` (~l.563)
- Constraint UNIQUE en `raa.registry_aa.document_id`: `raa/models/registry_aa.py:52–55`

**Inferred:**
- Si `raa` no está instalado, la llamada `self.env["raa.registry_aa"]` falla en runtime.
  `raa` **no** está declarado en `me/__manifest__.py` y **no puede estarlo**: `raa` depende de
  `me`, así que declararlo crearía un ciclo `me ↔ raa`. Acoplamiento implícito **deliberado**
  (decisión EPIC-005/TASK-002) — ver [`models.md`](models.md) → "Modelo externo: `raa.registry_aa`".

**Uncertain / pending definition:**
- No está definido qué ocurre si `raa.registry_aa` ya existe para ese `document_id`
  (constraint UNIQUE activa). El código no maneja ese caso explícitamente.
- No está definido si la creación en RAA es intencional como paso de negocio
  o es un efecto secundario de la arquitectura.


--------------------------------------------------

## 4. Inicialización de movimientos automáticos (sub-paso de Workflow 1)

Ocurre dentro de `me.document_exp.create()` después del paso RAA.
Crea movimientos automáticos que registran la trayectoria inicial del expediente.
El número y recorrido depende de la dependencia de origen (`dependence_id`).

### Pasos

> **Actualizado EPIC-004 (2026-06):** el Movimiento 1 ahora usa **`dependence_id`** como
> origen (no `jurisdiction_dependence`), y el guard ya no exige la jurisdicción. Así el 1er
> pase DEM→TMC se crea al ingresar aunque la jurisdicción esté vacía (en DEM la completa
> JUNCO después). Ver `business_rules.md`.

**Rama DEM (y cualquier origen distinto de TMC):**

1. El sistema busca `tmc.dependence` con `abbreviation = 'TMC'` y con `abbreviation = 'ME'`.
2. Crea Movimiento 1 (**origen → TMC**):
   - origen: **`dependence_id`** (DEM) — EPIC-004, opción A (antes era `jurisdiction_dependence`)
   - destino: TMC
   - `fojas`: `record.fojas` (snapshot en el momento de creación)
   - `is_automatic`: True
3. Crea Movimiento 2 (TMC → Mesa de Entradas):
   - origen: TMC
   - destino: Mesa de Entradas
   - `fojas`: `record.fojas`
   - `is_automatic`: True

**Rama TMC (dependence_id == TMC):**

1. El sistema detecta que el origen es TMC (`origin_is_tmc = True`).
2. **Omite el Movimiento 1** — el recorrido TMC→TMC no tiene sentido funcional.
3. Crea únicamente Movimiento TMC → Mesa de Entradas (mismo formato que Movimiento 2 arriba).

**Rama CM (dependence_id == CM):**

1. Crea Movimiento 1: CM → TMC (origen = `dependence_id` = CM; coincide con la jurisdicción
   auto-asignada de CM).
2. Crea Movimiento 2: TMC → Mesa de Entradas.

En todos los casos, los movimientos son condicionales: si TMC o ME no existen en la
base de datos, se omiten silenciosamente sin error.

### Evidence

**Observed in code:**
- Condicional `origin_is_tmc`: `me/models/document_exp.py`, método `create()`
- Movimiento 1 omitido para TMC: `if not origin_is_tmc and tmc_dependence` (EPIC-004; antes
  exigía `and record.jurisdiction_dependence`). Origen del Mov.1 = `record.dependence_id.id`.
- Backup auto-asignación CM/TMC: pre-super() loop en `create()`
- Campos `fojas` e `is_automatic` incluidos en cada movimiento automático

**Inferred:**
- Si `tmc.dependence (TMC)` no existe, ningún movimiento se crea (ninguno de los dos).
- Si `Mesa de Entradas` no existe (abbreviation='ME'), solo se crea el Movimiento 1 (DEM/CM).

**Uncertain / pending definition:**
- No está definido si la ausencia de estos movimientos es un estado válido del expediente.
- No hay constraint que garantice que estos movimientos existan.


--------------------------------------------------

## 5. Routing manual de expedientes (movimientos posteriores)

Después de creado el expediente, el usuario puede registrar movimientos adicionales
desde la pestaña "Movimientos" en el formulario.

### Pasos

1. El usuario abre el expediente existente.
2. Navega a la pestaña "Movimientos" (visible solo cuando el registro está guardado).
3. Agrega un nuevo movimiento en la lista editable:
   - `date` (requerido, default: ahora)
   - `origin_dependence_id` (requerido, pre-cargado automáticamente con el
     `destination_dependence_id` del último movimiento del expediente por `id`;
     si no hay movimientos previos, queda vacío; editable)
   - `destination_dependence_id` (requerido)
   - `user_id` (default: usuario activo — representa al responsable en destino,
     no necesariamente quien cargó el movimiento; auditoría de carga en `create_uid`)
4. Guarda el movimiento.

### Evidence

**Observed in code:**
- Lista editable de movimientos: `me/views/document_exp_views.xml:73–87`
- Pestaña visible solo si el registro tiene id: `me/views/document_exp_views.xml:70`
- `origin_dependence_id` y `destination_dependence_id` required=True: `me/models/document_movement.py`
- Constraint UNIQUE(expediente_id, origin_dependence_id, destination_dependence_id, date):
  impide duplicados exactos — `me/models/document_movement.py` `_sql_constraints`
- `_check_date_not_future`: rechaza date > now() — `me/models/document_movement.py`
- `_check_date_not_before_intake`: rechaza date.date() < expediente.intake_date — `me/models/document_movement.py`
- `user_id` representa al responsable en destino (no quien cargó); auditoría en `create_uid` (Odoo nativo)
- `user_id` readonly cuando `is_automatic = True`: `me/views/document_exp_views.xml`
- Pre-carga de `origin_dependence_id` vía `default_get()`: `me/models/document_movement.py` (`default_get`)
  — toma el `destination_dependence_id` del movimiento con mayor `id` del expediente

**Observed in code (post #027):**
- Regla de poseedor: solo el `user_id` del movimiento con mayor `id` puede registrar
  un nuevo pase desde la UI del formulario del expediente. Managers sin restricción.
  El guard de `write()` detecta comandos O2M CREATE y verifica el poseedor.
  → `me/models/document_exp.py` `write()`

**Observed in code (post #028):**
- Corrección del último movimiento manual: el poseedor actual puede corregir el
  movimiento con mayor id (solo si es manual, no automático).
  Campos corregibles por operador: fojas, user_id, legajo_number (este último solo si destino=LEG).
  Campos bloqueados para operador: origin_dependence_id, destination_dependence_id, date.
  → `me/models/document_movement.py` `write()`

**Observed in code (post #029):**
- Campo `current_holder_id` (Many2one res.users, stored computed) en `me.document_exp`:
  user_id del movimiento con mayor id. False si no hay movimientos.
  Se actualiza automáticamente al crear o corregir movimientos.
  → `me/models/document_exp.py` `_compute_current_holder_id`
- Filtro "En mi poder" en search view: domain `[('current_holder_id', '=', uid)]`.

**Observed in code (post #030):**
- Campo `default_responsible_id` (Many2one res.users) en `tmc.dependence`,
  extendido desde `me/models/dependence_ext.py`. Solo relevante cuando `is_internal=True`.
  Configurable por `me.group_manager` desde el formulario de la dependencia.
- `@api.onchange('destination_dependence_id')` en `me.document_movement`:
  · Destino interno con config → user_id = default_responsible_id.
  · Destino externo o sin destino → user_id = False.
  · Destino interno sin config → user_id sin cambio.
  La lógica de poseedor (#027/#028/#029) no cambia: solo cambia cómo se popula
  user_id al crear el movimiento, no el comportamiento post-guardado.
  → `me/models/document_movement.py` `_onchange_destination_dependence_id`

**Uncertain / pending definition:**
- No existe validación de orden cronológico entre movimientos (descartado para MVP, ver #002).
- No existe estado actual del expediente derivado de los movimientos.
  (No hay campo `state` en el modelo.)
- `_legacy_backlog.md` lista el workflow de estados como `[IDEA]` — pendiente de definición.

**Nota de comportamiento esperado:**
- La pre-carga de `origin_dependence_id` consulta el estado persistido en base,
  no el estado transitorio de la grilla. Si un manager elimina un movimiento sin
  guardar y luego agrega uno nuevo, el origen pre-cargado puede no reflejar la
  eliminación pendiente. Comportamiento correcto: guardar antes de agregar.
  Irrelevante para `me.group_user` (sin `perm_unlink` sobre `me.document_movement`,
  ver #018).

**Clasificación interna/externa de dependencias (#021):**

Cada `tmc.dependence` tiene un campo `is_internal` (Boolean, default=False)
agregado por el módulo `me` vía `_inherit`. Las dependencias del Tribunal
están marcadas como `is_internal=True` en `me/data/dependence_data.xml`:
TMC, ME, VOC, FC, DAL, DAT, DCD, DAF, DIC, AFC, **ARCH** y **LEG** (12 en total).
Todo lo demás (DEM, CM, jurisdicciones municipales) queda como externo.

Esta clasificación alimenta `has_reentry` en `me.document_exp`:
- Salida institucional: movimiento con `destination_dependence_id.is_internal = False`
- Reingreso institucional: movimiento con `destination_dependence_id.is_internal = True`
  ocurrido después de al menos una salida previa en el mismo expediente.
- Los movimientos automáticos apuntan a TMC y ME (ambos internos), por lo que
  nunca generan salida ni reingreso falsos.

El campo `has_reentry` es stored computed y se recalcula automáticamente al
agregar movimientos o al cambiar `is_internal` en una dependencia.

**Nota de upgrade:**
En bases existentes actualizadas con `-u me`, `is_internal` puede no haberse aplicado
a las dependencias internas (el archivo de datos usa `noupdate="1"`, que bloquea la
actualización de registros ya presentes). En ese caso, `has_reentry` permanece en
False para todos los expedientes históricos. El filtro "Con Reingreso Institucional"
requiere que ambas condiciones estén saneadas: valores de `is_internal` correctos y
un recompute explícito de `has_reentry`. En una instalación nueva el comportamiento
es correcto sin intervención adicional.


--------------------------------------------------

## 6. Progresión de UI basada en is_origin_complete

El formulario de `me.document_exp` muestra campos progresivamente
según el estado de completitud de la Fase 1 del expediente.

### Pasos

**Fase 1 — siempre visible:**

1. El usuario ve `dependence_id`, `document_type_id` (readonly, visible al seleccionar dependence_id),
   `number`, `period`.
2. `computed_name` muestra "Unnamed Document" hasta que los 3 campos de Fase 1 estén completos.

**Fase 2 — visible cuando `is_origin_complete = True`:**

3. Cuando `dependence_id`, `number` y `period` están completos, `is_origin_complete` se vuelve `True`.
4. `computed_name` muestra el nombre generado (ej. `EXP-000001-DEM/2025`).
5. Se habilitan: `jurisdiction_dependence`, `source_dependence_id` (opcional, filtrado
   a hijos de la jurisdicción), `intake_date`, `main_topic_ids`, `document_object`,
   `date`, `external_key`, `fojas`.

**Fase 3 — pestaña de movimientos (visible cuando el registro está guardado):**

6. Cuando el registro tiene `id` (fue guardado), aparece el notebook con la pestaña "Movimientos".
7. La pestaña "Documentos Relacionados" permanece siempre invisible.

### Evidence

**Observed in code:**
- `is_origin_complete` se computa sobre 3 campos: `me/models/document_exp.py`
  (`dependence_id`, `number`, `period`)
- `is_valid` sigue existiendo pero NO controla la visibilidad — mide completitud funcional
  (5 campos: `dependence_id`, `document_type_id`, `number`, `period`, `jurisdiction_dependence`)
- `computed_name` depende de los mismos 3 campos que `is_origin_complete`
- Visibilidad del grupo Fase 2: `me/views/document_exp_views.xml` (`invisible="not is_origin_complete"`)
- Visibilidad del notebook: `me/views/document_exp_views.xml` (`invisible="not id"`)
- Tab "Documentos Relacionados" siempre invisible
- `document_topic_ids` siempre invisible

**Inferred:**
- El usuario puede completar los campos de Fase 1 sin guardar el registro.
  `is_origin_complete` se evalúa en tiempo real.
- Los campos de Fase 2 se habilitan antes de guardar, si Fase 1 está completa.

**Uncertain / pending definition:**
- No está definido qué ocurre si el usuario limpia un campo de Fase 1 después de haber completado
  campos de Fase 2. Los campos de Fase 2 desaparecerían de la vista pero los datos podrían persistir.


--------------------------------------------------

## 7. Edición de fecha (SQL bypass)

Cuando el usuario edita el campo `date` de un expediente existente,
el sistema no usa el ORM estándar para actualizar `tmc.document`.

### Pasos

1. El usuario edita el campo `date` en el formulario.
2. Al guardar, `write()` detecta el campo `date` en `vals` y lo extrae.
3. El resto de los campos del documento base se actualizan normalmente vía ORM (`self.document_id.write(document_vals)`).
4. La fecha se actualiza directamente en la tabla `tmc_document` via SQL:
   `UPDATE tmc_document SET date = %s WHERE id = %s`
5. Luego `super().write(vals)` se ejecuta sin el campo `date`.

### Evidence

**Observed in code:**
- Intercepción del campo `date` en `write()`: `me/models/document_exp.py:184`
- Actualización vía SQL directo: `me/models/document_exp.py:177–180`
- Separación de flujos (ORM vs SQL): `me/models/document_exp.py:182–200`

**Inferred:**
- El bypass existe para evitar la constraint `_check_date_not_future` definida en `tmc.document`.
  El comentario en el método lo confirma: "evitando la validación problemática".
- El SQL directo actualiza la tabla sin pasar por ningún evento ORM
  (`_write`, computed fields recompute, tracking).

**Uncertain / pending definition:**
- No está definido si el bypass de `_check_date_not_future` es intencional como regla de negocio
  (los expedientes de ME pueden tener fechas futuras) o es una solución temporal.
- No está evaluado el comportamiento en entornos multi-company o con extensiones que
  interceptan `cr.execute`.
- No está definido si otros campos de `tmc.document` con constraints similares
  necesitarían el mismo tratamiento.
