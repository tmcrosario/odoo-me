# Workflow

> odoo-me se opera con **VS Code + Claude** (un solo operador). Los "agentes"
> nombrados acá (`product-spec`, `implementer`, `verifier`, `doc-close`, etc.) son
> **modos internos** de la misma sesión, no herramientas separadas. Las fases
> valen como compuertas de disciplina. Ver `doc/framework/tooling_layers.md` y
> `doc/framework/agents_and_artifacts.md`.

## Flujo general

0. **Setup project**: configurar identidad, módulos, herramientas, tests, git y
   riesgos en `doc/framework/project_config.md`.
1. **Idea / pedido**: capturar intención inicial.
2. **New idea**: si es una feature nueva, decidir nueva épica vs épica existente.
3. **Triage**: clasificar modo XS/S/M/L/XL.
4. **Task card**: crear el mínimo documento necesario dentro de `doc/tasks/EPIC-XXX/`.
5. **Asignación**: confirmar responsable y estado de toma antes de implementar.
6. **Spec/contract**: aclarar alcance y criterios. En L/XL o ante sensibilidad
   técnica, fijar el contrato técnico (diseño) antes de editar código, en la misma
   sesión (`/contract-draft`).
7. **Consolidar contexto**: antes de implementar, juntar en la task card el
   contexto necesario (objetivo, criterios, reglas relevantes ya leídas, riesgos)
   para no re-derivar nada al retomar. La memoria vive en el repo, no en el chat.
8. **Checks locales**: antes o durante la implementación, correr validaciones
   baratas y repetibles cuando estén disponibles (`compileall`, parseo XML,
   `git diff --check`, grep negativo, etc.).
9. **Implementación**: modificar código Odoo siguiendo el contrato si existe; no
   re-contratar lo ya fijado.
10. **Execution report**: registrar archivos, cambios, criterios, tests, riesgos y
    cómo probar (en la task card).
11. **Validación**: tests, revisión manual o N/A justificado.
12. **Verifier**: obligatorio para L/XL; opcional para S/M según riesgo.
13. **Commit ready**: preparar o ejecutar commit solo bajo pedido explícito del
    usuario.
14. **Doc close**: cerrar la task y actualizar docs canónicas solo si corresponde.

## Estados de una task

- `Draft`
- `Ready`
- `Implemented`
- `Verified`
- `Done`
- `Blocked`

## Tabla de transiciones

Cada transición declara qué modo la ejecuta y qué precondiciones deben cumplirse.
No pasar al siguiente estado si la precondición no está satisfecha o explícitamente
diferida con `N/A + motivo`.

| Transición | Modo que la ejecuta | Precondiciones |
| --- | --- | --- |
| Draft → Ready | modo `product-spec` o `contract-draft` | Acceptance criteria definidos; asignación lista (`responsable` y `estado de toma`); decisiones de negocio cerradas o `N/A + riesgo` |
| Ready → Implemented | modo `implementer` | Execution report generado en la task card; cambios efectivos en código Odoo o evidencia de no-cambio justificada |
| Implemented → Verified | modo `verifier` (o verificación liviana cuando no hay sensibilidad) | Close gate `Ready` con findings clasificados por severidad; bloque "Tests evidenciados" presente en M/L/XL |
| Verified → Done | modo `doc-close` (única ruta válida, vía `/doc-close`) | Acceptance criteria OK / N/A; tests evidenciados OK / `PENDIENTE USER-RUN` / `N/A + motivo`; verifier OK cuando el modo lo exige; docs canónicas actualizadas, diferidas con registro o `N/A` |
| cualquier → Blocked | cualquier dev | Bloque `Blocked` completo con: razón, propietario del bloqueo, fecha de bloqueo, acción mínima para destrabar |
| Blocked → estado anterior | quien resolvió el bloqueo | Acción mínima ejecutada y registrada en la task card |
| Override forzado (cierre sin cumplir alguna precondición) | cualquier dev | Sección `Override / forzado` con: fecha, dev responsable, motivo concreto, riesgo asumido. Cierre auditable |

### Reglas adicionales

- **Sin lead técnico con permisos especiales**: cualquier dev puede hacer override
  siempre con justificación documentada. Esto mantiene la traza auditable.
- **`/doc-close` es la única ruta a `Done`**: la verificación y la implementación no
  cierran documentación final.
- **Saltar estados**: no permitido. Si la implementación no requiere verifier (por
  ejemplo, cambio XS de copy), se marca `Verified: N/A + motivo` y se transiciona
  explícitamente, no se omite.

## Asignación de tasks

Toda task debe registrar:

- responsable;
- estado de toma: `disponible`, `tomada`, `bloqueada`;
- fecha de toma cuando alguien empieza;
- notas de coordinación si hay más de una persona.

Antes de implementar, verificar que la task no esté tomada por otra persona.

## Commit

El commit es un paso operativo separado de tests, verifier y cierre documental.
Usar `/commit-ready` para revisar estado, diff, riesgos y mensaje. No hacer commit
ni push sin pedido explícito.

## Regla práctica

El flujo completo es una herramienta de seguridad, no el camino obligatorio para
toda edición.

## Organización de trabajo

No usar backlog plano. Toda task debe vivir bajo una épica:

```text
doc/epics/EPIC-001_titulo.md
doc/tasks/EPIC-001/TASK-004_titulo.md
```
