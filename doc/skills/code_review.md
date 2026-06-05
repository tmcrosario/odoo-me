# Skill: code review

Usar esta skill para la revisión crítica de cambios de código Odoo, en la sesión
VS Code + Claude. Source of truth: `doc/skills/`.

## Enfoque

- Revisar **diff-first** cuando hay diff disponible.
- Separar issues confirmados de supuestos.
- Incluir referencias concretas a archivo/línea.
- Marcar secciones no aplicables como `N/A` con motivo.

## Checklist

### 1. Alcance

- Identificar modelos / vistas / actions / datos / seguridad / tests afectados.
- Confirmar referencia `EPIC-XXX/TASK-YYY` y `Módulo:` cuando aplique.

### 2. Arquitectura y diseño

- Preferir extender conceptos existentes antes de agregar modelos nuevos sin
  justificación.
- La lógica de negocio debe vivir en el backend, no solo en vistas.
- Evitar side effects ocultos y lógica duplicada.

### 3. Reglas de negocio

- Comparar implementación contra la task/spec y
  `doc/project/<modulo>/business_rules.md` cuando aplique.
- Marcar reglas nuevas no documentadas, validaciones faltantes o transiciones
  inconsistentes.

### 4. Compatibilidad Odoo

- Chequear uso de Python / Odoo API.
- Chequear sintaxis XML / vistas para la versión Odoo target.
- Revisar campos computados, constraints, lógica `onchange` y comportamiento batch.

### 5. Seguridad

- Modelos nuevos requieren consideración de ACL.
- Cambios de permisos requieren análisis explícito por rol.
- Caminos negativos sensibles deben tener test o quedar documentados como gap.

### 6. Tests y regresiones

- Verificar que se hayan agregado/actualizado tests o que `N/A` esté justificado.
- No declarar tests OK sin evidencia.
- Identificar regresiones probables.

## Output contract

Salida en español rioplatense, formato:

```md
1. Alcance de la task
2. Findings por severidad: blocker / high / medium / low / suggestion
3. Chequeo de seguridad
4. Consistencia documental
5. Tests y gaps
6. Riesgos
7. Decisión de cierre: Ready / Blocked
8. Fix mínimo sugerido
```
