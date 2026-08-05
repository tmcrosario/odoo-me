# EPIC-006 — Índice de tasks

Épica: `doc/epics/EPIC-006_usabilidad_form_expediente.md`

> Usabilidad del **formulario** de expedientes (EPIC-003 fue la vista lista). Mejoras
> chicas de UX, mayormente cosméticas.

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Botón "Save" textual visible solo en dirty | Ale Gallo | S | Done | Portado de `junco:EPIC-008/TASK-004`; primer asset frontend de `me`; suite 209/0/0; UI verificada en me2 |
| TASK-002 | Indicador "En Legajo Nº X" en el form + filtro "Adjuntos a Legajo" | Ale Gallo | S | Done | Computed `current_legajo_number` (último movimiento a LEG) + filtro de lista; strings inglés + i18n `es_AR`; suite 246/0/0; UI verificada |
