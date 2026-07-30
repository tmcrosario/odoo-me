# Brainstorming ME (Mesa de Entradas)

Documento vivo para ideas, dudas y posibles tareas del módulo `me`.

## Uso

- No es canónico.
- No reemplaza épicas, specs ni task cards.
- Sirve para capturar ideas sueltas y convertirlas después en tareas formales.
- Cuando algo se cierre, se mueve a épica/task y se deja acá solo como referencia.

## IDEA 1 - Búsqueda DEM por jurisdicción / procedencia (post-EPIC-004)

### Resumen

Tras EPIC-004, en los expedientes **DEM** los campos `jurisdiction_dependence` y
`source_dependence_id` ya no se cargan en ME (los completa JUNCO al vincular; en la UI
quedan **ocultos si vacíos / readonly si cargados**). Queda la duda de si hay que poder
**buscar** expedientes por esos dos campos en ME aunque estén ocultos en la carga.

Técnicamente sería chico (S): son campos **stored**, igual que los filtros por poseedor
(`current_holder_id`) y por oficina de destino (`current_location_dependence_id`) que ya
se hicieron en EPIC-003. Lo bloqueante **no es técnico sino de negocio**: ¿esa búsqueda
vive en ME o en JUNCO (que ahora gestiona esos datos para DEM)?

### Puntos a explorar

- [ ] ¿El uso real de "buscar por jurisdicción/procedencia" es frecuente en ME?
- [ ] Si se agrega, ¿confunde mostrar como filtro un campo que se ocultó en la carga?
- [ ] ¿Alcanza con un campo buscable, o se quiere group-by / searchpanel?

### Preguntas abiertas

- [ ] (a) ¿Alguien busca expedientes por jurisdicción/procedencia en ME?
- [ ] (b) Si sí, ¿se agrega el buscable/filtro aunque el campo esté oculto en el form?
- [ ] (c) ¿O esa búsqueda se hace en JUNCO, que ahora gestiona esos datos para DEM?

### Relación con otras ideas / reglas

- EPIC-003 (filtros de la search view: poseedor + oficina de destino, ya entregados).
- EPIC-004 (cesión de carga DEM a JUNCO).
- Siguiente paso cuando se retome: `/product-spec` para cerrar (a)/(b)/(c) antes de task.

## IDEA 2 - Subtema de Licitación: 25 hijos que mezclan subtipo con etapas del proceso

> **IMPLEMENTADO** (opción B1) → ver **EPIC-004/TASK-004** (Done, 2026-07-30). Licitación acotada
> a Privada/Pública del lado de ME (domain de vista, sin tocar `tmc_data`), coordinado y confirmado
> con junco. Se deja acá como referencia (el análisis de abajo es el registro original + corrección).

### Resumen

Al elegir el tema **Licitación**, el subtema (`secondary_topic_id`, "Specification") ofrece
**25 opciones** cuando el usuario espera **solo `Privada` / `Pública`** (el subtipo de licitación).

**No es un bug del código** (verificado 2026-07-24 en me2): el domain filtra bien a los hijos
del tema (`[('parent_id','=', main_topic_id)]`). El problema son los **datos**: el nomenclador
`tmc_data` le cuelga a `Licitación` 25 hijos directos que **mezclan dos dimensiones**:

- **Subtipo** (lo esperado): `Privada`, `Pública` (2).
- **Subtemas de clasificación documental** (23): `Adjudicación`, `Apertura de Sobres`, `Desierta`,
  `Deja Sin Efecto`, `Desestima Oferta`, `Llamado`, `Impugnación`, `Prórroga Contrato/Llamado`,
  `Rescisión - Extinción`, `Multa - Sanción`, `Recepción de Obra…`, etc.

Además `Concurso de Precios` **no tiene hijos** → su subtema queda vacío (mismo tema que la
pregunta "¿ocultar subtema si el tema no tiene hijos?").

### ⚠️ Corrección importante (revisado en repos, 2026-07-30)

El encuadre original de arriba ("las 23 son eventos del proceso, territorio de JUNCO") **es
falso** — corregido tras revisar los repos con el usuario:

