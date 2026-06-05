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

Verificado contra el código de `odoo-junco` (`junco/models/process_expediente.py`,
`junco/models/purchase_process.py`):

| Tema | Estado | Dónde |
| --- | --- | --- |
| Modelado de la relación | ✅ Tabla intermedia `junco.process_expediente` con metadatos (`date_linked`, `linked_by`, `change_reason`, `decree_ref`, `notes`) | junco |
| Expediente vigente | ✅ `is_current` + constraint `_check_single_current` (máximo uno vigente) | junco |
| Historial | ✅ One2many `expediente_ids` + `date_linked` + `linked_by` + `has_expediente_history` | junco |
| Seguridad | ✅ ACL del modelo link para manager/user/read_only | junco |
| Exclusividad (exp. en >1 proceso) | ❌ Abierta — sin constraint que lo impida | junco |
| Anulación del vigente | ❌ Abierta — comportamiento no definido | junco |
| Evento que motiva la incorporación | ⚠️ Parcial — `change_reason` captura el motivo; `continuity_event_id` está como TODO | junco |

> Las decisiones que faltan son de negocio y se cierran **en JUNCO** (su EPIC-002),
> no en este repo.

## Contrato de `me` hacia JUNCO (lo único que obliga a este repo)

La responsabilidad de `me` frente a la integración es **pasiva**: mantener estable la
superficie pública que JUNCO ya consume de `me.document_exp`. Cualquier cambio a estos
campos (rename, semántica, eliminación) **rompe JUNCO** y debe coordinarse:

- `computed_name`
- `date`
- `dependence_id`
- `jurisdiction_dependence`
- `document_movement_ids`

Este contrato es una **restricción de entrada para EPIC-001** (baseline de `me`): el
inventario y cualquier refactor del baseline deben preservar estos campos o versionar
el cambio con JUNCO.

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
