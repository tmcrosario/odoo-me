Quiero que generes un archivo llamado:

docs/architecture_diagram.md


Objetivo
--------------------------------------------------

El objetivo de este archivo es documentar la arquitectura del sistema
**odoo-me** de forma visual y sencilla.

El diagrama debe ayudar a entender rápidamente:

- cómo se relacionan los módulos
- cómo se relacionan los modelos principales
- cómo interactúa el sistema con el sistema documental base.


--------------------------------------------------
Contexto del sistema
--------------------------------------------------

El repositorio contiene dos módulos principales:

- `me` → Mesa de Entradas
- `raa` → Registro de Actos Administrativos

El sistema también depende de un sistema base de gestión documental
que provee el modelo:

tmc.document


Importante:

- el módulo `me` extiende el sistema documental base
- el módulo `raa` es independiente y no debe modificarse


--------------------------------------------------
Análisis requerido
--------------------------------------------------

Antes de generar el diagrama analizá:

me/models  
raa/models  

También revisá la documentación existente:

docs/system_overview.md  
docs/models.md  
docs/model_registry.md  
domain-rules/me/me_architecture.md  


Usá el código como fuente principal de verdad.


--------------------------------------------------
Qué debe mostrar el diagrama
--------------------------------------------------

El diagrama debe representar:

1. Sistema documental base
2. Módulo ME
3. Módulo RAA
4. Modelos principales
5. Relaciones principales entre modelos


En particular mostrar relaciones entre:

tmc.document  
me.document_exp  
me.document_movement  
raa.registry_aa


--------------------------------------------------
Formato del archivo
--------------------------------------------------

El archivo debe contener tres secciones.


--------------------------------------------------
1. System Architecture Overview
--------------------------------------------------

Un diagrama textual simple mostrando los módulos del sistema.

Ejemplo esperado:

Document Management System
    tmc.document
        │
        ▼
ME Module
    me.document_exp
        │
        ▼
    me.document_movement

RAA Module
    raa.registry_aa


--------------------------------------------------
2. Model Relationship Diagram
--------------------------------------------------

Un diagrama que muestre relaciones entre modelos.

Por ejemplo:

tmc.document
    │ (inherited / extended by)
    ▼
me.document_exp
    │ (one-to-many)
    ▼
me.document_movement


Si hay otras relaciones detectadas en el código,
incluírlas también.


--------------------------------------------------
3. Module Boundaries
--------------------------------------------------

Explicar brevemente qué responsabilidades tiene cada módulo:

ME  
RAA  
Base Document System


--------------------------------------------------
Importante
--------------------------------------------------

No inventar relaciones que no estén en el código.

Si alguna relación no está clara, marcarla como:

uncertain


--------------------------------------------------
Objetivo final
--------------------------------------------------

El archivo debe servir como **referencia visual rápida de la arquitectura**
para desarrolladores y agentes de IA.

Debe ser:

- claro
- simple
- fácil de mantener
- alineado con el código real.