# EPIC-005 — Índice de tasks

Épica: `doc/epics/EPIC-005_deuda_tecnica.md`

> Follow-ups de código derivados del inventario de EPIC-001/TASK-001 (§8.6 y §8.8). Las dos
> task cards existen y están `Done` (TASK-001, TASK-002).

| Task | Título | Responsable | Modo | Estado | Notas |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | Remover campo muerto `allowed_dependence_ids` | sin asignar | XS | Done | Removido + compute; sin referencias; suite 201/0/0; ai-context corregido |
| TASK-002 | Decidir/declarar dependencia `raa` en el manifest | sin asignar | S | Done | No declarable (sería circular `raa→me`); acoplamiento implícito documentado en `models.md` |