- Los 25 hijos son **temas de la taxonomía de Gestión Documental (GD)**, definidos en `tmc_data`
  (`tmc_document_topic_licitacion_*`). GD los usa para **clasificar DOCUMENTOS** (resoluciones,
  decretos, convenios, etc.) relacionados con una licitación (ej. una *Resolución de Adjudicación*
  → tema `Licitación` / subtema `Adjudicación`). **No son eventos de JUNCO**: JUNCO tiene su
  propio modelo `junco.process_event`, aparte.
- El árbol `tmc.document_topic` es **general y grande** (62 raíces / 201 temas); ME solo usa 4
  raíces (`_EXP_ROOT_TOPIC_XMLIDS`). `tmc.document` ofrece tema/subtema para todo tipo de
  documento, filtrado por dependencia (`document_topic_ids`).
- **El dato NO está mal** y **no se puede tocar en `tmc_data`** sin romper la clasificación
  documental de GD. Descarta el "reestructurar el árbol" del planteo original.
- Los 25 hijos **no tienen `dependence_ids`** → el filtro por dependencia de GD no ayuda (los
  vaciaría). Ese camino tampoco sirve.

**JUNCO consume el subtema (riesgo de correctitud, no solo UX):** `junco.purchase_process`
(`purchase_process.py` ~l.686-697) lee `exp.secondary_topic_id` y compara por XML ID contra
`tmc_document_topic_licitacion_publica` / `_privada` para derivar el subtipo del proceso. Si al
cargar la Licitación el usuario elige una de las **23 etapas** en vez de Privada/Pública, **la
derivación de JUNCO no matchea** → comportamiento por defecto/incorrecto. Es decir: mostrar 25
opciones **invita a un error de carga que rompe el downstream**. Privada/Pública son un **contrato
de facto** (JUNCO ya las hardcodea por xmlid).

**Reencuadre:** no es un bug de dato, es un **desajuste de concepto en ME**. ME reusa el
subtema-de-documento de GD como "subtipo del expediente", y son cosas distintas: GD quiere una
clasificación rica (25); el expediente/JUNCO quieren un subtipo angosto (Privada/Pública).
La decisión de fondo: **¿qué debe ser `secondary_topic_id` en un expediente de Licitación?**

- **(A) Aceptarlo:** el subtema ES el subtema documental de GD → 25 opciones "por diseño".
  **Contra:** deja abierto el error de carga que rompe la derivación de JUNCO (ver arriba). Riesgoso.
- **(B) Acotar el subtema del expediente al subtipo real (Privada/Pública) para Licitación.**
  Alinea la carga con lo que JUNCO consume. Dos caminos, ninguno rompe GD:
  - **(B1) ME referencia los dos xmlids** (`_licitacion_publica` / `_privada`) para el subtema de
    Licitación — **mismo patrón que JUNCO ya usa** (no inventa regla: reusa el contrato de facto).
    Todo en ME, sin tocar `tmc_data`. Pragmático. Ojo: acopla ME a esos xmlids (como junco).
  - **(B2) Discriminador aditivo en `tmc_data`** (flag "es subtipo" en Privada/Pública) → ME filtra
    por el flag, genérico. Más limpio y general, pero toca repo externo + coordinar.
- **(C) descartadas:** filtro por dependencia (vaciaría — los hijos no tienen `dependence_ids`);
  lista hardcodeada arbitraria (pero B1 no es arbitraria: son los xmlids del contrato con JUNCO).
- **Aparte:** ocultar el subtema cuando el tema no tiene hijos (Concurso de Precios → subtema vacío).

### Puntos a explorar

- [ ] ¿Las 23 "etapas" son subtemas del expediente en Mesa de Entradas, o son eventos del
      proceso que gestiona JUNCO? Si es lo segundo, no deberían colgar de `Licitación` como subtema.
- [ ] ¿El fix es de **datos** (reestructurar el árbol en `tmc_data`: subtipo vs etapas en
      nodos/niveles distintos) o hace falta un **discriminador** (flag "es subtipo" vs "es etapa")
      para que `me` filtre?
