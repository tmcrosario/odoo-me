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

[DONE]

Contexto:
Los movimientos (me.document_movement) representan la trazabilidad física
del expediente entre dependencias. Su integridad es crítica: un movimiento
incorrecto o duplicado contamina la historia del documento.

Modelo (me.document_movement):
  expediente_id             Many2one  required=True  ondelete=cascade
  date                      Datetime  required=True  default=now()
  origin_dependence_id      Many2one  required=True
  destination_dependence_id Many2one  required=True
  user_id                   Many2one  default=usuario actual

---- Decisiones cerradas ----

A. Movimiento sin documento
   Ya cubierto por expediente_id required=True + ondelete=cascade.
   Odoo impone la constraint a nivel DB. No requiere cambios adicionales.

B. Duplicado (opción a1)
   Un movimiento duplicado es exactamente:
     mismo expediente_id + mismo origin_dependence_id
     + mismo destination_dependence_id + misma date (Datetime exacto)
   Implementar con _sql_constraints UNIQUE sobre esos 4 campos.
   No se usa ventana temporal ni comparación por día.
   Nota: con origin y destination required (decisión C), no hay NULLs
   en la constraint y el comportamiento de UNIQUE es predecible.

C. Origen y destino obligatorios (opción c1)
   origin_dependence_id y destination_dependence_id pasan a required=True.
   Motivo: un movimiento sin origen o sin destino no tiene valor de
   trazabilidad real. Los movimientos automáticos en create() ya los
   setean explícitamente — compatible con este cambio.

D. Fecha futura
   date no puede ser posterior a now() al momento de guardar.
   Validar con @api.constrains('date').

E. Fecha anterior a intake_date del expediente
   date.date() no puede ser anterior a expediente_id.intake_date.
   date es Datetime, intake_date es Date — comparar truncando a Date.
   Validar con @api.constrains('date', 'expediente_id').

F. Orden cronológico entre movimientos (descartado para MVP)
   No se exigirá orden cronológico entre movimientos del mismo expediente.
   Los operadores pueden registrar movimientos retroactivamente.
   Puede revisarse en una task futura.

---- Criterios de aceptación ----

Modelo (me/models/document_movement.py):
- [x] expediente_id required=True ya está
- [x] origin_dependence_id: agregar required=True
- [x] destination_dependence_id: agregar required=True
- [x] _sql_constraints: UNIQUE(expediente_id, origin_dependence_id,
      destination_dependence_id, date) con mensaje claro en español
- [x] @api.constrains('date'): date no puede ser futura
- [x] @api.constrains('date', 'expediente_id'):
      date.date() >= expediente_id.intake_date

Tests (archivo nuevo: me/tests/test_document_movement.py):
- [x] Crear movimiento sin origin_dependence_id lanza error
- [x] Crear movimiento sin destination_dependence_id lanza error
- [x] Crear dos movimientos idénticos (mismo exp+orig+dest+date) lanza error
- [x] Crear dos movimientos mismo exp+orig+dest pero fecha distinta no falla
- [x] Crear movimiento con date > now() lanza ValidationError
- [x] Crear movimiento con date.date() < expediente.intake_date lanza ValidationError
- [x] Crear movimiento con date.date() == expediente.intake_date no falla
- [x] Crear movimiento con todos los campos válidos no falla

Impacto técnico:
- models: me/models/document_movement.py
  (required en origin/destination, _sql_constraints, 2 x @api.constrains)
- create() en me.document_exp: los movimientos automáticos ya setean
  origin_dependence_id y destination_dependence_id — sin impacto
- tests: nuevo me/tests/test_document_movement.py
- views: origin_dependence_id y destination_dependence_id ya aparecen
  en la pestaña de movimientos — required=True no requiere cambios de vista

--------------------------------------------------
### #003 – Integración con RAA
--------------------------------------------------

[DONE]

Contexto:
Al crear un expediente en ME, el sistema registra automáticamente un acto
administrativo en el módulo RAA (Registro de Actos Administrativos),
vinculándolo al tmc.document recién creado.

---- Comportamiento implementado ----

Creación (me/models/document_exp.py — create()):
  Se crea un registro raa.registry_aa con document_id = tmc.document creado.
  Usa sudo(): el operador no necesita permisos en raa.registry_aa.
  Ocurre después de crear tmc.document, antes de los movimientos automáticos.
  Constraint UNIQUE(document_id) en raa impide doble creación por el mismo doc.

Eliminación (me/models/document_exp.py — unlink()):
  Se elimina raa.registry_aa antes de tmc.document para evitar violación de FK.
  raa.registry_aa.unlink() puede eliminar tmc.document si está "vacío"
  (sin date, document_object ni temas). Por eso unlink() en me captura document
  antes de llamar a raa.unlink() y verifica si aún existe después.

---- Arquitectura de la relación ----

  raa/__manifest__.py: "depends": ["tmc", "me"]  — raa depende de me
  me/__manifest__.py:  "depends": ["tmc"]         — me NO declara raa

  Acoplamiento implícito: me llama a raa.registry_aa sin declararlo como
  dependencia. Si raa no está instalado, me.document_exp.create() falla
  en runtime. En el stack actual ambos módulos siempre se instalan juntos.
  El código documenta esto con un comentario explícito.

  entry_date en raa.registry_aa usa default=today. No recibe intake_date
  del expediente. Comportamiento aceptado.

---- Decisiones cerradas ----

1. La creación es automática, en create() de me.document_exp.
2. Se dispara al crear el expediente.
3. Solo se pasa document_id al registro RAA.
4. sudo() es intencional: los operadores no necesitan permisos en RAA.
5. El acoplamiento implícito (me sin depends de raa) es conocido y aceptado.

---- Gaps conocidos ----

- No hay tests que verifiquen la creación de raa.registry_aa en create().
- No hay tests para unlink() (orden de eliminación y comportamiento cascada).

---- Impacto técnico ----

- me/models/document_exp.py: create() y unlink()
- raa/models/registry_aa.py: UNIQUE constraint, unlink() personalizado
- me/ai-context.md: sección RAA Integration
- domain-rules/me/workflows.md: Workflow 3
- docs/system_narrative.md: sección 3.4

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

