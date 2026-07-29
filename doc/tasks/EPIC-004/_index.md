# EPIC-004 — Índice de tasks

Épica: `doc/epics/EPIC-004_reacotamiento_carga_me_traspaso_junco.md`

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Reacotamiento de la carga DEM (cesión jurisdicción/origen a JUNCO) | sin asignar | L | Done (sobre develop) | Validada end-to-end en me2 (`-u me,junco`). Deploy a prod diferido (usuario). JUNCO EPIC-010 Done |
| TASK-002 | Carga de jurisdicción/origen en DEM con tema Nota (excepción a TASK-001) | Ale Gallo | L | Done (sobre develop) | Las Notas no van a JUNCO → ME las carga al ingreso (obligatorio, guard write). + validaciones de fecha + label i18n. Suite 233/0/0; UI verificada. Coordinado con junco (EPIC-010/TASK-003) |
