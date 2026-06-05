---
description: Convierte una idea o pedido en especificación funcional liviana antes de contrato o implementación
argument-hint: [EPIC-XXX/TASK-YYY | descripción]
---

Convertí una idea o pedido en especificación funcional liviana antes de contrato o implementación.

Pedido: $ARGUMENTS

## Cuándo usar

- La intención de negocio necesita ordenarse.
- Hay dudas de alcance o criterios.
- Una idea ya fue ubicada en una épica, pero todavía no está lista como task implementable.

## Contexto permitido

1. Pedido del usuario.
2. Epic card correspondiente.
3. Task card si ya existe.
4. Documentos `doc/project/*` solo si son necesarios para reglas existentes.

## Output

```md
Referencia: EPIC-XXX / EPIC-XXX/TASK-YYY / N/A
Objetivo:
Alcance:
No incluye:
Reglas conocidas:
Preguntas abiertas:
Acceptance criteria:
Modo sugerido:
Responsable sugerido:
Próxima acción:
```

## Reglas

- No inventar reglas de negocio.
- Si no hay épica clara, volvé a `/new-idea`.
- Mantené la especificación proporcional al modo XS/S/M/L/XL.
