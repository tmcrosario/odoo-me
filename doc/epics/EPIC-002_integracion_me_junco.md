# EPIC-002 — Integración ME ↔ JUNCO (proceso licitatorio)

Estado: Gobernada en `odoo-junco` (acá: solo contrato de campos + decisión #4 parkeada)
Riesgo global en `me`: bajo (no se implementa lógica de integración en este repo)
Módulo: `me` (consumido por `junco`, repo `odoo-junco`)
Owner: `odoo-junco`

## Dueño y dirección del acoplamiento

**La integración se implementa y documenta en `odoo-junco`, no acá.** `junco` depende
de `me` (`__manifest__.py: depends = ["tmc", "me"]`); `me` **no** referencia a `junco`
ni puede hacerlo con dependencia dura (sería circular). Por eso toda la lógica de la
relación proceso↔expedientes vive del lado JUNCO.

- Épica dueña: `odoo-junco/doc/epics/EPIC-002_integracion_junco_me.md` (+
  `odoo-junco/doc/tasks/EPIC-002/`).
- Este documento queda como **puntero**: registra qué espera JUNCO de `me` y la única
  decisión que podría tocar `me`. **No abrir tasks de integración en `odoo-me`.**

## Estado real (AS-IS, ya implementado en JUNCO)

> ⚠️ **Snapshot histórico, no fuente de verdad.** Describe a JUNCO tal como se relevó; lo vigente
> está en `odoo-junco/doc/epics/EPIC-002_integracion_junco_me.md`, que figura **Done** y lleva una
> corrección de EPIC-014: **un proceso = un expediente** (el vínculo multi-expediente con
> vigencia e históricos no se materializó). Esta tabla no se mantiene desde `me`.

Verificado contra el código de `odoo-junco` (`junco/models/process_expediente.py`,
`junco/models/purchase_process.py`):

| Tema | Estado | Dónde |
| --- | --- | --- |
| Modelado de la relación | ✅ Tabla intermedia `junco.process_expediente` con metadatos (`date_linked`, `linked_by`, `change_reason`, `decree_ref`, `notes`) | junco |
| Expediente vigente | ✅ `is_current` + constraint `_check_single_current` (máximo uno vigente) | junco |
| Historial | ⚠️ Superado por junco:EPIC-014 — One2many `expediente_ids` + `date_linked` + `linked_by` existen, pero el historial multi-expediente no se usa (un proceso = un expediente). `has_expediente_history` **no existe** en el código de junco | junco |
| Seguridad | ✅ ACL del modelo link para manager/user/read_only | junco |
| Exclusividad (exp. en >1 proceso) | ❌ Abierta — sin constraint que lo impida | junco |
| Anulación del vigente | ❌ Abierta — comportamiento no definido | junco |
| Evento que motiva la incorporación | ⚠️ Parcial — `change_reason` captura el motivo; `continuity_event_id` está como TODO | junco |

> Las decisiones que faltan son de negocio y se cierran **en JUNCO**, no en este repo. Ojo: la
> EPIC-002 de junco ya está cerrada, así que el estado actual de las filas ❌/⚠️ de arriba se
> consulta en el repo de junco (no está relevado acá).

## Contrato de `me` hacia JUNCO (lo único que obliga a este repo)

La responsabilidad de `me` frente a la integración es **pasiva**: mantener estable la
superficie pública que JUNCO ya consume de `me.document_exp`. Cualquier cambio a esta
superficie (rename, semántica, firma, eliminación) **rompe JUNCO** y debe coordinarse.

Relevado en `odoo-junco/junco/` (código, vistas y tests) el 2026-10-02:

**Campos que JUNCO lee** de `me.document_exp`:

- `computed_name`, `date`, `document_object`, `intake_date`
- `dependence_id`, `jurisdiction_dependence`, `source_dependence_id`
- `main_topic_id`, `main_topic_ids`, `secondary_topic_id` (JUNCO deriva el tipo de proceso
  del tema/subtema y filtra la elegibilidad por tema principal)
- `document_id` (acceso al `tmc.document` por `_inherits`; lo usa el wizard de la Junta)

`computed_name` es un computed **sin `store` ni `search`**: JUNCO solo lo lee. No asumir que se
puede usar en un dominio (`search` directo sobre ese campo lanza `ValueError`).

**Método que JUNCO llama:** `action_set_origin_from_junco(jurisdiction_id, source_id=False)`.
Firma, idempotencia y alcance (solo DEM; rechaza Notas con `UserError`) son parte del contrato.

**Alta por ORM:** los tests de JUNCO crean expedientes con `dependence_id`, `document_type_id`,
`number`, `period`, `date`, `intake_date`, `document_object`, `main_topic_ids`,
`secondary_topic_ids` y, en algunos, `jurisdiction_dependence` y `source_dependence_id`. Volver
obligatorio otro campo, o quitar uno de estos, rompe esa suite.

**Comportamiento:** ME rechaza con `ValidationError` una licitación sin subtema (JUNCO lo asserta
en su suite) — ver `EPIC-004/TASK-005` y `business_rules.md`.

**Relaciones y seguridad:**

- JUNCO apunta a `me.document_exp` con `junco.process_expediente.expediente_id`
  (`ondelete='restrict'`: **no se puede borrar un expediente vinculado a un proceso**; verificado
  2026-10-02: el `unlink()` falla con `RestrictViolation` de PostgreSQL, no con un mensaje de usuario) y con
  `predecessor_expediente_ids` (many2many).
- Los grupos de JUNCO cuelgan de los de ME: `junco.group_read_only`/`group_user` implican
  `me.group_read_only` y `junco.group_manager` implica `me.group_manager` — ver `security.md`.

**Ya no forma parte del contrato:** `document_movement_ids` (figuraba antes; JUNCO no lo
referencia en código, vistas ni tests).

Este contrato es una **restricción para cualquier refactor de `me`** (rige desde EPIC-001): hay
que preservar la superficie o versionar el cambio con JUNCO. Para volver a relevarlo:
`grep -rhoE "(expediente_id|current_expediente_id|new_exp|exp)\.[a-z_]+" junco --include=*.py --exclude-dir=tests`
desde `odoo-junco/`.

## Única decisión que podría tocar `me` (parkeada)

**#4 — Visibilidad desde ME.** Si en algún momento se quiere que el form del expediente
en ME muestre a qué proceso de JUNCO pertenece:

- está **bloqueado por arquitectura**: `me` no puede importar `junco` (dependencia
  circular);
- requeriría un **módulo puente** o un computed sin dependencia de manifest;
- es una **decisión de UX/negocio aún no tomada**.

**Default actual: no se implementa.** La relación se ve desde JUNCO. Si se reabre,
se trata como épica/spec aparte (escala a L por tocar la frontera entre módulos).

## Reglas / decisiones durables

- No inventar reglas de negocio: las decisiones abiertas (exclusividad, anulación del
  vigente, `continuity_event_id`) se cierran **en JUNCO** con el usuario.
- No abrir trabajo de integración en `odoo-me`. Si surge necesidad en `me`, es solo la
  decisión #4 y se evalúa como épica nueva.
- No romper el contrato de campos consumidos por JUNCO sin coordinar.

## Cierre de épica (lado `me`)

Esta épica no produce implementación en `odoo-me`. Se considera **encaminada** una vez
que: (a) este puntero queda registrado, (b) el contrato de campos está reflejado como
restricción en EPIC-001, y (c) la decisión #4 permanece parkeada o se promueve a épica
propia. El avance funcional se mide en `odoo-junco`.
