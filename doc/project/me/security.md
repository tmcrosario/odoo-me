# Seguridad — módulo `me` (Mesa de Entradas)

Baseline verificado contra `me/security/*` y el código (EPIC-001/TASK-002, 2026-06-19);
**revalidado tras `junco:EPIC-015` (commits `bfb1926` + `181d2e6`), 2026-07-15.**

**Insight central — la seguridad de `me` NO se lee del CSV.** Hay dos ejes distintos:

- **`write()`**: el ACL del CSV es deliberadamente **permisivo** (el operativo tiene
  `write`/`create`), pero la frontera real la imponen **guards imperativos en Python**, más
  estrictos que el CSV. Quien lea solo el CSV **sobrestima** lo que puede hacer un operativo.
- **`create()`**: **no tiene guard de grupo** — la frontera es el **ACL**, y como el `create()`
  corre **elevado** (`sudo()`, ver más abajo) ese ACL **debe chequearse explícitamente antes de
  elevar** (`self.check_access('create')`). Sin eso, la elevación lo saltea por completo.

> **Regla durable (aprendida en `junco:EPIC-015/TASK-003`):** *la elevación no exime del ACL del
> propio sistema*. Al elevar para escribir en otro sistema, hay que chequear primero el ACL del
> modelo propio contra el llamador real.

## Grupos (`me/security/me_groups.xml`)

Categoría `module_category_me` ("ME") + privilege `res_groups_privilege_me` (patrón Odoo 19).

**Postura (junco:EPIC-015, opción 1): ME edita ME y solo LEE GD (`tmc`).**

| Grupo (xmlid) | Nombre | Hereda (`implied_ids`) | Cmd | Notas |
| --- | --- | --- | --- | --- |
| `me.group_user` | User | `base.group_user` + `tmc.group_read_only` | `(6,0)` | Edita ME; **solo lee GD**. Antes heredaba `tmc.group_user` (escribía GD) |
| `me.group_manager` | Manager | `me.group_user` + `tmc.group_manager` | `(4,)` | Full-stack, sin cambios. `implied_by_ids = base.group_erp_manager` |
| `me.group_read_only` | Read Only | `base.group_user` + `tmc.group_read_only` | `(6,0)` | **No es standalone.** Es la base de lectura de la que cuelga `junco.group_user` |

**Por qué `(6,0)` y no `(4,)`:** `(6,0)` **reemplaza** el set de herencias — es lo que remueve
`tmc.group_user` de `me.group_user` al correr `-u me`. `(4,)` es **aditivo**: en un update dejaría
el grant viejo pegado (Odoo no revoca grupos ya materializados). `me.group_manager` sigue en `(4,)`
porque **no se le quita nada** (es inocuo, no es un defecto). `base.group_user` va explícito porque
los grupos read-only no encadenan a él.

> ⚠️ **Defecto conocido — `junco:EPIC-015/TASK-004`** (repo dueño: `odoo-junco`): si el usuario
> tiene cualquier grupo de JUNCO, el dropdown del privilegio **ME no ofrece «User»** (solo Read
> Only y Manager), porque `junco.group_user` implica `me.group_read_only` y el widget borra las
> opciones de menor nivel (`res_user_group_ids_field.js:154`); *Read Only* quedó por encima de
> *User* por un desempate por `id` (ambos rank 1, `sequence` 0).
> **Workaround**: asignar `me.group_user` desde Configuración → Grupos (o por ORM) hasta el fix.
> **La escalera actual NO es correcta** — no tomarla como referencia.

### Acoplamiento cross-sistema (entrante y saliente)

- **Saliente (ME → GD):** el operativo **lee** GD; **no escribe**. Las únicas escrituras a GD son
  **elevadas y acotadas** (tabla de `sudo()`).
- **Entrante (JUNCO → ME):** `junco.group_user` cuelga de **`me.group_read_only`** con `(6,0)`
  (`odoo-junco/junco/security/junco_groups.xml:27`) y `junco.group_manager` de `me.group_manager`.
  ⇒ **`me.group_read_only` es contrato cross-repo**: cambiarlo impacta a JUNCO — coordinar.