[DONE]

Contexto:
me.document_movement registra la trazabilidad del expediente entre
dependencias. La semántica de user_id era ambigua: defaulteaba al
usuario de sesión, mezclando "quién cargó" con "quién queda a cargo".

Esta task aclara esa ambigüedad redefiniendo user_id como el responsable
operativo en destino, y delegando la auditoría de carga a create_uid
(campo nativo de Odoo, siempre disponible sin lógica custom).

---- Decisiones cerradas ----

1. Semántica de user_id
   user_id = el usuario Odoo que queda a cargo del expediente en la
   dependencia destino del movimiento.
   No se agrega ningún campo nuevo (receiver_employee_id descartado).

2. Auditoría de carga
   create_uid (Odoo nativo) registra quién creó el registro.
   No se muestra en la vista estándar — accesible por developer mode.

3. Default
   default=lambda self: self.env.user se mantiene. En el caso más
   frecuente el operador que carga el movimiento ES quien queda a cargo.
   El operador puede cambiarlo si el receptor es otra persona.

4. Readonly en automáticos
   user_id es readonly cuando is_automatic = True, consistente con fojas.

5. No se vincula tmc.hr.office con tmc.dependence (fuera de scope).

6. Obligatoriedad
   El campo no tiene required=True. El default cubre el caso normal.

---- Criterios de aceptación ----

Modelo (me/models/document_movement.py):
- [x] user_id: string="Responsible", help actualizado a nueva semántica

Vistas (me/views/document_exp_views.xml):
- [x] user_id: readonly="is_automatic" en lista y form del notebook

i18n (me/i18n/es_AR.po):
- [x] field_description: "Responsible" → "Responsable"
- [x] help: traducción de la nueva ayuda

Tests (me/tests/test_document_movement.py — clase TestResponsibleUser011):
- [x] user_id defaultea al usuario de sesión en movimiento manual
- [x] user_id puede ser distinto al usuario de sesión
- [x] movimientos automáticos tienen user_id asignado
- [x] create_uid queda asignado al usuario de sesión al crear el movimiento

Resultado: 0 failed, 0 errors of 4 tests

Documentación:
- [x] ai-context.md: user_id semántica actualizada
- [x] domain-rules/me/workflows.md: Workflow 5 actualizado

--------------------------------------------------
### #012 – Comportamiento condicional de jurisdicción y repartición
--------------------------------------------------

[DONE]

Contexto:
El campo jurisdiction_dependence actualmente no tiene domain filter en la
vista — muestra las 191 dependencias del nomenclador. Tampoco existe
comportamiento diferenciado según la dependencia de origen elegida en Fase 1.

Se definen tres reglas funcionales que condicionan la visibilidad y el valor
de jurisdiction_dependence y source_dependence_id según el valor de
dependence_id.

---- Datos del nomenclador ----

tmc.dependence_order contiene ~204 registros jerárquicos.
Los 21 registros con código 1.XX.00 (hijos directos de Administración Central)
son las "jurisdicciones madre":
  1.01.00 CONCEJO MUNICIPAL (CM)
  1.02.00 DEPARTAMENTO EJECUTIVO (DEM)
  1.03.00 SECRETARÍA DE HACIENDA Y ECONOMÍA
  1.04.00 SECRETARÍA DE PLANEAMIENTO
  1.05.00 SECRETARÍA DE GOBIERNO
  1.06.00 SECRETARÍA DE OBRAS PÚBLICAS
  1.07.00 SECRETARÍA DE AMBIENTE
  1.08.00 SECRETARÍA DE SALUD PÚBLICA
  1.09.00 DESARROLLO SOCIAL / PROMOCIÓN SOCIAL
  1.10.00 SECRETARÍA DE PRODUCCIÓN
  1.11.00 SECRETARÍA DE CULTURA Y EDUCACIÓN
  1.12.00 SECRETARÍA GENERAL
  1.13.00 TRIBUNAL MUNICIPAL DE CUENTAS (TMC)
  1.14.00–1.17.00 Turismo, Control, Transporte, Economía Social
  1.90.00, 1.91.00 Servicios de deuda / Tesorería

Sub-dependencias (2do nivel y más profundos) deben aparecer únicamente
en source_dependence_id, no en jurisdiction_dependence.

---- Reglas ----

1. Expedientes del TMC — auto-asignación de jurisdicción
   Cuando dependence_id.abbreviation == 'TMC', jurisdiction_dependence
   se asigna automáticamente al registro TMC y es readonly para el operador.
   Al cambiar dependence_id a otro valor, jurisdiction_dependence se limpia.

2. Expedientes del Concejo Municipal — ocultamiento y auto-asignación
   Cuando dependence_id.abbreviation == 'CM':
   - jurisdiction_dependence y source_dependence_id se ocultan en la vista
   - jurisdiction_dependence se auto-asigna al registro CM internamente
   - El sistema genera el movimiento automático CM→TMC normalmente
   El operador nunca ve ni edita esos campos para expedientes CM.

3. Campo jurisdicción restringido a jurisdicciones madre del nomenclador
   jurisdiction_dependence muestra solo los 21 registros 1.XX.00.
   Las sub-dependencias (2do nivel o más) no deben aparecer aquí;
   pertenecen exclusivamente a source_dependence_id.

---- Decisiones cerradas ----

A. "Jurisdicciones madre" = hijos directos de tmc_dependence_adm en el nomenclador
   Campo computed nuevo `allowed_jurisdiction_ids` que consulta:
     tmc.dependence_order donde parent_id == tmc_dependence_adm
   y mapea .dependence_id. Retorna los ~21 registros 1.XX.00 dinámicamente.
   Usa env.ref('tmc_data.tmc_dependence_adm', raise_if_not_found=False),
   patrón ya establecido en _EXP_ROOT_TOPIC_XMLIDS.
   Sin hardcoding de abbreviations. No toca odoo-tmc.

