# ME – Spec-driven development workflow

Este documento describe cómo está organizado el proyecto **ME (Mesa de Entradas)** para trabajar de forma **spec-driven** (basada en especificaciones) y no únicamente de forma ad-hoc.

El objetivo es que cualquier persona que trabaje en el sistema pueda:

- entender rápidamente **dónde están las reglas del sistema**,
- saber **qué documentación consultar antes de modificar algo**,
- seguir un **flujo claro para analizar e implementar cambios**.

Este enfoque también facilita el trabajo con **AI-assisted development** (por ejemplo con Claude).

---

# 1. Capas de documentación y reglas

El proyecto está organizado en varias capas, cada una con un rol claro.

---

## Arquitectura del sistema

Archivo:

domain-rules/me/me_architecture.md

Este archivo describe:

- los modelos principales del sistema ME
- cómo se relacionan entre sí
- la dependencia con el sistema base de documentos (`tmc.document`)
- principios arquitectónicos del módulo

Principios típicos:

- no duplicar entidades existentes
- preferir extender modelos existentes
- evitar crear nuevos modelos si el concepto puede representarse con campos o relaciones

---

## Normas técnicas y de estilo

Archivo:

domain-rules/me/coding_standards.md

Define:

- estilo de código (PEP8)
- idioma del código (inglés)
- convenciones de nombres
- cuándo actualizar documentación
- cuándo agregar tests

También incluye checklist para cambios que afectan:

- modelos
- vistas
- reglas de negocio
- seguridad

---

## Reglas Odoo y Odoo 19

Archivos:

ai-rules/odoo/odoo_common.mdc  
ai-rules/odoo/odoo19.mdc

Cubren buenas prácticas de desarrollo en Odoo:

- uso correcto del ORM
- diseño de modelos
- seguridad
- diseño de vistas
- convenciones específicas de Odoo 19

Ejemplos:

- evitar SQL directo cuando puede usarse ORM
- evitar lógica compleja en vistas
- usar correctamente `_()` para traducciones

---

## Reglas de negocio

Archivo:

docs/rules_business.md

Este archivo es la **fuente de verdad funcional** del sistema.

Aquí se documentan:

- reglas de documentos
- reglas de movimientos
- restricciones del workflow
- condiciones de edición o bloqueo

Si una regla funcional cambia, **este archivo debe actualizarse**.

---

## Modelo de datos documentado

Archivos:

docs/models.md  
docs/model_registry.md

### models.md

Describe:

- modelos principales
- campos importantes
- relaciones entre modelos

Puede incluir diagramas o ejemplos de flujo.

---

### model_registry.md

Lista autorizada de modelos `_name`.

Su objetivo es evitar que durante el desarrollo se creen modelos innecesarios.

Antes de introducir un nuevo modelo se debe verificar si el concepto puede representarse mediante:

- nuevos campos
- relaciones
- extensión de modelos existentes

---

## Prompts de ejemplo

Archivo:

docs/prompt_examples.md

Contiene plantillas para pedir a la IA:

- nuevas funcionalidades
- cambios de lógica
- correcciones de bugs
- auditorías de código
- revisiones de integridad del sistema

Estos prompts obligan a la IA a:

- consultar reglas
- revisar documentación
- analizar impacto antes de escribir código

---

## Backlog / TODO

Archivo:

docs/todo_me.md

Lista:

- ideas futuras
- mejoras posibles
- riesgos detectados
- deuda técnica

Cada entrada debería incluir:

- breve descripción
- impacto estimado
- prioridad

---

# 2. Skills: cómo trabajar

Además de reglas y documentación, el proyecto define **skills** que describen **cómo debe trabajarse en distintas situaciones**.

Esto ayuda a mantener consistencia durante el desarrollo.

---

## Nueva funcionalidad

Archivo:

skills/feature_development.md

Flujo recomendado:

1. Entender el pedido y clasificar el tipo de cambio.
2. Detectar impacto en:
   - modelos
   - vistas
   - seguridad
   - automatizaciones
   - documentación
3. Verificar impacto en reglas de negocio (`docs/rules_business.md`).
4. Verificar documentación que debe actualizarse.
5. Proponer un plan de implementación.
6. Generar código compatible con Odoo 19.
7. Cerrar con checklist de integridad.

---

## Corrección de bugs

Archivo:

skills/bugfix_workflow.md

Flujo:

1. reproducir el problema
2. localizar la causa
3. verificar reglas de negocio
4. decidir si el problema está en código o documentación
5. aplicar fix mínimo
6. actualizar documentación si corresponde
7. proponer tests si la regla afectada es importante

---

## Revisión de código

Archivo:

skills/code_review.md

Checklist de revisión:

- coherencia con arquitectura
- coherencia con reglas de negocio
- compatibilidad con Odoo 19
- seguridad y control de accesos
- necesidad de tests

---

# 3. Qué ocurre cuando se envía un prompt

Cuando se envía un prompt siguiendo `docs/prompt_examples.md`, el flujo esperado es:

---

## 1. Clasificar el tipo de pedido

El sistema debe determinar si el pedido es:

- nueva funcionalidad → usar `feature_development`
- corrección de bug → usar `bugfix_workflow`
- auditoría o revisión → usar `code_review`

---

## 2. Cargar contexto del sistema

Antes de proponer cambios se deben consultar:

domain-rules/me/me_architecture.md  
domain-rules/me/coding_standards.md  
ai-rules/odoo/odoo_common.mdc  
ai-rules/odoo/odoo19.mdc  
docs/rules_business.md  
docs/models.md  
docs/model_registry.md

---

## 3. Analizar impacto

Antes de escribir código se debe identificar:

- modelos afectados
- vistas afectadas
- seguridad
- posibles cambios en reglas funcionales

---

## 4. Verificar documentación

Se debe comprobar si el cambio:

- modifica reglas existentes
- introduce nuevos conceptos
- requiere actualizar modelos o diagramas

---

## 5. Proponer un plan

Antes de escribir código se debe presentar:

- impacto esperado
- cambios necesarios
- archivos afectados

Solo después se genera código.

---

## 6. Considerar tests

Si el cambio afecta reglas de negocio o modelo de datos:

- se deben proponer tests
- o justificar por qué no son necesarios

---

## 7. Cierre del cambio

La respuesta final debe incluir:

- archivos afectados
- impacto funcional
- documentación a actualizar
- tests sugeridos
- posibles riesgos o tareas pendientes

---

# 4. Dependencias del sistema

El módulo **ME** depende de un sistema base de documentos.

Modelo base:

tmc.document

El sistema ME extiende este modelo para agregar comportamiento específico de Mesa de Entradas.

Esto implica que:

- algunos campos y comportamientos provienen del sistema base
- ciertos nombres de modelos o archivos reflejan esta herencia
- no debe duplicarse lógica que ya pertenece al sistema base de documentos

---

# 5. Alcance actual del desarrollo

El foco actual del desarrollo es el módulo:

ME (Mesa de Entradas)

El repositorio también contiene el módulo:

RAA – Registro de Actos Administrativos

Sin embargo:

- RAA se considera **fuera del alcance actual**
- no deben proponerse cambios estructurales en ese módulo
- debe tratarse como una integración externa

---

# 6. Por qué este enfoque es spec-driven

Este enfoque es **spec-driven** porque el comportamiento esperado del sistema está descrito en documentos:

- arquitectura
- reglas de negocio
- modelo de datos

El flujo de desarrollo recomendado es:

1. leer la especificación
2. analizar impacto
3. actualizar la especificación si es necesario
4. implementar código coherente con la especificación

Esto permite que el sistema evolucione de forma controlada y mantenible.