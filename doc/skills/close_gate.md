# Skill: close gate

Usar esta skill para validar si una task Odoo está lista para cierre documental, en
la sesión VS Code + Claude. Source of truth: `doc/skills/`.

La verificación devuelve `Ready` o `Blocked`. El cierre documental final lo hace
`/doc-close`, ningún otro paso marca `Done`.

## Inputs

- Referencia: `EPIC-XXX/TASK-YYY`.
- Módulo afectado (`me` / `raa`) si aplica.
- Alcance y archivos cambiados.
- Execution report.
- Bloque "Tests evidenciados" en task card (en M/L/XL es obligatorio).
- Impacto en documentación.

## Checklist

### 1. Implementación

- ¿La implementación cubre el alcance pedido?
- Si no se esperaba cambio de código, marcar `N/A` con motivo.

### 2. Acceptance criteria

- ¿Todos los criterios están satisfechos, bloqueados o explícitamente `N/A`?
- ¿Quedan supuestos abiertos?

### 3. Seguridad

- Si hubo impacto en permisos / seguridad: verificar ACL, grupos, record rules y
  caminos negativos.
- Si no hubo impacto, marcar `N/A` con motivo.

### 4. Tests evidenciados

- En M/L/XL, **bloque obligatorio**: si está vacío o ausente, devolver `Blocked`.
- Si los tests no se ejecutaron y no hay evidencia, marcar
  `Estado: PENDIENTE USER-RUN`.
- No marcar `OK` sin evidencia (salida pegada por el usuario o capturada en sesión).
- Cambios documentación-only pueden usar `Estado: N/A + motivo`.

### 5. Documentación

- Confirmar que la task card registra implementación, tests, riesgos e impacto en
  docs.
- Las docs canónicas pueden quedar pendientes de consolidación si la task card lo
  deja registrado expresamente (sin SLA por defecto, revisión on-demand).

### 6. Bloqueos y override

- Si la task pasó por `Blocked`, verificar que el bloque "Bloqueos" haya quedado
  completo.
- Si hay sección "Override / forzado", marcarla expresamente en el output para que
  `/doc-close` la considere.

## Output contract

Salida en español rioplatense, formato:

```md
1. Alcance de la task
2. Estado de implementación: OK / BLOCKED / N/A
3. Acceptance criteria: OK / BLOCKED / N/A
4. Seguridad: OK / BLOCKED / N/A
5. Tests evidenciados: OK / PENDIENTE USER-RUN / N/A + motivo
6. Documentación: OK / pendiente / N/A
7. Override / forzado: presente sí/no
8. Decisión de cierre: Ready / Blocked
9. Acción mínima para destrabar
```