- La **regla del stack** ("cada `*.group_user` edita SU sistema y hereda solo LECTURA del de abajo")
  es **BR-016, gobernada en `odoo-junco`** (`odoo-junco/doc/project/security.md`). Acá se documenta
  **el lado ME**, no la regla entera.

> **Caveat de UI (verificado):** `tmc_menu` está gateado a `tmc.group_user,tmc.group_manager,
> base.group_system` (`odoo-tmc/tmc/views/tmc_menus.xml:7`) — **`tmc.group_read_only` no está**.
> ⇒ un operativo de ME tiene ACL de lectura sobre GD pero **no ve la app GD**. El fix vive en
> `odoo-tmc` (repo que ME no gobierna); decidido y **diferido** del lado junco.

## ACL — `me/security/ir.model.access.csv` (matriz CRUD)

El CSV **existe** y cubre los 2 modelos propios × 3 grupos.

| Modelo | Grupo | read | write | create | unlink |
| --- | --- | :-: | :-: | :-: | :-: |
| `me.document_exp` | `group_manager` | ✅ | ✅ | ✅ | ✅ |
| `me.document_exp` | `group_user` | ✅ | ✅ | ✅ | ❌ |
| `me.document_exp` | `group_read_only` | ✅ | ❌ | ❌ | ❌ |
| `me.document_movement` | `group_manager` | ✅ | ✅ | ✅ | ✅ |
| `me.document_movement` | `group_user` | ✅ | ✅ | ✅ | ❌ |
| `me.document_movement` | `group_read_only` | ✅ | ❌ | ❌ | ❌ |

`group_user` tiene `write`/`create` a nivel ORM pero **acotado por los guards de abajo**.
`unlink` solo para manager en ambos modelos.

## Record rules

**No hay `ir.rule` en `me`.** La seguridad a nivel de fila/operación NO se hace con record
rules: se hace con **guards imperativos en `write()`** (ver abajo). Es una decisión de diseño
a tener en cuenta al razonar la postura de seguridad.

## Guards de backend (la frontera real)

### `me.document_exp.write()` — guard al inicio del método (`me/models/document_exp.py`, ~l.623)
Si el usuario **no** es `me.group_manager` y **no** hay contexto `me_create_in_progress`:
- solo se permiten escrituras que sean **comandos de `document_movement_ids`** (alta/edición
  de movimientos, con sus propias reglas); cualquier otro campo → `AccessError`
  ("Existing expedientes can only be modified by an Intake Register manager.").
- **Canal EPIC-004 (`me_origin_from_junco`):** excepción restringida a exactamente
  `jurisdiction_dependence` / `source_dependence_id`, para que JUNCO complete el origen de un
  DEM vía `action_set_origin_from_junco()` (valida DEM-only + nomenclador, eleva con `sudo()`).
  No referencia grupos de `junco` (evita dependencia inversa); seguridad = validación interna
  + superficie mínima.

### `me.document_exp.create()` (`me/models/document_exp.py`, ~l.499)
**No tiene guard de grupo**: la frontera es el **ACL**, chequeado explícitamente
(`self.check_access('create')`) **antes** de elevar — ver la tabla de `sudo()` y la regla durable
del encabezado.

### `me.document_movement.write()` (`me/models/document_movement.py`, ~l.139)
Si el usuario **no** es manager (y no `me_create_in_progress`), al corregir un movimiento:
- debe ser el **último movimiento manual** (`_is_last_manual_movement()`) — si no, `AccessError`;
- debe ser el **poseedor** (`record.user_id == env.user`) — si no, `AccessError`;
- solo campos en `_OPERATOR_EDITABLE_FIELDS = {fojas, user_id, legajo_number}` — si no, `AccessError`;
- `legajo_number` solo si el destino es `LEG` — si no, `AccessError`.

### Reglas de poseedor (resumen #027/#028/#029)
- Solo el poseedor (`user_id` del último movimiento) registra un pase nuevo desde la UI; el
  alta de movimiento por no-poseedor se rechaza (guard en `me.document_exp.write()` rama
  `is_only_create_cmds`). Managers sin restricción.
