# Arquitectura — módulo `me` (Mesa de Entradas)

> **Vigencia.** Este documento es la consolidación del *ME Architecture Analysis
> Report* original (snapshot de código del **2026-03-26**, versión 19.0.1.0.0
> post-migración Odoo 14). Es la columna vertebral de la arquitectura de `me`, pero
> **es parcialmente histórico**: las task cards #021–#030 introdujeron cambios que
> ya están reflejados en [`workflows.md`](workflows.md) y en
> [`_legacy_backlog.md`](_legacy_backlog.md) y que
> **superan** algunas afirmaciones de acá (p. ej. `is_origin_complete` reemplazó a
> `is_valid` para visibilidad; `me.document_movement` ya tiene `_sql_constraints` y
> checks de fecha; existen `current_holder_id`, `is_internal`/`has_reentry` y reglas
> de poseedor; `ir.model.access` definido para los modelos de `me`). Donde este doc
> y `workflows.md` discrepen, **`workflows.md` es más reciente**.
>
> La **reconciliación definitiva contra el código actual** es trabajo de **EPIC-001
> (baseline de mesa de entradas)**. No tratar las secciones marcadas como
> *Uncertain* como reglas cerradas.
>
> Docs hermanos: [`models.md`](models.md) · [`business_rules.md`](business_rules.md)
> · [`workflows.md`](workflows.md) · [`security.md`](security.md) ·
> [`tmc_base_reference.md`](tmc_base_reference.md).

---

## Metodología

Cada conclusión en este documento está clasificada en uno de tres niveles:

- **Observed in code** — comportamiento explícitamente visible en el código fuente
- **Inferred from implementation** — comportamiento probable deducido por estructura, relaciones o vistas, sin garantía definitiva
- **Uncertain / pending definition** — aspectos no demostrables con el código actual

Toda conclusión referencia, cuando es posible: archivo, modelo y método específico.

---

## 1. Propósito del módulo ME

**Observed in code:**
`me/__manifest__.py` describe el módulo como "TMC ME" con `_description = "Expediente Registry"` en `me/models/document_exp.py`.

El módulo `me` implementa el sistema de **Mesa de Entradas** del Tribunal Municipal de Cuentas. Su responsabilidad central es:

- Registrar expedientes administrativos como entidades propias dentro del sistema documental del TMC
- Vincular automáticamente cada expediente con el sistema de Registro de Actos Administrativos (`raa`)
- Registrar y preservar el historial de movimientos (routing) de cada expediente entre dependencias
- Proveer una interfaz de gestión de expedientes con visibilidad progresiva según el nivel de completitud del registro

**Inferred from implementation:**
El módulo actúa como **punto de ingreso** de documentos al sistema. El flujo automático creado en `create()` (`me/models/document_exp.py`, líneas 142–160) sugiere que todo expediente ingresa por una dependencia jurisdiccional externa, pasa por el TMC, y llega a la Mesa de Entradas. Este flujo inicial es fijo y automático.

**Observed in code:**
El módulo depende exclusivamente de `tmc` (`me/__manifest__.py`). No tiene dependencias de otros módulos de Odoo estándar más allá del módulo base implícito.

---

## 2. Modelos detectados

### 2.1 `me.document_exp`

**Archivo:** `me/models/document_exp.py`
**Clase:** `DocumentExp`
**Herencia:** `_inherits = {"tmc.document": "document_id"}` (herencia por delegación)

**Propósito:** Representa un expediente administrativo registrado en la Mesa de Entradas. Extiende el modelo documental base (`tmc.document`) mediante delegación, agregando campos y comportamiento específico del módulo ME.

#### Campos propios (definidos en `me.document_exp`)

| Campo | Tipo | Requerido | Notas |
|---|---|---|---|
| `document_id` | Many2one(`tmc.document`) | Sí | Enlace de delegación, `ondelete="cascade"` |
| `external_key` | Char | No | Clave externa usada por la Municipalidad |
| `jurisdiction_dependence` | Many2one(`tmc.dependence`) | Sí | Dependencia jurisdiccional del expediente |
| `fojas` | Integer | No | Número de fojas del expediente |
| `number` | Integer | Sí (reforzado) | Heredado de `tmc.document`, marcado `required=True` localmente |
| `allowed_dependence_ids` | Many2many(`tmc.dependence`) | No | Computed, sin dependencias declaradas |
| `is_valid` | Boolean | No | Computed: True si todos los campos clave están completos |
| `computed_name` | Char | No | Computed: nombre en formato `EXP-XXXXXX-ABR/AÑO` |
| `document_movement_ids` | One2many(`me.document_movement`) | No | Historial de movimientos del expediente |

**Observed in code:**
Hay un campo comentado en el código: `asunto` (Char, "Asunto"), `document_exp.py` líneas 38–41. No está activo.

#### Campos heredados por delegación desde `tmc.document`

**Observed in code** (`tmc/models/document.py`):

