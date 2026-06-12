# EPIC-004 — Reacotamiento de la carga de ME: traspaso de clasificación a JUNCO

Estado: Draft
Riesgo global: alto/sensible (campos persistentes hoy required, workflow de movimientos, create(), validaciones, migración de datos, contrato cross-módulo)
Módulo: `me` (contraparte en `junco`, repo `odoo-junco`)
Owner: sin asignar

## Objetivo

Redefinir el alcance funcional del ingreso de expedientes en ME: dejar de cargar desde
ME los campos clasificatorios/funcionales que pasarán a completarse desde JUNCO, y
rediseñar la lógica de movimientos automáticos en consecuencia. ME queda acotado como
**sistema de ingreso y trazabilidad**; JUNCO pasa a completar parte de la información
funcional/clasificatoria.

> **Definición funcional, no implementación.** Esta épica no se implementa hasta cerrar
> el spec y el reparto ME↔JUNCO. Próximo paso: `/product-spec`.

## Contexto

Hasta ahora ME funcionaba con una carga más completa del expediente. El cambio mueve a
JUNCO la responsabilidad de **dos campos de origen/jurisdicción**, pero **solo para los
expedientes que JUNCO maneja (DEM/CM compras)**; los expedientes TMC conservan su carga
actual. ME conserva además los campos de clasificación temática y el objeto del
expediente.
El cambio impacta el contrato de campos que JUNCO ya consume de `me.document_exp`
(ver EPIC-002): hoy JUNCO **lee** `jurisdiction_dependence`; con este cambio podría
pasar a **escribirlo**, invirtiendo la dirección del dato. Requiere contraparte en la
EPIC-002 de `odoo-junco`.

## Alcance por tipo de origen (clave)

El traspaso aplica **solo a los expedientes que JUNCO maneja**: origen **DEM o CM** y
que sean **compras**. Los expedientes de **TMC no se ven en JUNCO** y **conservan su
carga actual en ME** (incluida `source_dependence_id`). Esto ya está aclarado del lado
JUNCO (solo ve DEM/CM compras).

Comportamiento actual por origen (`_onchange_dependence`, ~líneas 371-395):

| Origen | `jurisdiction_dependence` | `source_dependence_id` | ¿Va a JUNCO? |
| --- | --- | --- | --- |
| **DEM** (else) | manual (queda `False` hasta cargar) | manual; required si hay sub-dependencias (constraint ~línea 360) | Sí (si es compra) |
| **CM** | auto `= dependence_id` (línea 385) | se limpia (`False`), no se usa | Sí (si es compra) |
| **TMC** | auto `= dependence_id` (línea 383) | manual, **se conserva** (no required) | **No** |

## Campos afectados (AS-IS, grounded en `me/models/document_exp.py`)

ME **deja de cargar — solo para expedientes DEM/CM que van a JUNCO** (pasan a JUNCO):

| Campo | Estado actual | Cambio propuesto |
| --- | --- | --- |
| `jurisdiction_dependence` | Many2one, **required=True**; en DEM es manual, en CM es auto; alimenta `_compute_allowed_*`, `computed_name`, constraints y la derivación de movimientos | dejar de cargarse en ME para DEM/CM (lo completa JUNCO) |
| `source_dependence_id` | Many2one; en DEM es manual (lo relevante), en CM no se usa; **en TMC se conserva** | dejar de cargarse en ME para el flujo DEM/CM; **intacto para TMC** |

ME **conserva** (siguen cargándose en ME — corrección sobre la versión inicial):

| Campo | Nombre funcional | Estado actual | Nota |
| --- | --- | --- | --- |
| `main_topic_id` | subject (tema) | proxy compute/inverse sobre `main_topic_ids` (tmc.document) | ej. "Licitación" |
| `secondary_topic_id` | specification (subtema) | proxy sobre topics secundarios, domain por `main_topic_id` | ej. "Privada"/"Pública" |
| `document_object` | reference (objeto) | **required=True** (~línea 100); la UI ya lo etiqueta "Reference" | ej. "Compra de Equipamiento Informático". **Candidato a reutilizarse en JUNCO como objeto de la compra/contratación** (JUNCO lo leería; sin inversión, ME sigue siendo fuente) |

