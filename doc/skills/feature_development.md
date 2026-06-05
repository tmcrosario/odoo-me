# Skill: feature development

Usar esta skill al implementar una feature o mejora Odoo con impacto funcional, en
la sesión VS Code + Claude. Source of truth: `doc/skills/`.

## Pasos

### 1. Entender el pedido

Restated en términos técnicos y confirmá la referencia `EPIC-XXX/TASK-YYY` y el
campo `Módulo:` (`me` / `raa`) cuando aplique.

Identificá el tipo de cambio:

- nuevo campo;
- nuevo modelo;
- relación;
- reporte;
- cambio de vista;
- cambio de workflow / estados;
- regla de negocio;
- automation / cron;
- refactor;
- bugfix funcional.

Pedir aclaración antes de codear si el alcance o los criterios son ambiguos.

### 2. Detectar impacto

Evaluar explícitamente:

- modelos y campos;
- vistas / actions / menus;
- seguridad (ACL, grupos, record rules);
- datos (XML/CSV);
- reglas de negocio;
- campos computados / constraints;
- tests;
- documentación.

Evaluar también impacto en base de datos, migraciones y dependencias circulares.

### 3. Planificar antes de codear

Para M / L / XL o cambios sensibles, dejar un plan corto antes de editar:

- objetivo;
- archivos afectados;
- cambios esperados en modelo / vista / seguridad / datos;
- tests a agregar/actualizar;
- riesgos;
- impacto en documentación.

### 4. Implementar

- Hacer el cambio más chico y cohesivo que cumpla la task.
- Las validaciones de backend mandan; no cubrir reglas de negocio solo con
  `readonly`/`invisible`.
- No ampliar permisos sin criterio explícito.

### 5. Validar y reportar

Preparar tests y pasos manuales. Tests por defecto quedan como `PENDIENTE USER-RUN`
salvo que haya evidencia.

## Execution report

Salida en español rioplatense, formato:

```md
Referencia: EPIC-XXX/TASK-YYY
Módulo:
Archivos cambiados:
Qué cambió:
Acceptance criteria status:
Tests agregados/actualizados:
Tests corridos: OK / PENDIENTE USER-RUN / N/A + motivo
Cómo probar:
Impacto en documentación:
Riesgos / pendientes:
```

Recordar: la implementación **no** marca la task como `Done` documental. El cierre
es un paso aparte (`/doc-close`).
