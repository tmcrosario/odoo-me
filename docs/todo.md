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

[DONE]

Objetivo:
Agregar validación en modelo.

Criterios:
- constraint
- mensaje claro
- test

Implementación:
- _validate_dependence(): valida que dependence_id.abbreviation esté en
  {'DEM', 'TMC', 'CM'}. Lanza ValidationError con mensaje claro.
- Llamado explícitamente en create() y write() cuando 'dependence_id' está
  en vals. Patrón elegido sobre @api.constrains porque dependence_id es
  un campo delegado (_inherits) cuyos triggers no se propagan al hijo.
- Tests: test_dependence_invalid_abbreviation_raises,
  test_dependence_valid_abbreviations_accepted.

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

[DONE]

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

--------------------------------------------------
### #009 – Selección jerárquica dependiente de jurisdicción
--------------------------------------------------

[DONE]

Contexto:
En la vista form de me.document_exp, `jurisdiction_dependence` permite
elegir la dependencia de jurisdicción del expediente (Many2one → tmc.dependence).
Se agrega un segundo campo dependiente que muestra solo las dependencias
hijas de la jurisdicción seleccionada (la dependencia específica que originó
el expediente dentro de esa jurisdicción).

---- Análisis del nomenclador ----

tmc.dependence: modelo plano, 191 registros. Sin parent_id, sin jerarquía propia.

tmc.dependence_order: 197 registros. Campos relevantes:
  - dependence_id → tmc.dependence (qué dependencia es)
  - parent_id     → tmc.dependence (cuál es su padre)
  - code          → código jerárquico X.XX.XX (3 segmentos, zero-padded)

La jerarquía se obtiene consultando tmc.dependence_order donde
parent_id = jurisdiction_dependence.id, y mapeando .dependence_id.

Las jurisdicciones permitidas (DEM, TMC, CM) tienen o tendrán hijos
en el nomenclador:
  - DEM (1.02.00): 8 hijos actuales
  - CM: tiene hijos
  - TMC (1.13.00): 11 dependencias internas cargadas por #010
    (rango 1.13.80–1.13.89). El campo tendrá opciones disponibles
    cuando jurisdiction_dependence = TMC.

Nota sobre codificación de dependencias propias de TMC:
  El campo code en tmc.dependence_order usa exclusivamente 3 segmentos (X.XX.XX).
  No usar 4 segmentos (1.13.01.01) para dependencias propias de TMC.
  Usar el rango reservado 1.13.80–1.13.99 para dependencias internas de TMC.
  #010 usó 1.13.80–1.13.89. Quedan slots 1.13.90–1.13.99 para incorporaciones
  futuras. Motivo: mantener consistencia con el formato establecido, y reservar
  un rango poco probable de colisión con el nomenclador oficial externo.
  El campo code no afecta la búsqueda de hijos (que usa parent_id).

---- Decisiones ----

1. El campo apunta a tmc.dependence (no a tmc.dependence_order).
   Motivo: consistencia con jurisdiction_dependence, semántica correcta,
   el usuario ve el nombre de la dependencia, no el código.

2. Domain del campo hijo: campo computed auxiliary allowed_sub_dependence_ids
   (Many2many, compute), que consulta tmc.dependence_order por parent_id
   y mapea .dependence_id. Domain en vista referencia ese campo.
   Patrón consistente con allowed_dependence_ids ya existente en el modelo.

3. Nombre técnico: source_dependence_id
   (Many2one → tmc.dependence, required=False)
   Nombre en inglés, sufijo _id estándar Odoo, sin colisión con campos
   de movimientos (origin_dependence_id, destination_dependence_id).

4. Label visible: "Repartición"

5. Obligatorio: No.
   Motivo: la jurisdicción puede ser suficiente en algunos casos.

6. Auto-limpieza: Sí, vía onchange sobre jurisdiction_dependence.
   Si cambia la jurisdicción, source_dependence_id se limpia para evitar
   datos inconsistentes.

7. Impacto en movimientos automáticos: ninguno en esta tarea.
   Los movimientos en create() siguen usando jurisdiction_dependence
   como origen del movimiento 1. source_dependence_id no se incorpora.

---- Criterios de aceptación ----