| Campo heredado | Tipo | Notas |
|---|---|---|
| `name` | Char (computed, stored) | Generado automáticamente por `tmc.document` |
| `dependence_id` | Many2one(`tmc.dependence`) | Requerido en base |
| `document_type_id` | Many2one(`tmc.document_type`) | Requerido en base |
| `period` | Selection | Año, requerido en base |
| `date` | Date | Fecha del documento |
| `document_object` | Char (max 250) | Objeto/referencia del documento |
| `main_topic_ids` | Many2many(`tmc.document_topic`) | Asuntos principales |
| `secondary_topic_ids` | Many2many(`tmc.document_topic`) | Asuntos secundarios |
| `document_topic_ids` | Many2many(`tmc.document_topic`) | Temas relacionados a la dependencia |
| `related_document_ids` | Many2many(`tmc.document`) | Documentos relacionados |
| `highlight_ids` | One2many(`tmc.highlight`) | Anotaciones/destacados |

#### Computed fields

**Observed in code** (`me/models/document_exp.py`):

- **`_compute_allowed_dependencies`** (línea 61–69)
  - `@api.depends()` sin argumentos — se calcula una sola vez al instanciar
  - Busca en `tmc.dependence` por `abbreviation in ['DEM', 'TMC', 'CM']`
  - Sin dependencias declaradas, el campo no se recalcula si cambian los registros de `tmc.dependence`

- **`_compute_is_valid`** (línea 71–81)
  - Depends: `dependence_id, document_type_id, number, period, jurisdiction_dependence`
  - Retorna `True` solo si los cinco campos están completos

- **`_compute_name`** (línea 83–91)
  - Depends: `dependence_id, document_type_id, number, period, jurisdiction_dependence`
  - Formato: `EXP-{number:06d}-{dependence_id.abbreviation}/{period}`
  - Usa la abreviatura de `dependence_id` (no de `jurisdiction_dependence`)
  - Default cuando incompleto: `"Documento Sin Nombre"`

#### Métodos

**Observed in code** (`me/models/document_exp.py`):

- **`_onchange_dependence`** (línea 93–108)
  - Limpia `document_type_id`
  - Si hay `dependence_id`, busca el tipo con `abbreviation='EXP'` y lo asigna automáticamente
  - Retorna domain para `document_type_id`: solo tipo con abreviatura `EXP`

- **`_onchange_document_data`** (línea 110–127)
  - Valida duplicados en `tmc.document` por: `dependence_id, document_type_id, number, period`
  - No incluye `jurisdiction_dependence` en la búsqueda de duplicados
  - Retorna un `warning`, no lanza error — el guardado no se bloquea desde la UI

- **`create(vals)`** (línea 129–161)
  - Extrae campos base: `dependence_id, document_type_id, number, period, date, document_object`
  - Crea `tmc.document` manualmente con esos campos
  - Llama a `super().create(vals)` con `document_id` ya asignado
  - Crea `raa.registry_aa` vinculado al `tmc.document` creado
  - Crea movimiento 1: `jurisdiction_dependence → TMC` (si existe TMC por abreviatura)
  - Crea movimiento 2: `TMC → Mesa de Entradas` (búsqueda por `name ilike 'Mesa de Entradas'`)
  - Los movimientos solo se crean si ambas dependencias existen; no hay error ni aviso si no se encuentran

- **`write(vals)`** (línea 182–200)
  - Extrae `date` de `vals` antes de procesarlo
  - Escribe campos base (`dependence_id, document_type_id, number, period, document_object`) directamente en `self.document_id`
  - Llama a `_update_document_date()` si `date` estaba presente
  - Llama a `super().write(vals)` con `date` ya removido de vals

- **`_update_document_date(date_val)`** (línea 163–180)
  - Convierte `date_val` a string `YYYY-MM-DD`
  - Ejecuta SQL directo: `UPDATE tmc_document SET date = %s WHERE id = %s`
  - Evita las validaciones del ORM de `tmc.document` sobre la fecha
  - El comentario en el código confirma que es intencional: "evitando la validación problemática"

- **`unlink()`** (línea 202–205)
  - Llama `record.document_id.unlink()` explícitamente antes de `super().unlink()`
  - El `ondelete="cascade"` de `document_id` ya propagaría la eliminación automáticamente; la llamada es redundante

#### Constraints

**Observed in code:** No hay `@api.constrains` ni `_sql_constraints` definidos en `me.document_exp`.
Las validaciones de unicidad y formato provienen del modelo base `tmc.document` (ver sección 2.3).

---

### 2.2 `me.document_movement`

**Archivo:** `me/models/document_movement.py`
**Clase:** `Movement`
**Herencia:** Ninguna (`models.Model` directo)

**Propósito:** Registra cada movimiento o transferencia de un expediente entre dependencias. Es el modelo de trazabilidad del sistema.

#### Campos

**Observed in code** (`me/models/document_movement.py`):