- Corrección del último movimiento manual restringida por poseedor + campos editables (#028).
- `fojas` queda bloqueado post-creación salvo manager / campo editable del último movimiento (#018).

## `sudo()` — elevaciones deliberadas (fronteras de privilegio)

| Lugar | Por qué |
| --- | --- |
| **`create()` → `super(... .sudo()).create()`** (~l.547; `check_access` ~l.546; des-elevación ~l.550) | **junco:EPIC-015**: el operativo ya solo lee GD, pero el `_inherits` crea el `tmc.document` padre **dentro** de este `super()`. Se eleva para permitir el alta; se **des-eleva** de inmediato (`records.sudo(self.env.su)`) para que movimientos y demás corran con los permisos del usuario. **Precedido por `self.check_access('create')`**: la elevación saltearía el ACL de `me.document_exp` (`ir.model.access.check` corta por `env.su`) |
| `create()` → `raa.registry_aa.sudo().create()` (~l.563) | el alta en RAA es un efecto interno del sistema; el operador no necesita permisos en `raa` |
| `_set_main_topic_id()` / `_set_secondary_topic_id()` / `write()` → `document_id.sudo().write()` (~l.257 / 268 / 697) | campos delegados van a `tmc.document`; el operativo hereda `tmc.group_read_only` (solo `read` sobre `tmc.document`), así que sin `sudo` no podría. El guard de ME es la frontera |
| `action_set_origin_from_junco()` → `sudo().write()` (~l.437; def ~l.389) | da permiso ORM para escribir los 2 campos de origen; el canal `me_origin_from_junco` los acota en `write()` |

Todas son `sudo()` **acotadas**: a una operación puntual (las 3 últimas) o a un tramo con
des-elevación inmediata + chequeo previo de ACL (el `create()`).

## Caminos negativos (cubiertos por tests — ver `tests_plan.md`)

- **Permisos cross-sistema (junco:EPIC-015)** → `TestMeSecurity` (`me/tests/test_security.py`):
  el operativo hereda `tmc.group_read_only` y **no** `tmc.group_user`; crea expedientes (el padre
  se crea con el `create` elevado); **lee** `tmc.document` pero no lo escribe ni lo crea.
- **ACL del expediente bajo elevación** → `TestMeSecurity.test_me_read_only_cannot_create_expediente`:
  un lector no puede crear expedientes, y el test **discrimina** que el `AccessError` venga del ACL
  de `me.document_exp` (no del de `me.document_movement`, que lo enmascaraba).
- No-poseedor no puede registrar/corregir movimiento → `TestMovementPoseedor027`, `TestMovementCorrection028`.
- Operador no puede escribir campos arbitrarios del expediente / movimiento → guards (arriba);
  EPIC-004 verifica que un `me.group_user` no puede escribir `jurisdiction_dependence` por
  write crudo pero sí vía el método controlado (`TestDocumentExp`, bloque EPIC-004).
- Bloqueo de `fojas` y matriz de permisos → `TestFojasLock` (#018).

## ACL de modelos externos que `me` usa

- **`tmc.document`** (vía `_inherits`): el operativo hereda **`tmc.group_read_only`** → `1,0,0,0`
  (`odoo-tmc/tmc/security/ir.model.access.csv:10`): **solo lectura**. Toda escritura de ME sobre
  `tmc.document` (campos delegados y alta del padre) va por **`sudo()` acotado**. Solo
  `me.group_manager` alcanza `tmc.group_manager` (`1,1,1,1`) por herencia directa.
- Resto de `tmc.*` (`tmc.dependence` extendido, `tmc.document_type`, `tmc.dependence_order`):
  lectura cubierta por `tmc.group_read_only`.
- `raa.registry_aa`: el alta la hace `me` con `sudo()`; el operador no requiere ACL en `raa`.

> **Bypass registrado (deuda pre-existente, no huérfana):** `_update_document_date()`
> (`document_exp.py`, ~l.603; SQL crudo ~l.617) escribe `tmc.document` **por SQL directo**, esquivando
> ORM y ACL. **No la causó junco:EPIC-015** y no se rompe bajo la opción 1. Está parkeada como deuda de
> seguridad pre-existente en `odoo-junco/doc/project/brainstorming.md` → "Deuda de seguridad detectada
> (auditoría EPIC-015, 2026-07)", junto con `raa.group_manager` (que no hereda `tmc.group_manager`).
> Sigue siendo **pregunta abierta** (no hay decisión sobre si debe gobernarse), pero tiene dueño.
