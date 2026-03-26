# ME – Backlog técnico y funcional

Estados:
[TODO]
[IDEA]
[WIP]
[DONE]

------------------------------------

[IDEA] – Definir estados de expedientes

Contexto:
El modelo document_exp no parece tener un workflow formal.

Preguntas abiertas:
- ¿Un expediente puede cerrarse?
- ¿Se pueden agregar documentos luego de cerrado?
- ¿Cómo se representa el estado en document_exp?

Impacto técnico:
- reglas de negocio
- vistas
- permisos
- posibles campos nuevos

------------------------------------

[TODO] – Revisar integridad de document_movement

Contexto:
Los movimientos registran la trazabilidad de documentos.

Objetivo:
Verificar si el sistema impide:

- movimientos sin documento
- movimientos duplicados
- inconsistencias cronológicas

Impacto técnico:
- modelo document_movement
- posibles constraints
- reglas de negocio

------------------------------------

[IDEA] – Integración futura con RAA

Contexto:
Algunos documentos podrían terminar generando actos administrativos.

Preguntas abiertas:
- ¿Cómo se vincula document_exp con registry_aa?
- ¿Se crea automáticamente un registro en RAA?

Impacto técnico:
- integración entre módulos
- posibles campos relacionales



--------------------------------------------------
[IDEA] – Restricción de origen de expediente
--------------------------------------------------

Contexto:
Los expedientes en ME deben tener un origen (dependencia),
pero aún no está claro cómo restringirlo.

Preguntas:
- ¿Las dependencias válidas son fijas o configurables?
- ¿Depende del tipo de documento?
- ¿Depende del usuario?
- ¿Se valida solo en la vista o también en backend?

Opciones:
1. Lista fija en código
2. Configuración en modelo
3. Basado en tipo de documento

Impacto:
- models (validación)
- views (domain)
- rules_business.md
- system_overview.md


--------------------------------------------------
[DECISION] – Origen restringido por domain en vista
--------------------------------------------------

Decisión tomada:
El campo dependence_id se restringe mediante domain en la vista.

Motivo:
Solución simple y suficiente para primera versión.

Impacto:
- views
- system_overview.md

Siguiente paso:
Agregar validación backend (opcional en futuro)


--------------------------------------------------
[TODO] – Validación backend de origen
--------------------------------------------------

Descripción:
Agregar validación en modelo para asegurar que el origen sea válido.

Checklist:
- [ ] constraint en model
- [ ] mensaje de error claro
- [ ] test manual