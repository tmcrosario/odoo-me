# EPIC-004 / TASK-004 — Acotar el subtema de Licitación a Privada/Pública

Estado: Done
Modo: S
Riesgo: bajo (domain de vista en ME; sin tocar `tmc_data`; JUNCO ya valida su lado)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Fecha de toma: 2026-07-30
- Notas: viene de IDEA 2 (`brainstorming.md`), coordinada y confirmada con `odoo-junco`.

## Objetivo

Al cargar un expediente con tema **Licitación**, que el subtema (`secondary_topic_id`) ofrezca
**solo los 2 subtipos reales — Privada / Pública —** en vez de los **25 hijos** del tema (la
taxonomía documental de GD). JUNCO deriva su `process_type` de este subtema, así que mostrar 25
opciones invita a un error de carga que rompe el downstream.

## Alcance

- Campo computed `allowed_secondary_topic_ids` (no-stored, calcado de `allowed_exp_topic_ids`,
  `relation=` explícito para no colisionar): **Licitación → los 2 xmlids `_licitacion_publica` /
  `_privada`**; cualquier otro tema → hijos del tema (comportamiento anterior). Depende de
  `main_topic_id` (el proxy) para reaccionar en vivo en el form.
- `secondary_topic_id` pasa a filtrar por `[('id','in', allowed_secondary_topic_ids)]`.
- **Tweak Concurso de Precios:** el subtema se **oculta** cuando el tema no tiene subtemas
  permitidos (`invisible="not main_topic_id or not allowed_secondary_topic_ids"`) → no queda un
  dropdown vacío.

No incluye:

- **Tocar `tmc_data`** (el árbol queda intacto — ver guardrail). No hay `@api.constrains`
  (es ayuda de carga por domain; JUNCO tiene el enforcement duro de su lado).
- Migrar dato viejo (expedientes con subtema "etapa" ya cargados no se tocan; el valor se sigue
  mostrando, solo el dropdown para nuevos quedó acotado).

## Reglas conocidas / guardrail (verificado + confirmado con junco, 2026-07-30)

- Los 25 hijos de Licitación son **taxonomía documental de GD** (usada por resoluciones, decretos,
  convenios…), **no** eventos de JUNCO (JUNCO tiene `junco.process_event` propio). El árbol
  `tmc.document_topic` es general (62 raíces / 201 temas); ME usa 4 raíces. **El dato NO está mal.**
- **JUNCO consume el subtema:** `_derive_process_type_from_exp` (`purchase_process.py:692-699`)
  mapea `publica→public_tender`, `privada→private_tender`, otra cosa→`False`; el gate
  `_set_current_expediente_id` **ya lanza UserError** si es `False`. → El recorte **alinea** con un
  requisito que junco ya imponía; vuelve ese error inalcanzable por UI para expedientes nuevos.
  **Sin regresión, sin migrar** (junco confirmó y agregó `test_licitacion_without_subtype_rejected`,
  `d3497c8`, para blindar el camino ORM).
- **⚠️ Guardrail:** junco depende de que las "etapas" sigan siendo hijos de `_licitacion` vía
  **otro campo** (`junco.process_event.document_topic_id` = `licitacion.child_ids`). Por eso el
  recorte es **domain de vista en ME y NO toca `tmc_data`**.

## Acceptance criteria

- [x] Licitación → subtema ofrece **solo Privada/Pública** (2, no 25).
- [x] Otros temas → subtema **sin cambios** (hijos del tema).
- [x] Concurso de Precios (sin hijos) → subtema **oculto** (no dropdown vacío).
- [x] **No se toca `tmc_data`** (las 23 etapas siguen colgando de Licitación → `process_event`
      de junco intacto).
- [x] Suite `/me` verde + UI verificada en me2.

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md` (`-u me`, path OCA completo, `--test-tags /me`, `me_test`).
- Fecha: 2026-07-30
- Resultado: **0 failed, 0 error(s) of 241 tests** (stats 295). `test_licitacion_subtopic.py`
  (5 métodos: solo publica/privada, excluye etapas pero siguen colgando de Licitación, reacciona
  al proxy antes de guardar, no-regresión de otros temas, Concurso vacío). Aplicado a me2 + restart.
  UI verificada por el usuario.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido.

## Resultado / cierre

Cerrada (Done) el 2026-07-30 sobre `develop`. El subtema de Licitación se acota a Privada/Pública
(domain de vista en ME, sin tocar `tmc_data`), alineado con lo que JUNCO consume y confirmado con
ellos. Concurso de Precios oculta el subtema vacío. IDEA 2 (`brainstorming.md`) marcada implementada.