- [ ] Ocultar el subtema cuando el tema no tiene hijos (caso Concurso de Precios).

### Preguntas abiertas

- [ ] ¿Quién es dueño de la decisión del árbol de temas? El fix probablemente vive en `tmc_data`
      (repo externo, no se toca desde este flujo) — igual que el nomenclador del #033.
- [ ] ¿El subtema debería tener enforcement backend (`@api.constrains`) o seguir siendo solo
      ayuda de carga por `domain`? (mismo dilema que los temas raíz).

### Verificado en junco (revisión de código, 2026-07-30)

Investigación adversarial de 2 lentes sobre `odoo-junco` (consumo real + impacto del recorte):

- **JUNCO lee el subtema en UN solo lugar de producción:** `_derive_process_type_from_exp`
  (`purchase_process.py:692-699`) — `publica→public_tender`, `privada→private_tender`, cualquier
  otra cosa (etapa/vacío)→`False`. **No escribe** el subtema en ningún lado (solo `_persist_dem_origin`
  escribe jurisdicción/origen). Ninguna vista de junco pone domain sobre el campo.
- **JUNCO ya exige Privada/Pública hoy:** el gate `_set_current_expediente_id` (`:751-758`) lanza
  `UserError` ("Correct the classification in ME first") si la derivación da `False`. → El recorte
  de ME (B1) **alinea con un requisito que ya existe** y vuelve ese error **inalcanzable** para
  expedientes nuevos. **Sin regresión, sin migrar dato** (los preexistentes con subtema "etapa"
  junco ya los tolera/rechaza igual). La elegibilidad del picker filtra por **tema principal, no
  por subtema** → no cambia.
- **⚠️ Guardrail (único riesgo, condicional):** junco depende de que las "etapas" sigan siendo
  **hijos de `tmc_document_topic_licitacion`**, pero vía **otro campo** —
  `junco.process_event.document_topic_id`, cuyo dropdown de "Actos" sale de `licitacion.child_ids`
  (`process_event.py:206-217`). Por eso el recorte **DEBE ser B1 (domain de vista en ME)** y **NO
  tocar `tmc_data`**. Reestructurar el árbol rompería el dropdown de Actos y la derivación de
  estado/`call_document` de junco. (Refuerza descartar B2-reestructuración; un flag aditivo sería
  inocuo, pero B1 es más simple y ya alcanza).
- Gap menor (de junco, informativo): ningún test de junco cubre el fallback "licitación sin
  subtipo → False → UserError".

**Confirmado por junco (chat, 2026-07-30):** ambos puntos SÍ — Privada/Pública son los únicos
subtipos reconocidos, ningún flujo necesita otro, adelante con B1, sin regresión, no requieren
cambios. Cerraron el gap: agregaron `test_licitacion_without_subtype_rejected` (`d3497c8`, suite
junco 175/0) que blinda el camino ORM/import que el recorte de vista no cubre. **→ B1 habilitado
para implementar** (domain de vista en ME, sin tocar `tmc_data`).

### Relación con otras ideas / reglas

- #033 (nomenclador mal modelado en `tmc_data`) — misma clase de problema.
- junco:EPIC-011 (temas raíz) y el `process_type` que JUNCO deriva del tema.
- `business_rules.md` → "Subtema acotado al tema" + Limitaciones conocidas (caso Licitación).
- Siguiente paso cuando se retome: `/product-spec` (define subtipo vs etapa antes de cualquier
  cambio de datos o código).

## IDEA 3 - Botón "Save" textual visible solo cuando el form está dirty (portable de junco)

> **IMPLEMENTADO** en `me` → ver **EPIC-006/TASK-001** (Done, 2026-07-27). Se deja acá solo como
> referencia (convención: idea cerrada → épica/task). Lo de abajo es el registro original.

Viene de **junco:EPIC-008/TASK-004** (commit `f4f7aae`, repo `odoo-junco`). Patrón **100%
cosmético/UX, portable**.

### Resumen