| Campo | Tipo | Requerido | Notas |
|---|---|---|---|
| `expediente_id` | Many2one(`me.document_exp`) | Sí | `ondelete="cascade"` |
| `date` | Datetime | Sí | Default: `fields.Datetime.now` |
| `origin_dependence_id` | Many2one(`tmc.dependence`) | No | Dependencia de origen |
| `destination_dependence_id` | Many2one(`tmc.dependence`) | No | Dependencia de destino |
| `user_id` | Many2one(`res.users`) | No | Default: usuario actual |

**Observed in code:** Hay un campo comentado: `notes` (Text, "Observaciones"), línea 19. No está activo.

**Observed in code:** No hay métodos, constraints, ni lógica de negocio definida en este modelo. Es un modelo de registro puro.

---

### 2.3 `tmc.document` (modelo base — repositorio `odoo-tmc`)

**Archivo:** `odoo-tmc/tmc/models/document.py`
**Herencia:** Ninguna (modelo base)

Este modelo provee la base documental del sistema. `me.document_exp` hereda de él por delegación.

**Constraints que aplican a `me.document_exp` por herencia:**

**Observed in code** (`tmc/models/document.py`):

- `_name_unique`: UNIQUE(`name`) — el nombre generado del documento debe ser único en el sistema
- `_check_date_not_future()`: la fecha no puede ser futura
- `_check_document_object_length()`: `document_object` máximo 125 caracteres (excepto tipo DIC)
- `_check_period()`: el período debe ser ≥ 1948 y no puede ser futuro
- `_check_number()`: validación de número según tipo de documento

**Inferred from implementation:**
El `write()` personalizado de `me.document_exp` usa SQL directo para actualizar la fecha (`_update_document_date`) precisamente para eludir la constraint `_check_date_not_future` del modelo base `tmc.document`. El comentario en el código lo confirma (`me/models/document_exp.py`, línea 164).

---

### 2.4 `raa.registry_aa` (módulo `raa` — contexto solamente)

**Archivo:** `raa/models/registry_aa.py`

**Observed in code** (`me/models/document_exp.py`, líneas 137–140):
Este modelo se crea automáticamente desde `me.document_exp.create()`:

```python
self.env["raa.registry_aa"].create({
    "document_id": record.document_id.id,
})
```

No debe modificarse. Se documenta aquí solo para describir la dependencia implícita.

---

## 3. Relaciones entre modelos

### Diagrama textual

```
tmc.document  (base, repositorio odoo-tmc)
    │
    │  _inherits (delegación via document_id)
    ▼
me.document_exp
    │                          │
    │  One2many                │  auto-crea en create()
    ▼                          ▼
me.document_movement       raa.registry_aa
    │
    │  Many2one (origin / destination)
    ▼
tmc.dependence
```

### Relaciones detalladas

**Observed in code:**

| Desde | Relación | Hacia | Campo | Archivo |
|---|---|---|---|---|
| `me.document_exp` | Many2one (delegación) | `tmc.document` | `document_id` | `document_exp.py:9` |
| `me.document_exp` | One2many | `me.document_movement` | `document_movement_ids` | `document_exp.py:57` |
| `me.document_exp` | Many2one | `tmc.dependence` | `jurisdiction_dependence` | `document_exp.py:28` |
| `me.document_exp` | Many2many (computed) | `tmc.dependence` | `allowed_dependence_ids` | `document_exp.py:17` |
| `me.document_movement` | Many2one | `me.document_exp` | `expediente_id` | `document_movement.py:7` |
| `me.document_movement` | Many2one | `tmc.dependence` | `origin_dependence_id` | `document_movement.py:13` |
| `me.document_movement` | Many2one | `tmc.dependence` | `destination_dependence_id` | `document_movement.py:16` |
| `me.document_movement` | Many2one | `res.users` | `user_id` | `document_movement.py:20` |
| `raa.registry_aa` | Many2one | `tmc.document` | `document_id` | `raa/models/registry_aa.py` |

**Observed in code** (por delegación `_inherits`):

`me.document_exp` hereda y expone directamente todos los campos de `tmc.document`, incluyendo:

- Many2one → `tmc.dependence` (`dependence_id`)
- Many2one → `tmc.document_type` (`document_type_id`)
- Many2many → `tmc.document_topic` (`main_topic_ids`, `secondary_topic_ids`, `document_topic_ids`)
- One2many → `tmc.highlight` (`highlight_ids`)
- Many2many → `tmc.document` (`related_document_ids`)

---

## 4. Flujo funcional inferido

### 4.1 Creación de un expediente

**Observed in code** (`me/models/document_exp.py`, método `create()`, líneas 129–161):

