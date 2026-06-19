# Seguridad — módulo `me` (Mesa de Entradas)

Baseline verificado contra `me/security/*` y el código (EPIC-001/TASK-002, 2026-06-19).
**Insight central:** el ACL del CSV es deliberadamente **permisivo** (operadores tienen
`write`/`create`), pero la seguridad efectiva la imponen **guards en Python** (`write()` de
ambos modelos) — más estrictos que el CSV. Quien lea solo el CSV subestima la postura real.

## Grupos (`me/security/me_groups.xml`)

Categoría `module_category_me` ("ME") + privilege `res_groups_privilege_me` (patrón Odoo 19).

| Grupo (xmlid) | Nombre | Hereda (`implied_ids`) | Notas |
| --- | --- | --- | --- |
| `me.group_user` | User | `tmc.group_user` | Registra y gestiona expedientes |
| `me.group_manager` | Manager | `me.group_user` + `tmc.group_manager` | Acceso completo; `implied_by_ids = base.group_erp_manager` (ERP Manager ⇒ ME Manager) |
| `me.group_read_only` | Read Only | — (standalone) | Solo lectura |

## ACL — `me/security/ir.model.access.csv` (matriz CRUD)

§8.5 **resuelto**: el CSV **existe** y cubre los 2 modelos propios × 3 grupos.

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

### `me.document_exp.write()` (`me/models/document_exp.py`, ~l.539)
Si el usuario **no** es `me.group_manager` y **no** hay contexto `me_create_in_progress`:
- solo se permiten escrituras que sean **comandos de `document_movement_ids`** (alta/edición
  de movimientos, con sus propias reglas); cualquier otro campo → `AccessError`
  ("Existing expedientes can only be modified by an Intake Register manager.").
- **Canal EPIC-004 (`me_origin_from_junco`):** excepción restringida a exactamente
  `jurisdiction_dependence` / `source_dependence_id`, para que JUNCO complete el origen de un
  DEM vía `action_set_origin_from_junco()` (valida DEM-only + nomenclador, eleva con `sudo()`).
  No referencia grupos de `junco` (evita dependencia inversa); seguridad = validación interna
  + superficie mínima.

### `me.document_movement.write()` (`me/models/document_movement.py`, l.139)
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
| `create()` → `raa.registry_aa.sudo().create()` (l.560) | el alta en RAA es un efecto interno; el operador no necesita permisos en `raa` |
| `create()`/`write()` → `document_id.sudo().write()` (l.260/271/694) | campos delegados van a `tmc.document`, donde `tmc.document.user` tiene `perm_write=0`; sin `sudo` el operador no podría. El guard de ME es la frontera |
| `action_set_origin_from_junco()` → `sudo()` (l.449) | da permiso ORM para escribir los 2 campos de origen; el guard `me_origin_from_junco` los acota |

Todas son `sudo()` **acotadas a una operación puntual**; el guard previo de ME es la frontera
de seguridad antes de elevar.

## Caminos negativos (cubiertos por tests — ver `tests_plan.md`)

- No-poseedor no puede registrar/corregir movimiento → `TestMovementPoseedor027`, `TestMovementCorrection028`.
- Operador no puede escribir campos arbitrarios del expediente / movimiento → guards (above);
  EPIC-004 verifica que un `me.group_user` no puede escribir `jurisdiction_dependence` por
  write crudo pero sí vía el método controlado (`TestDocumentExp`, bloque EPIC-004).
- Bloqueo de `fojas` y matriz de permisos → `TestFojasLock` (#018).

## ACL de modelos externos que `me` usa

- `tmc.*` (`tmc.document` vía `_inherits`, `tmc.dependence` extendido, `tmc.document_type`,
  `tmc.dependence_order`): cubiertos por los grupos `tmc.group_user`/`tmc.group_manager` que
  `me` hereda vía `implied_ids`. Escrituras a `tmc.document` van por `sudo()` (ver arriba).
- `raa.registry_aa`: el alta la hace `me` con `sudo()`; el operador no requiere ACL en `raa`.