En Odoo 19 el guardado del form es la nube/check del breadcrumb, que a algunos operativos les
cuesta encontrar. La idea es un botón **"Save" explícito en el `<header>`** que aparece **solo
cuando el registro está "dirty"** (modificado sin persistir) y desaparece al guardar.
**Cero JS**: es un botón nativo `special="save"` + una regla **SCSS** que lo muestra/oculta según
la clase `o_form_dirty` que el renderer de Odoo ya pone. Es el **mismo guardado nativo**, solo
hecho visible; convive con la nube del breadcrumb (redundancia a favor del usuario).

### Qué haría falta en `me` (si se adopta) — 3 piezas

1. **Botón** en el `<header>` del form (antes del statusbar): `<button string="Save"
   special="save" class="btn-outline-primary o_me_form_save_button" data-hotkey="s"/>`
   (clase renombrada `o_me_form_save_button` para no depender de assets de junco).
2. **SCSS nuevo** (`me/static/src/scss/…`): oculto por defecto (`display:none`), visible con
   `.o_form_view:has(.o_form_renderer.o_form_dirty) … { display:inline-flex }`, estilo outline
   (fondo blanco en reposo, como el botón "New").
3. **Registrar el SCSS** en `__manifest__.py` → `"assets": {"web.assets_backend": [...]}`.

### Grounding en `me` (verificado 2026-07-24)

- ✅ **`me` NO usa `boolean_toggle`** en sus forms → la trampa que avisaron (los toggles
  autoguardan en Odoo 19 y rompen el "dirty + Save") **no aplica hoy**. Si se agrega un toggle a
  esos forms, pasarle `options="{'autosave': false}"`.
- ✅ **(al implementar)** `me` **ahora sí** tiene `me/static/src/scss/` + sección `assets` en el
  manifest — fue su **primer asset de frontend**. El grounding original decía "no tiene assets":
  cierto al 2026-07-24, ya no tras EPIC-006/TASK-001.

### Puntos a explorar

- [ ] ¿En qué form(s)? Criterio de junco: SÍ en forms de carga/edición operativa donde se tipean
      varios campos antes de guardar; **arrancar por el form principal de `document_exp`** y ver
      con el usuario si suma antes de esparcirlo. NO en wizards, solo-lectura, o forms con toggles
      de acción inmediata.
- [ ] ¿Conviene un asset backend global o acotarlo? (define la superficie del SCSS).

### Preguntas abiertas

- [x] ¿Lo adopta `me`? **Sí** — EPIC-006/TASK-001, solo `document_exp` por ahora.
- [ ] ¿Esparcir a otros forms (movimiento, raa)? Diferido; se evalúa caso por caso (nueva task en EPIC-006).

### Relación con otras ideas / reglas

- Fuente: `junco:EPIC-008/TASK-004` (`odoo-junco`, commit `f4f7aae`; suite junco 100/100 + UI OK
  en me2 al commit). **No se toca junco desde acá**; esto es solo para replicar en `me` si se ve útil.
- Riesgo bajo: sin modelo, sin ACL, sin JS. Regla Odoo 19 de `me`: `<list>` no `<tree>`, sin `attrs`.
- Estado: **cerrada** (EPIC-006/TASK-001, Done). Para esparcir a otros forms, abrir nueva task en EPIC-006.

## IDEA 4 - 1er movimiento de una Nota: origen = jurisdicción (no "Departamento Ejecutivo")

> **IMPLEMENTADO** → ver **EPIC-004/TASK-003** (Done, 2026-07-30). Se deja acá como referencia
> (convención: idea cerrada → épica/task). El análisis de abajo es el registro original.

### Resumen