```
Usuario crea me.document_exp con campos mínimos
    (dependence_id, jurisdiction_dependence, number, period)
    │
    ├─ [Observed] Se crea tmc.document con: dependence_id, document_type_id,
    │             number, period, date, document_object
    │
    ├─ [Observed] Se crea raa.registry_aa vinculado al tmc.document
    │
    ├─ [Observed] Movimiento automático 1: jurisdiction_dependence → TMC
    │             (solo si TMC existe en tmc.dependence por abbreviation='TMC')
    │
    └─ [Observed] Movimiento automático 2: TMC → Mesa de Entradas
                  (solo si existe en tmc.dependence por name ilike 'Mesa de Entradas')
```

### 4.2 Visibilidad progresiva en la interfaz

**Observed in code** (`me/views/document_exp_views.xml`):

```
Estado inicial (is_valid = False):
    Visible: dependence_id, jurisdiction_dependence, document_type_id, number, period
    Oculto:  main_topic_ids, document_object, date, external_key, fojas, notebook

Estado completo (is_valid = True):
    También visible: main_topic_ids, document_object, date, external_key, fojas

Después del primer guardado (id existe):
    Visible: tab "Movimientos" con historial editable
    Siempre oculto: tab "Documentos Relacionados" (invisible="1" hardcodeado)
```

### 4.3 Movimientos posteriores

**Inferred from implementation:**
El usuario puede agregar movimientos manualmente desde el tab "Movimientos" (lista editable, `document_exp_views.xml`, línea 73). No hay lógica de negocio que valide origen/destino, secuencia o unicidad en movimientos adicionales. El modelo `me.document_movement` no tiene constraints propios.

### 4.4 Estados de workflow

**Uncertain / pending definition:**
No existe ningún campo `state` ni selection de estado en `me.document_exp` ni en `me.document_movement`. No hay flujo de aprobación, cierre, ni archivo implementado en el código actual. `docs/todo.md` registra esto como `[IDEA]`.

---

## 5. Lógica de negocio detectada

### 5.1 Asignación automática del tipo de documento

**Observed in code** (`me/models/document_exp.py`, `_onchange_dependence`, líneas 93–108):

Cuando el usuario selecciona una `dependence_id`, el sistema busca automáticamente el `tmc.document_type` con `abbreviation='EXP'` y lo asigna. El campo `document_type_id` queda restringido por domain a ese único tipo. El usuario no elige el tipo manualmente.

### 5.2 Validación de duplicados (solo warning, sin enforcement)

**Observed in code** (`me/models/document_exp.py`, `_onchange_document_data`, líneas 110–127):

Si ya existe un `tmc.document` con el mismo `dependence_id + document_type_id + number + period`, se muestra un warning. No es un error — el guardado no se bloquea. No hay backend constraint que prevenga el duplicado al guardar.

La búsqueda de duplicados no incluye `jurisdiction_dependence`. Dos expedientes con la misma combinación base pero distinta jurisdicción generarían warning pero podrían guardarse.

### 5.3 Filtro de dependencias permitidas (hardcodeado)

**Observed in code** (`me/models/document_exp.py`, línea 66–69; `me/views/document_exp_views.xml`, línea 41):

Las dependencias habilitadas para `dependence_id` están filtradas por las abreviaturas `['DEM', 'TMC', 'CM']`. Este filtro aparece tanto en el computed field como en el domain de la vista. Es estático en el código, no configurable.

### 5.4 Bypass de validación de fecha via SQL directo

**Observed in code** (`me/models/document_exp.py`, `_update_document_date`, líneas 163–180):

La actualización de `date` en `write()` se realiza con una query SQL directa sobre `tmc_document`, evitando el ORM y por ende la constraint `_check_date_not_future` de `tmc.document`. El comentario en el código confirma que es intencional.

### 5.5 Creación en cadena al guardar un expediente

**Observed in code** (`me/models/document_exp.py`, `create()`, líneas 129–161):

Un único `create()` del usuario desencadena la creación de:
1. Un registro `tmc.document`
2. Un registro `raa.registry_aa`
3. Hasta dos registros `me.document_movement`

Los movimientos automáticos son condicionales: solo se crean si las dependencias buscadas existen. Si no existen, no hay error ni aviso al usuario.

### 5.6 Eliminación en cascada

**Observed in code** (`me/models/document_exp.py`, `unlink()`, líneas 202–205):

Al eliminar un `me.document_exp`, se llama explícitamente a `record.document_id.unlink()`. Dado que `document_id` tiene `ondelete="cascade"`, esta eliminación ya ocurriría automáticamente; la llamada explícita es redundante pero no incorrecta.

**Inferred from implementation:**
La eliminación del `tmc.document` puede disparar la lógica condicional de `raa.registry_aa.unlink()`, que elimina el registro RAA solo si el documento base está "vacío". No hay garantía de que el registro RAA se elimine siempre junto con el expediente.

---

## 6. Supuestos de diseño detectados

### 6.1 Herencia por delegación sobre `tmc.document`

**Observed in code** (`me/models/document_exp.py`, línea 6):

```python
_inherits = {"tmc.document": "document_id"}
```

