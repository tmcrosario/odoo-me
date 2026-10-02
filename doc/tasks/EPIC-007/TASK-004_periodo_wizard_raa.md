# EPIC-007 / TASK-004 — Período del wizard de RAA calculado al abrirlo

Estado: Draft
Modo: S
Riesgo: bajo/medio (default de un wizard que crea documentos y registros RAA; `raa` no tiene tests)
Módulo: `raa`
Responsable: sin asignar

## Asignación

- Estado de toma: disponible
- Responsable: sin asignar
- Fecha de toma: N/A
- Notas de coordinación: surgió de la auditoría de documentación (2026-09-24); registrado en
  `brainstorming.md` IDEA 7. **Conviene resolverlo antes del 31/12.**

## Objetivo

Que el período propuesto por el wizard de RAA sea el año **actual al abrirlo**, no el del momento
en que arrancó el servidor.

## Alcance

Incluye:

- `raa.entry.period` (`raa/wizards/entry.py`): hoy `default=str(date.today().year)`, que se evalúa
  **una sola vez al importar el módulo**. Después de Año Nuevo, y hasta reiniciar Odoo, propone el año
  anterior. Lo comparten el wizard de carga y el de búsqueda de faltantes (ambas vistas son de `raa.entry`);
- con ese período, `create_registry_aa()` busca o **crea** `tmc.document` y registra el RAA: si el
  usuario no mira el campo, carga los actos en el año equivocado.

No incluye: cambiar la lógica de carga ni de búsqueda de faltantes.

## Acceptance criteria (propuestos — a confirmar antes de implementar)

- [ ] El default de `period` se calcula cada vez que se abre el wizard (no al importar el módulo).
- [ ] Criterio de "año actual": a confirmar con el usuario (fecha del servidor, que es UTC, o fecha
      local del usuario, como ya hace `entry_date` con `context_today`).
- [ ] Test que fije el default con una fecha simulada (`raa` no tiene carpeta `tests/`: habría que crearla).

## Validación

Test con `patch` de la fecha + prueba manual abriendo el wizard. Tests: `PENDIENTE USER-RUN` hasta
implementar.

## Bloqueos

N/A

## Resultado

Pendiente.
