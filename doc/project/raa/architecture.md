# Arquitectura — módulo `raa` (Registro de Actos Administrativos)

> **Stub / boundary.** `raa` se considera **estable y fuera del scope** del trabajo
> sobre `me`. Se puede leer para contexto, pero **no se modifica sin pedido
> explícito**. No hay documentación de negocio propia de `raa` más allá de esto; si
> en el futuro entra en scope, este árbol (`doc/project/raa/`) se completa on-demand.

## Qué se sabe (desde la óptica de `me`)

- Modelo principal: **`raa.registry_aa`** (`raa/models/registry_aa.py`).
- Tiene `document_id` (Many2one → `tmc.document`) con constraint **UNIQUE** sobre
  `document_id` (`_document_id_unique` en `raa/models/registry_aa.py`).
- Se **crea automáticamente** desde `me.document_exp.create()`:
  `env_create["raa.registry_aa"].sudo().create({"document_id": record.document_id.id})`
  (`create()` en `me/models/document_exp.py`; con `sudo()` porque el alta en RAA es un efecto interno
  y el operativo no tiene ACL de escritura en `raa`).

## Riesgo de acoplamiento

`raa` **no está declarado** como dependencia en `me/__manifest__.py` pese a que `me`
lo instancia en `create()`. Si `raa` no está instalado, la creación de expedientes
falla en runtime. Detalle en [`../me/architecture.md`](../me/architecture.md) (sección 11).

## Regla

No proponer cambios estructurales ni de dominio sobre `raa`. Cualquier necesidad de
tocarlo escala a una decisión explícita del usuario.
