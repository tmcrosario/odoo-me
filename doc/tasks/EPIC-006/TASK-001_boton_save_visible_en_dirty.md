# EPIC-006 / TASK-001 — Botón "Save" textual visible solo en dirty

Estado: Done
Modo: S
Riesgo: bajo (UX/cosmético; sin modelo, ACL ni JS)
Módulo: `me`
Responsable: Ale Gallo

## Asignación

- Estado de toma: cerrada (Done)
- Notas: portado de `junco:EPIC-008/TASK-004` (repo dueño del patrón: `odoo-junco`).
  Registrado antes como IDEA 3 en `brainstorming.md`.

## Objetivo

Que el form de `me.document_exp` muestre un botón **"Save"** textual en el header, visible
**solo cuando el registro está dirty** (modificado sin persistir), para el usuario operativo
al que la nube/check del breadcrumb de Odoo 19 le cuesta encontrar. Convive con la nube (no
la reemplaza).

## Alcance

Incluye:

- `<header>` + `<button special="save" class="btn-outline-primary o_me_form_save_button">`
  en el form principal de expediente (`document_exp_view_form`).
- SCSS nuevo (`me/static/src/scss/me_form_save_button.scss`) que oculta el botón por defecto
  y lo muestra cuando el renderer tiene `o_form_dirty`.
- Sección `assets` (`web.assets_backend`) en `__manifest__.py` — **primer asset de frontend
  de `me`**.
- Test de regresión (`test_save_button.py`): arch + registro del asset.

No incluye:

- Otros forms (movimiento, `raa`): decisión diferida (ver Preguntas abiertas de la épica).
- Enforcement/lógica de guardado: es el guardado **nativo** de Odoo, solo hecho visible.

## Acceptance criteria

- [x] En un registro **limpio** el botón **no** aparece; el form se ve normal.
- [x] Al **editar** cualquier campo aparece "Save" en el header, estilo outline (fondo
      blanco en reposo, borde/texto de marca, como "New").
- [x] Click en Save (o Alt+S) guarda con el flujo nativo y el botón desaparece.
- [x] El scope del SCSS no afecta **ningún otro form** del backend (todas las reglas
      cuelgan de `.o_me_form_save_button`).
- [x] Suite `/me` verde tras el cambio.

## Decisiones de diseño

- **Barra NO se colapsa (junco-literal).** El form de `me` no tiene widget `state`/statusbar,
  así que su `<header>` existe solo para el botón. La primera versión **colapsaba** la barra
  vacía en limpio, pero eso provocaba un **salto de layout ~44px** al pasar a dirty (la barra
  aparece y empuja el sheet). Se descartó: una `.o_form_statusbar` vacía es solo `~py-2` de
  `$body-bg` **sin borde ni min-height** (verificado en `web/.../form_controller.scss`) →
  imperceptible. Se dejó el patrón literal de junco (salto ~28px, aceptado por el usuario en
  UI). Alternativa "cero salto" (reservar espacio con `visibility`) quedó documentada por si
  se pide.
- **`special="save"`** dispara un reload extra al guardar respecto del Save nativo del control
  panel (traza confirmada en fuente). Es el costo del patrón **zero-JS** y es el mismo que
  junco shippeó y validó en UI. Aceptado; no bloquea.
- **`data-hotkey="s"`** coexiste con el Save del control panel: el dispatcher toma el primero
  en el DOM (el nativo) → sin doble-guardado ni error (verificado en `hotkey_service.js`).

## Validación

- **Revisión adversarial multi-agente** (5 lentes) sobre el diff: 6 findings reales, todos
  `minor`. Corregidos en código: salto de layout (→ junco-literal) y test solo-arch (→ guard
  del asset). Descartados: filtración del SCSS global y soporte de `:has()` (Odoo 19 =
  navegadores evergreen). Los de doc (IDEA 3 desactualizada, inventario de tests) se saldaron
  en este cierre.
- **UI verificada en me2** (usuario, 2026-07-27): limpio→sin botón, editar→aparece,
  Save→guarda y desaparece; el movimiento leve al editar "no es molesto".

## Tests evidenciados

- Estado: OK
- Comando: canónico de `tests_plan.md` (`-u me`, `--addons-path` completo con las 5 rutas
  OCA, `--test-tags /me`, `me_test`).
- Fecha: 2026-07-27
- Resultado: **0 failed, 0 error(s) of 209 tests** (stats `me: 259`) sobre `me_test`.
  Antes: 207 → +2 métodos (`TestSaveButton`). Aplicado a me2 (`-u me`) + restart odoo.

## Estado / próximo paso

**Done.** Push: usuario. Deploy a prod: diferido.

## Resultado / cierre

Cerrada (Done) el 2026-07-27 sobre `develop`. Botón Save dirty-only en el form de expediente,
patrón zero-JS portado de `junco:EPIC-008/TASK-004`. Introdujo el **primer asset de frontend
de `me`** (`me/static/src/scss/` + `assets` en el manifest). Suite 209/0/0, UI verificada en
me2. IDEA 3 (`brainstorming.md`) marcada como implementada apuntando acá.