> UX: estos tres se quieren mostrar con etiquetas Subject / Specification / Reference,
> no como "Tema/Subtema/Objeto" (relabel menor en la vista de carga; `main_topic_id` y
> `secondary_topic_id` no tienen `string` propio hoy).

## Cambio en movimientos automáticos

Flujo objetivo:

- **1er pase:** DEM → TMC
- **2do pase:** TMC → ME

Hoy el origen del 1er pase se deriva de la carga manual de jurisdicción/dependencia de
origen (compute que setea `jurisdiction_dependence = dependence_id`, ~líneas 380-386).
Sin esa carga, hay que definir **cómo se determina el origen del 1er pase**.

## Alcance

Incluye (a precisar en spec):

- tratamiento de los dos campos cedidos (`jurisdiction_dependence`, `source_dependence_id`):
  ocultar / quitar de la fase de carga / dejar de ser required / pasar a readonly desde JUNCO;
- relabel UX de los campos conservados (subject/specification/reference);
- rediseño de la lógica de movimientos automáticos y de la determinación del origen;
- impacto en `create()`, validaciones/constraints, fases del formulario, tests y docs;
- reparto de responsabilidad ME↔JUNCO (fuente de verdad y momento de completado);
- tratamiento de expedientes ya existentes (migración / convivencia).

No incluye:

- la implementación (se abre como tasks recién tras el spec);
- la lógica interna de JUNCO ajena a estos campos.

## Módulos afectados

- Módulo principal: `me`
- Módulos secundarios afectados: `junco` (repo `odoo-junco`) — debe asumir la carga de
  los campos cedidos.
- Dependencias entre módulos: `junco` depende de `me`; `me` no puede depender de
  `junco`. La inversión del flujo de `jurisdiction_dependence` debe resolverse sin
  introducir dependencia circular.

## Reglas / decisiones durables

- No inventar reglas de negocio: el tratamiento de cada campo, la determinación del
  origen del 1er pase y la migración se deciden con el usuario en el spec.
- Cambios sobre campos persistentes required, workflow y create() escalan a L/XL y
  exigen contrato técnico antes de tocar código.
- Coordinar con la EPIC-002 de `odoo-junco`: el contrato de campos cambia de dirección.
- **Scoping por origen (no negociable):** el traspaso aplica solo a expedientes DEM/CM
  compras (los que ve JUNCO). Los expedientes TMC conservan su carga actual, incluida
  `source_dependence_id`. Cualquier cambio de carga debe ser condicional por origen.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |

> Sin tasks aún. Se abren recién tras `/product-spec`.

## Preguntas abiertas

1. Para los dos campos cedidos (solo flujo DEM/CM): ¿se ocultan, se quitan de la fase de
   carga, dejan de ser required, o pasan a readonly alimentados por JUNCO?
   (`jurisdiction_dependence` es hoy `required=True` → cambia constraints y `create()`).
   El tratamiento debe ser **condicional por origen**: TMC no se toca.
2. CM ya tiene `jurisdiction_dependence` auto (`= dependence_id`) y no usa source: ¿qué
   cede CM realmente, o el traspaso aplica en la práctica solo a DEM?
3. ¿Cómo se determina el origen del 1er pase (DEM→TMC) sin la carga manual de
   jurisdicción/origen en los expedientes DEM?
4. EPIC-002 / dirección del dato: si JUNCO completa `jurisdiction_dependence`, ¿quién es
   la fuente de verdad y en qué momento? ¿ME lo deja vacío al ingresar?
5. Expedientes existentes cargados con la lógica anterior: ¿migración, convivencia, o
   se respeta el dato viejo? ¿Qué pasa con el required histórico?
6. ¿ME sigue mostrando los dos campos cedidos en modo lectura (provenientes de JUNCO) o
   desaparecen de su UI de carga (solo para DEM/CM)?
7. `document_object` como objeto compartido: ¿JUNCO lo reutiliza como objeto de la
   compra/contratación? Si es así, ME es la fuente (JUNCO lee) — definir cómo se enlaza.

## Cierre de épica

Pendiente.
