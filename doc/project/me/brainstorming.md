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