`me.document_exp` no es una tabla independiente con todos los campos. Usa `_inherits` (delegación), lo que implica que los datos base viven en la tabla `tmc_document` y los datos específicos del módulo ME viven en `me_document_exp`. Ambas tablas están siempre vinculadas por `document_id`.

**Inferred from implementation:**
Esta decisión permite reutilizar toda la lógica del sistema documental base sin duplicarla, y hace que `me.document_exp` sea reconocido automáticamente por el resto del sistema como un documento `tmc.document`.

### 6.2 `me.document_exp` ≠ `tmc.document_exp`

**Observed in code:**
El módulo `tmc` define su propio modelo `tmc.document_exp` que también hereda de `tmc.document` por delegación. El módulo `me` define `me.document_exp` que hereda directamente de `tmc.document`, **no** de `tmc.document_exp`. Son modelos distintos con propósitos distintos y tablas separadas.

**Inferred from implementation:**
`tmc.document_exp` parece ser la especialización genérica de tipo EXP en el sistema base. `me.document_exp` es la entidad de negocio específica de la Mesa de Entradas, con lógica propia de movimientos, RAA y jurisdicción.

### 6.3 `me.document_movement` como modelo de trazabilidad puro

**Observed in code** (`me/models/document_movement.py`):

El modelo no tiene lógica, validaciones ni métodos propios. Solo registra: quién movió el expediente, de dónde, a dónde y cuándo. La responsabilidad de la lógica de routing inicial está en `me.document_exp.create()`, no en `me.document_movement`.

### 6.4 Acoplamiento implícito `me` → `raa`

**Observed in code** (`me/models/document_exp.py`, línea 138):

```python
self.env["raa.registry_aa"].create(...)
```

El módulo `me` referencia directamente a `raa.registry_aa` en su lógica de `create()`. Sin embargo, `raa` no figura en las dependencias declaradas de `me/__manifest__.py`. El acoplamiento es real pero no está declarado formalmente.

---

## 7. Inconsistencias entre documentación y código

