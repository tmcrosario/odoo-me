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

### Resumen

Al elegir el tema **Licitación**, el subtema (`secondary_topic_id`, "Specification") ofrece
**25 opciones** cuando el usuario espera **solo `Privada` / `Pública`** (el subtipo de licitación).

**No es un bug del código** (verificado 2026-07-24 en me2): el domain filtra bien a los hijos
del tema (`[('parent_id','=', main_topic_id)]`). El problema son los **datos**: el nomenclador
`tmc_data` le cuelga a `Licitación` 25 hijos directos que **mezclan dos dimensiones**:

- **Subtipo** (lo esperado): `Privada`, `Pública` (2).
- **Etapas/actos del proceso licitatorio** (23): `Adjudicación`, `Apertura de Sobres`, `Desierta`,
  `Deja Sin Efecto`, `Desestima Oferta`, `Llamado`, `Impugnación`, `Prórroga Contrato/Llamado`,
  `Rescisión - Extinción`, `Multa - Sanción`, `Recepción de Obra…`, etc. — conceptualmente son
  **eventos del proceso** (territorio de JUNCO `process_event`), no subtipos del expediente.

Además `Concurso de Precios` **no tiene hijos** → su subtema queda vacío (mismo tema que la
pregunta "¿ocultar subtema si el tema no tiene hijos?").

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
