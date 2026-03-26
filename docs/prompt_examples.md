These prompts are examples.
They should be adapted depending on the current development phase
of the ME module.

## ME – Prompt examples for AI-assisted development

This file contains reusable prompt templates to work with the
**ME (Mesa de Entradas)** module.

The prompts assume that the assistant has access to the project rules
and documentation:

- docs/system_overview.md
- docs/models.md
- docs/model_registry.md
- docs/rules_business.md
- docs/tmc_base_system.md
- domain-rules/me/me_architecture.md
- me/ai-context.md
- ai-rules/*
- skills/*


--------------------------------------------------
Base prompt template
--------------------------------------------------

Use this template as a starting point for any request.

Contexto:
- Tipo de cambio: [análisis / bugfix / nueva funcionalidad / migración / auditoría]
- Zona del sistema: [modelos, vistas o módulos involucrados]

Objetivo funcional:
[qué querés lograr y por qué]

Criterios de aceptación:
[comportamientos que deben cumplirse]


--------------------------------------------------
Prompt A – Analizar una parte del módulo
--------------------------------------------------

Contexto:
- Tipo de tarea: análisis de arquitectura
- Zona del sistema: modelo específico del módulo ME

Objetivo:
Quiero entender cómo funciona el modelo
y qué responsabilidades tiene dentro del sistema.

Criterios de aceptación:
- Explicar el propósito del modelo
- Explicar sus relaciones
- Explicar su rol en el flujo documental


--------------------------------------------------
Prompt B – Revisar lógica de movimientos
--------------------------------------------------

Contexto:
- Tipo de tarea: análisis funcional
- Zona del sistema: document_movement

Objetivo:
Quiero revisar si la implementación actual de movimientos
garantiza trazabilidad correcta de documentos.

Criterios de aceptación:
- Identificar reglas de creación de movimientos
- Identificar restricciones existentes
- Detectar posibles inconsistencias


--------------------------------------------------
Prompt C – Agregar campo a un modelo
--------------------------------------------------

Contexto:
- Tipo de cambio: nueva funcionalidad
- Zona del sistema: modelo existente

Objetivo:
Agregar un campo que permita almacenar información adicional
sobre el documento.

Criterios de aceptación:
- Campo visible en vistas relevantes
- No romper relaciones existentes
- Mantener coherencia con `tmc.document`


--------------------------------------------------
Prompt D – Migración a Odoo 19
--------------------------------------------------

Contexto:
- Tipo de tarea: migración técnica
- Zona del sistema: módulo ME

Objetivo:
Detectar partes del módulo que deben adaptarse
para Odoo 19.

Criterios de aceptación:
- Detectar vistas incompatibles (`tree`, `attrs`, etc.)
- Detectar APIs antiguas
- Identificar posibles refactors necesarios


--------------------------------------------------
Prompt E – Auditoría del módulo
--------------------------------------------------

Contexto:
- Tipo de tarea: auditoría técnica
- Alcance: módulo ME completo

Objetivo:
Detectar problemas potenciales en arquitectura
o inconsistencias entre código y documentación.

Criterios de aceptación:
- Identificar inconsistencias
- Identificar posibles mejoras
- Identificar documentación desactualizada