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

[IDEA]

Contexto:
La vista form actual de me.document_exp muestra los campos en un orden
plano sin distinción conceptual entre origen administrativo, procedencia
física y fechas del trámite.

Se requiere reorganizar la carga del expediente en dos fases progresivas
y clarificar la semántica de los campos de fecha.

---- Cambios definidos ----

Fase 1 — Origen (siempre visible):
- Título "Origen" encima de `dependence_id`
- Campos visibles: `dependence_id`, `number`, `period`
- `dependence_id` representa el origen administrativo del expediente
  (DEM, TMC, CM)

Fase 2 — Procedencia (visible al completar los 3 campos de Fase 1):
- Título "Procedencia" encima de `jurisdiction_dependence`
- Campos que se habilitan: `jurisdiction_dependence`, `document_type_id`
- `jurisdiction_dependence` representa la oficina de origen físico
- `document_type_id` se completa automáticamente con EXP, no editable
- Al completar los 3 campos de Fase 1 también se habilita
  el resto de los campos existentes (temas, objeto, fojas, etc.)

---- Decisión cerrada: is_valid ----

`is_valid` no cambia su semántica ni sus 5 dependencias:
(dependence_id, document_type_id, number, period, jurisdiction_dependence)

La progresión visual de Fase 1 se controla con un campo computed separado
(nombre en inglés, a definir — tentativo: `is_origin_complete`), que depende
solo de: `dependence_id`, `number`, `period`.

Motivo: no mezclar completitud funcional del expediente con progresión
visual de carga inicial. Son dos conceptos distintos.

---- Análisis del campo `date` (fuente de verdad: código) ----

`date` se define en tmc.document como `fields.Date()` sin default.
En la vista de ME ya tiene semántica explícita:
  string="Fecha de inicio del trámite"
  help="Fecha en que inicia el trámite/documento"

Comportamiento observado en código:
- No participa en create(): no se pasa en vals al guardar el expediente.
  Queda vacío hasta que el operador lo complete manualmente.
- En write(): se extrae de vals y se actualiza vía SQL directo en
  _update_document_date() — bypassa la constraint _check_date_not_future.
- No tiene relación con la fecha de los movimientos automáticos.
  Los movimientos usan fields.Datetime.now() en create(), de forma
  completamente independiente.

Constraints heredadas de tmc.document que afectan a `date`:
- _check_date_not_future: no puede ser fecha futura (ME la bypassa).
- El año de `date` debe coincidir con `period` (excepto tipo CONV).

Campo `entry_date` en tmc.document (comentado en el código base):
- Existe como campo computado pero está desactivado:
  `# entry_date = fields.Date(compute="_compute_entry_date", readonly=True)`
- Lógica computada: deriva la fecha de raa.registry_aa.entry_date;
  si no existe, usa create_date como fallback.
- En la vista de ME también está comentado.
- No permite ingreso manual — es computed y readonly.

Conclusión:
- `date` = fecha de inicio del trámite (la del documento físico). Claro.
- Fecha de ingreso al TMC: no existe como campo editable en ME.
  `entry_date` existe en el modelo base pero está comentado, es computed
  y no cubre el caso de ingreso manual con fecha distinta a create_date.

---- Decisión abierta: fecha de ingreso al TMC ----

¿La fecha de ingreso al TMC debe ser:
  a) La fecha de carga en el sistema (create_date, automática, no editable)
  b) Un campo editable en me.document_exp que el operador complete
     con la fecha real de llegada física al Tribunal

Ejemplo concreto:
- Expediente llega físicamente: martes 2 de abril
- Se carga en el sistema: miércoles 3 de abril
- ¿Se debe poder registrar el martes 2 como fecha de ingreso?

Si la respuesta es (b):
- Nuevo campo en me.document_exp (nombre en inglés)
- Nombre tentativo: `intake_date`
- Campo editable, separado de `date` (fecha del documento)
- `entry_date` del modelo base no es reutilizable directamente:
  es computed, depende de RAA y no permite ingreso manual

Convención de nombres:
Todos los nombres técnicos de campos nuevos deben estar en inglés.

---- Criterios de aceptación (parciales — pendiente decisión de intake_date) ----

- [ ] Campo computed `is_origin_complete` en me.document_exp,
      dependiente de dependence_id + number + period
- [ ] Vista reorganizada: grupo "Origen" (Fase 1) y grupo "Procedencia" (Fase 2)
- [ ] Fase 2 controlada por `is_origin_complete`, no por `is_valid`
- [ ] `document_type_id` readonly en la vista (no editable manualmente)
- [ ] Test: is_origin_complete = True con los 3 campos; Fase 2 visible
- [ ] Definir e implementar campo de fecha de ingreso al TMC (pendiente)

Impacto técnico:
- models: nuevo campo `is_origin_complete` en me.document_exp;
  posible nuevo campo `intake_date` (a confirmar)
- views: reorganización de grupos, títulos, visibilidad por fase,
  document_type_id readonly
- workflows: sin impacto en create() salvo que se agregue intake_date
  con valor default o requerimiento de ingreso manual
- tests: test de is_origin_complete, actualizar test de is_valid si aplica
- documentación: actualizar ai-context.md (sección UI progresiva y campos)