B. Caso CM: auto-asignar jurisdiction_dependence = CM, ocultar campos, mantener movimiento
   jurisdiction_dependence conserva required=True — siempre tiene valor:
   - DEM: el operador lo elige manualmente
   - TMC: auto-asignado por onchange
   - CM: auto-asignado por onchange (y backup en create() para API)
   El movimiento CM→TMC se genera porque jurisdiction_dependence == CM record.
   El operador no ve el campo.
   source_dependence_id queda vacío para CM.

   Constraint _check_source_dependence_required (de #017): agregar excepción CM
   para que no exija source_dependence_id cuando dependence_id == CM.

---- Criterios de aceptación ----

Modelo (me/models/document_exp.py):
- [x] Nuevo campo allowed_jurisdiction_ids: Many2many computed, sin argumentos en
      @api.depends(), consulta tmc.dependence_order hijos de tmc_dependence_adm
- [x] _onchange_dependence (extender el existente):
      - si TMC: jurisdiction_dependence = registro TMC
      - si CM: jurisdiction_dependence = registro CM, limpiar source_dependence_id
      - cualquier otro caso: limpiar jurisdiction_dependence
- [x] create(): backup — si dependence_id es TMC o CM y jurisdiction_dependence
      no viene en vals, auto-asignarlo antes de super().create()
- [x] _check_source_dependence_required: condición `not in ('CM', 'TMC')`
      TMC también exento (TMC tiene sub-deps en el nomenclador)

Vista (me/views/document_exp_views.xml):
- [x] Agregar <field name="allowed_jurisdiction_ids" invisible="1"/>
- [x] Agregar <field name="dependence_abbreviation" invisible="1"/> (proxy para expresiones client-side)
- [x] jurisdiction_dependence: domain="[('id', 'in', allowed_jurisdiction_ids)]"
      readonly="dependence_abbreviation == 'TMC'"
- [x] jurisdiction_dependence e source_dependence_id: invisible="dependence_abbreviation == 'CM'"
      (ocultos individualmente — intake_date permanece visible en el mismo grupo)

Tests (me/tests/test_document_exp.py):
- [x] allowed_jurisdiction_ids incluye HAC, GOB, DEM, CM, TMC y otras
      (no solo las 3 de dependence_id)
- [x] Crear expediente con dependence_id=TMC: jurisdiction_dependence == TMC,
      1 solo movimiento automático (TMC→ME)
- [x] Crear expediente con dependence_id=CM: jurisdiction_dependence == CM,
      movimiento automático CM→TMC generado, source_dependence_id vacío sin error
- [x] Crear expediente con dependence_id=DEM sin jurisdiction_dependence:
      falla (required=True sigue activo para DEM)
- [x] onchange dependence_id→TMC: jurisdiction_dependence auto-completado
- [x] onchange dependence_id TMC→DEM: jurisdiction_dependence limpiado

---- Nota operativa ----

Para expedientes CM, jurisdiction_dependence queda con valor CM en la DB
aunque el operador nunca lo ve. Es el origen del movimiento 1 (CM→TMC).
El movimiento TMC→ME (movimiento 2) siempre se genera para todos los orígenes:
  DEM: movimiento 1 = jurisdiction→TMC, movimiento 2 = TMC→ME
  TMC: solo movimiento TMC→ME (movimiento 1 omitido por origin_is_tmc)
  CM:  movimiento 1 = CM→TMC, movimiento 2 = TMC→ME

---- Impacto técnico ----

- models: me/models/document_exp.py
  (campo allowed_jurisdiction_ids, extender _onchange_dependence,
   backup en create(), excepción CM en constraint)
- views: me/views/document_exp_views.xml
  (allowed_jurisdiction_ids invisible, domain, readonly TMC, invisible CM)
- tests: me/tests/test_document_exp.py (6 tests nuevos)
- documentación: docs/todo.md (esta task)

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

---- Decisiones de implementación ----

1. secondary_topic_id es opcional.
   No todo tema tiene subtemas definidos.

2. Campos proxy Many2one en me.document_exp:
   main_topic_id (Many2one, compute+inverse) — envuelve main_topic_ids
   secondary_topic_id (Many2one, compute+inverse) — envuelve secondary_topic_ids
   Motivo: many2many_tags permite selección múltiple y siempre muestra
   un input vacío extra que el operador interpreta como tercer nivel.
   Los proxies Many2one garantizan selección única y dropdown estándar.

3. Domain de main_topic_id:
   [('parent_id', '=', False), ('id', 'in', allowed_exp_topic_ids)]
   allowed_exp_topic_ids es un campo computed en me.document_exp que
   devuelve solo Licitación y Nota, resueltos por XML ID de tmc_data.
   Motivo: los temas EXP son independientes del organismo de origen
   (DEM/TMC/CM), pero no deben mostrar los ~195 temas raíz del sistema.
   El filtro se hace por tipo de documento (EXP) en lugar de por dependencia.

4. Domain de secondary_topic_id: [('parent_id', '=', main_topic_id)]
   Solo hijos directos del tema seleccionado. Un nivel.

5. Onchange main_topic_id → limpia secondary_topic_id.

6. Vista: main_topic_id string="Asunto", secondary_topic_id sin label
   para que aparezca como refinamiento visual del asunto.
   allowed_exp_topic_ids declarado invisible para que el domain lo use.

---- Correcciones post-implementación ----

Fix 1: domain cambiado de
  [('parent_id', '=', False), ('id', 'in', document_topic_ids)]
  a [('parent_id', '=', False)]
  Error: filtraba por organismo de origen, DEM y CM quedaban sin temas.

Fix 2: domain cambiado de [('parent_id', '=', False)]
  a [('parent_id', '=', False), ('id', 'in', allowed_exp_topic_ids)]
  Error: mostraba todos los ~195 temas raíz del sistema.
  Solución final: allowed_exp_topic_ids resuelve Licitación y Nota por XML ID.

---- Impacto técnico (implementado) ----

- models: main_topic_id, secondary_topic_id, _compute_*, _set_*, _onchange_*
- views: campos Many2one en Fase 2, secondary invisible cuando sin main
- tests: TestSecondaryTopics (lógica M2M base), TestTopicProxyFields (proxies)
         incluye test_main_topic_id_available_regardless_of_dependence

--------------------------------------------------
### #014 – Nomenclador de temas y subtemas para expedientes
--------------------------------------------------

[DONE]

Contexto:
El modelo tmc.document_topic define los temas (nivel 1) y subtemas (nivel 2)
disponibles para clasificar expedientes. Los temas cargados corresponden al
tipo de documento EXP y están disponibles para expedientes de cualquier
organismo de origen (DEM, TMC, CM).

Nota sobre la definición original:
  La task fue inicialmente titulada "...para expedientes del TMC", lo que
  generó el error de vincular los temas solo a la dependencia TMC.
  La corrección conceptual es: estos temas pertenecen al tipo de documento EXP,
  no a un organismo específico. En me.document_exp, el campo main_topic_id
  usa domain [('parent_id', '=', False)] — sin filtrar por dependence_id —
  por lo que los temas son accesibles para expedientes de DEM, TMC y CM
  sin necesidad de vinculación adicional en dependence.xml.
  El vínculo Licitación+Nota→TMC en dependence.xml queda como dato de
  referencia para tmc.document genérico, pero no afecta me.document_exp.

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

--------------------------------------------------
### #015 – Fojas en movimientos de expediente
--------------------------------------------------

[DONE]

Contexto:
En cada pase del expediente entre dependencias pueden agregarse fojas nuevas.
Para mantener trazabilidad completa, cada movimiento debe registrar cuántas
fojas tenía el expediente en ese momento — no el valor actual, sino el
snapshot histórico al momento del pase.

Componentes descartados o delegados:
- Ajuste TMC en create(): implementado en #016 [DONE]
- Usuario receptor: delegado a #011 [IDEA] — no se resuelve aquí

---- Decisiones cerradas ----

A. Semántica del campo fojas en movimientos
   El campo fojas en me.document_movement almacena el TOTAL de fojas del
   expediente en el momento exacto en que se registra ese movimiento.
   No es un delta (fojas agregadas en ese pase). No es un ingreso libre
   sin referencia. Es un snapshot: captura el estado del expediente en
   ese instante de tiempo.
   Motivo: la trazabilidad requiere saber cuántas fojas circularon con
   el expediente en cada pase — si el expediente creció, queda registrado.

B. Valor por defecto de fojas

   Movimientos automáticos (creados por create() de me.document_exp):
     fojas se inyecta explícitamente como record.fojas al construir el
     dict de cada movimiento automático en create(). No depende de ningún
     default del campo — el valor real del expediente en ese instante se
     pasa directamente.
     Si expediente.fojas == 0 (campo no completado o expediente nuevo),
     el movimiento registra 0. Correcto: 0 fojas es un estado válido.

   Movimientos manuales (agregados por el operador en el tab de movimientos):
     fojas se pre-carga vía default_get() usando el expediente del contexto.
     La vista pasa el contexto {'default_expediente_id': id}.
     Odoo resuelve 'default_expediente_id' en super().default_get() y lo
     entrega como defaults['expediente_id']. La implementación lee ese valor
     para resolver expediente.fojas y devolverlo como default de fojas.
     Si no hay contexto (movimiento creado fuera de la vista del expediente),
     fojas cae al default=0 del campo. No es un error.

C. Editabilidad de fojas

   Movimientos automáticos:
     fojas es readonly. El operador no puede modificarlo.
     Motivo: el valor fue tomado en el momento exacto del create(); editarlo
     después rompería la semántica de snapshot.
     Implementación: is_automatic = True en esos movimientos;
     la vista aplica readonly="is_automatic" sobre fojas en lista y form.

   Movimientos manuales:
     fojas es editable. El valor pre-cargado (por default_get) puede
     corregirse si el operador registra el pase retroactivamente o si
     cometió un error en el conteo.
     Implementación: is_automatic = False por default → readonly="is_automatic"
     evalúa a False → campo editable.

D. División de la task (cerrada: no se divide)
   Componente 3 ya está en #016 y componente 2 en #011.
   #015 queda exclusivamente sobre fojas — un solo campo, un solo flujo.
   No amerita subdivisión adicional.

---- Nota operativa ----

E. Snapshot vs. valor actualizado
   El campo fojas en cada movimiento registra el total de fojas del expediente
   en el momento exacto del pase — no se actualiza si expediente.fojas cambia
   después. Esto es correcto por diseño (decisión A).
   El operador debe saber que el valor en movimientos históricos refleja el
   estado en ese instante, no el valor actual del expediente.
   Punto a cubrir en el manual de operación; no requiere cambios técnicos.

---- Criterios de aceptación ----

Modelo (me/models/document_movement.py):
- [x] Nuevo campo: fojas = fields.Integer(string="Fojas", default=0)
- [x] Nuevo campo: is_automatic = fields.Boolean(default=False)
      (True cuando el movimiento fue creado por create() de me.document_exp)
- [x] default_get(): leer defaults.get('expediente_id') — resuelto por
      super().default_get() desde el contexto {'default_expediente_id': id}
      que pone la vista — y pre-cargar fojas = expediente.fojas.
      Si defaults no tiene expediente_id, fojas queda en el default=0 del campo.

Modelo (me/models/document_exp.py — create()):
- [x] Al crear movimientos automáticos: incluir fojas=record.fojas e
      is_automatic=True en el dict de valores de cada movimiento

Vista (me/views/document_exp_views.xml):
- [x] Agregar columna fojas en la lista de movimientos (tab Movimientos)
- [x] Agregar campo fojas en el form inline de movimiento
- [x] is_automatic con invisible="1" en lista (column_invisible) y form
- [x] fojas con readonly="is_automatic" en lista y form

Tests (me/tests/test_document_movement.py — clase TestFojasMovimiento):
- [x] Crear expediente con fojas=5: ambos movimientos automáticos tienen fojas == 5
- [x] Movimientos automáticos tienen is_automatic == True
- [x] Movimiento manual (creado sin is_automatic) tiene is_automatic == False
- [x] Movimiento manual creado explícitamente con fojas=0 no falla
- [x] Crear expediente con fojas=0 (default): movimientos automáticos tienen fojas == 0
- [x] default_get() pre-carga fojas desde el contexto default_expediente_id

Nota sobre tests existentes:
  El setUp de TestDocumentMovement crea un expediente sin fojas explícitas
  (fojas=0 por default de #017). Los movimientos automáticos creados en ese
  setUp tendrán fojas=0. Los tests de esa clase no verifican fojas — no se rompen.
  Los nuevos tests deben crear expedientes con fojas=5 para el caso no trivial.

---- Impacto técnico ----

- models: me/models/document_movement.py — 2 campos nuevos + default_get
- models: me/models/document_exp.py — pasar fojas e is_automatic en create()
- views: me/views/document_exp_views.xml — columna fojas + readonly condicional
- tests: casos listados arriba (en test_document_movement.py, nueva clase)
- documentación:
  - ai-context.md: actualizar tabla de campos de me.document_movement
    (agregar fojas e is_automatic)

--------------------------------------------------
### #016 – Corregir movimientos automáticos cuando dependencia es TMC
--------------------------------------------------

[DONE]

Contexto:
Al crear un expediente en me.document_exp, create() genera dos movimientos
automáticos que documentan el ingreso físico del expediente:

  Movimiento 1: jurisdiction_dependence → TMC
  Movimiento 2: TMC → Mesa de Entradas

Este comportamiento es correcto cuando el expediente proviene de DEM o CM,
donde jurisdiction_dependence es una dependencia distinta a TMC.

Sin embargo, cuando dependence_id = TMC, jurisdiction_dependence también
es TMC (el propio Tribunal), por lo que el Movimiento 1 resulta en:

  Movimiento 1: TMC → TMC   ← sin sentido funcional

Un expediente no puede "pasar" de una dependencia a sí misma.
Este movimiento contamina la trazabilidad del expediente.

---- Comportamiento esperado ----

Si dependence_id.abbreviation == 'TMC':
  Generar únicamente:
    Movimiento 1: TMC → Mesa de Entradas
  Omitir el movimiento TMC → TMC.

Si dependence_id.abbreviation != 'TMC' (DEM, CM):
  Comportamiento actual sin cambios:
    Movimiento 1: jurisdiction_dependence → TMC
    Movimiento 2: TMC → Mesa de Entradas

La condición se evalúa sobre dependence_id del expediente (el origen
del documento), no sobre jurisdiction_dependence.

---- Implementación esperada ----

Archivo: me/models/document_exp.py, método create()

La lógica actual crea ambos movimientos incondicionalmente.
Debe reemplazarse por un condicional:
  - Si dependence_id == TMC: crear solo el movimiento TMC → ME.
  - Si dependence_id != TMC: crear ambos movimientos (comportamiento actual).

Las dependencias TMC y ME ya se buscan por abbreviation ('TMC', 'ME') —
el patrón de búsqueda no cambia.

---- Criterios de aceptación ----

Modelo (me/models/document_exp.py):
- [x] create() no genera movimiento TMC→TMC cuando dependence_id = TMC
- [x] create() genera un único movimiento TMC→ME cuando dependence_id = TMC
- [x] create() mantiene comportamiento actual (2 movimientos) para DEM y CM

Tests (me/tests/test_document_exp.py o test_document_movement.py):
- [x] Expediente con dependence_id=TMC: exactamente 1 movimiento automático,
      con origin=TMC y destination=ME (cubierto por TestJurisdictionConditional012)
- [x] Expediente con dependence_id=TMC: no existe movimiento TMC→TMC
- [x] Expediente con dependence_id=DEM: sigue generando 2 movimientos — regresión

---- Impacto técnico ----

- models: me/models/document_exp.py — condicional en create()
- tests: 3 casos nuevos (ver arriba)
- views: sin cambios
- workflows.md: Workflow 4 — agregar rama para dependence_id=TMC

--------------------------------------------------
### #017 – Campos obligatorios en Fase 2 del expediente
--------------------------------------------------

[DONE]

Contexto:
Al cargar un expediente en la vista form, la Fase 2 muestra campos que
deberían ser obligatorios para garantizar la completitud funcional del
registro. Tres campos fueron detectados como opcionales cuando no deberían
serlo: source_dependence_id, date y fojas.

Relación con tasks anteriores:
- #009 decidió source_dependence_id como opcional (decisión 5).
  Esta task revisa esa decisión con criterio condicional.
- #008 implementó intake_date como required=True. date es un campo distinto
  (la fecha del documento, la que figura en el papel), que queda
  required=False en me.document_exp.

---- Decisiones cerradas ----

A. fojas = required en vista y modelo
   required=True en la definición del campo Integer.
   El valor 0 es aceptado (significa 0 fojas — válido, sin error).
   No se impone valor mínimo.
   La vista hereda required automáticamente del modelo.

B. date = required en vista + validación manual en create() y write()
   View: required="1" en la línea del campo date.
   Backend: validación manual — NOT @api.constrains('date'), porque date
   es campo delegado via _inherits de tmc.document y los constrains no
   se propagan al modelo hijo (mismo patrón que #005 para dependence_id).
   Implementación:
     - create(): verificar que date esté en vals antes de super()
     - write(): verificar en el bloque de extracción de date_val
   Nota técnica: date se extrae de vals ANTES de llamar super().create()
   para evitar que tmc.document.create() lo procese como objeto datetime.date
   (tmc.document espera string para hacer slicing [:4] al comparar con period).
   Se aplica vía SQL con _update_document_date() igual que write().

C. source_dependence_id = required condicional (cuando hay opciones)
   Required SOLO cuando allowed_sub_dependence_ids es no vacío.
   Motivo: si la jurisdicción no tiene hijos en el nomenclador,
   el campo required bloquea la creación sin que el operador pueda
   seleccionar nada — comportamiento inaceptable.
   View: required="allowed_sub_dependence_ids" (truthy cuando la lista
   tiene items; allowed_sub_dependence_ids ya está declarado invisible).
   Backend: @api.constrains('source_dependence_id', 'jurisdiction_dependence')
   — campo propio de me.document_exp, constraint sí funciona.
   Condición: if record.allowed_sub_dependence_ids and not
   record.source_dependence_id → raise ValidationError.

---- Criterios de aceptación ----

Modelo (me/models/document_exp.py):
- [x] fojas: agregar default=0 (required en vista; Integer required=True rechaza 0)
- [x] date: agregar check manual en create() antes de super()
      que lanza ValidationError si date no está en vals o es falsy
- [x] date: agregar check en write() en el bloque de extracción de date_val
      que lanza ValidationError si date_val es None/False
- [x] source_dependence_id: agregar @api.constrains(
      'source_dependence_id', 'jurisdiction_dependence')
      con condición: if record.allowed_sub_dependence_ids and not
      record.source_dependence_id → raise ValidationError

Vista (me/views/document_exp_views.xml):
- [x] date: agregar required="1"
- [x] source_dependence_id: agregar required="allowed_sub_dependence_ids"
- [x] fojas: agregar required="1" en la vista

Tests (me/tests/test_document_exp.py):
- [x] Crear expediente sin date lanza ValidationError
- [x] Crear expediente con date válida no falla
- [x] Crear expediente con fojas=0 no falla (0 es válido)
- [x] Crear expediente con jurisdiction que tiene hijos y sin
      source_dependence_id lanza ValidationError
- [x] Crear expediente con jurisdiction sin hijos y sin
      source_dependence_id no falla (conditional required)
- [x] Crear expediente con jurisdiction que tiene hijos y con
      source_dependence_id válido no falla

---- Impacto técnico ----

- models: me/models/document_exp.py — 3 cambios (fojas required,
  date validation manual, source_dependence_id constraint)
- views: me/views/document_exp_views.xml — required en date y
  source_dependence_id
- tests: casos listados arriba
- documentación: ai-context.md — actualizar tabla de campos:
  fojas (agregar Required: Sí), date (agregar nota de required),
  source_dependence_id (actualizar Required: condicional)

--------------------------------------------------
### #019 – i18n: normalización de strings del módulo me
--------------------------------------------------

[DONE]

Contexto:
Todos los strings del módulo me estaban hardcodeados en español, en
contraste con el stack tmc (inglés). La normalización alinea el módulo
con el idioma fuente del stack y mueve las traducciones a es_AR.po.

Alcance:
- me/models/document_exp.py: string= y help= de todos los campos a inglés;
  mensajes de ValidationError a inglés; warning dict con _()
- me/models/document_movement.py: _description, constraint message,
  string=/help= de todos los campos, ValidationErrors a inglés
- me/views/document_exp_views.xml: remover overrides string= redundantes
  (cuando el modelo ya define el label correcto); mantener overrides
  semánticamente distintos (Reference, Subject, Document Date)
- me/views/me_menus.xml: "Mesa de Entrada" → "Intake Register",
  "Registro de Expedientes" → "Expediente Registry"
- me/__manifest__.py: summary → "Document Intake Management System"
- me/i18n/es_AR.po: reescritura completa (5 entradas Odoo 14 → 60+ entradas)
- me/tests/test_document_exp.py: actualizar string "Documento sin nombre"
  → "Unnamed Document" en test_computed_name_empty_when_phase1_incomplete

Vocabulario base del stack (consistencia con tmc):
- "Repartición" → "Source Dependence" (técnico); "Repartición" (es_AR.po)
- "Jurisdicción" → "Jurisdiction"
- "Fojas" → "Page Count" (técnico); "Fojas" (es_AR.po)
- "Mesa de Entrada" → "Intake Register" (fuente); traducción → "Mesa de Entrada"
- "Expediente" → se mantiene como término de dominio

Estrategia XML:
  No duplicar string= en XML cuando el campo ya define el label correcto en
  Python. Mantener solo overrides que difieren semánticamente del modelo
  (Reference vs Object, Subject vs Topics, Document Date vs Date).

Resultado de tests: 0 failed, 0 error(s) of 74 tests.

--------------------------------------------------
### #018 – Matriz de permisos de módulo me
--------------------------------------------------

[DONE]

Contexto:
El módulo me define tres grupos funcionales (me.group_user, me.group_manager,
me.group_read_only) pero no tiene ir.model.access.csv. Los grupos son
asignables en la UI pero no controlan ningún modelo. Esto genera tres
problemas concretos detectados en el análisis de permisos post-#017:

Problema 1 — grupos sin efecto real:
  me.group_user y me.group_manager no gatan acceso a me.document_exp ni a
  me.document_movement. En Odoo, un modelo sin ir.model.access es accesible
  exclusivamente por administradores técnicos (base.group_system). Cualquier
  usuario en me.group_manager que intente acceder a un expediente por API
  recibe AccessError.

Problema 2 — dependencia oculta con tmc.group_manager:
  me.document_exp usa _inherits sobre tmc.document. El ORM ejecuta
  tmc.document.write() para campos delegados (dependence_id, number, period,
  document_object, etc.). tmc.group_user tiene perm_write=0 sobre tmc.document;
  solo tmc.group_manager tiene perm_write=1. Un me.group_manager que no sea
  también tmc.group_manager recibirá AccessError al editar un expediente,
  aunque tenga permisos correctos en los modelos de me.

Problema 3 — base.group_system como bypass funcional:
  El único has_group() en todo el sistema (write() en me.document_exp, para
  restringir edición de fojas post-creación) referencia base.group_system,
  el grupo técnico de configuración de Odoo. Esto impide que un me.group_manager
  corrija un error operativo en fojas sin intervención del admin técnico.
  Es aceptable como parche provisional; no como política durable.

Relación con otras tasks:
  - #015 implementó snapshot de fojas en movimientos (depende de permisos
    para que la restricción de escritura sea operativa con usuarios reales)
  - #017 implementó base.group_system para fojas (el parche que esta task resuelve)
  - #011 (responsable operativo, [IDEA]) puede verse afectado por el modelo de
    grupos que se defina aquí

---- Decisiones cerradas ----

A. Separación funcional me.group_user vs me.group_manager (cerrada)

   me.group_user (operador):
     Registra ingresos y pases. No corrige registros existentes.
     Permisos: read + create en ambos modelos; sin write ni unlink.
     Implica tmc.group_user para poder crear tmc.document vía _inherits.

   me.group_manager (gestor):
     Supervisa y corrige. Tiene acceso completo (CRUD).
     Implica tmc.group_manager para poder editar tmc.document vía _inherits.
     Es el único rol funcional de ME que puede corregir fojas post-creación
     (ver decisión C).

   Matriz de permisos:

     me.document_exp:
       me.group_manager   → R W C U (1,1,1,1)
       me.group_user      → R _ C _ (1,0,1,0)
       me.group_read_only → R _ _ _ (1,0,0,0)

     me.document_movement:
       me.group_manager   → R W C U (1,1,1,1)
       me.group_user      → R _ C _ (1,0,1,0)
       me.group_read_only → R _ _ _ (1,0,0,0)

   Patrón coherente con tmc (tmc.group_user: R_C_ en tmc.document).

   Implied_ids resultante:
     me.group_manager → tmc.group_manager (decisión B) → tmc.group_user → base.group_user
     me.group_user    → tmc.group_user (nuevo) → base.group_user

B. me.group_manager implica tmc.group_manager (cerrada)
   me.document_exp usa _inherits sobre tmc.document. Editar cualquier campo
   delegado (dependence_id, number, period, document_object) requiere
   perm_write=1 sobre tmc.document, que solo tiene tmc.group_manager.
   Decisión: agregar implied_ids = [(4, ref('tmc.group_manager'))] en
   me.group_manager. Un ME manager obtiene la capacidad de escritura sobre
   tmc.document automáticamente, sin asignación manual doble.
   Motivo: preferir un sistema que no pueda quedar mal configurado por omisión.

C. me.group_manager puede corregir fojas post-creación (cerrada)
   Con A definida, me.group_user nunca llega al check de fojas en write()
   porque no tiene perm_write en me.document_exp (AccessError antes).
   me.group_manager es el nivel más alto del módulo y el responsable de
   correcciones excepcionales. No se crea me.group_admin separado.
   Decisión: reemplazar has_group('base.group_system') por
   has_group('me.group_manager') en write() de me.document_exp.

---- Decisiones secundarias (no bloquean) ----

D. ¿Debe me agregar una regla para base.group_erp_manager?
   RAA lo tiene (CRUD en todos sus modelos). TMC no lo tiene.
   Puede agregarse junto con el ir.model.access.csv por consistencia con RAA,
   o postergar. No bloquea la primera implementación.
   Estado: postergar o agregar en la misma iteración.

---- Criterios de aceptación ----

Seguridad (me/security/):
- [x] Crear ir.model.access.csv con las reglas de la matriz (decisión A):
      me.document_exp y me.document_movement para manager, user y read_only
- [x] Agregar implied_ids = [(4, ref('tmc.group_manager'))] en me.group_manager
      en me_groups.xml (decisión B)
- [x] Agregar implied_ids = [(4, ref('tmc.group_user'))] en me.group_user
      en me_groups.xml (necesario para que el operador pueda crear tmc.document)

Modelo (me/models/document_exp.py):
- [x] Reemplazar has_group('base.group_system') por has_group('me.group_manager')
      en el check de fojas en write() (decisión C)

Tests (me/tests/test_document_exp.py):
- [x] Simplificar TestFojasLock.setUp(): eliminar la creación dinámica de
      ir.model.access (ya no necesaria cuando exista ir.model.access.csv)
- [x] Verificar que un usuario con me.group_manager (sin base.group_system,
      sin asignación manual adicional de tmc.group_manager) puede crear y
      editar expedientes — tmc.group_manager se obtiene por implied_ids
- [x] Verificar que me.group_user (operador) puede crear expedientes pero
      no puede editarlos ni eliminarlos
- [x] Verificar que me.group_manager puede corregir fojas post-creación
- [x] Verificar que me.group_user no puede corregir fojas post-creación
      (AccessError por perm_write=0, no ValidationError)

Documentación:
- [x] Actualizar me/ai-context.md: sección de grupos y política de permisos
- [x] Documentar implied_ids: me.group_manager → tmc.group_manager,
      me.group_user → tmc.group_user

---- Impacto técnico ----

- security: me/security/ir.model.access.csv — nuevo archivo (6 reglas mínimo)
- security: me/security/me_groups.xml — implied_ids en manager y user
- models: me/models/document_exp.py — has_group → me.group_manager
- tests: me/tests/test_document_exp.py — simplificar y ampliar TestFojasLock
- documentación: me/ai-context.md

Condición de [DONE]:
  Un usuario con me.group_manager (sin base.group_system, sin asignación
  manual adicional) puede crear y editar expedientes, y puede corregir fojas.
  Un usuario con me.group_user puede crear expedientes y movimientos, pero no
  puede editarlos ni corregir fojas.
  Todo el acceso a modelos está controlado por ir.model.access.

--------------------------------------------------
### #020 – Pre-carga automática de origin_dependence_id en movimientos manuales
--------------------------------------------------

[DONE]

Contexto:
Al agregar un movimiento manual desde la pestaña "Movimientos", origin_dependence_id
quedaba vacío. En el flujo normal de pase, el origen del nuevo movimiento coincide
con el destino del movimiento anterior. Se pre-carga automáticamente para agilizar
la carga.

date no forma parte del alcance — ya tiene default=fields.Datetime.now.

---- Decisiones cerradas ----

1. Mecanismo: default_get(), patrón establecido por fojas (default_expediente_id)
2. "Último movimiento" = el de mayor id (determinístico, orden de inserción)
3. Movimientos automáticos cuentan — el último automático siempre tiene
   destination=ME, que es el origen correcto para el primer movimiento manual
4. Sin movimientos previos: origin queda vacío (estado degenerado, sin default)
5. El campo sigue siendo editable

---- Criterios de aceptación ----

Modelo (me/models/document_movement.py):
- [x] default_get() extendido: si hay expediente_id en contexto, pre-carga
      origin_dependence_id con destination del movimiento de mayor id
- [x] expediente_id leído con fallback desde contexto:
      defaults.get('expediente_id') or self._context.get('default_expediente_id')
      — robusto frente a fields_list que no incluya expediente_id (comportamiento
      real de la lista inline en Odoo 19)
- [x] Sin movimientos previos → origin no se pre-carga (False)

Tests (me/tests/test_document_movement.py — clase TestAutoOriginPreload020):
- [x] default_get() pre-carga origin con destination del último movimiento (por id)
- [x] movimientos automáticos cuentan como "último movimiento"
- [x] sin movimientos previos, origin queda vacío
- [x] sin default_expediente_id en contexto, origin queda vacío
- [x] la pre-carga de origin no altera fojas ni is_automatic
- [x] fields_list en tests replica el comportamiento real de la UI (sin expediente_id)

Resultado: 0 failed, 0 errors of 91 tests

Documentación:
- [x] ai-context.md: default_get() actualizado
- [x] domain-rules/me/workflows.md: Workflow 5 actualizado

---- Notas de comportamiento ----

Pre-carga y movimientos eliminados sin guardar:
  La pre-carga de origin_dependence_id consulta el último movimiento persistido
  en base. Si un manager elimina un movimiento desde la grilla pero no guarda,
  y luego agrega un nuevo movimiento, la pre-carga tomará el destino del movimiento
  eliminado (aún en base). Para que la pre-carga refleje la eliminación, el manager
  debe guardar primero.
  Este comportamiento es aceptable: me.group_user no tiene perm_unlink en
  me.document_movement (ver #018), por lo que el escenario no puede ocurrirle
  al operador. Para el manager, guardar antes es el flujo correcto.

--------------------------------------------------

--------------------------------------------------
### #021 – Detección de reingreso institucional de expedientes
--------------------------------------------------

[TODO]

Contexto:
Los usuarios necesitan identificar expedientes que salieron físicamente del
Tribunal de Cuentas hacia una institución externa y luego reingresaron.

La trazabilidad existe en me.document_movement, pero actualmente no está
modelada la distinción entre dependencias internas del Tribunal y externas.
Los movimientos entre dependencias internas no cuentan como salida ni como
reingreso — solo los cruces institucionales son relevantes.

Toda dependencia del TMC cuenta como interna.
Todo lo que no sea dependencia del TMC cuenta como externo.

Salida institucional  = movimiento con destination_dependence_id externo.
Reingreso institucional = movimiento con destination_dependence_id interno,
  ocurrido después de al menos una salida institucional previa en el expediente.

---- Decisiones cerradas ----

A. Clasificación interna/externa: extender tmc.dependence desde me via _inherit

   Campo is_internal (Boolean, default=False) en me/models/dependence_ext.py.
   No se modifica ningún archivo de tmc. El campo pertenece al módulo me.
   Datos iniciales en me/data/dependence_data.xml: is_internal=True para
   TMC, ME, VOC, FC, DAL, DAT, DCD, DAF, DIC, AFC.
   Todo lo demás (DEM, CM, jurisdicciones municipales) queda False por defecto.

B. Campo en me.document_exp: has_reentry (Boolean, stored, computed)

   Algoritmo: recorrer document_movement_ids ordenados por id.
   has_reentry = True si existe al menos un movimiento con
   destination.is_internal = False (salida) seguido de al menos uno con
   destination.is_internal = True (reingreso).
   depends: document_movement_ids.destination_dependence_id.is_internal
   Los movimientos automáticos tienen destino interno → no generan reingresos.

C. No se modelan reentry_count ni last_reentry_date por ahora.
   El caso de uso actual es identificar y filtrar. Pueden agregarse en task futura.

D. UI: filtro predefinido en search view. Sin columna ni contador en list view.

---- Criterios de aceptación ----

Modelo (me/models/dependence_ext.py — nuevo):
- [ ] _inherit = 'tmc.dependence'
- [ ] Campo is_internal: Boolean, default=False

Datos (me/data/dependence_data.xml — nuevo o extender existente):
- [ ] is_internal = True para: TMC, ME, VOC, FC, DAL, DAT, DCD, DAF, DIC, AFC

Modelo (me/models/document_exp.py):
- [ ] Campo has_reentry: Boolean, stored, computed
- [ ] @api.depends('document_movement_ids.destination_dependence_id.is_internal')
- [ ] Algoritmo: salida antes de reingreso (no solo coexistencia de ambos)
- [ ] Movimientos automáticos (destino siempre interno) no generan falsos positivos

Vista (me/views/document_exp_views.xml):
- [ ] Filtro predefinido en search view: "Con reingreso institucional"
      domain=[('has_reentry', '=', True)]

i18n (me/i18n/es_AR.po):
- [ ] Traducción de has_reentry y de is_internal

Tests (me/tests/ — clase TestHasReentry021):
- [ ] Expediente sin salidas → has_reentry = False
- [ ] Expediente con salida pero sin reingreso → has_reentry = False
- [ ] Expediente con salida y reingreso posterior → has_reentry = True
- [ ] Solo movimientos automáticos (destinos internos) → has_reentry = False
- [ ] Secuencia interno → externo → externo → interno → has_reentry = True
- [ ] is_internal recalcula has_reentry si se modifica en una dependencia

---- Impacto técnico ----

- me/models/dependence_ext.py (nuevo)
- me/models/document_exp.py
- me/data/dependence_data.xml (nuevo o extender)
- me/__manifest__.py — registrar dependence_ext.py en models y data
- me/views/document_exp_views.xml
- me/i18n/es_AR.po
- me/tests/test_document_exp.py

Documentación:
- me/ai-context.md: is_internal en extensión de tmc.dependence; has_reentry en me.document_exp
- domain-rules/me/workflows.md: nota en Workflow 5 sobre clasificación interna/externa

--------------------------------------------------