Hoy el **1er movimiento automático** de un DEM usa `dependence_id` (DEM / "Departamento
Ejecutivo") como origen → `DEM → TMC`. Fue **decisión de EPIC-004** (opción A): usar
`dependence_id` y **no** la jurisdicción, para que el movimiento exista **aunque la
jurisdicción esté vacía** (caso compras, donde JUNCO la completa después).

Para **Notas** ese bloqueo **no aplica**: la jurisdicción es **obligatoria y siempre está**
al ingreso (EPIC-004/TASK-002). Entonces el 1er movimiento podría reflejar la **secretaría
real** que originó el expediente: `jurisdicción → TMC` en vez del genérico `DEM → TMC`.

### Viabilidad (verificada en código, 2026-07-29)

- ✅ **Ningún constraint del movimiento** restringe el origen (solo valida fecha no futura,
  fecha ≥ ingreso, y legajo). Una jurisdicción es un origen válido.
- ✅ **Nada computa sobre `origin.is_internal`**: `has_reentry` / `is_currently_internal`
  miran el **destino**. Cambiar el origen del 1er movimiento **no** afecta el rastreo interno.
- El cambio sería acotado en `create()` (bloque de movimientos automáticos): para Notas con
  jurisdicción, usar `jurisdiction_dependence` como origen del 1er movimiento.

### Puntos a explorar

- [ ] **¿Jurisdicción o repartición?** `source_dependence_id` (la repartición) es **más
      específica** que la jurisdicción. ¿El origen del movimiento debería ser la repartición
      cuando existe, y la jurisdicción si no? (el usuario pidió "jurisdicción").
- [ ] **Consistencia con compras:** las compras seguirían con `DEM → TMC` (jurisdicción vacía
      al ingreso). ¿Está bien que Notas y compras difieran en el 1er origen? (parece sí:
      Notas tienen el dato, compras no).
- [ ] **`is_internal` de las jurisdicciones** está inconsistente en el dato (en me2: 3 con
      `true`, 31 con `NULL`) — no bloquea (nada computa sobre origin.is_internal), pero conviene
      entender qué significa antes de mostrarla como origen.
- [ ] Defensivo: si una Nota no tuviera jurisdicción (no debería, es obligatoria), caer a
      `dependence_id`.

### Preguntas abiertas

- [ ] ¿El origen del 1er movimiento de una Nota debe ser la **jurisdicción** o la
      **repartición** (source)? Decisión de negocio/usuario.
- [ ] ¿Solo Notas, o esto también aplicaría a compras el día que JUNCO complete la jurisdicción?

### Relación con otras ideas / reglas

- Habilitado por **EPIC-004/TASK-002** (Notas cargan jurisdicción obligatoria al ingreso).
- Toca la regla "Movimientos iniciales automáticos" de `business_rules.md` (workflow) →
  cambio de regla de negocio, requiere AC antes de implementar. Modo estimado: **S**.
- Siguiente paso si se retoma: cerrar jurisdicción-vs-repartición y `/new-task` en EPIC-004.

### Cómo funciona HOY (verificado en dato real, 2026-07-29)

El origen del 1er movimiento es un **snapshot al crear**; **no** sigue cambios posteriores de
la jurisdicción. Corte temporal limpio en me2:

- **Antes de EPIC-004** (creados 2026-06-10/11, 12 exps): origen = **jurisdicción** de ese
  momento (todos "SECRETARÍA DE HACIENDA Y ECONOMÍA", el valor de entonces).
- **Desde EPIC-004** (2026-06-17+, 25 exps): origen = **`dependence_id`** ("DEPARTAMENTO
  EJECUTIVO"), fijo.

**El caso que reportó el usuario (EXP-039310):** licitación pre-EPIC-004; su movimiento congeló
origen="Hacienda", y **JUNCO después le cambió la jurisdicción a "Planeamiento"** vía
`action_set_origin_from_junco` — que actualiza `jurisdiction_dependence` pero **no toca el
movimiento ya creado**. Por eso jurisdicción≠origen-del-movimiento. Es **dato legacy**, no un bug
del código actual, y **JUNCO no escribe movimientos de ME** (verificado por grep).

**Implicación para esta idea (buena):** poner origen = jurisdicción para **Notas** es seguro
justo porque el desfase que se ve arriba es un fenómeno de **compras+JUNCO** (jurisdicción
seteada DESPUÉS del alta). En Notas la jurisdicción se carga **al ingreso**, es obligatoria y
**JUNCO nunca las toca** → el snapshot queda siempre consistente con la jurisdicción. La idea es,
en esencia, **recuperar el origen=jurisdicción de pre-EPIC-004, pero solo para Notas** (donde es
estable). Compras siguen con "Departamento Ejecutivo".
