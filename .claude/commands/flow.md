---
description: Clasifica el pedido y recomienda el menor flujo seguro; sin pedido, analiza estados y prioridades
argument-hint: [EPIC-XXX/TASK-YYY | descripción del pedido]
---

Clasificá el pedido del usuario y recomendá el menor flujo seguro de trabajo. Si no hay task, épica ni pedido concreto, detectá esa falta de foco y ofrecé un análisis de estados y prioridades del trabajo pendiente.

Pedido: $ARGUMENTS

## Prompt

Usá `doc/framework/delivery_modes.md` y `AGENTS.md`. No leas contexto amplio salvo necesidad clara.

Si se invoca sin task, épica ni pedido concreto, no intentes clasificar una implementación. Informá que falta una referencia de trabajo y preguntá si quiere un análisis de prioridades y estados de lo pendiente. Para ese análisis podés leer:

1. `doc/epics/_index.md`;
2. `doc/tasks/_index.md`;
3. índices puntuales `doc/tasks/EPIC-XXX/_index.md` cuando el resumen global no alcance;
4. task cards puntuales solo si son necesarias para entender bloqueo, estado de toma o próximo paso.

Devolvé:

```md
Modo recomendado: XS/S/M/L/XL
Motivo:
Riesgo:
Sensibilidad Odoo:
Épica/task: nueva idea / EPIC-XXX/TASK-YYY / requiere clasificación
Responsable/estado de toma: sin asignar/disponible/tomada/bloqueada/desconocido
Documento sugerido:
Próximo paso:
Acción mínima:
```

Si no hay task, épica ni pedido concreto, devolvé:

```md
No indicás una task, épica ni pedido concreto para clasificar.
¿Querés que revise el estado de épicas/tasks pendientes y te proponga prioridades para retomar?

Si confirmás, voy a revisar índices de épicas y tasks, estados de toma, bloqueos y próximos pasos posibles.
```

Si el usuario confirma el análisis de prioridades, devolvé:

```md
## Panorama

| Estado | Cantidad | Nota |
| --- | ---: | --- |
| En curso/tomadas |  |  |
| Disponibles/no abordadas |  |  |
| Bloqueadas |  |  |
| Pendientes de definición |  |  |
| Pendientes de implementación |  |  |
| Pendientes de verificación/cierre |  |  |

## Detalle

| Prioridad | Ref | Task | Estado toma | Estado doc | Riesgo | Próximo paso | Motivo |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | EPIC-XXX/TASK-YYY |  |  |  |  |  |  |

## Próxima Acción Recomendada

`/comando EPIC-XXX/TASK-YYY`

Motivo:
```

## Reglas

- Salida siempre en español rioplatense.
- No expandir contexto si no es estrictamente necesario.
- Si la tarea es ambigua, pedí una aclaración corta antes de clasificar.
- Si no hay task, épica ni pedido concreto, pedí confirmación para análisis de prioridades antes de leer contexto amplio.
- En análisis de prioridades, priorizá tasks `disponible` o desbloqueables con mayor claridad de acceptance criteria y menor riesgo; no tomes decisiones de negocio por inferencia.
- En análisis de prioridades, usá obligatoriamente las secciones `## Panorama`, `## Detalle` y `## Próxima Acción Recomendada`.
- Reportá tasks `tomada` o `bloqueada` sin proponer pisarlas, salvo que el usuario pida reasignación o destrabe.
- Si el modo es L/XL o toca áreas sensibles Odoo, recomendá un plan/contrato técnico antes de implementar.
- Próximos pasos válidos: `/new-idea`, `/new-task`, `/product-spec`, `/prepare-task`, `/contract-draft`, `/test-run`, `/doc-close`, `/commit-ready`.
- Recomendá un solo próximo paso principal y, si aplica, el paso posterior esperado.
