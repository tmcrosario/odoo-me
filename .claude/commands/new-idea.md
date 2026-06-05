---
description: Registra y clasifica una idea nueva antes de convertirla en épica o task
argument-hint: [descripción de la idea]
---

Registrá y clasificá una idea nueva antes de convertirla en épica o task.

Idea: $ARGUMENTS

## Cuándo usar

- El usuario propone una feature/capacidad que todavía no existe.
- No está claro si pertenece a una épica existente.
- La idea aún es exploratoria y no merece task card completa.

## Contexto permitido

Leer solo:

1. pedido del usuario;
2. `doc/epics/_index.md`;
3. epic cards candidatas puntuales, si el índice sugiere coincidencia;
4. `doc/project/*` solo si es necesario para evitar duplicación o riesgo.

No leer backlog completo ni crear tasks por inercia.

## Output

```md
Idea:
Clasificación: nueva épica / dentro de épica existente / duda
Épica sugerida: EPIC-XXX / nueva EPIC-XXX / N/A
Motivo:
Tamaño inicial: XS/S/M/L/XL
Riesgo:
Preguntas abiertas:
Siguiente paso recomendado:
```

## Reglas

- Si la idea abre una capacidad funcional nueva, sugerí nueva épica.
- Si es una mejora dentro de una capacidad existente, sugerí task dentro de esa épica.
- Si falta información, hacé una pregunta breve antes de crear documentos.
- No inventar reglas de negocio.
