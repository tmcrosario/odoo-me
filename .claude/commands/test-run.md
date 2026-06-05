---
description: Coordina ejecución de tests y exige evidencia; no declara OK sin salida
argument-hint: [EPIC-XXX/TASK-YYY | módulo]
---

Coordiná la ejecución de los tests definidos en `doc/project/tests_plan.md`.

Referencia: $ARGUMENTS

Comando de tests por módulo (correr desde la raíz del stack `odoo-docker-stack/`).
odoo-me tiene dos módulos custom: `me` (mesa de entradas) y `raa`. Correr el
módulo que toca la task:

```bash
# Mesa de entradas
docker compose -f develop.yml run --rm odoo odoo -d <TEST_DB> -u me --test-tags /me --stop-after-init --log-level=test

# RAA
docker compose -f develop.yml run --rm odoo odoo -d <TEST_DB> -u raa --test-tags /raa --stop-after-init --log-level=test
```

## Reglas

- Si no podés ejecutar tests desde el entorno actual, pedí al usuario que corra el comando y pegue la salida.
- No declarar OK sin evidencia. Por default, los tests quedan `PENDIENTE USER-RUN`.
- Registrar el estado de tests en la task card.