Modelo:
- [ ] Campo source_dependence_id: Many2one(tmc.dependence, required=False)
      en me.document_exp
- [ ] Campo computed allowed_sub_dependence_ids: Many2many(tmc.dependence),
      depende de jurisdiction_dependence; consulta tmc.dependence_order
      donde parent_id = jurisdiction_dependence.id
- [ ] Onchange sobre jurisdiction_dependence que limpia source_dependence_id

Vista:
- [ ] source_dependence_id en Fase 2, debajo de jurisdiction_dependence,
      con string="Repartición"
- [ ] Domain del campo referencia allowed_sub_dependence_ids
- [ ] Visible cuando is_origin_complete = True

Tests:
- [ ] source_dependence_id se filtra a hijos de la jurisdicción seleccionada
- [ ] source_dependence_id se limpia al cambiar jurisdiction_dependence
- [ ] Expediente sin source_dependence_id se crea sin error (campo opcional)

Impacto técnico:
- models: source_dependence_id, allowed_sub_dependence_ids, onchange
- views: campo nuevo en Fase 2, domain dependiente de jurisdicción
- workflows: sin cambios en create() ni movimientos automáticos
- tests: casos listados arriba
- documentación: actualizar ai-context.md y workflows.md (Fase 2)

Nota:
Las dependencias internas de TMC (Mesa de Entradas y 10 áreas adicionales)
fueron cargadas en #010. El campo source_dependence_id tendrá opciones
disponibles para TMC desde el momento en que #010 esté implementada.

--------------------------------------------------
### #010 – Cargar dependencias internas de TMC en el nomenclador
--------------------------------------------------

[DONE]

Contexto:
La task #009 agrega el campo source_dependence_id en me.document_exp,
que filtra dependencias hijas de jurisdiction_dependence a través de
tmc.dependence_order. Para que ese campo funcione cuando la jurisdicción
sea TMC, deben existir dependencias internas de TMC cargadas en el
nomenclador con parent_id = tmc_dependence_tmc.

---- Estructura del nomenclador en 1.13.xx ----

Registros existentes bajo 1.13.xx (nomenclador oficial externo):

  1.13.00  →  dependence_id: tmc_dependence_tmc (TRIBUNAL MUNICIPAL DE CUENTAS, abbr='TMC')
               parent_id: tmc_dependence_adm (ADMINISTRACIÓN CENTRAL)
               — nodo raíz de TMC en el organigrama oficial

  1.13.01  →  dependence_id: tmc_dependence_tmc_sub (Tribunal Municipal de Cuentas, sin abbr)
               parent_id: tmc_dependence_tmc
               — entrada oficial existente del nomenclador externo, hijo directo de TMC

Las nuevas dependencias internas se agregan como entradas adicionales dentro del
rango reservado 1.13.80–1.13.99, sin interferir con los códigos oficiales existentes.
Deben tener:
  - parent_id = tmc_dependence_tmc  (mismo que 1.13.01)
  - code dentro del rango 1.13.80–1.13.99

---- Distinción importante ----

tmc_dependence_tmc (tmc.dependence):
  Registro de la entidad "TRIBUNAL MUNICIPAL DE CUENTAS", abbreviation='TMC'.
  Es el padre al que se vinculan los nuevos registros via parent_id.

tmc_dependence_order_1_13_00 (tmc.dependence_order):
  Es la representación de TMC en el organigrama jerárquico (código 1.13.00).
  No es el padre funcional de las nuevas entradas — lo es la dependencia en sí.

---- Listado confirmado de dependencias internas ----

