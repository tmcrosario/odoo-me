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
JUNCO gestionará procesos licitatorios. Cada proceso licitatorio puede
estar asociado a uno o más expedientes que ingresan por Mesa de Entradas.

Un proceso no nace vinculado a un único expediente fijo. A lo largo de
su historia puede incorporar nuevos expedientes. Ejemplo:

1. Ingresa por ME el expediente X (licitación privada).
2. Se crea o identifica en JUNCO un proceso licitatorio asociado a X.
3. La licitación queda anulada.
4. Ingresa por ME el expediente Y, que representa una nueva actuación
   o relanzamiento de esa misma licitación.
5. El expediente Y se incorpora al mismo proceso licitatorio.
6. El expediente X queda en el historial del proceso.
7. El expediente Y pasa a ser el expediente actual/vigente del proceso.

Principios arquitectónicos:
- ME es la puerta de entrada de los expedientes.
- JUNCO tiene su propia carga de datos y lógica, independiente de ME.
- JUNCO usa expedientes ya creados en ME como insumo del proceso.
- La relación es dinámica: un proceso puede acumular expedientes en el tiempo.
- Dentro del proceso siempre debe poder identificarse cuál es el expediente
  actual o vigente, y cuáles son históricos.

Decisiones abiertas:

1. Modelado de la relación proceso–expedientes
   - ¿La relación es una lista simple (Many2many) o una tabla intermedia
     con metadatos (ej. fecha de incorporación, motivo, estado)?
   - ¿Se registra el evento que motivó la incorporación de cada expediente?
     (inicio, anulación, relanzamiento, ampliación, etc.)

2. Identificación del expediente actual/vigente
   - ¿Se marca explícitamente con un campo booleano (is_current) en la
     relación, o se infiere por orden cronológico?
   - ¿Puede haber más de un expediente vigente simultáneamente, o siempre
     hay exactamente uno?
   - ¿Qué sucede si el expediente vigente se anula: el proceso queda sin
     expediente vigente hasta que ingrese uno nuevo?

3. Exclusividad del expediente entre procesos
   - ¿Un expediente puede pertenecer a más de un proceso licitatorio?
   - Si no, ¿quién valida esa restricción: ME, JUNCO, o ambos?

4. Visibilidad desde ME
   - ¿ME necesita mostrar referencia a JUNCO en el formulario del expediente?
   - ¿O la visibilidad es unidireccional: solo desde JUNCO hacia ME?
   - Si ME muestra referencia, ¿es solo informativa o permite navegar al proceso?

5. Eventos que disparan la incorporación de un nuevo expediente
   - ¿Qué estados o eventos del proceso habilitan agregar un nuevo expediente?
   - ¿El operador de JUNCO elige manualmente qué expediente incorporar,
     o ME "notifica" a JUNCO de expedientes candidatos?

6. Representación del historial
   - ¿El historial de expedientes se muestra dentro del proceso licitatorio
     como una línea de tiempo, una tabla, o solo un listado?
   - ¿Se requiere registrar quién incorporó cada expediente y cuándo?

Impacto técnico:
- models: estructura de la relación entre junco.proceso y me.document_exp
  (tabla intermedia vs. campo relacional directo, a definir)
- views: posible referencia en formulario de expediente de ME (a definir)
- workflows: eventos del proceso que implican incorporar un nuevo expediente
- tests: proceso con múltiples expedientes, cambio de vigente, historial
- documentación: actualizar ai-context.md y architecture_diagram.md

--------------------------------------------------
### #008 – Rediseño de vista form de expediente (fases de carga y fechas)
--------------------------------------------------

[TODO]

Contexto:
La vista form actual de me.document_exp muestra los campos en un orden
plano sin distinción conceptual entre origen administrativo, procedencia
física y fechas del trámite.

Se requiere reorganizar la carga del expediente en dos fases progresivas
y agregar el campo `intake_date` para registrar la recepción física del
expediente en Mesa de Entradas.

---- Fases del formulario ----

Fase 1 — Origen (siempre visible):
- Título "Origen" encima de `dependence_id`
- Campos visibles: `dependence_id`, `number`, `period`
- `dependence_id` representa el origen administrativo (DEM, TMC, CM)

