Estoy trabajando con dos repositorios Odoo relacionados.

Repositorio 1 (base):
odoo-tmc

Repositorio 2 (extensión):
odoo-me


--------------------------------------------------
Relación entre repositorios
--------------------------------------------------

El repositorio `odoo-tmc` contiene el sistema base de gestión documental.

El modelo principal es:

tmc.document

Este modelo define la entidad base "documento" del sistema.


El repositorio `odoo-me` implementa el módulo **Mesa de Entradas (ME)**.

Este módulo extiende el sistema documental base.


Conceptualmente:

tmc.document
      ↓ extended by
document_exp
      ↓ tracked through
document_movement


--------------------------------------------------
Objetivo de esta tarea
--------------------------------------------------

Quiero que analices **ambos repositorios juntos**
para entender correctamente la arquitectura del sistema.

El análisis debe seguir este orden:


FASE 1 — Analizar sistema base (`odoo-tmc`)
--------------------------------------------

Revisar especialmente:

tmc/models/document.py

Identificar:

- definición del modelo `tmc.document`
- campos importantes
- relaciones
- constraints
- métodos relevantes
- lógica de numeración
- lógica de clasificación o dependencias


Explicar brevemente:

- qué representa el modelo `tmc.document`
- qué responsabilidades tiene dentro del sistema documental.



FASE 2 — Analizar extensión (`odoo-me`)
--------------------------------------------

Revisar:

me/models
me/views
me/security
me/wizards

Especial atención a:

document_exp
document_movement


Identificar:

- herencias de `tmc.document`
- campos agregados por ME
- lógica específica del módulo
- relaciones entre modelos
- posibles reglas de negocio.



FASE 3 — Arquitectura combinada
--------------------------------------------

Explicar cómo se combinan ambos repositorios.

Mostrar:

- qué responsabilidades quedan en el sistema base
- qué responsabilidades agrega el módulo ME

Explicar claramente:

- qué pertenece al sistema documental base
- qué pertenece a Mesa de Entradas.



FASE 4 — Flujo funcional del sistema
--------------------------------------------

Inferir el flujo del sistema completo.

Ejemplo conceptual:

documento creado en sistema base
↓
documento registrado en ME
↓
movimientos del documento
↓
procesamiento interno



FASE 5 — Riesgos arquitectónicos
--------------------------------------------

Detectar posibles problemas como:

- lógica duplicada entre repositorios
- dependencias implícitas
- herencias frágiles
- posibles conflictos en migración a Odoo 19.



--------------------------------------------------
Reglas importantes
--------------------------------------------------

- No inventar comportamiento que no esté en el código.
- Si algo depende del sistema base, indicarlo explícitamente.
- Distinguir entre:

Observed in code  
Inferred from implementation  
Uncertain / pending definition



--------------------------------------------------
Objetivo final
--------------------------------------------------

Generar un informe llamado:

Document System Architecture Analysis

El informe debe explicar claramente:

- arquitectura del sistema documental base
- arquitectura del módulo ME
- cómo interactúan ambos sistemas
- implicancias para la migración a Odoo 19.