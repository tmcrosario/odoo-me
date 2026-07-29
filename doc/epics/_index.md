# Índice de épicas — odoo-me

Las épicas agrupan capacidades o líneas funcionales. Las tasks viven bajo
`doc/tasks/EPIC-XXX/`.

| Épica | Título | Módulo | Estado | Notas |
| --- | --- | --- | --- | --- |
| EPIC-001 | Reverse-engineering + baseline de mesa de entradas | `me` | Done (develop) | 4/4 tasks Done; doc canónica verificada y datada vs código; §7/§8 reconciliados |
| EPIC-002 | Integración ME ↔ JUNCO (proceso licitatorio) | `me` (consumido por `junco`) | Gobernada en `odoo-junco` | Implementada/documentada en JUNCO. Acá: solo contrato de campos (input de EPIC-001) + decisión #4 (visibilidad ME) parkeada. No abrir tasks de integración acá |
| EPIC-003 | Usabilidad y filtros de la vista de expedientes | `me` | Done (develop) | Filtros por usuario (S) y por oficina interna de destino (L). Ambas tasks Done; suite 201/0/0; UI verificada. Deploy a prod diferido |
| EPIC-004 | Reacotamiento de la carga de ME: traspaso de clasificación a JUNCO | `me` (+ `junco`) | Done (develop) | TASK-001: DEM cede jurisdiction/source a JUNCO vía `action_set_origin_from_junco`; 1er movimiento DEM→TMC desacoplado. **TASK-002**: excepción DEM+Nota (no van a JUNCO → ME carga al ingreso) + validaciones de fecha + label i18n; suite 233/0/0. Validada end-to-end en me2; deploy a prod diferido. Contraparte junco EPIC-010 Done (+ EPIC-010/TASK-003 agendada) |
| EPIC-005 | Deuda técnica (limpieza post-baseline) | `me` | Done (develop) | TASK-001 removió `allowed_dependence_ids`; TASK-002 decidió no declarar `raa` (circular `raa→me`), documentado |
| EPIC-006 | Usabilidad del formulario de expedientes | `me` | En progreso (develop) | TASK-001 Done: botón "Save" dirty-only (portado de `junco:EPIC-008/TASK-004`); **primer asset frontend de `me`**; suite 209/0/0; UI verificada. Épica abierta para más mejoras de form |

## Épicas de otros repos que aterrizaron código en `me`

> **Filas-puntero, no cards espejo.** El **repo dueño es `odoo-junco`**: las cards viven allá y
> **no se editan desde ME**. Acá se registra qué tocaron en `me` y dónde quedó la verdad durable
> (las canónicas de `doc/project/me/`). La numeración `EPIC-0XX` es **de junco** — se namespacea
> con `junco:` para no chocar con la numeración local de ME (EPIC-001..005).

| Épica (repo dueño) | Título | Qué tocó en `me` | Verdad durable en ME |
| --- | --- | --- | --- |
| **`junco:EPIC-011`** (`odoo-junco`) | Clasificar expedientes de compra directa / concurso de precios | `_EXP_ROOT_TOPIC_XMLIDS` +2 temas raíz (contratación directa, concurso de precios) y su test — commit `f0af6ac` | [`business_rules.md`](../project/me/business_rules.md) (regla "Temas raíz del expediente") · [`models.md`](../project/me/models.md) |
| **`junco:EPIC-015`** (`odoo-junco`) | Permisos cross-sistema: ME edita ME y solo lee GD (opción 1) | `me_groups.xml` (`implied_ids` de `group_user`/`group_read_only`), `create()` elevado + `check_access` previo, suite `test_security.py` — commits `bfb1926` + `181d2e6` | [`security.md`](../project/me/security.md) (postura, grupos, elevaciones, regla durable) |

**Cerrado (gobernado en junco):** `junco:EPIC-015/TASK-004` — el dropdown del privilegio ME no
ofrecía «User» a usuarios con grupos de JUNCO. Resuelto con la **cadena real** (opción b):
`me.group_user` implica `me.group_read_only` → la escalera es estructural (ranks 1<2<3) y no
depende del desempate por `id`. Fijado por `TestMeSecurity.test_me_privilege_ladder_order`.
Detalle en [`security.md`](../project/me/security.md).
