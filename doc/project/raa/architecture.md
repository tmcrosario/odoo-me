# Arquitectura — módulo `raa` (Registro de Actos Administrativos)

> **Stub / boundary.** `raa` se considera **estable y fuera del scope** del trabajo
> sobre `me`. Se puede leer para contexto, pero **no se modifica sin pedido
> explícito**. No hay documentación de negocio propia de `raa` más allá de esto; si
> en el futuro entra en scope, este árbol (`doc/project/raa/`) se completa on-demand.
> Relevado desde la óptica de `me` (2026-10-02); **`raa` no tiene tests**.

## Qué se sabe (desde la óptica de `me`)

- Modelo principal: **`raa.registry_aa`** (`raa/models/registry_aa.py`).
- Tiene `document_id` (Many2one → `tmc.document`) con constraint **UNIQUE** sobre
  `document_id` (`_document_id_unique` en `raa/models/registry_aa.py`).
- Se **crea automáticamente** desde `me.document_exp.create()`:
  `env_create["raa.registry_aa"].sudo().create({"document_id": record.document_id.id})`
  (`create()` en `me/models/document_exp.py`; con `sudo()` porque el alta en RAA es un efecto interno
  y el operativo no tiene ACL de escritura en `raa`).

## Qué más tiene `raa`

- **Wizards** (ambos sobre el mismo modelo `raa.entry`, con sus rangos en `raa.number_range`):
  *carga de actos* por rangos de números (`create_registry_aa()`: busca o **crea** el
  `tmc.document` y le registra el RAA) y *búsqueda de faltantes* (`search_missing()`: qué números
  faltan para un tipo + dependencia + período). Ambos comparten el campo `period`.
- **Reporte** de números faltantes (`raa/reports/missing_raa*`).
- **Grupos propios** (`raa/security/raa_groups.xml`, privilegio "RAA"): `User` y `Read Only` solo
  leen; `Manager` (implicado por `base.group_erp_manager`) tiene acceso total sobre
  `raa.registry_aa`, `raa.entry` y `raa.number_range`. **Ningún grupo de `me` implica un grupo de RAA.**

## `raa.registry_aa.unlink()` puede borrar el `tmc.document` padre

Al borrar un registro RAA, si su `tmc.document` está "vacío" (sin `date`, `document_object`, temas
principales, documentos relacionados ni destacados), `unlink()` borra también el documento. Eso
aplica a los documentos que crea el wizard de carga; un **expediente de `me` siempre tiene `date`**,
así que su documento no se borra por esta vía. Igual, `me.document_exp.unlink()` borra el RAA
primero y chequea `document.exists()` antes de borrar el documento. Permisos de ese borrado:
[`../me/security.md`](../me/security.md) → `me.document_exp.unlink()`.

## Acoplamiento con `me` (decisión cerrada)

`raa` **no está declarado** como dependencia en `me/__manifest__.py` pese a que `me`
lo instancia en `create()`, y **no se puede declarar**: `raa` depende de `me`, así que declararlo
cerraría un ciclo `me ↔ raa` (decisión EPIC-005/TASK-002). Si `raa` no está instalado, la creación
de expedientes falla en runtime; en este stack siempre se co-instalan (`-i me,raa`). Detalle en
[`../me/models.md`](../me/models.md) y [`../me/architecture.md`](../me/architecture.md) (§9.7).

## Regla

No proponer cambios estructurales ni de dominio sobre `raa`. Cualquier necesidad de
tocarlo escala a una decisión explícita del usuario.