Fase 2 — Procedencia (visible cuando is_origin_complete = True):
- Título "Procedencia" encima de `jurisdiction_dependence`
- Campos que se habilitan: `jurisdiction_dependence`, `document_type_id`,
  `intake_date`, y el resto de los campos existentes (temas, objeto, fojas…)
- `jurisdiction_dependence` representa la oficina de origen físico
- `document_type_id` se completa automáticamente con EXP, no editable
- `intake_date` es obligatorio y lo completa el operador manualmente

---- Campo is_origin_complete ----

Campo computed en me.document_exp.
Depende de: `dependence_id`, `number`, `period`.
Controla la progresión visual de Fase 1 a Fase 2.

No reemplaza ni modifica `is_valid`.
`is_valid` mantiene sus 5 dependencias originales:
(dependence_id, document_type_id, number, period, jurisdiction_dependence)

Motivo: completitud funcional del expediente y progresión visual de carga
son dos conceptos distintos. No mezclarlos.

---- Arquitectura de fechas ----

No todos los documentos en tmc.document tienen ingreso físico por ME.
La fecha de ingreso físico es un atributo del circuito, no del documento.
tmc.document no debe tener campo de ingreso físico.

Circuitos y campos:
- ME (expedientes):      `intake_date` en me.document_exp (nuevo)
- RAA (actos formales):  `entry_date` en raa.registry_aa (ya existe)
- Gestión documental:    no aplica el concepto

Los tres campos de fecha tienen semánticas distintas:
  `date`        = fecha propia del documento (la que figura en el papel)
  `create_date` = alta técnica del registro (Odoo, automático, no editable)
  `intake_date` = recepción física en Mesa de Entradas (editable, obligatorio)

El campo `entry_date` en tmc.document está comentado y no debe
descomentarse: mezclaría circuitos distintos en el modelo base.
El método _compute_entry_date que persiste en el código es deuda técnica.

---- Definición de intake_date ----

Nombre técnico:   intake_date
Modelo:           me.document_exp
Tipo:             fields.Date()
Obligatorio:      sí (required=True)
Default:          ninguno — el operador lo carga conscientemente
Editable:         sí, por el operador de ME
Fecha futura:     no permitida (constraint en me.document_exp)
Relación period:  no validada — un EXP/2023 puede ingresar en 2025
Ubicación en UI:  Fase 2, visible cuando is_origin_complete = True

Definición funcional:
  Fecha en que el expediente fue recibido físicamente en Mesa de
  Entradas del Tribunal Municipal de Cuentas.

Ejemplo:
  - Expediente llega físicamente: martes 2 de abril
  - Se carga en el sistema:       miércoles 3 de abril
  - intake_date = 2 de abril  (lo ingresa el operador)
  - create_date = 3 de abril  (automático, no editable)

---- Decisiones abiertas ----

Ninguna. La task está lista para implementación.

---- Criterios de aceptación ----

Modelo:
- [ ] Campo computed `is_origin_complete` en me.document_exp
      dependiente de: dependence_id, number, period
- [ ] Campo `intake_date` en me.document_exp:
      required=True, sin default, sin validación contra period
- [ ] Constraint en me.document_exp: intake_date no puede ser fecha futura

Vista:
- [ ] Grupo "Origen" visible siempre: dependence_id, number, period
- [ ] Grupo "Procedencia" visible solo cuando is_origin_complete = True:
      jurisdiction_dependence, document_type_id, intake_date,
      y el resto de los campos existentes
- [ ] document_type_id readonly en la vista (no editable manualmente)
- [ ] intake_date visible en Fase 2, obligatorio en la vista

Tests:
- [ ] is_origin_complete = True solo con los 3 campos de Fase 1 completos
- [ ] is_origin_complete = False si falta alguno de los 3
- [ ] intake_date rechaza fecha futura
- [ ] intake_date acepta fecha de año distinto al period
- [ ] Crear expediente sin intake_date falla por required

Impacto técnico:
- models: is_origin_complete, intake_date, constraint de fecha futura
- views: reorganización de grupos, títulos, visibilidad condicional,
         document_type_id readonly, intake_date en Fase 2
- workflows: create() no se modifica (intake_date sin default, el ORM
             rechazará el registro si no se provee — comportamiento estándar)
- tests: casos listados arriba
- documentación: actualizar ai-context.md (UI progresiva, campos de fecha)