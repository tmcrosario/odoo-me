# EPIC-007 — Mantenimiento y endurecimiento post-baseline

Estado: En progreso (sobre develop) — TASK-001..003 y 005 a 011 Done, TASK-004 Draft (derivada al dev de `raa`)
Riesgo global: medio (TASK-001 toca seguridad/ACL; el resto es acotado)
Módulo: `me` (+ `raa`)
Owner: sin asignar

## Objetivo

Agrupar correcciones y endurecimientos **chicos** que aparecen después del baseline y que no
pertenecen a una línea funcional: gobierno de permisos de una escritura no cubierta, fallos
intermitentes y formato de traducciones. Las épicas EPIC-005 (deuda técnica del baseline) y
EPIC-006 (usabilidad del formulario) no los cubren.

## Contexto

Estos cambios se hicieron entre 2026-08-14 y 2026-09-17, algunos a pedido de la sesión de `odoo-junco`
y otros por hallazgos propios, y quedaron registrados solo como commits. Las tasks `Done` de esta
épica son **retroactivas**: se redactaron después de los commits, con la evidencia de tests que hubo
en cada momento.

## Alcance

Incluye:

- escrituras a `tmc.document` fuera del ORM que hoy saltean el ACL;
- fallos intermitentes de constraints de fecha;
- formato de las traducciones `es_AR` de `me` y `raa` (Odoo 19);
- correcciones de defaults que dependen de la fecha (TASK-004);
- decisiones chicas de clasificación y de la regla de poseedor (TASK-005 y TASK-006).

No incluye:

- funcionalidad nueva de la carga de expedientes (va en EPIC-004 o una épica propia);
- el barrido de comentarios del código (IDEA 6) ni la comparación de fechas en UTC (IDEA 7, salvo
  lo que cubre TASK-004).

## Módulos afectados

- Módulo principal: `me`
- Módulos secundarios afectados: `raa` (TASK-003 y TASK-004)
- Dependencias entre módulos: N/A (sin cambios de manifest)

## Reglas / decisiones durables

- El SQL crudo de `_update_document_date()` se mantiene (escapa la regla año == período de
  `tmc.document`); lo que se gobierna es su ACL. Ver `security.md`.
- El formato del `.po` de Odoo 19 está en `doc/framework/odoo_development_rules.md` →
  *Translations (i18n)*.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Gobernar por ACL la escritura de fecha de GD por SQL crudo | Ale Gallo | L | `me` | Done |
| TASK-002 | Tolerar saltos de reloj en la fecha no futura de movimientos | Ale Gallo | S | `me` | Done |
| TASK-003 | Formato Odoo 19 de las traducciones `es_AR` de `me` y `raa` | Ale Gallo | S | `me` / `raa` | Done |
| TASK-004 | Período del wizard de RAA calculado al abrirlo, no al arrancar el servidor | sin asignar | S | `raa` | Draft |
| TASK-005 | Contratación Directa no ofrece subtemas | Ale Gallo | S | `me` | Done |
| TASK-006 | Regla de poseedor también al crear un movimiento directo | Ale Gallo | L | `me` | Done |
| TASK-007 | Completar las traducciones `es_AR` de `me` | Ale Gallo | S | `me` | Done |
| TASK-008 | Poseedor no clickeable en la grilla de movimientos | Ale Gallo | XS | `me` | Done |
| TASK-009 | Documentar que ser poseedor no da permisos | Ale Gallo | XS | `me` | Done |
| TASK-010 | Secretaría de Vocalía y Contadores Fiscales como dependencias internas | Ale Gallo | L | `me` | Done |
| TASK-011 | Un pase a una oficina externa no lleva poseedor | Ale Gallo | L | `me` | Done |

## Preguntas abiertas

- TASK-004: acceptance criteria propuestos, a confirmar antes de implementar.

## Cierre de épica

Pendiente.