Todas son hijas directas de TMC (parent_id = tmc_dependence_tmc).
No hay subniveles internos en esta iteración.

  Código    Nombre                              Abbr   XML ID (propuesto)
  -------   ---------------------------------   ----   --------------------------
  1.13.80   Mesa de Entradas                    ME     tmc_dependence_me         ← ya existe en dependence.xml
  1.13.81   Vocalía                             VOC    tmc_dependence_voc
  1.13.82   Secretaría de Vocalía               SEC    tmc_dependence_sec
  1.13.83   Fiscalía de Cuentas                 FC     tmc_dependence_fc
  1.13.84   Contadores Fiscales                 CF     tmc_dependence_cf
  1.13.85   Dirección de Innovación y Calidad   DIC    tmc_dependence_dic
  1.13.86   Dirección de Asuntos Legales        DAL    tmc_dependence_dal
  1.13.87   Dirección de Asuntos Técnicos       DAT    tmc_dependence_dat
  1.13.88   Dirección de Coordinación y Despacho DCD   tmc_dependence_dcd
  1.13.89   Dirección Administrativa Financiera DAF    tmc_dependence_daf
  1.13.90   Asistentes de Fiscalía de Cuentas   AFC    tmc_dependence_afc

  Slots libres: 1.13.91–1.13.99 (9 disponibles para futuras incorporaciones)

---- Criterios de aceptación ----

Data (odoo-tmc-data):
- [ ] Las 10 dependencias nuevas (VOC, SEC, FC, CF, DIC, DAL, DAT, DCD, DAF, AFC)
      existen en dependence.xml con name y abbreviation correctos
- [ ] Las 11 dependencias (ME + 10 nuevas) tienen registro en dependence_order.xml con:
      - parent_id = tmc_dependence_tmc
      - code en el rango 1.13.80–1.13.99 según la tabla
- [ ] ME (tmc_dependence_me) solo requiere su entrada en dependence_order.xml
      — ya existe en dependence.xml

Tests:
- [ ] Al buscar hijos de TMC en tmc.dependence_order, se retornan las 11 dependencias
- [ ] Las dependencias son recuperables con:
      tmc.dependence_order.search([('parent_id', '=', tmc_id)])

Impacto técnico:
- data: odoo-tmc-data/dependence.xml (10 registros nuevos) y
        odoo-tmc-data/dependence_order.xml (11 registros nuevos)
- tests: verificar que las dependencias aparecen en el filtro de #009
- documentación: sin impacto directo

--------------------------------------------------
### #011 – Responsable operativo en movimientos de expediente
--------------------------------------------------

[IDEA]

Nota de implementación:
El modelo base me.document_movement y la pestaña "Movimientos" en la
vista form están implementados (commit 7d6208f, [ADD] task #011 exp
movements). Esta task define la evolución siguiente: enriquecer los
movimientos con información del responsable operativo (receptor físico
del expediente), que es distinto del usuario de sesión (user_id).

Contexto:
me.document_movement registra la trazabilidad del expediente entre
dependencias. El modelo actual tiene:
  - expediente_id       → me.document_exp
  - date                → Datetime (default: now)
  - origin_dependence_id  → tmc.dependence
  - destination_dependence_id → tmc.dependence
  - user_id             → res.users (default: usuario de sesión)

user_id registra quién cargó el movimiento en Odoo, no necesariamente
quién entregó o recibió físicamente el expediente.

El usuario quiere poder reflejar algo como:
  - Origen: Mesa de Entradas
  - Destino: Vocalía
  - Usuario responsable / receptor: Juan Pérez

---- Hallazgos del análisis técnico ----

Tres estructuras coexisten sin vínculo entre sí:

1. res.users (Odoo)
   — cuenta de sesión, ya presente en el movimiento como user_id
   — no tiene relación declarada con tmc.hr.employee

2. tmc.hr.employee (custom HR)
   — modelo propio del TMC: nombre, legajo, email, puesto, oficina
   — office_id → tmc.hr.office (pertenece a una oficina)
   — NO tiene user_id ni vínculo con res.users

3. tmc.hr.office (custom HR)
   — unidad organizacional con jerarquía (parent_id)
   — employee_ids (One2many → tmc.hr.employee)
   — manager_id (→ tmc.hr.employee)
   — NO tiene vínculo con tmc.dependence

Consecuencia:
  tmc.hr.office y tmc.dependence representan dimensiones distintas
  del mismo organismo. Una es la estructura organizacional de RRHH
  (quién trabaja dónde, bajo qué jefatura). La otra es el nomenclador
  institucional administrativo (qué áreas existen para fines documentales).
  No hay FK entre ambas en el código actual.

  Un movimiento hoy: "el expediente pasó de dependencia A a dependencia B,
  y fue cargado por el usuario de sesión X."
  Un movimiento futuro podría incluir: "lo recibió el empleado Y de la
  oficina Z."

