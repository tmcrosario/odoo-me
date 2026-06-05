# Tasks

Las tasks no viven sueltas: siempre pertenecen a una épica.

## Estructura esperada

```text
doc/tasks/
  _index.md                       # índice global liviano
  templates/                      # templates canónicos por modo
  EPIC-001/
    _index.md                     # índice de tasks de la épica
    TASK-001_titulo_corto.md
    TASK-002_titulo_corto.md
```

## Templates

Usar los templates canónicos de `doc/tasks/templates/`:

- `task_xs.md`
- `task_s.md`
- `task_m.md`
- `task_full.md`

No hay template genérico único por épica en V1: mantener XS/S/M/FULL evita sobredocumentar cambios chicos y fuerza a elegir intensidad.
