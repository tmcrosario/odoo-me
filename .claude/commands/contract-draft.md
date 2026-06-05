---
description: Prepara un plan/contrato técnico antes de implementar (areas, archivos, AC mapping, riesgos Odoo)
argument-hint: [EPIC-XXX/TASK-YYY]
---

Prepará un plan técnico (contrato) antes de tocar código: áreas afectadas, archivos esperados, mapeo de acceptance criteria y riesgos Odoo. Es el paso de diseño previo a la implementación, en la misma sesión.

Referencia: $ARGUMENTS

## Cuándo usar

- La task ya tiene objetivo, alcance y acceptance criteria.
- Querés orientar la implementación antes de editar código.
- El cambio es M/L/XL o toca áreas sensibles y conviene fijar el diseño primero.

## Output

```md
Referencia: EPIC-XXX/TASK-YYY
Modo: XS/S/M/L/XL
Responsable:
Objetivo:
Áreas técnicas esperadas:
Archivos esperados:
Acceptance criteria mapping:
Riesgos Odoo:
Plan de tests:
Plan de implementación:
```

## Reglas

- Este paso NO modifica código: solo fija el diseño.
- Si toca modelos, permisos, workflow, datos, migración, seguridad o auditoría, escalá a L/XL y dejá explícitos los riesgos antes de implementar.
- Persistí el plan en la task card (`doc/tasks/EPIC-XXX/TASK-YYY_*.md`).
- No inventar reglas de negocio.