---- Decisiones abiertas ----

1. Semántica del movimiento
   - ¿Qué representa exactamente un movimiento?
   - ¿Es un evento de transferencia formal (dependencia → dependencia),
     un evento operativo (persona → persona), o ambos?
   - ¿Debe quedar registrado quién entregó (origen) y quién recibió
     (destino), o solo uno de ellos?

2. Suficiencia de user_id actual
   - ¿user_id (res.users, el que cargó el movimiento) es suficiente
     como trazabilidad operativa?
   - ¿O se requiere distinguir entre "quién cargó en el sistema" y
     "quién recibió físicamente el expediente"?

3. Qué entidad representa al responsable
   - ¿res.users (cuenta Odoo)?
   - ¿tmc.hr.employee (empleado del TMC, sin cuenta Odoo)?
   - ¿tmc.hr.office (oficina que recibe, sin persona específica)?
   - ¿Una combinación (oficina + empleado receptor, derivado de la oficina)?

4. Relación entre tmc.hr.office y tmc.dependence
   - ¿Existe correspondencia funcional entre una oficina (HR) y una
     dependencia (nomenclador)? ¿Es 1:1, 1:N, o independiente?
   - ¿Debería modelarse ese vínculo para permitir derivar la oficina
     desde la dependencia destino, o son mundos separados que no deben
     cruzarse en esta capa?

5. Asignación del responsable
   - ¿El operador selecciona manualmente al receptor en el movimiento?
   - ¿O se deriva automáticamente del usuario de sesión o de la oficina
     asociada a la dependencia destino?
   - ¿Qué pasa con los movimientos automáticos (los 2 que genera create())?

6. Obligatoriedad
   - ¿El campo de receptor/responsable es obligatorio o opcional?
   - ¿Los movimientos automáticos del create() tendrían receptor?

7. Impacto en trazabilidad y auditoría
   - ¿La trazabilidad operativa debe aparecer en la vista del expediente?
   - ¿Como lista de movimientos con receptor visible?
   - ¿Genera algún tipo de notificación o acuse?

Decisiones técnicas que dependen de las anteriores:
   - si agregar receiver_employee_id (tmc.hr.employee) o receiver_office_id
     (tmc.hr.office) o ambos al modelo me.document_movement
   - si vincular tmc.hr.office con tmc.dependence (nuevo campo en alguno)
   - si user_id pasa a ser "quien cargó" vs "quien es responsable"
   - si el domain del receptor depende de la dependencia destino

Impacto técnico:
- models: me.document_movement y posiblemente tmc.hr.office o tmc.dependence
- views: formulario de movimiento y/o vista del expediente
- workflows: create() automático, movimientos manuales
- tests: trazabilidad operativa, asignación de receptor
- documentación: actualizar ai-context.md y workflows.md

--------------------------------------------------
### #012 – Comportamiento condicional de jurisdicción y repartición
--------------------------------------------------

[IDEA]

Contexto:
El campo jurisdiction_dependence actualmente no tiene domain filter en la
vista — muestra las 191 dependencias del nomenclador. Tampoco existe
comportamiento diferenciado según la dependencia de origen elegida en Fase 1.

Se definen tres reglas funcionales que condicionan la visibilidad y el valor
de jurisdiction_dependence y source_dependence_id según el valor de
dependence_id:

---- Reglas ----

1. Expedientes del TMC — auto-asignación de jurisdicción
   Cuando dependence_id.abbreviation == 'TMC', jurisdiction_dependence
   debe asignarse automáticamente a "TRIBUNAL MUNICIPAL DE CUENTAS"
   (tmc_dependence_tmc) y ser readonly para el operador.
   Si el operador cambia dependence_id (Fase 1), jurisdiction_dependence
   se limpia y vuelve a ser editable.

2. Expedientes del Concejo Municipal — ocultamiento de campos
   Cuando dependence_id.abbreviation == 'CM', los campos
   jurisdiction_dependence y source_dependence_id no deben mostrarse.
   Motivo: en ese contexto esos campos no aplican.

