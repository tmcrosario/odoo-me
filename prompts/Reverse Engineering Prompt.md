Estoy trabajando en un proyecto Odoo llamado "odoo-me".

Es un sistema orientado a la gestión de documentos administrativos dentro de una organización. En particular, para mi módulo `me`, el manejo de expedientes.

El objetivo de esta tarea es realizar un análisis arquitectónico profundo del módulo `me` para comprender cómo funciona actualmente el sistema antes de continuar su migración y evolución.

--------------------------------------------------
Contexto del sistema
--------------------------------------------------

El repositorio contiene dos módulos principales:

- `me` → Mesa de Entradas
- `raa` → Registro de Actos Administrativos

El módulo `me` gestiona principalmente:

- documentos (del tipo expediente)
- movimientos de documentos
- trazabilidad del flujo documental

El módulo `raa` gestiona el registro formal de actos administrativos.

IMPORTANTE:

- `raa` ya está implementado y no debe modificarse
- podés leer `raa` solo para entender el contexto general del sistema
- el foco exclusivo del análisis es `me`

--------------------------------------------------
Dependencia de sistema base
--------------------------------------------------

El sistema se apoya en un sistema base de gestión documental.

Modelo base principal:

`tmc.document`

Algunos modelos del módulo `me` (por ejemplo `document_exp.py`) utilizan herencia
sobre ese modelo base.

Por lo tanto:

- algunos nombres de modelos y archivos no deben cambiarse
- `me` extiende el sistema documental existente
- no debe asumirse que `me` redefine el modelo documental base

Para entender mejor el sistema documental base, revisá también:

- `docs/tmc_base_system.md`

Ese documento describe los modelos principales del sistema documental,
incluyendo:

- `tmc.document`
- `tmc.dependence`
- `tmc.document_type`
- `tmc.document_topic`
- `tmc.institutional_classifier`

Estos modelos pueden aparecer indirectamente en relaciones,
campos heredados, dominios o lógica del módulo `me`.

Si detectás dependencias con estos modelos, mencionarlas en el análisis.

--------------------------------------------------
Repositorio del sistema base
--------------------------------------------------

El modelo `tmc.document` pertenece a un repositorio separado:

`odoo-tmc`

Ese repositorio contiene el sistema documental base
utilizado por el módulo ME.

Si el código está disponible, revisá especialmente:

- `tmc/models/document.py`
- otros modelos dentro del módulo `tmc`

para entender:

- campos heredados por `document_exp`
- lógica base del documento
- posibles restricciones o comportamientos heredados.

Si parte del comportamiento del sistema depende de estos modelos,
mencionarlo explícitamente en el análisis.

--------------------------------------------------
Estado actual del proyecto
--------------------------------------------------

El módulo `me` proviene de una implementación previa en Odoo 14.

Actualmente el objetivo es:

- migrarlo a Odoo 19
- comprender completamente su arquitectura actual
- mejorar la documentación para desarrollo asistido con IA
- continuar el desarrollo del sistema

El sistema todavía está en evolución, por lo que algunas reglas pueden no estar completamente definidas.

--------------------------------------------------
Documentación existente a tener en cuenta
--------------------------------------------------

Antes de analizar el código, revisá la documentación actual del proyecto, especialmente:

- `docs/system_overview.md`
- `docs/models.md`
- `docs/model_registry.md`
- `docs/rules_business.md`
- `docs/coding_standards.md`
- `domain-rules/me/me_architecture.md`
- `me/ai-context.md`

Importante:

- usá estos archivos como hipótesis iniciales del sistema
- luego validalos o corregilos a partir del código real
- si encontrás inconsistencias entre documentación y código, señalalas explícitamente

--------------------------------------------------
Objetivo principal de esta tarea
--------------------------------------------------

Quiero que realices un reverse engineering del módulo `me`.

Tu tarea es analizar el código existente para inferir:

- arquitectura del sistema
- entidades principales
- relaciones
- workflow implícito
- lógica de negocio implementada

NO quiero que modifiques código.

NO quiero refactors.

Solo quiero análisis arquitectónico y funcional.

--------------------------------------------------
Alcance del análisis
--------------------------------------------------

Analizá principalmente:

- `me/models`
- `me/views`
- `me/security`
- `me/wizards`

También podés revisar `raa` para entender el contexto general, pero no propongas cambios en ese módulo.

--------------------------------------------------
Cosas que quiero que identifiques
--------------------------------------------------

Durante el análisis del módulo `me`, identificá:

1. Modelos definidos en el módulo
2. Herencias de modelos, especialmente con `tmc.document`
3. Relaciones entre modelos:
   - Many2one
   - One2many
   - Many2many
4. Campos importantes
5. Campos computados (`compute`)
6. Constraints (`_constraints`, `@api.constrains`, SQL constraints si existen)
7. Overrides de métodos importantes:
   - `create`
   - `write`
   - `unlink`
   - `name_get`
   - `default_get`
   - otros métodos relevantes
8. Métodos que implementan lógica de negocio
9. Dependencias entre modelos
10. Lógica relacionada con movimientos de documentos
11. Posible workflow del sistema
12. Cómo interactúa `me` con el sistema documental base
13. Qué rol cumplen las vistas en el flujo del sistema
14. Qué rol cumplen seguridad y grupos en el comportamiento del módulo
15. Campos heredados desde `tmc.document` que el módulo `me` utiliza directa o indirectamente

