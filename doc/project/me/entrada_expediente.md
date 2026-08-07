# Entrada del expediente en ME — reglas y anclaje normativo

> Base de conocimiento de las reglas de **ENTRADA** del expediente en Mesa de Entradas (ME),
> con su **procedencia**. El "cómo" técnico (observado en código) vive en
> [`business_rules.md`](business_rules.md); acá va el **"por qué / de dónde"** y el contrato
> cross-repo con JUNCO, para que las reglas de entrada no queden dispersas.
>
> **Regla:** no se inventan reglas de negocio. Lo que la fuente no confirma queda *(a confirmar)*.

## Anclaje normativo (por qué ME es liviano acá)

ME **no tiene una ordenanza propia** (dato del usuario): no existe una "Ordenanza de Mesa de
Entradas". El anclaje normativo de ME es:

- **Ord. 7.767** (carta orgánica / funcionamiento del TMC, 2004). **ME es parte del TMC**, comparte
  el marco. El rol de **veedor** del TMC en la Junta de Compras se ancla en el **art. 20**
  (detalle y cita en `odoo-junco` → `doc/project/normativa.md` §2 y `circuito_veedor_pro11.md`).
- **Procedimientos internos**, no una ordenanza: **PRO-11 "Función Veedor TMC"** (Rev. 03, manual
  **oficial** del TMC). Es la fuente del circuito de entrada.
- El **Decreto 438** (reglamento de compras) es **dominio de JUNCO** — no se documenta acá.

Por eso ME no lleva un `normativa.md` grande (quedaría fino). Si con el tiempo ME acumula
decisiones normativas durables, replicar el patrón de junco (cita textual + referencia + mapeo).

## Circuito de entrada (PRO-11) — DEM / CM / TMC

Fuente: **PRO-11** (`odoo-junco` → `doc/project/references/documentacion_interna/PRO 11 Funcion
Veedor TMC.pdf`), vía `circuito_veedor_pro11.md`. Verificado contra el código de ME donde aplica.

| Origen | Cómo entra (PRO-11) | Jurisdicción / Repartición en ME (código) |
| --- | --- | --- |
| **DEM** (Departamento Ejecutivo / Municipalidad) | Alta en el Sistema **MEGE/ME** | Se **ceden a JUNCO**: vacías al ingresar, las escribe JUNCO (EPIC-004). **Excepción Nota**: ME las carga al ingreso (EPIC-004/TASK-002). |
| **CM** (Concejo Municipal) | **Sello de recepción** (trato distinto; no pasa por Junta de Compras) | `jurisdiction` = el origen CM (auto); **NO se carga repartición** (`source_dependence_id` vacío) — solo se **marca** el origen CM. |
| **TMC** (interno del Tribunal) | Origina en el propio TMC | `jurisdiction` = TMC (auto); `source` manual. |

- Solo se admiten estos 3 orígenes (filtro `['DEM','TMC','CM']`; ver `business_rules.md`).
- El comportamiento CM/TMC (jurisdicción auto, CM sin repartición) está en
  `document_exp.py::_onchange_dependence` — coincide con PRO-11.

## Identificación del expediente

- **PRO-11**: `Exp - Nro (MR) - Abrev. Secretaría - Año`; Referencia **"Llamado a licitación"**;
  Nº Expte DEM/CM.
- **En ME (código)**: `EXP-XXXXXX-ORIGEN/AÑO` (ej. `EXP-000042-DEM/2025`), donde **ORIGEN = la
  abreviatura del origen (DEM/CM/TMC)**, calculado en tiempo real (`computed_name`).
- **Decisión (usuario, validada 2026-08-07):** en Mesa de Entradas el identificador usa el
  **origen** (DEM/CM/TMC), **no** la secretaría que menciona el PRO-11 — **está bien así**. No es
  un gap: es la granularidad **deliberada** de ME. La secretaría fina vive en
  `jurisdiction_dependence` (para DEM-compras, cedida a JUNCO).

## Contrato de origen DEM/CM ↔ JUNCO — lado ME

La regla del **stack** es **BR-021, gobernada en `odoo-junco`** (asimetría de origen del
expediente autorizante). Acá se registra **el lado ME**, sin duplicarla:

- **DEM**: ME **cede** jurisdicción/origen a JUNCO; JUNCO los escribe sobre `me.document_exp` vía
  `action_set_origin_from_junco()` (EPIC-004). La "Repartición Solicitante" de JUNCO espeja el
  `source`.
- **CM**: entra por **sello de recepción**; ME solo **marca** el origen CM; **no** se carga
  repartición; **no** pasa por Junta de Compras.
- **TMC interno**: excluido del selector de expediente autorizante en JUNCO (BR-005).
- **Excepción DEM+Nota** (EPIC-004/TASK-002): las Notas **no** van a JUNCO → ME carga
  jurisdicción/origen al ingreso (y `action_set_origin_from_junco` rechaza Notas, defensa en
  profundidad).

Ref.: `business_rules.md` (regla "Permisos cross-sistema" y las de EPIC-004); `odoo-junco` →
`business_rules.md` **BR-021**, `circuito_veedor_pro11.md`, `normativa.md` §2.

## Qué es dominio de ME vs cross-repo

- **De ME**: el circuito de **entrada** (alta DEM / sello CM / TMC), la identificación, los
  movimientos iniciales, las validaciones de carga. Documentado acá + `business_rules.md`.
- **De JUNCO** (no se documenta acá, solo se referencia): el reglamento de compras (Decreto 438),
  el circuito del **veedor** post-entrada (PRO-11 completo), el `process_type`, BR-005/BR-021.

## Validado (usuario, 2026-08-07)

- [x] **Identificador**: usa el **origen** (DEM/CM/TMC), no la secretaría — **está bien así**
      (ver Identificación). Es la granularidad deliberada de ME.
- [x] **No** hay reglas de entrada del PRO-11 sin contemplar que deban volverse BR (a la fecha).
