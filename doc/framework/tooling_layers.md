# Operación y compuertas

odoo-me se trabaja con un **único entorno: VS Code + Claude**. No hay OpenCode ni
Cursor. Un solo operador recorre todas las fases en la misma sesión.

El framework original repartía el trabajo entre una capa de metodología (OpenCode)
y una capa de implementación code-aware (Cursor / coding agent). Acá esa separación
**no aplica**: se conserva solo como **compuertas de disciplina internas**, no como
límites entre herramientas.

## Fases como compuertas

| Fase | Qué cubre | Compuerta |
| --- | --- | --- |
| Preparar / definir | Metodología, épicas, task cards, alcance, criterios, contrato preliminar | No se implementa sin acceptance criteria claros |
| Contrato técnico | Diseño definitivo cuando hay sensibilidad o lectura de código necesaria | En L/XL o áreas sensibles, fijar el diseño antes de editar |
| Implementar | Cambios Odoo sobre el código real y el diff | Solo en este paso se toca `models/`, `views/`, `security/`, `data/`, `tests/` |
| Verificar | Revisión crítica diff-first, criterios, riesgos, tests | L/XL exige verifier; close gate `Ready`/`Blocked` |
| Cerrar | Cierre documental con evidencia | Único paso que marca `Done`, vía `/doc-close` |

Aunque sea un solo operador, las compuertas siguen vigentes: **criterios antes de
implementar, evidencia antes de declarar tests OK, y cierre documental como paso
explícito y separado del commit.**

## Evidencia de tests

La evidencia de ejecución de tests es su propia compuerta:

- **user-run** (el dev pega la salida) — **default Odoo seguro**;
- **CI-run** (cuando haya CI activo);
- **agent-run** con permiso explícito (excepción acotada).

**Ningún paso puede declarar tests `OK` sin evidencia.**

## Configuración del proyecto

Las elecciones activas de odoo-me (módulos, comandos de test, git, riesgos) viven
en `doc/framework/project_config.md`.
