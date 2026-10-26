# EPIC-007 — Índice de tasks

Épica: `doc/epics/EPIC-007_mantenimiento_post_baseline.md`

> Las tasks `Done` son **retroactivas** (se redactaron después de los commits).

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Gobernar por ACL la escritura de fecha de GD por SQL crudo | Ale Gallo | L | Done | `check_access('write')` + `sudo()` en `create()`; a pedido de junco (auditoría EPIC-015). Suite 255/0/0 |
| TASK-002 | Tolerar saltos de reloj en la fecha no futura de movimientos | Ale Gallo | S | Done | Margen de 60 s; arregla además un test viejo que fallaba de noche. Suite 258/0/0 |
| TASK-003 | Formato Odoo 19 de las traducciones `es_AR` de `me` y `raa` | Ale Gallo | S | Done | `#. module:` faltante (no cargaba es_AR) + `#. odoo-python` en 31 entradas + typo. Suite 258/0/0 |
| TASK-004 | Período del wizard de RAA calculado al abrirlo | sin asignar | S | Draft | Hoy se fija al arrancar Odoo; criterios propuestos, a confirmar |
| TASK-005 | Contratación Directa no ofrece subtemas | Ale Gallo | S | Done | Decisión del usuario; solo el dominio del subtema. Suite 259/0/0; UI verificada |
| TASK-006 | Regla de poseedor también al crear un movimiento directo | Ale Gallo | L | Done | Opción (a) de IDEA 8: `create()` de `me.document_movement`. Suite 265/0/0 |
| TASK-007 | Completar las traducciones `es_AR` de `me` | Ale Gallo | S | Done | 50 entradas nuevas + prefijo `model_terms` corregido; UI verificada |
