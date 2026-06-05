# Documentation policy

## Docs vivas

Durante implementación, la verdad operativa vive en:

- epic card correspondiente;
- task card `EPIC-XXX/TASK-YYY`;
- `doc/epics/_index.md`;
- `doc/tasks/_index.md`;
- `doc/tasks/EPIC-XXX/_index.md`.

## Docs canónicas

Actualizar documentos canónicos del proyecto solo cuando haya una regla durable, cambio estructural o decisión que deba sobrevivir a la task.

## Cierre documental

Una task dentro de una épica puede pasar a `Done` cuando existan:

- acceptance criteria OK;
- tests OK, user-run pendiente explícito o N/A justificado;
- verifier OK si el modo lo exige;
- riesgos bloqueantes resueltos o documentados.

La épica pasa a cierre solo cuando sus tasks necesarias están `Done`, canceladas o explícitamente diferidas.

## SLA de docs canónicas pendientes

- **Sin SLA estricto** por defecto. Una task que registra "Docs canónicas pendientes de consolidación" no expira automáticamente.
- **Revisión on-demand**: cuando algún miembro del equipo percibe que la deuda documental molesta o crece, se abre una task `S` para hacer barrida y consolidar.
- **No archivar tasks `Done` por edad**: las tasks Done quedan en sitio para preservar linaje y facilitar búsqueda.

Si en algún proyecto consumidor emerge deuda crónica, definir un SLA específico para ese proyecto en `doc/framework/project_config.md`.
