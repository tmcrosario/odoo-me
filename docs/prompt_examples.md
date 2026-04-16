# ME – Prompts templates

Este archivo define una forma **estructurada y consistente** de trabajar con IA
en el módulo ME (Mesa de Entradas).

Se basa en:

- el backlog (`todo.md`)
- la documentación del sistema
- un flujo de trabajo con modos (definición / implementación / revisión / fix)

---

## Principio clave

👉 El desarrollo SIEMPRE parte del backlog (`todo.md`)

- No se trabaja con ideas sueltas
- Toda tarea debe tener un ID (#XXX)

---

## Regla 1 – Decisiones abiertas

Si una tarea tiene decisiones abiertas:

❌ NO se puede implementar  
✔ primero se debe trabajar en modo "definición"

---

## Regla 2 – Tests obligatorios

Toda implementación debe incluir tests.

Reglas:
- Crear o actualizar tests en tests/
- Validar comportamiento implementado
- No cerrar tarea sin tests

Excepciones:
- solo si se justifica explícitamente

---

## Regla 3 – Commits (formato obligatorio)

La IA NO debe ejecutar commits.

Debe sugerir:

- commit name
- descripción breve

Formato requerido:

commit name:
[IMP] mejoras o ajustes funcionales
[FIX] corrección de errores
[ADD] nuevas funcionalidades o módulos
[REM] eliminación de funcionalidades o código
[REF] refactor (sin cambios funcionales)
[MIG] migraciones entre versiones de Odoo
[UPD] actualizaciones de documentación o configuración
[WIP] trabajo en progreso (evitar en rama principal)

description:
Explicación breve del cambio realizado (1–3 líneas)

---

## Regla 4 – Criterio de cierre

Una tarea NO se considera completa si:

- no tiene tests
- no fue validada funcionalmente
- no es consistente con workflows / narrative
- requería actualización de documentación y esta no fue realizada o justificada

---

## Comando mínimo diario (uso recomendado)

Formato:

Avanzá con #ID | modo: X | opciones

Modos disponibles:

- definición → analizar y cerrar decisiones (sin código)
- implementación → escribir código
- revisión → auditar o validar implementación
- fix → corregir errores

Opciones comunes:

- con tests
- sin código
- validar lógica
- validar consistencia

---

## Ejemplos

- Avanzá con #001 | modo: definición | sin código
- Avanzá con #002 | modo: implementación | con tests
- Avanzá con #002 | modo: revisión
- Avanzá con #002 | modo: fix

---

## Template base

Contexto:
- Tarea backlog: #ID
- Tipo de cambio: [análisis / bugfix / nueva funcionalidad / refactor]
- Zona del sistema: [modelos, vistas, wizards]

Modo:
[definición / implementación / revisión / fix]

Objetivo funcional:
[qué querés lograr]

Criterios de aceptación:
[comportamientos esperados]

---

## Template 0 – Generar tarea de backlog

Contexto:
- Tipo de tarea: generación de backlog

Objetivo:
Convertir una idea en una entrada estructurada para todo.md

Instrucciones:
- Analizar la idea en lenguaje natural
- Determinar si corresponde:
  - [IDEA] → si hay decisiones abiertas
  - [TODO] → si ya es implementable
- No asumir decisiones no definidas

Salida requerida:

- ID (#XXX)
- Estado: [IDEA] o [TODO]

Contexto:
[descripción clara del problema o necesidad]

Decisiones abiertas (solo si aplica):
- ...

Criterios de aceptación (solo si aplica):
- ...

Impacto técnico:
- models
- views
- workflows
- tests
- documentación

Restricciones:
- No escribir código
- No implementar

---

## Template 1 – Definición (sin código)

Usar cuando hay ambigüedad o decisiones abiertas.

Salida requerida:

1. Alcance funcional
2. Escenarios posibles
3. Decisiones necesarias
4. Riesgos
5. Impacto en:
   - modelos
   - vistas
   - reglas de negocio
   - tests
   - documentación

⚠️ No escribir código

---

## Template 2 – Implementación

Regla operativa:
- No implementar si hay decisiones abiertas

Expectativas de análisis:

- Revisar:
  - docs/system_narrative.md
  - docs/system_overview.md
  - domain-rules/me/workflows.md
  - me/ai-context.md

Salida requerida:

1. Plan breve (archivos afectados)

2. Implementación

3. Tests:
   - crear o actualizar tests en tests/
   - explicar qué validan
   - indicar si se ejecutaron

4. Validación:
   - coherencia con workflows
   - coherencia con narrative

5. Documentación:
   - indicar qué archivos de documentación se ven impactados
   - indicar cuáles fueron actualizados efectivamente
   - si no se actualizó ninguno, justificar por qué
   - indicar si la task puede cerrarse sin cambios de documentación o no

6. Sugerencia de commit (obligatoria al cierre):

commit name:
[IMP]/[FIX]/[ADD]/[REM]/[REF]/[MIG]/[UPD]/[WIP] descripción corta

description:
Explicación breve del cambio

Regla adicional:
- Elegir la etiqueta que mejor represente el objetivo principal del cambio
- No ejecutar commits
- Siempre devolver commit name y description al finalizar

---

## Template 3 – Revisión

Objetivo:
Validar calidad e integridad de una implementación.

Salida requerida:

- Problemas detectados
- Riesgos
- Inconsistencias con:
  - narrative
  - workflows
- Gaps de tests
- Gaps de documentación

---

## Template 4 – Fix

Objetivo:
Corregir un error específico.

Salida requerida:

1. Causa raíz
2. Corrección
3. Tests asociados
4. Documentación:
   - indicar qué archivos de documentación se ven impactados
   - indicar cuáles fueron actualizados efectivamente
   - si no se actualizó ninguno, justificar por qué
5. Sugerencia de commit (obligatoria al cierre)

commit name:
[IMP]/[FIX]/[ADD]/[REM]/[REF]/[MIG]/[UPD]/[WIP] descripción corta

description:
Explicación breve del cambio

---

## Template 5 – Auditoría

Objetivo:
Detectar inconsistencias en el sistema completo.

Salida requerida:

- Hallazgos (alto / medio / bajo)
- Problemas en:
  - lógica
  - seguridad
  - tests
  - documentación
- Recomendaciones

---

## Reglas de uso

- No inventar comportamiento
- Priorizar código como fuente de verdad
- Marcar como "Uncertain" lo no definido
- No ejecutar commits
- Mantener consistencia con ai-context.md

---

## Flujo de trabajo recomendado

1. Crear o elegir tarea en todo.md
2. Ejecutar modo definición (si aplica)
3. Ejecutar modo implementación (con tests)
4. Ejecutar revisión
5. Actualizar documentación si aplica
6. Commit manual


## Regla adicional – Idioma del código y textos del sistema

Todo el código generado debe estar en inglés.

Aplica a:
- modelos
- campos
- métodos
- variables
- tests
- XML ids
- comentarios técnicos
- mensajes de error (`ValidationError`, `UserError`, etc.)
- labels técnicos o textos definidos en código/Python/XML que luego puedan traducirse

No escribir mensajes hardcodeados en español dentro del código fuente.
La localización al español debe resolverse mediante el mecanismo de traducciones de Odoo.

El español se usa solo para:
- documentación
- backlog
- descripciones funcionales