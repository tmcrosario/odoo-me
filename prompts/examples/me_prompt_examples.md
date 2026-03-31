# ME – Ejemplos de Prompts para Desarrollo Asistido con IA

Este archivo define una forma **simple y consistente** de interactuar con IA
cuando se trabaja en el módulo ME (Mesa de Entradas).

El objetivo es estandarizar cómo:

- pedimos cambios
- analizamos comportamiento
- implementamos funcionalidades
- validamos resultados (tests + documentación)

Está inspirado en enfoques estructurados como SIGOP,
pero adaptado al módulo ME y manteniéndose liviano.

---

## Cómo usar estos prompts

1. Definir claramente qué querés hacer (feature, bugfix, análisis, etc.)
2. Usar uno de los templates de abajo
3. Siempre incluir:
   - contexto
   - objetivo funcional
   - criterios de aceptación
4. Exigir cierre con:
   - tests (o explicación si no se ejecutaron)
   - actualización de documentación si corresponde

---

## Template base

Usar este template como punto de partida.

Contexto:
- Tipo de cambio: [análisis / bugfix / nueva funcionalidad / migración / auditoría]
- Zona del sistema: [modelos, vistas, wizards, seguridad]

Objetivo funcional:
[qué querés lograr y por qué]

Criterios de aceptación:
[comportamientos esperados]

Restricciones:
- No inventar comportamiento no presente en el código
- Priorizar consistencia con:
  - me/ai-context.md
  - docs/me_architecture_analysis_report.md
  - docs/architecture_diagram.md
  - domain-rules/me/workflows.md

---

## Template 1 – Feature / Nueva funcionalidad

Regla operativa:
- No cerrar la tarea sin validar tests y documentación.

Contexto:
- Tipo de cambio: nueva funcionalidad
- Zona del sistema: [modelo/vista específica]

Objetivo funcional:
[describir funcionalidad en lenguaje de negocio]

Expectativas de análisis:
- Revisar:
  - me/ai-context.md
  - domain-rules/me/workflows.md
- Identificar impacto en:
  - modelos
  - vistas
  - create/write
  - tests

Criterios de aceptación:
- La funcionalidad se comporta según lo esperado
- No rompe flujos existentes
- Tests agregados o actualizados
- Documentación actualizada si corresponde

Salida requerida:
1) Plan breve
2) Implementación
3) Tests (o explicación)
4) Cambios en documentación
5) Sugerencia de commit:
   - commit name
   - descripción breve

---

## Template 2 – Bugfix

Regla operativa:
- Encontrar causa raíz antes de proponer solución.

Contexto:
- Tipo de cambio: bugfix
- Zona del sistema: [modelo/vista]
- Error observado:
[mensaje de error o comportamiento incorrecto]

Objetivo funcional:
Corregir el problema sin romper comportamiento existente.

Expectativas de análisis:
- Identificar:
  - método involucrado
  - constraint o validación
  - flujo afectado
- Verificar consistencia con workflows

Criterios de aceptación:
- Error corregido
- No se introduce regresión
- Tests agregados o actualizados

Salida requerida:
1) Causa raíz
2) Fix mínimo
3) Tests
4) Impacto en documentación
5) Comentario de commit

---

## Template 3 – Análisis de código

Contexto:
- Tipo de tarea: análisis
- Zona del sistema: [modelo/módulo]

Objetivo:
Entender comportamiento y responsabilidades del código.

Criterios de aceptación:
- Explicar:
  - propósito del modelo
  - relaciones
  - lógica principal
  - rol en el workflow

Clasificación obligatoria:
- Observed in code
- Inferred
- Uncertain

---

## Template 4 – Auditoría

Contexto:
- Tipo de tarea: auditoría
- Alcance: módulo ME completo o parcial

Objetivo:
Detectar inconsistencias entre:

- código
- workflows
- ai-context
- documentación

Criterios de aceptación:
- Hallazgos clasificados por severidad
- Identificación de:
  - inconsistencias
  - gaps de tests
  - gaps de documentación

Salida:
- Lista de problemas
- Propuesta de corrección

---

## Template 5 – Tests

Regla operativa:
- Toda funcionalidad debe tener tests asociados.

Contexto:
- Tipo de tarea: tests
- Zona del sistema: [modelo/flujo]

Objetivo:
Validar comportamiento del sistema.

Criterios de aceptación:
- Usar TransactionCase
- Crear datos mínimos
- Validar:
  - creación de registros
  - constraints
  - efectos secundarios (ej: movimientos)

Casos típicos:
- creación de expediente
- generación de movimientos
- validaciones

---

## Ejemplos específicos del módulo ME

### Ejemplo – Crear expediente

Contexto:
- Tipo de cambio: validación de workflow
- Zona: me.document_exp

Objetivo:
Verificar que la creación de expediente:

- crea tmc.document
- crea movimientos iniciales
- crea registro en RAA

Criterios:
- comportamiento alineado con ai-context
- no duplicar lógica

---

### Ejemplo – Revisar movimientos

Contexto:
- Tipo de tarea: análisis funcional
- Zona: me.document_movement

Objetivo:
Verificar trazabilidad del documento.

Criterios:
- movimientos correctamente relacionados
- origen/destino coherentes

---

### Ejemplo – Agregar campo

Contexto:
- Tipo de cambio: feature
- Zona: modelo existente

Objetivo:
Agregar campo adicional sin romper:

- _inherits con tmc.document
- relaciones existentes

Criterios:
- visible en UI
- consistente con modelo base

---

## Reglas de uso (muy importante)

- No inventar comportamiento
- Priorizar código sobre documentación
- Marcar como "Uncertain" lo que no esté claro
- No cerrar tareas sin:
  - tests
  - validación funcional
- Mantener consistencia con ai-context.md

---

## Flujo recomendado de trabajo

1. Definir tarea
2. Ejecutar prompt (feature / bugfix / análisis)
3. Implementar cambios
4. Validar con tests
5. Actualizar documentación
6. Commit