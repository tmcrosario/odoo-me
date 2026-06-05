# Testing policy

## Principios

- El framework trae `/test-run`, pero no trae la suite real de los módulos Odoo.
- El bootstrap inicial (`doc/framework/project_config.md`) debe registrar si la
  suite real ya existe, dónde vive y cómo se ejecuta, por módulo (`me`, `raa`).
- No declarar tests OK sin evidencia.
- Registrar comando ejecutado, resultado y alcance.
- Si no se ejecutaron tests, marcar `PENDIENTE USER-RUN` o `N/A` con motivo.
- Si el módulo todavía no tiene suite real configurada, marcar `PENDIENTE DEFINIR`
  y pedir decisión.

## Evidencia mínima

```md
Tests: OK / PENDIENTE USER-RUN / N/A
Comando: ...
Resultado: ...
Fecha: ...
```

## Odoo

Cada módulo define su comando canónico en `doc/project/<modulo>/tests_plan.md`.

El comando canónico puede ser:

- suite completa;
- suite por módulo;
- CI;
- validación manual documentada solo si la task justifica `N/A` para tests
  automatizados.
