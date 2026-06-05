# Reglas de negocio — módulo `me` (Mesa de Entradas)

> Consolida `docs/rules_business.md` (invariantes conceptuales) y la sección "Reglas
> de negocio activas" de `docs/system_narrative.md` (v1.0, 2026-03-31, la más
> reciente). Las reglas marcadas como **principio sin enforcement** o **limitación**
> NO deben asumirse como cerradas: su estado real se reconcilia contra código en
> EPIC-001. El comportamiento operativo detallado vive en [`workflows.md`](workflows.md).

## Invariantes del sistema (deben cumplirse siempre)

1. Todo movimiento pertenece a exactamente un expediente; no hay movimiento sin
   documento.
2. Los expedientes deben permanecer trazables a través de su historial de movimientos.
3. ME **extiende** el sistema documental base (`tmc.document`), no lo reemplaza. ME no
   crea documentos standalone: todo expediente origina en el sistema base.

Cualquier feature que viole estos invariantes debe rechazarse o redefinir
explícitamente las reglas.

## Reglas activas (observadas en código)

| Regla | Descripción |
|---|---|
| Tipo de documento automático | Al elegir la dependencia de origen, el tipo `EXP` se asigna sin intervención del usuario. |
| Dependencias de origen permitidas | Solo DEM, TMC o CM (filtro hardcodeado `['DEM','TMC','CM']`). |
| Nombre generado | Formato `EXP-XXXXXX-ORIGEN/AÑO` (ej. `EXP-000042-DEM/2025`), calculado en tiempo real. |
| Movimientos iniciales automáticos | Al crear: DEM → 2 movimientos (jurisdicción→TMC, TMC→ME); TMC → 1 (TMC→ME, omite TMC→TMC); CM → 2 (CM→TMC, TMC→ME). |
| Registro automático en RAA | Todo expediente queda registrado en `raa.registry_aa` al crearse. |
| Fojas — bloqueo post-creación | El número de fojas no se modifica una vez guardado, excepto por un Responsable de Mesa de Entradas; las variaciones se registran vía movimientos. |
| Aviso de duplicado | Si existe un expediente con igual origen+número+período, el sistema **avisa pero no bloquea** el guardado. |
| Fecha del documento | Puede diferir de la fecha de registro (admite fechas pasadas; ver bypass SQL en `architecture.md`). |
| Integridad de movimientos | Origen y destino obligatorios; fecha no futura ni anterior al ingreso; no se permiten movimientos duplicados exactos (expediente+origen+destino+fecha). |
| Poseedor actual | Solo el `user_id` del último movimiento puede registrar un pase nuevo desde la UI (managers sin restricción) — #027/#028/#029. |
| Salida / reingreso institucional | Derivado de `is_internal` por dependencia; `has_reentry` marca reingreso tras una salida previa — #021/#030. |

## Append-only (principio, sin enforcement técnico)

El diseño establece que los movimientos son **append-only** (no modificables ni
eliminables retroactivamente). **Es un principio declarativo**: a la fecha del
análisis no hay constraint/override que lo enforce más allá de los permisos de grupo.
Formalizarlo es un ítem de backlog. (Verificar estado actual en EPIC-001.)

## Limitaciones conocidas (no implementado)

- **Sin estados de expediente** (no hay ciclo de vida abierto/en proceso/cerrado).
- **Sin ubicación actual calculada** más allá de `current_holder_id` / último
  movimiento.
- **Sin validación de continuidad** entre movimientos (el destino de uno no se valida
  contra el origen del siguiente; orden cronológico no enforced).
- **Sin documentos relacionados** (tab deshabilitado).
- **Fragilidad**: el movimiento automático a "Mesa de Entradas" depende de encontrar
  la dependencia por nombre/abreviatura; si no existe, se omite sin aviso.

## Relación con RAA

Algunos expedientes quedan asociados a actos administrativos en `raa.registry_aa`.
RAA es un **punto de integración externo**: fuera del scope de ME, no se modifica sin
pedido explícito.
