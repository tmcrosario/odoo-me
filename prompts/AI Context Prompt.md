Quiero que generes un archivo llamado:

me/ai-context.md

Este archivo servirá como contexto técnico para desarrollo asistido con IA
en el módulo ME.


--------------------------------------------------
Paso 1 — Analizar el código del módulo
--------------------------------------------------

Primero analizá completamente el módulo:

me/models  
me/views  
me/security  
me/wizards

También tené en cuenta que el módulo depende del sistema base de documentos
y en particular del modelo:

tmc.document


--------------------------------------------------
Paso 2 — Revisar documentación existente
--------------------------------------------------

Antes de generar el archivo, revisá la documentación existente del proyecto:

docs/system_overview.md  
docs/models.md  
docs/model_registry.md  
docs/rules_business.md  
domain-rules/me/me_architecture.md  


Usá esta documentación como **contexto inicial**, pero verificá
su consistencia con el código.

Si detectás inconsistencias entre código y documentación,
priorizá el comportamiento observado en el código.


--------------------------------------------------
Objetivo del archivo
--------------------------------------------------

El archivo debe resumir cómo funciona el módulo ME para que
una IA pueda entender rápidamente:

- qué hace el módulo
- qué modelos existen
- cómo se relacionan
- qué responsabilidades tiene cada modelo
- qué restricciones de diseño existen
- cómo se integra con el sistema documental base


El objetivo es que una IA pueda entender el módulo
**sin tener que leer todo el código del repositorio**.


--------------------------------------------------
Importante
--------------------------------------------------

No inventes comportamiento que no esté en el código.

Si algo no está claro, marcarlo como:

pending definition

Diferenciar entre:

- comportamiento observado en el código
- comportamiento inferido
- comportamiento no definido.


--------------------------------------------------
Estructura requerida del archivo
--------------------------------------------------

1. Module Overview

Explicación breve del propósito del módulo ME
dentro del sistema.


2. Relationship with Base Document System

Explicar cómo interactúa el módulo con `tmc.document`.

Indicar si los modelos del módulo:

- heredan de este modelo
- lo extienden
- o simplemente lo referencian.


3. Core Models

Describir los modelos principales detectados en el módulo:

me.document_exp  
me.document_movement

Para cada modelo incluir:

- propósito
- responsabilidades
- relaciones principales
- archivo donde está definido.


4. Conceptual Relationship

Mostrar cómo se relacionan los modelos.

Ejemplo esperado:

tmc.document  
    ↓ extension  
me.document_exp  
    ↓ movements  
me.document_movement  


5. Document Lifecycle (inferred)

Describir el flujo funcional inferido del sistema.

Ejemplo:

document created in base system  
↓  
registered in ME  
↓  
movement between units  
↓  
processing


6. Design Constraints

Reglas arquitectónicas importantes detectadas en el código.

Ejemplos posibles:

- ME extiende `tmc.document`
- `document_movement` mantiene trazabilidad
- movimientos deben referenciar un documento
- historial de movimientos no debería eliminarse


7. Current Development Status

Explicar que el módulo:

- proviene de una implementación en Odoo 14
- está siendo migrado a Odoo 19
- sigue en evolución.


8. Related Documentation

Indicar qué documentos contienen más detalle:

docs/models.md  
docs/model_registry.md  
domain-rules/me/me_architecture.md  
docs/rules_business.md  


9. Module Boundaries

Explicar qué cosas están fuera del alcance del módulo.

En particular:

RAA module.

Aclarar que:

- RAA puede leerse para entender contexto
- pero no debe modificarse.


--------------------------------------------------
Formato esperado
--------------------------------------------------

El archivo debe ser:

- claro
- conciso
- estructurado
- fácil de leer para IA

Debe servir como **referencia rápida de arquitectura**
antes de generar código dentro del módulo ME.