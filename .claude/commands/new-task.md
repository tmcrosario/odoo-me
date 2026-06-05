---
description: Crea o propone una task card dentro de una épica con el template más chico compatible con el riesgo
argument-hint: [EPIC-XXX | descripción de la task]
---

Creá o propové una task card dentro de una épica usando el template más pequeño compatible con el riesgo.

Pedido: $ARGUMENTS

## Requisito

Toda task pertenece a una épica: `EPIC-XXX/TASK-YYY`.

Toda task debe registrar:

- Responsable: `sin asignar` o nombre/persona/equipo.
- Estado de toma: `disponible`, `tomada` o `bloqueada`.

Antes de crear o preparar handoff para una task existente, revisá:

- si ya tiene responsable;
- si el estado de toma es `tomada`;
- si hay notas de coordinación o bloqueo.

Si no hay épica clara, usá primero `/new-idea`.

## Reglas

- XS: usar `doc/tasks/templates/task_xs.md` o nota mínima.
- S: usar `doc/tasks/templates/task_s.md`.
- M: usar `doc/tasks/templates/task_m.md`.
- L/XL: usar `doc/tasks/templates/task_full.md`.
- Si es la primera task de una épica, crear también `doc/tasks/EPIC-XXX/_index.md`.
- No proponer implementación si la task está `tomada` por otra persona, salvo handoff explícito.
- Incluir un bloque **Estado / próximo paso** en la task card (memoria de reanudación entre sesiones).
- No inventar reglas de negocio.

## Output

```md
Referencia: EPIC-XXX/TASK-YYY
Responsable:
Estado de toma:
Notas de coordinación:
Modo:
Riesgo:
Archivo sugerido:
Resumen:
Acceptance criteria iniciales:
```