3. Campo jurisdicción restringido a nodos madre del nomenclador
   jurisdiction_dependence debe mostrar solo las dependencias que son
   nodos padre en el nomenclador institucional (jurisdicciones madre),
   no subdependencias. Las subdependencias (reparticiones, oficinas,
   direcciones internas) deben aparecer exclusivamente en
   source_dependence_id, filtradas por la jurisdicción elegida.

---- Decisiones abiertas ----

A. Definición técnica de "jurisdicción madre"
   El modelo tmc.dependence es plano. La jerarquía está en
   tmc.dependence_order. Las "madres" son dependencias que tienen
   hijos en ese modelo (aparecen como parent_id de otros registros)
   y cuyo código termina en .00 (e.g., 1.02.00, 1.13.00).

   Opciones técnicas:
   - Lista fija hardcoded (igual que el filtro de dependence_id):
     simple, requiere mantenimiento manual si el nomenclador crece.
   - Campo computed que consulta tmc.dependence_order:
     más dinámico, requiere definir el criterio exacto de "madre".
   - Flag is_jurisdiction en tmc.dependence (en odoo-tmc):
     más limpio, pero toca el módulo base.

   Esta decisión determina cómo se filtra el domain de
   jurisdiction_dependence y bloquea la implementación hasta cerrarse.

B. Constraint required=True de jurisdiction_dependence cuando CM
   jurisdiction_dependence tiene required=True en el modelo.
   Ocultarlo sin resolver ese constraint provoca que create() falle.

   Opciones:
   - Auto-asignar a la dependencia CM misma al ocultar el campo:
     satisface el required sin cambiar el modelo; simple pero semánticamente
     impreciso (jurisdiction = dependence en ese caso).
   - Cambiar required=False y agregar constraint condicional:
     campo obligatorio solo cuando dependence_id.abbreviation != 'CM'.
     Requiere cambio en el modelo.

   Esta decisión bloquea las reglas 1 y 2 hasta cerrarse.

---- Impacto técnico ----

- models: onchange sobre dependence_id para auto-asignar o limpiar
          jurisdiction_dependence; posible cambio de required;
          posible computed field para domain de jurisdicciones madre
- views: readonly/invisible condicionales según dependence_id;
         domain filtrado en jurisdiction_dependence
- workflows: actualizar Workflow 1 Fase 2 y Workflow 6 Fase 2
- tests: auto-asignación TMC, bloqueo de edición manual, ocultamiento CM,
         filtro de jurisdicciones madre en el domain
- documentación: ai-context.md, workflows.md, system_narrative.md

--------------------------------------------------
### #013 – Selección de subtema en el campo asunto
--------------------------------------------------

[DONE]

Contexto:
El campo "Asunto" en el formulario de expediente muestra solo
main_topic_ids (temas generales, nivel 1). El campo secondary_topic_ids
(subtemas, nivel 2) existe en tmc.document con domain y onchange ya
definidos, pero no está expuesto en la vista de me.document_exp.

El operador necesita poder elegir tema Y subtema al completar el asunto.
Ejemplo: tema "Licitación" → subtema "Privada" o "Pública".

---- Análisis técnico del modelo heredado ----

tmc.document ya tiene los siguientes campos (accesibles en me.document_exp
vía _inherits):

  document_topic_ids:
    related field — temas disponibles para dependence_id del documento
    (todos los temas asociados a esa dependencia vía dependence_id.document_topic_ids)

  main_topic_ids:
    Many2many(tmc.document_topic)
    domain: [('parent_id', '=', False), ('id', 'in', document_topic_ids)]
    → solo temas raíz (nivel 1, sin parent)

  secondary_topic_ids:
    Many2many(tmc.document_topic)
    domain: [('parent_id', 'in', main_topic_ids)]
    → subtemas de los temas seleccionados

  _onchange_main_topic_ids (en tmc.document):
    → limpia secondary_topic_ids al cambiar main_topic_ids
    → retorna domain dinámico para secondary_topic_ids
    → este comportamiento se hereda en me.document_exp vía _inherits

La ME view actualmente solo muestra main_topic_ids con string="Asunto".
secondary_topic_ids no está en la vista.
El mecanismo de filtrado y limpieza ya existe en el módulo base.

