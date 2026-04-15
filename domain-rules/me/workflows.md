# Módulo ME — Workflows

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

6. El usuario completa `jurisdiction_dependence` e `intake_date` (ambos obligatorios).
   Opcionalmente, completa `source_dependence_id` ("Repartición"), cuyas opciones
   están filtradas a las dependencias hijas de `jurisdiction_dependence` según el
   nomenclador (`tmc.dependence_order`). Al cambiar `jurisdiction_dependence`,
   `source_dependence_id` se limpia automáticamente.
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

1. `super().create(vals_list)` es invocado con los campos del expediente en `vals`.
2. El mecanismo `_inherits` de Odoo detecta los campos del padre
   (`dependence_id`, `document_type_id`, `number`, `period`, `date`, `document_object`)
   y crea automáticamente el registro `tmc.document`.
3. Odoo asigna el `document_id` resultante al registro `me.document_exp`.
4. El registro `me.document_exp` queda creado y vinculado al `tmc.document`.

### Evidence

**Observed in code:**
- Llamada a `super().create()`: `me/models/document_exp.py:135`
- Mecanismo `_inherits`: `me/models/document_exp.py:6`

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
- Creación de `raa.registry_aa`: `me/models/document_exp.py:137–140`
- Campo `document_id` pasado al registro RAA: `me/models/document_exp.py:139`
- Constraint UNIQUE en `raa.registry_aa.document_id`: `raa/models/registry_aa.py:52–55`

**Inferred:**
- Si `raa` no está instalado, la llamada `self.env["raa.registry_aa"]` falla en runtime.
  `raa` no está declarado como dependencia en `me/__manifest__.py`.
  Ver también: `docs/architecture_diagram.md` — sección IMPORTANT.

**Uncertain / pending definition:**
- No está definido qué ocurre si `raa.registry_aa` ya existe para ese `document_id`
  (constraint UNIQUE activa). El código no maneja ese caso explícitamente.
- No está definido si la creación en RAA es intencional como paso de negocio
  o es un efecto secundario de la arquitectura.


--------------------------------------------------

## 4. Inicialización de movimientos automáticos (sub-paso de Workflow 1)

Ocurre dentro de `me.document_exp.create()` después del paso RAA.
Crea dos movimientos automáticos que registran la trayectoria inicial del expediente.

### Pasos

**Movimiento 1 — Jurisdicción → TMC:**

1. El sistema busca `tmc.dependence` con `abbreviation = 'TMC'`.
2. Si existe `jurisdiction_dependence` en el expediente y existe TMC, crea un movimiento:
   - origen: `jurisdiction_dependence`
   - destino: `tmc.dependence (TMC)`
   - fecha: `Datetime.now()`
   - usuario: usuario activo (`self.env.uid`)

**Movimiento 2 — TMC → Mesa de Entradas:**

3. El sistema busca `tmc.dependence` con `abbreviation = 'ME'`.
4. Si existen ambas dependencias (TMC y Mesa de Entradas), crea un segundo movimiento:
   - origen: `tmc.dependence (TMC)`
   - destino: `tmc.dependence (Mesa de Entradas)`
   - fecha: `Datetime.now()`
   - usuario: usuario activo

### Evidence

**Observed in code:**
- Búsqueda de TMC: `me/models/document_exp.py:142`
- Búsqueda de Mesa de Entradas por nombre: `me/models/document_exp.py:143`
- Movimiento 1 (jurisdicción → TMC): `me/models/document_exp.py:144–151`
- Movimiento 2 (TMC → Mesa de Entradas): `me/models/document_exp.py:153–160`
- Ambos movimientos son condicionales — no se crean si las dependencias no existen.

**Inferred:**
- Si `tmc.dependence (TMC)` no existe en la base de datos, ninguno de los dos movimientos se crea sin error.
- Si `Mesa de Entradas` no existe (o su nombre difiere), solo se crea el movimiento 1.

**Uncertain / pending definition:**
- La búsqueda de `Mesa de Entradas` usa `ilike` (búsqueda parcial, case-insensitive).
  Si existen múltiples dependencias con ese nombre en el nombre, se usará la primera encontrada (`limit=1`).
  No está definido si esto es correcto o un riesgo.
- No está definido si la ausencia de estos movimientos es un estado válido del expediente.
- No hay constraint que garantice que estos movimientos existan en el expediente.


--------------------------------------------------

## 5. Routing manual de expedientes (movimientos posteriores)

Después de creado el expediente, el usuario puede registrar movimientos adicionales
desde la pestaña "Movimientos" en el formulario.

### Pasos

1. El usuario abre el expediente existente.
2. Navega a la pestaña "Movimientos" (visible solo cuando el registro está guardado).
3. Agrega un nuevo movimiento en la lista editable:
   - `date` (requerido, default: ahora)
   - `origin_dependence_id` (requerido)
   - `destination_dependence_id` (requerido)
   - `user_id` (default: usuario activo)
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

**Uncertain / pending definition:**
- No existen reglas de transición definidas en el código.
  Cualquier combinación origen/destino es válida (solo se exige que ambos existan).
- No existe validación de orden cronológico entre movimientos (descartado para MVP, ver #002).
- No existe estado actual del expediente derivado de los movimientos.
  (No hay campo `state` en el modelo.)
- No está definido si el usuario puede editar o eliminar movimientos existentes.
  El modelo no tiene restricciones que lo impidan.
- `docs/todo.md` lista el workflow de estados como `[IDEA]` — pendiente de definición.


--------------------------------------------------

## 6. Progresión de UI basada en is_origin_complete

El formulario de `me.document_exp` muestra campos progresivamente
según el estado de completitud de la Fase 1 del expediente.

### Pasos

**Fase 1 — siempre visible:**

1. El usuario ve `dependence_id`, `document_type_id` (readonly, visible al seleccionar dependence_id),
   `number`, `period`.
2. `computed_name` muestra "Documento sin nombre" hasta que los 3 campos de Fase 1 estén completos.

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
