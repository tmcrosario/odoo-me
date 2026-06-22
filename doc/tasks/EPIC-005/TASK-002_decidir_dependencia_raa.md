# EPIC-005 / TASK-002 — Decidir/declarar dependencia `raa` en el manifest

Estado: Done (decisión)
Modo: S
Riesgo: bajo (terminó en doc; no se tocó el manifest)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: cerrada (Done)
- Notas: follow-up de EPIC-001/TASK-001 (§8.8).

## Objetivo

Decidir si declarar `raa` como dependencia de `me` en el manifest (el manifest declara
`["tmc", "tmc_data"]` pero `create()` siempre crea `raa.registry_aa`).

## Hallazgo (decisivo)

**`raa` depende de `me`** (`raa/__manifest__.py`: `depends = ["tmc", "me"]`). Agregar `raa`
a los `depends` de `me` crearía una **dependencia circular** `me ↔ raa` → rompe la carga de
módulos. **No se puede declarar.** El "acoplamiento implícito" del comentario en `create()`
es, de hecho, el diseño correcto dado el ciclo.

Esto **no es** la misma clase que `tmc_data` (ahí `me → tmc_data` era una dependencia limpia
hacia abajo; acá la dirección está invertida: `me` usa un modelo de un módulo que depende de `me`).

## Decisión (usuario)

**Opción 1 — documentar, no tocar el manifest.** `me` y `raa` se co-instalan siempre en este
stack (`-i me,raa`). Se documenta el acoplamiento implícito y su justificación (el ciclo) en
`models.md`. No se endurece `create()` (no se prevé instalar `me` sin `raa`).

## Acceptance criteria

- [x] Determinada la viabilidad de declarar `raa` (no: sería circular).
- [x] Decisión tomada (opción 1: documentar).
- [x] `models.md` documenta el acoplamiento implícito + consecuencia (si falta `raa`,
  `create()` falla) + justificación (ciclo).

## Riesgo residual (anotado)

Si alguna vez se instala `me` sin `raa`, `create()` falla al crear `raa.registry_aa`. Mitigación
disponible si el escenario aparece: guardar la creación con `if 'raa.registry_aa' in self.env`.
Hoy no aplica.

## Tests evidenciados

- Estado: N/A + motivo — task de decisión/documentación; no modifica código.

## Estado / próximo paso

**Done.** Sin cambios de código. Push (doc): usuario.

## Resultado / cierre

Cerrada (Done) el 2026-06-22. Decisión: no declarar `raa` (sería circular, `raa → me`);
acoplamiento implícito documentado en `models.md`. Cierra EPIC-005.