---- Decisiones ----

1. secondary_topic_ids es opcional.
   No todo tema tiene subtemas definidos. El operador puede completar el
   asunto con solo el tema general.

2. Label visible: "Subtema".

3. Widget: many2many_tags (igual que main_topic_ids).

4. Visibilidad: visible solo cuando main_topic_ids no está vacío.
   Si no hay tema seleccionado, el subtema no aplica.

5. Sin cambios en el modelo.
   secondary_topic_ids ya existe en tmc.document con domain correcto.
   No se re-declara en me.document_exp.

---- Criterios de aceptación ----

Vista:
- [ ] Campo secondary_topic_ids en Fase 2, debajo de main_topic_ids,
      con string="Subtema", widget="many2many_tags"
- [ ] Invisible cuando main_topic_ids está vacío

Comportamiento:
- [ ] Al cambiar main_topic_ids, secondary_topic_ids se limpia
      (onchange ya existe en tmc.document, hereda automáticamente)
- [ ] Si el tema no tiene subtemas definidos, el campo aparece vacío
      y el operador no puede seleccionar valores

Tests:
- [ ] secondary_topic_ids filtra correctamente a hijos del tema elegido
- [ ] secondary_topic_ids se limpia al cambiar main_topic_ids
- [ ] Expediente creado sin secondary_topic_ids no falla (campo opcional)
- [ ] Expediente creado con secondary_topic_ids lo persiste correctamente

Impacto técnico:
- models: sin cambios (campo ya existe en tmc.document)
- views: agregar secondary_topic_ids en Fase 2 en
         me/views/document_exp_views.xml, debajo de main_topic_ids
- workflows: actualizar Workflow 1 paso 6 (mención de subtema)
- tests: casos listados arriba
- documentación: ai-context.md (Fase 2 campos), system_narrative.md (sección 3.3)

--------------------------------------------------
### #014 – Nomenclador de temas y subtemas para expedientes del TMC
--------------------------------------------------

[DONE]

Contexto:
El modelo tmc.document_topic define los temas (nivel 1) y subtemas (nivel 2)
disponibles para clasificar documentos. Cada dependencia en tmc.dependence
tiene un campo document_topic_ids (Many2many) que determina qué temas son
seleccionables cuando esa dependencia es el origen del documento.

En tmc.document, el campo document_topic_ids es un related sobre
dependence_id.document_topic_ids. El domain de main_topic_ids filtra a los
temas raíz de ese conjunto. Si una dependencia no tiene temas asignados,
el campo asunto queda vacío y el operador no puede seleccionar ningún tema.

---- Análisis técnico ----

Módulo y datos:
  - Modelo: tmc.document_topic, definido en odoo-tmc
  - Datos maestros: odoo-tmc-data/tmc_data/data/tmc/document_topic.xml
    (más de 150 registros, noupdate="1", forcecreate="false")
  - Vínculo temas ↔ dependencias: configurado en
    odoo-tmc-data/tmc_data/data/tmc/dependence.xml
    mediante document_topic_ids en cada registro de tmc.dependence

Estado actual de TMC:
  tmc_dependence_tmc (TRIBUNAL MUNICIPAL DE CUENTAS) NO tiene
  document_topic_ids asignado en dependence.xml.
  Consecuencia: para expedientes con dependence_id = TMC, el campo
  "Asunto" (main_topic_ids) devuelve conjunto vacío — el operador
  no puede seleccionar ningún tema.

  El tema raíz tmc_document_topic_tmc ("Tribunal de Cuentas") existe en
  document_topic.xml pero no está vinculado a tmc_dependence_tmc y no
  tiene subtemas. No se usa ni se reutiliza en esta task.

