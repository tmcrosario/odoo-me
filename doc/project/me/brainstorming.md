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
