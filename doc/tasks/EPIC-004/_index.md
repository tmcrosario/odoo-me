# EPIC-004 — Índice de tasks

Épica: `doc/epics/EPIC-004_reacotamiento_carga_me_traspaso_junco.md`

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO) | sin asignar | L | Done (sobre develop) | Validada end-to-end en me2 (`-u me,junco`). Deploy a prod diferido (usuario). JUNCO EPIC-010 Done |
| TASK-002 | Carga de jurisdicción/origen en DEM con tema Nota (excepción a TASK-001) | Ale Gallo | L | Done (sobre develop) | Las Notas no van a JUNCO → ME las carga al ingreso (obligatorio, guard write). + validaciones de fecha + label i18n. Suite 233/0/0; UI verificada. Coordinado con junco (EPIC-010/TASK-003) |
| TASK-003 | 1er movimiento de una Nota: origen = jurisdicción (no "Departamento Ejecutivo") | Ale Gallo | S | Done (sobre develop) | Habilitada por TASK-002 (Notas tienen jurisdicción estable). Compras intactas. Suite 236/0/0; UI verificada |
| TASK-004 | Acotar el subtema de Licitación a Privada/Pública (+ ocultar subtema sin hijos) | Ale Gallo | S | Done (sobre develop) | Domain de vista en ME (sin tocar `tmc_data`); alinea con lo que JUNCO consume (confirmado, junco agregó test `d3497c8`). Suite 241/0/0; UI verificada |
| TASK-005 | Subtema de Licitación requerido (upstream de JUNCO) | Ale Gallo | S | Done (sobre develop) | Pedido de junco. Required condicional + validación create/write (no `@api.constrains`, no rompe dato viejo). Concurso/directa intactos. Suite 254/0/0; UI verificada |
| TASK-006 | Tema requerido al alta + filtro "Sin clasificar" | Ale Gallo | XS | Done (sobre develop) | Que una compra sin tema no quede invisible para JUNCO. Required de vista (solo nuevas) + filtro `main_topic_ids=False`; sin backend (JUNCO ya gatea por tema). Suite 254/0/0; UI verificada |
