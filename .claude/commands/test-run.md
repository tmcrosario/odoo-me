---
description: Coordina ejecución de tests y exige evidencia; no declara OK sin salida
argument-hint: [EPIC-XXX/TASK-YYY | módulo]
---

Coordiná la ejecución de los tests definidos en `doc/project/<modulo>/tests_plan.md`
(para `me`: `doc/project/me/tests_plan.md`).

Referencia: $ARGUMENTS

Comando de tests: **leelo y copialo de `doc/project/me/tests_plan.md`** (sección
"Comando canónico"). No se duplica acá: una copia desactualizada es la causa del
verde falso. Lo que no se negocia:

- DB de test **dedicada y NO servida** (`me_test`). Sobre una DB que la instancia ya
  sirve (me1/me2) el runner recolecta **0 tests**.
- `--addons-path` explícito **y completo** (las 9 rutas, incluidas las 5 de OCA): sin él
  el runner corre **0 tests**; sin las rutas OCA `tmc` no carga y se saltea todo el grafo.
  Copiar también los parámetros de conexión del canónico (`--db_host`/`--db_user`/`--db_password`).
- Verificar la línea de resultado `... of N tests` con **N > 0** y `0 failed, 0 error(s)`.
  `0 tests of 0` **no es evidencia**.

odoo-me tiene dos módulos custom: `me` (mesa de entradas) y `raa`. **`raa` no tiene
suite** (no existe `raa/tests/`): para `raa` la evidencia de tests es `N/A`, no un
comando que devuelve 0 tests.

## Reglas

- Si no podés ejecutar tests desde el entorno actual, pedí al usuario que corra el comando y pegue la salida.
- No declarar OK sin evidencia. Por default, los tests quedan `PENDIENTE USER-RUN`.
- Registrar el estado de tests en la task card.