> **Reconciliación EPIC-001/TASK-001 (2026-06-19).** Las 8 inconsistencias quedan
> resueltas/obsoletas/reclasificadas (el código cambió desde el snapshot 2026-03-26):
>
> - **7.1 → obsoleta:** `me/ai-context.md` **ahora existe** (creado post-snapshot).
> - **7.2 → resuelta:** integración RAA implementada (`create()` l.560, `unlink()` l.711)
>   y documentada en `business_rules.md` ("Registro automático en RAA"). `docs/todo.md` migró.
> - **7.3 → resuelta:** movimientos automáticos documentados en `business_rules.md`.
> - **7.4 → reclasificada:** append-only sin enforcement absoluto, pero ACL (user sin
>   `unlink`) + guard `write()` (#028) lo acotan para operadores; documentado como principio
>   declarativo en `business_rules.md` + `security.md`.
> - **7.5 / 7.6 → resueltas:** `_inherits` (delegación, dos tablas) explícito en `models.md`.
> - **7.7 → obsoleta:** `document_topic_ids` ya no está en la vista (removido post-snapshot).
> - **7.8 → documentada:** el tab sigue invisible (ahora "Related Documents",
>   `document_exp_views.xml` l.115) → limitación conocida en `business_rules.md`.
>
> El texto original de cada ítem se conserva abajo como memoria del análisis.

### 7.1 `me/ai-context.md` — no existe

**Observed in code:**
El archivo `me/ai-context.md` es referenciado en múltiples documentos de planificación y en el prompt de análisis, pero **no existe en el repositorio**. No se puede evaluar su contenido.

### 7.2 `docs/todo.md` — integración RAA marcada como [IDEA] cuando ya está implementada

**Observed in code vs docs:**
`docs/todo.md` registra como `[IDEA]`: "How does document_exp link with registry_aa?". Sin embargo, esta integración **ya está implementada** en `me.document_exp.create()` (`document_exp.py`, líneas 137–140). La documentación no refleja el estado actual del código.

### 7.3 `docs/rules_business.md` — movimientos automáticos no documentados

**Observed in code vs docs:**
Las reglas de negocio documentan que "cada movimiento pertenece a un documento" y que los movimientos son append-only. Sin embargo, **no documentan** que dos movimientos iniciales se crean automáticamente en `create()`. Esta es una regla de negocio con impacto funcional significativo ausente en `rules_business.md`.

### 7.4 `docs/rules_business.md` — principio append-only sin enforcement técnico

**Observed in code:**
El principio "los movimientos son append-only" está documentado. Sin embargo, en el código no existe ningún constraint, override de `write()` o `unlink()`, ni regla de acceso que impida modificar o eliminar movimientos existentes. El principio es declarativo en la documentación, no técnico en el código.

### 7.5 `domain-rules/me/me_architecture.md` — diagrama conceptual no aclara el tipo de herencia

**Observed in code vs docs:**
El diagrama muestra `tmc.document → document_exp`, lo que es correcto en concepto. Sin embargo, no aclara que `me.document_exp` usa `_inherits` (delegación), no `_inherit` (extensión). La diferencia es técnicamente significativa: con delegación se crean dos registros en dos tablas distintas, y el comportamiento en queries y constraints difiere.

### 7.6 `docs/models.md` / `model_registry.md` — tipo de herencia no especificado

**Observed in code vs docs:**
La documentación describe `document_exp` como una "extensión" de `tmc.document` sin especificar el mecanismo. El código usa `_inherits`, no `_inherit`. Esta distinción debería estar documentada explícitamente.

### 7.7 `document_topic_ids` en vista — campo invisible sin documentación de propósito

**Observed in code** (`me/views/document_exp_views.xml`, línea 67):

```xml
<field name="document_topic_ids" invisible="1"/>
```

El campo aparece en la vista de forma pero siempre invisible. No hay documentación que explique por qué está presente pero oculto ni cuándo podría activarse.

### 7.8 Tab "Documentos Relacionados" — siempre invisible, sin documentación de estado

**Observed in code** (`me/views/document_exp_views.xml`, línea 89):

```xml
<page string="Documentos Relacionados" invisible="1">
```

El tab está hardcodeado como siempre invisible. No hay documentación que explique si esto es temporal, una funcionalidad pendiente, o una decisión deliberada.

---

## 8. Aspectos inciertos

> **Reconciliación EPIC-001/TASK-001 (2026-06-19).** Estado de los 8 inciertos:
>
> - **8.1 → reclasificado:** sigue sin campo `state`; es **limitación conocida**
>   (`business_rules.md`), no incierto. Agregar estados es decisión de producto pendiente.
> - **8.2 → reclasificado:** `N/A` mientras no haya estados (atado a 8.1).
> - **8.3 → resuelto:** `dependence_id` = origen del expediente (DEM/TMC/CM); `jurisdiction_dependence`
>   = jurisdicción/secretaría. Documentado en `business_rules.md` (regla multi-año, cesión DEM/EPIC-004).
> - **8.4 → resuelto/documentado:** si no existe "Mesa de Entradas", el 2º movimiento se omite
>   sin aviso → limitación conocida (`business_rules.md`) + gap de test (`tests_plan.md` #5).
> - **8.5 → resuelto:** `ir.model.access.csv` **existe** (TASK-002, `security.md`).
> - **8.6 → resuelto:** `allowed_dependence_ids` es **artefacto muerto** (computed pero sin
>   referencia en vistas/código; la vista usa domain hardcodeado). Candidato a remoción (task aparte).
> - **8.7 → reclasificado:** el "quién agrega/corrige movimientos" está resuelto (guards #027/#028,
>   `security.md`); el routing/continuidad entre movimientos sigue sin reglas (limitación conocida).
> - **8.8 → riesgo abierto:** `raa` es dependencia **implícita no declarada** en el manifest
>   (acoplamiento deliberado, pero `create()` siempre crea `raa.registry_aa`). Misma clase que el
>   `tmc_data` ya corregido → evaluar declararla (requiere aprobación de deps).
>
> El texto original de cada ítem se conserva abajo como memoria del análisis.

Los siguientes aspectos no están claramente definidos en el código actual y no deben asumirse:

### 8.1 Estados del expediente

**Uncertain / pending definition:**
No existe campo `state` ni lógica de apertura/cierre/archivo. `docs/todo.md` registra esto como `[IDEA]` sin decisión tomada.

### 8.2 Restricciones de edición por estado

**Uncertain / pending definition:**
No hay lógica que restrinja la edición de un expediente según su estadio en el proceso. No se puede inferir qué campos deberían ser readonly en qué momento, más allá de lo que controla `is_valid`.

### 8.3 Propósito diferencial de `jurisdiction_dependence` vs `dependence_id`

**Uncertain / pending definition:**
Ambos campos apuntan a `tmc.dependence`. La distinción conceptual está parcialmente en el `help` de cada campo. El flujo automático usa `jurisdiction_dependence` como origen del primer movimiento, pero no está documentado en qué otros contextos se diferencia de `dependence_id` ni qué restricciones aplican a cada uno.

### 8.4 Comportamiento cuando `Mesa de Entradas` no existe como dependencia

**Uncertain / pending definition:**
El segundo movimiento automático busca la dependencia por `name ilike 'Mesa de Entradas'` (`document_exp.py`, línea 143). Si esa dependencia no existe en la base de datos, el movimiento simplemente no se crea sin ningún error ni aviso. El comportamiento esperado en ese escenario no está definido.

### 8.5 Reglas de acceso al modelo (`ir.model.access.csv`)

**Uncertain / pending definition:**
No existe un archivo `ir.model.access.csv` en `me/security/`. No está claro si las reglas de acceso son provistas por el módulo `tmc`, si están ausentes, o si están implementadas de otra forma. En ausencia de reglas explícitas, el comportamiento de Odoo puede variar por versión.

### 8.6 Uso funcional de `allowed_dependence_ids`

**Uncertain / pending definition:**
El campo `allowed_dependence_ids` es computed con `@api.depends()` vacío (`document_exp.py`, línea 61). En la vista, el domain de `dependence_id` está duplicado y hardcodeado. No está claro si `allowed_dependence_ids` tiene un uso funcional activo o es un artefacto de diseño previo sin conexión real con la vista.

### 8.7 Reglas de negocio de routing de movimientos posteriores

**Uncertain / pending definition:**
Más allá de los dos movimientos automáticos iniciales, no hay reglas de negocio que definan cómo, quién puede agregar movimientos, ni qué dependencias son válidas como origen o destino en movimientos adicionales.

### 8.8 Impacto real de la dependencia `raa` no declarada en manifest

**Uncertain / pending definition:**
`me/__manifest__.py` no lista `raa` como dependencia. `me.document_exp.create()` crea registros de `raa.registry_aa`. El impacto en instalaciones donde `raa` no esté presente no está documentado ni hay manejo de error para ese caso.

---

## 9. Impacto para la migración a Odoo 19

### 9.1 [RESUELTO] Sintaxis `<list>` en vistas

**Observed in code** (`me/views/document_exp_views.xml`, líneas 8 y 73):

Las vistas usan `<list>`. La acción usa `view_mode="list,form"`. La migración de nomenclatura de vistas ya está aplicada.

### 9.2 [RESUELTO] Sintaxis inline de visibilidad

**Observed in code** (`me/views/document_exp_views.xml`):

Las vistas usan sintaxis Odoo 17+:
```xml
invisible="not dependence_id"
invisible="not is_valid"
invisible="not id"
```
No se usa la sintaxis antigua `attrs="{'invisible': [...]}"`. Ya migrado.

### 9.3 [PENDIENTE DE VERIFICAR] `name_get()` deprecado en modelos base

**Inferred from implementation** (`tmc/models/category.py`):

El modelo base `tmc.category` implementa `name_get()`. Este método fue deprecado en Odoo 17 en favor de `_compute_display_name()`. El impacto en `me` es indirecto, pero puede generar warnings o comportamiento inesperado en `tmc.document_topic` y `tmc.hr.office`, que son usados en `me.document_exp`.

### 9.4 [RIESGO] SQL directo en `write()`

**Observed in code** (`me/models/document_exp.py`, `_update_document_date`, línea 177):

```python
self.env.cr.execute(
    "UPDATE tmc_document SET date = %s WHERE id = %s",
    (date_str, self.document_id.id)
)
```

El SQL directo puede:
- No invalidar el caché del ORM de Odoo 19
- Omitir hooks del framework (computed stores, tracking, audit log)
- Comportarse de forma impredecible si la tabla `tmc_document` cambia de nombre o estructura

### 9.5 [RIESGO] Búsqueda por nombre literal en `create()`

**Observed in code** (`me/models/document_exp.py`, línea 143):

```python
mesa_entrada_dependence = self.env['tmc.dependence'].search(
    [('name', 'ilike', 'Mesa de Entradas')], limit=1
)
```

Esta búsqueda depende del nombre exacto de una dependencia en la base de datos. Si el nombre cambia, el movimiento automático no se crea sin ningún error. Es un punto de fragilidad operativa, no relacionado con la versión de Odoo.

### 9.6 [PENDIENTE DE VERIFICAR] Ausencia de `ir.model.access.csv`

**Observed in code:**
El módulo `me` no tiene archivo de acceso. En Odoo 19 el framework puede ser más estricto en el chequeo de permisos. Verificar si el módulo `tmc` define accesos para los modelos de `me`, o si el archivo debe crearse.

### 9.7 [RIESGO] Dependencia de `raa` no declarada en manifest

**Observed in code** (`me/__manifest__.py`, `me/models/document_exp.py`):

`raa` no está en las dependencias del manifest de `me`, pero se referencia directamente en `create()`. En Odoo 19, si `raa` no está instalado, la carga del módulo puede fallar o producir errores en tiempo de ejecución.

---

## 10. Recomendaciones para documentación

Las siguientes actualizaciones alinearían la documentación con el código real. No implican cambios de código.

### 10.1 Crear `me/ai-context.md`

El archivo es referenciado en múltiples lugares pero no existe. Debería crearse describiendo:
- Propósito del módulo ME
- Modelos principales y sus responsabilidades
- Flujo automático en `create()` (tmc.document + raa.registry_aa + 2 movimientos)
- Restricciones no obvias: filtro DEM/TMC/CM, búsqueda de Mesa de Entradas por nombre
- Diferencia entre `me.document_exp` y `tmc.document_exp`

### 10.2 Actualizar `docs/models.md`

- Especificar que `me.document_exp` usa `_inherits` (delegación), no `_inherit` (extensión)
- Listar campos heredados desde `tmc.document` que el módulo ME utiliza
- Documentar el campo `computed_name` y su formato exacto: `EXP-{number:06d}-{dependence_abbr}/{period}`
- Documentar el campo `is_valid` y sus cinco dependencias
- Aclarar la diferencia entre `me.document_exp` y `tmc.document_exp`

### 10.3 Actualizar `docs/rules_business.md`

- Documentar los dos movimientos automáticos creados en `create()`
- Documentar que la validación de duplicados es solo un warning (no bloquea el guardado)
- Documentar que el filtro de dependencias para `dependence_id` está hardcodeado: `['DEM', 'TMC', 'CM']`
- Aclarar que el principio append-only de movimientos no tiene enforcement técnico actualmente
- Documentar la integración automática con `raa.registry_aa` al crear un expediente

### 10.4 Actualizar `domain-rules/me/me_architecture.md`

- Agregar nota sobre herencia por delegación (`_inherits`) vs extensión (`_inherit`)
- Describir la relación entre `me.document_exp` y `tmc.document_exp` (son modelos distintos)
- Documentar el estado de los tabs ocultos: "Documentos Relacionados" y `document_topic_ids`

### 10.5 Actualizar `docs/todo.md`

- Marcar como `[DONE]` la integración con `raa.registry_aa` (ya implementada en `create()`)
- Agregar como `[TODO]` la creación de `ir.model.access.csv` si se confirma que falta
- Agregar como `[TODO]` la formalización del principio append-only con constraint técnico
- Agregar como `[TODO]` la definición del comportamiento cuando `Mesa de Entradas` no existe
- Agregar como `[TODO]` declarar `raa` como dependencia en `me/__manifest__.py`

---

*Las secciones 1–10 provienen del análisis de solo lectura original. No proponen
cambios de código ni refactors. Fuente primaria: código del módulo `me`.*

---

## 11. Capas del sistema y boundaries

> Consolidado desde el antiguo `docs/architecture_diagram.md`. Relaciones observadas
> en código.

```
    ┌─────────────────────────────────────┐
    │   Base Document System (odoo-tmc)   │
    │   tmc.document / tmc.dependence /    │
    │   tmc.document_type                  │
    └──────────────────┬──────────────────┘
                       │ _inherits (delegación) — document_id → tmc.document
                       ▼
    ┌─────────────────────────────────────┐
    │         ME Module (odoo-me)         │
    │   me.document_exp                   │
    │        │ One2many                   │
    │        ▼                            │
    │   me.document_movement              │
    └──────────────────┬──────────────────┘
                       │ auto-creado en create() — document_id → tmc.document
                       ▼
    ┌─────────────────────────────────────┐
    │        RAA Module (odoo-me)         │
    │   raa.registry_aa                   │
    │   (read-only desde la óptica de ME) │
    └─────────────────────────────────────┘
```

**Boundaries de módulo:**

- **ME (`me/`)** — gestiona el ingreso de expedientes. Owns: `me.document_exp`,
  `me.document_movement`. Depende de `tmc.document`, `tmc.dependence`,
  `tmc.document_type`. Usa implícitamente `raa.registry_aa` (**no declarado** en
  `me/__manifest__.py`).
- **RAA (`raa/`)** — registro de actos administrativos. Owns: `raa.registry_aa`
  (UNIQUE en `document_id`). Se lee/crea desde ME en `create()`; **no se modifica
  desde ME**. Ver [`../raa/architecture.md`](../raa/architecture.md).
- **Base TMC (`odoo-tmc`, repo externo)** — provee `tmc.document`/`tmc.dependence`/
  `tmc.document_type`. Define `_check_date_not_future`, que `me.document_exp` evita
  vía SQL directo. Solo lectura. Ver [`tmc_base_reference.md`](tmc_base_reference.md).

> **Acoplamiento implícito (riesgo):** `me.document_exp.create()` llama a
> `self.env["raa.registry_aa"].create(...)` pero `raa` no figura en las dependencias
> del manifest de `me`. Si `raa` no está instalado, `create()` falla en runtime.
> (`me/models/document_exp.py:138`).

## 12. Principios de arquitectura

> Consolidado desde el antiguo `domain-rules/me/me_architecture.md`.

- **Single source of truth** — cada concepto del dominio tiene una representación
  canónica.
- **Extensión sobre duplicación** — ME extiende el sistema documental base en vez de
  crear modelos de documento duplicados.
- **Separación de responsabilidades** — la lógica de negocio vive en los modelos;
  las vistas definen la UI; la documentación describe las reglas del dominio.
- **Comportamiento predecible** — el routing y la trazabilidad deben comportarse de
  forma consistente.
- **Seguridad de desarrollo asistido por IA** — inspeccionar modelos existentes
  antes de crear; extender la arquitectura existente; no inventar comportamiento; lo
  no claro se marca como *pending definition* (ver `AGENTS.md`).
