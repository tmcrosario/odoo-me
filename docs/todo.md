# ME – Backlog técnico y funcional

--------------------------------------------------
### Regla 1 (obligatoria)
--------------------------------------------------

Si una tarea tiene decisiones funcionales abiertas,
NO se puede pasar a implementación.

Opciones:
- resolver primero en modo "definición"
- o documentar riesgo explícitamente

--------------------------------------------------
Estados:
--------------------------------------------------

[TODO]  pendiente
[IDEA]  necesita definición
[WIP]   en progreso
[DONE]  completado

--------------------------------------------------
### #001 – Estados de expediente
--------------------------------------------------

[IDEA]

Contexto:
El modelo document_exp no tiene workflow definido.

Decisiones abiertas:
- ¿Puede cerrarse un expediente?
- ¿Se puede modificar luego de cerrado?
- ¿Qué estados existen?

Impacto:
- models
- views
- reglas de negocio
- permisos

--------------------------------------------------
### #002 – Integridad de movimientos
--------------------------------------------------

[TODO]

Contexto:
Los movimientos representan la trazabilidad del documento.

Objetivo:
Validar que el sistema impida:
- movimientos sin documento
- duplicados
- inconsistencias de fecha

Criterios de aceptación:
- constraint en modelo
- validación backend
- test asociado

--------------------------------------------------
### #003 – Integración con RAA
--------------------------------------------------

[IDEA]

Contexto:
El sistema podría generar actos administrativos.

Decisiones abiertas:
- ¿La creación es automática?
- ¿Cuándo se dispara?
- ¿Qué datos se envían?

Impacto:
- integración entre módulos
- modelos relacionales

--------------------------------------------------
### #004 – Restricción de origen de expediente
--------------------------------------------------

[DONE]

Decisión:
El origen se restringe por domain en la vista.

Motivo:
Solución simple para MVP.

--------------------------------------------------
### #005 – Validación backend de origen
--------------------------------------------------

[TODO]

Objetivo:
Agregar validación en modelo.

Criterios:
- constraint
- mensaje claro
- test

--------------------------------------------------
### #006 – Nomenclador de dependencias del Tribunal
--------------------------------------------------

[DONE]

Contexto:
Los movimientos automáticos de expedientes dependen de que existan
dependencias específicas en la base de datos. Si no existen, los
movimientos se omiten silenciosamente sin aviso al operador.

Las dependencias requeridas por create() en me.document_exp son:
- TMC   (buscada por abbreviation='TMC')
- Mesa de Entradas (buscada por name ilike 'Mesa de Entradas')

---- Hallazgos ----

TMC:
- EXISTE en odoo-tmc-data como tmc_dependence_tmc
- name='TRIBUNAL MUNICIPAL DE CUENTAS', abbreviation='TMC'
- Incluida en el clasificador institucional (código 1.13.00,
  todos los clasificadores vigentes)
- El movimiento 1 (jurisdicción → TMC) SE CREA correctamente

Mesa de Entradas:
- NO EXISTE en el nomenclador (odoo-tmc-data/dependence.xml)
- El movimiento 2 (TMC → Mesa de Entradas) NUNCA SE CREA
  en ninguna instalación actual
- Falla silenciosa: sin error, sin aviso al operador

Riesgo de búsqueda por ilike:
- La búsqueda name ilike 'Mesa de Entradas' es frágil:
  si el nombre difiere o hay variantes, retorna un resultado
  inesperado o ninguno
- TMC se busca por abbreviation='TMC' — criterio más robusto
  Mesa de Entradas debería seguir el mismo patrón

---- Decisiones ----

1. Dependencias mínimas requeridas: TMC y Mesa de Entradas.
   TMC ya existe y está bien definida.
   Mesa de Entradas debe crearse.

2. Dónde agregar Mesa de Entradas:
   En odoo-tmc-data (dependence.xml), como subdependencia de TMC.
   Mismo patrón que tmc_dependence_tmc_sub.
   No se modifica odoo-tmc (modelo), solo los datos de referencia.

3. Abbreviation para Mesa de Entradas: 'ME'
   Permite buscar por abbreviation='ME' en lugar de name ilike.
   Consistente con el patrón de búsqueda de TMC.

4. Actualizar criterio de búsqueda en create():
   Reemplazar name ilike 'Mesa de Entradas' por abbreviation='ME'.
   Referencia: me/models/document_exp.py:139

5. Verificación en instalación:
   No se implementa hook en esta iteración.
   Corrección de datos es suficiente para desbloquear el flujo.

---- Criterios de aceptación ----

- [ ] Dependencia "Mesa de Entradas" agregada en odoo-tmc-data
      (dependence.xml) con abbreviation='ME', como subdependencia de TMC
- [ ] create() en me.document_exp actualizado: buscar por
      abbreviation='ME' en lugar de name ilike 'Mesa de Entradas'
- [ ] Test: al crear un expediente, se generan los 2 movimientos
      automáticos correctamente
- [ ] Verificar in_actual_nomenclator en instalación: TMC debe
      aparecer marcada como activa para ser seleccionable en el campo
      jurisdiction_dependence (si aplica el filtro)

Impacto:
- odoo-tmc-data: dependence.xml (nuevo registro)
- me/models/document_exp.py: línea 139 (criterio de búsqueda)
- tests

--------------------------------------------------
### #007 – Relación entre ME y el módulo JUNCO (Proceso Licitatorio)
--------------------------------------------------

[IDEA]

Contexto:
El módulo JUNCO gestionará procesos licitatorios. Su punto de partida
es un expediente existente en ME: un proceso licitatorio siempre se
origina en un expediente de Mesa de Entradas.

La carga de datos del proceso licitatorio es independiente de ME.

Cardinalidad definida:
- 1 expediente (me.document_exp) puede tener múltiples procesos licitatorios
- cada proceso licitatorio pertenece a un único expediente
- se requiere historial: un proceso puede quedar desierto, nulo o ser
  modificado, y luego iniciarse un nuevo proceso sobre el mismo expediente

Decisiones abiertas:
- ¿Dónde vive la relación? Opciones:
  a) JUNCO tiene un campo Many2one → me.document_exp (JUNCO depende de ME)
  b) ME tiene un campo One2many → junco.proceso (ME depende de JUNCO)
  c) La relación se resuelve sin dependencia directa entre módulos
     (ej. referencia por external_key u otro campo desacoplado)
- ¿ME necesita conocer los procesos licitatorios asociados a un expediente,
  o la visibilidad es solo desde JUNCO?
- ¿La vista de ME muestra un tab/resumen de procesos licitatorios?
- ¿Qué campos mínimos define un proceso licitatorio a efectos del vínculo
  con ME? (fecha, tipo, estado)
- ¿Los estados del proceso licitatorio están definidos?
  (desierto, nulo, adjudicado, en curso, etc.)
- ¿Existe un estado en me.document_exp que deba cambiar cuando
  se vincula un proceso licitatorio?

Impacto técnico:
- models: relación entre me.document_exp y junco.proceso (a definir)
- views: posible tab en formulario de expediente (a definir)
- workflows: ciclo de vida del proceso licitatorio y su relación con el expediente
- tests: creación de proceso sobre expediente existente, historial múltiple
- documentación: actualizar ai-context.md y architecture_diagram.md