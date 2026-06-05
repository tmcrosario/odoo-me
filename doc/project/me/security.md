# Seguridad — módulo `me` (Mesa de Entradas)

> **Stub.** No había un documento de seguridad previo en `docs/`. Lo conocido se
> recogió de `docs/system_narrative.md` (2026-03-31) y de las task cards (#018, #027).
> El **baseline verificado contra `me/security/` y el código se cierra en EPIC-001.**
> No asumir lo de acá como completo ni cerrado.

## Grupos (conocido)

El módulo `me` define tres grupos de acceso:

- **Usuario** (`me.group_user`) — registra y gestiona expedientes.
- **Responsable / Manager** (`me.group_manager`) — acceso completo, incluida
  configuración (p. ej. `default_responsible_id` por dependencia); puede levantar el
  bloqueo de `fojas` post-creación y corregir/eliminar movimientos.
- **Solo lectura** — visualiza expedientes sin modificarlos.

## ACL (conocido)

- Existen reglas `ir.model.access` para `me.document_exp` y `me.document_movement`
  (según `system_narrative.md`). **A verificar**: contenido exacto de
  `me/security/ir.model.access.csv`, permisos por grupo y `perm_unlink` (#018 indica
  que `me.group_user` no tiene unlink sobre `me.document_movement`).
- Restricciones de acceso a modelos de otros módulos (`tmc`, `raa`) dependen de la
  configuración de esos módulos.

## Reglas de poseedor (backend, conocido)

- Solo el `user_id` del último movimiento puede registrar un pase nuevo desde la UI
  (managers sin restricción) — guard en `write()` de `me.document_exp` (#027/#029).
- Corrección del último movimiento manual restringida por campos (#028).

## Pendiente de baseline (EPIC-001)

- [ ] Inventariar `me/security/*` (CSV + record rules + grupos XML) contra el código.
- [ ] Mapear permisos CRUD por grupo y modelo.
- [ ] Verificar caminos negativos (¿hay tests `with_user` + `AccessError`?).
- [ ] Confirmar si `tmc`/`raa` proveen ACL para modelos usados por `me`.