--------------------------------------------------
También analizá
--------------------------------------------------

Intentá detectar si existen:

- estados de workflow
- restricciones de edición
- lógica de routing de documentos
- lógica de trazabilidad
- lógica de auditoría o historial
- numeración o secuencias
- acciones de menú que revelen flujo funcional
- comportamiento implícito en dominios, contextos o acciones de vistas

Si el código no lo deja claro, indicarlo como:

`uncertain / pendiente de definición`

--------------------------------------------------
Metodología esperada
--------------------------------------------------

Quiero que distingas claramente entre tres niveles de conclusión:

1. Observed in code
   - comportamiento explícitamente visible en el código

2. Inferred from implementation
   - comportamiento probable deducido por estructura, relaciones o vistas

3. Uncertain / pending definition
   - aspectos no demostrables con el código actual

No mezcles estos tres niveles.

Cuando identifiques comportamiento relacionado con documentos,
considerá que parte de la lógica puede provenir del modelo base
`tmc.document`.

Si un campo o comportamiento parece depender de ese modelo base,
indicarlo explícitamente.

--------------------------------------------------
Después del análisis
--------------------------------------------------

Generá un documento llamado:

`ME Architecture Analysis Report`

El documento debe incluir las siguientes secciones.

--------------------------------------------------
1. Propósito del módulo ME
--------------------------------------------------

Descripción general del objetivo del módulo dentro del sistema.

--------------------------------------------------
2. Modelos detectados
--------------------------------------------------

Lista de modelos encontrados en el módulo.

Para cada modelo incluir:

- nombre técnico del modelo (`_name` o herencia relevante)
- archivo donde está definido
- propósito del modelo
- relaciones principales
- campos importantes
- métodos relevantes

--------------------------------------------------
3. Relaciones entre modelos
--------------------------------------------------

Explicar cómo se relacionan los modelos entre sí.

Especial atención a:

- `document_exp`
- `document_movement`
- `tmc.document`

Si corresponde, mostrar una representación simple tipo árbol o diagrama textual.

--------------------------------------------------
4. Flujo funcional inferido
--------------------------------------------------

Describir el flujo del sistema basado en el código.

Por ejemplo:

creación de documento  
↓  
registro en mesa de entradas  
↓  
movimientos del documento  
↓  
procesamiento interno

Aclarar siempre qué parte está observada y qué parte es inferida.

--------------------------------------------------
5. Lógica de negocio detectada
--------------------------------------------------

Listar métodos o partes del código donde haya reglas funcionales importantes.

Por ejemplo:

- validaciones
- restricciones
- automatismos
- comportamientos en create/write
- generación de movimientos
- bloqueo de acciones

--------------------------------------------------
6. Supuestos de diseño detectados
--------------------------------------------------

Identificar decisiones arquitectónicas implícitas en el código.

Por ejemplo:

- por qué se extiende `tmc.document`
- por qué existe `document_movement`
- qué responsabilidades parecen pertenecer a cada modelo

--------------------------------------------------
7. Inconsistencias entre documentación y código
--------------------------------------------------

Comparar el código con:

- `docs/models.md`
- `docs/rules_business.md`
- `domain-rules/me/me_architecture.md`
- `me/ai-context.md`

Indicar:

- qué partes de la documentación parecen correctas
- qué partes están incompletas
- qué partes deberían corregirse

--------------------------------------------------
8. Aspectos inciertos
--------------------------------------------------

Listar partes del sistema cuyo comportamiento no esté claro.

No inventes respuestas para cerrar huecos.

--------------------------------------------------
9. Impacto para la migración a Odoo 19
--------------------------------------------------

Detectar posibles puntos sensibles de migración como:

- uso de APIs antiguas
- vistas con `tree`
- uso de `attrs`
- patrones de Odoo 14 que cambian en Odoo 19
- campos o vistas que puedan requerir adaptación
- posibles dependencias implícitas del framework antiguo

--------------------------------------------------
10. Recomendaciones para documentación
--------------------------------------------------

Sin modificar código ni proponer refactors funcionales, indicá qué habría que actualizar en:

- `docs/models.md`
- `docs/rules_business.md`
- `domain-rules/me/me_architecture.md`
- `me/ai-context.md`

La idea es que este punto sirva para alinear la documentación con el código real.

--------------------------------------------------
Reglas importantes para tu análisis
--------------------------------------------------

- No inventar comportamiento que no esté en el código
- No proponer refactors todavía
- No proponer cambios en `raa`
- Marcar como `uncertain` lo que no esté claro
- No asumir que la documentación actual es totalmente correcta
- Priorizar el código como fuente principal de verdad
- Usar la documentación actual como contexto, no como prueba definitiva

--------------------------------------------------
Objetivo final
--------------------------------------------------

Este análisis servirá para:

- mejorar la documentación del sistema
- alinear documentación y código
- actualizar archivos como:

  - `docs/models.md`
  - `docs/rules_business.md`
  - `domain-rules/me/me_architecture.md`
  - `me/ai-context.md`

- preparar el módulo para migración a Odoo 19
- continuar el desarrollo del módulo `me` con mejor base arquitectónica