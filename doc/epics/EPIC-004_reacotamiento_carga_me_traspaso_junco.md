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

Hasta ahora ME funcionaba con una carga más completa del expediente. El cambio mueve la
responsabilidad de cuatro campos hacia JUNCO y simplifica la carga inicial. Esto
impacta directamente el contrato de campos que JUNCO ya consume de `me.document_exp`
(ver EPIC-002): hoy JUNCO **lee** `jurisdiction_dependence`; con este cambio podría
pasar a **escribirlo**, invirtiendo la dirección del dato. Requiere contraparte en la
EPIC-002 de `odoo-junco`.

## Campos afectados (AS-IS, grounded en `me/models/document_exp.py`)

| Campo | Estado actual | Cambio propuesto |
| --- | --- | --- |
| `jurisdiction_dependence` | Many2one, **required=True**; alimenta `_compute_allowed_*`, `computed_name`, constraints y la derivación de movimientos | dejar de cargarse en ME (lo completa JUNCO) |
| `source_dependence_id` | Many2one; constraint cruzada con jurisdiction (`_check` ~línea 360) | dejar de cargarse en ME |
| `main_topic_id` (subject) | proxy compute/inverse sobre `main_topic_ids` (tmc.document) | dejar de cargarse en ME |
| `document_object` (specification) | **required=True** (~línea 100) | dejar de cargarse en ME |

## Cambio en movimientos automáticos

Flujo objetivo:

- **1er pase:** DEM → TMC
- **2do pase:** TMC → ME

Hoy el origen del 1er pase se deriva de la carga manual de jurisdicción/dependencia de
origen (compute que setea `jurisdiction_dependence = dependence_id`, ~líneas 380-386).
Sin esa carga, hay que definir **cómo se determina el origen del 1er pase**.

## Alcance

Incluye (a precisar en spec):

- qué campos dejan de cargarse en ME exactamente y **con qué tratamiento** (ocultar /
  quitar de la fase de carga / dejar de ser required / pasar a readonly desde JUNCO);
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

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |

> Sin tasks aún. Se abren recién tras `/product-spec`.

## Preguntas abiertas

1. Por cada campo: ¿se oculta, se quita de la fase de carga, deja de ser required, o
   pasa a readonly alimentado por JUNCO? (`jurisdiction_dependence` y `document_object`
   son hoy `required=True` → cambia constraints y `create()`).
2. ¿Cómo se determina el origen del 1er pase (DEM→TMC) sin carga de jurisdicción ni
   dependencia de origen?
3. EPIC-002 / dirección del dato: si JUNCO completa `jurisdiction_dependence`, ¿quién es
   la fuente de verdad y en qué momento? ¿ME lo deja vacío al ingresar?
4. Expedientes existentes cargados con la lógica anterior: ¿migración, convivencia, o
   se respeta el dato viejo? ¿Qué pasa con el required histórico?
5. ¿ME sigue mostrando estos campos en modo lectura (provenientes de JUNCO) o
   desaparecen de su UI de carga?

## Cierre de épica

Pendiente.
