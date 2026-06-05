# EPIC-002 — Integración ME ↔ JUNCO (proceso licitatorio)

Estado: Draft
Riesgo global: alto (relación entre módulos, modelos persistentes, reglas de negocio abiertas)
Módulo: `me` (+ `junco`, repo `odoo-junco`)
Owner: sin asignar

## Objetivo

Definir y, eventualmente, implementar la relación entre los expedientes de Mesa de
Entradas (`me.document_exp`) y los procesos licitatorios gestionados por JUNCO. Un
proceso puede incorporar varios expedientes a lo largo de su historia, con un
expediente vigente y otros históricos.

## Contexto

Semilla: task #007 (`doc/project/me/_legacy_backlog.md`). JUNCO es la otra punta de
esta integración y ya tiene su contraparte documental en `odoo-junco`. Principios
acordados:

- ME es la puerta de entrada de los expedientes.
- JUNCO usa expedientes ya creados en ME como insumo del proceso.
- La relación es dinámica: un proceso acumula expedientes en el tiempo.
- Siempre debe poder identificarse el expediente vigente vs. los históricos.

## Alcance

Incluye (a definir en spec):

- modelado de la relación proceso↔expedientes;
- identificación del expediente vigente;
- reglas de exclusividad y visibilidad desde ME;
- representación del historial.

No incluye:

- el baseline de `me` (EPIC-001);
- la lógica interna de JUNCO ajena a la relación.

## Módulos afectados

- Módulo principal: `me`
- Módulos secundarios afectados: `junco` (repo `odoo-junco`)
- Dependencias entre módulos: la dirección del acoplamiento (¿`junco`→`me`,
  `me`→`junco`, o tabla intermedia neutral?) es una decisión abierta.

## Reglas / decisiones durables

- No inventar reglas de negocio: las decisiones abiertas se cierran con el usuario
  antes de implementar.
- Cambios que toquen modelos persistentes o la relación entre módulos escalan a L/XL.

## Tasks

| Task | Título | Responsable | Modo | Módulo | Estado |
| --- | --- | --- | --- | --- | --- |

> Sin tasks aún. Próximo paso sugerido: `/product-spec` para cerrar las decisiones
> abiertas antes de abrir una task implementable.

## Preguntas abiertas

(Heredadas de #007 — ninguna decidida.)

1. **Modelado de la relación**: ¿Many2many simple o tabla intermedia con metadatos
   (fecha de incorporación, motivo, estado)? ¿Se registra el evento que motivó cada
   incorporación (inicio, anulación, relanzamiento, ampliación)?
2. **Expediente vigente**: ¿campo booleano `is_current` en la relación o inferencia
   cronológica? ¿Puede haber más de uno vigente? ¿Qué pasa si el vigente se anula?
3. **Exclusividad**: ¿un expediente puede pertenecer a más de un proceso? Si no,
   ¿quién valida (ME, JUNCO o ambos)?
4. **Visibilidad desde ME**: ¿ME muestra referencia a JUNCO en el form del
   expediente? ¿Unidireccional JUNCO→ME? ¿Informativa o navegable?
5. **Eventos que disparan incorporación**: ¿qué estados/eventos del proceso habilitan
   agregar un expediente? ¿Selección manual en JUNCO o ME "notifica" candidatos?
6. **Historial**: ¿línea de tiempo, tabla o listado? ¿Se registra quién incorporó
   cada expediente y cuándo?

## Cierre de épica

Pendiente.