Relación con #013:
  #013 resuelve la UX: exponer secondary_topic_ids en la vista.
  Esta task (#014) resuelve los datos: qué temas existen y están
  disponibles para TMC. Son independientes entre sí, pero #014 es
  prerequisito funcional de #013 cuando la dependencia sea TMC —
  sin los datos, #013 no tiene contenido que mostrar.

---- Temas y subtemas a cargar ----

Origen funcional: opciones del sistema viejo de Mesa de Entradas,
reinterpretadas en estructura tema + subtema:

  Sistema viejo → Estructura nueva
  ---------------------------------
  Licitación Pública           → Licitación / Pública        (ambos ya existen, solo vincular)
  Licitación Privada           → Licitación / Privada        (ambos ya existen, solo vincular)
  Lic. Adjunta Documentacion   → Licitación / Documentación  (subtema nuevo)
  Lic. Fórmula Descargo        → Licitación / Descargo       (subtema nuevo)
  Lic. Fórmula Impugnación     → Licitación / Impugnación    (subtema nuevo)
  Notas externas               → Nota / Externa              (tema y subtemas nuevos)
  [nueva categoría]            → Nota / Interna              (subtema nuevo)
  Notas originadas en el TMC   → Nota / Originada en el TMC  (subtema nuevo)
  Informes / Actuaciones       → Nota / Informe               (subtema nuevo)

---- Definición funcional del tema "Nota" ----

Tema raíz: "Nota"

Subtemas confirmados y sus significados:

  Externa:
    Nota que ingresa desde afuera del Tribunal.
    Origen: externo al TMC.

  Interna:
    Nota que circula entre áreas o reparticiones dentro del Tribunal.
    Origen y destino: ambos internos al TMC.
    No sale físicamente del organismo.

  Originada en el TMC:
    Nota generada por el Tribunal que sale físicamente hacia afuera
    y luego reingresa en un expediente a través de Mesa de Entradas.
    Aunque comparte origen interno con "Interna", su recorrido es
    distinto: tiene trayectoria externa y reingreso posterior.
    Caso operativo específico que debe quedar diferenciado de
    una nota interna común.

Los cuatro subtemas son conceptualmente distintos y se crean por separado.

---- Resumen de registros nuevos a crear ----

  document_topic.xml:
    tmc_document_topic_nota                   — "Nota" (tema raíz, nivel 1)
    tmc_document_topic_nota_externa           — "Externa" (subtema)
    tmc_document_topic_nota_interna           — "Interna" (subtema)
    tmc_document_topic_nota_originada_tmc     — "Originada en el TMC" (subtema)
    tmc_document_topic_nota_informe           — "Informe" (subtema)
    tmc_document_topic_licitacion_documentacion — "Documentación" (subtema de Licitación)
    tmc_document_topic_licitacion_descargo    — "Descargo" (subtema de Licitación)
    tmc_document_topic_licitacion_impugnacion — "Impugnación" (subtema de Licitación)
  dependence.xml — tmc_dependence_tmc.document_topic_ids:
    Vincular: tmc_document_topic_licitacion (tema raíz existente)
              tmc_document_topic_nota (tema raíz nuevo)
    Los subtemas son visibles automáticamente a través del domain de secondary_topic_ids.

---- Criterios de aceptación ----

Data:
- [ ] Tema raíz "Nota" creado en document_topic.xml
- [ ] Subtemas de "Nota" creados: Externa, Interna, Originada en el TMC, Informe
- [ ] Subtemas nuevos de "Licitación" creados: Documentación, Descargo, Impugnación
- [ ] tmc_dependence_tmc.document_topic_ids configurado con: Licitación y Nota
- [ ] Los subtemas existentes de Licitación (Pública, Privada) quedan disponibles
      automáticamente al vincular el tema raíz

Tests:
- [ ] Para dependence_id = TMC, document_topic_ids devuelve al menos
      tmc_document_topic_licitacion y tmc_document_topic_nota
- [ ] Los subtemas de Licitación incluyen: Pública, Privada, Documentación, Descargo, Impugnación
- [ ] Los subtemas de Nota incluyen: Externa, Interna, Originada en el TMC, Informe

---- Impacto técnico ----

- models: sin cambios
- data: odoo-tmc-data/tmc_data/data/tmc/document_topic.xml (8 registros nuevos)
        odoo-tmc-data/tmc_data/data/tmc/dependence.xml (agregar document_topic_ids
        a tmc_dependence_tmc)
- views: sin cambios de código
- tests: casos listados arriba (en odoo-me o en odoo-tmc-data, según convenga)
- documentación: system_narrative.md sección 3.3 (agregar temas disponibles para TMC)