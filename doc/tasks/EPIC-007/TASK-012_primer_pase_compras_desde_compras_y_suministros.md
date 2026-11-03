# EPIC-007 / TASK-012 — El 1er pase de las compras DEM sale de Compras y Suministros

Estado: Draft
Modo: L
Riesgo: medio (cambia la lógica de los movimientos automáticos del alta; no toca modelos, ACL ni datos)
Módulo: `me`
Responsable: sin asignar

## Asignación

- Estado de toma: sin tomar
- Notas de coordinación: `demo-junco` confirmó (2026-11-03) que junco no lee el origen del 1er pase ni asume
  que sea DEM. `exp.dependence_id` sigue siendo DEM. Origen: IDEA 13 de `doc/project/me/brainstorming.md`.

## Objetivo

Que en las compras que ingresan con origen DEM, el 1er pase automático salga de Compras y Suministros del
nomenclador (`tmc_data.tmc_dependence_comp`) hacia TMC, en lugar de DEM → TMC. En la práctica todas las
compras llegan desde Compras y Suministros, más allá de la jurisdicción que las pida.

## Alcance

Incluye:

- en `me.document_exp.create()`, el origen del 1er pase pasa a ser Compras y Suministros cuando el expediente
  tiene origen DEM y su tema principal es Licitación, Concurso de Precios o Contratación Directa;
- la regla se evalúa una sola vez, al ingreso, con el tema que tenga el alta en ese momento;
- tests, y docs (`workflows.md`, `business_rules.md`, `models.md` si corresponde, `tests_plan.md`).

No incluye:

- cambiar `dependence_id` del expediente (sigue siendo DEM);
- tocar los expedientes ya cargados ni migrar pases existentes;
- CM y TMC (conservan su 1er pase actual) ni las Notas (siguen con la jurisdicción como origen);
- ocultar la jurisdicción y la repartición en la vista (IDEA 14, descartada);
- cambiar JUNCO ni `action_set_origin_from_junco()`.

## Reglas decididas (usuario, 2026-11-03)

- Alcance: Licitación, Concurso de Precios y Contratación Directa.
- Aplica solo a las compras con origen DEM.
- Sin tema en el alta: el pase sale como hoy (DEM → TMC). Si el tema cambia después, el pase no se toca.
- El 2.º pase (TMC → ME) no cambia.

## Acceptance criteria

- [ ] Una Licitación con origen DEM crea el 1er pase Compras y Suministros → TMC y el 2.º TMC → ME, ambos
      automáticos.
- [ ] Un Concurso de Precios y una Contratación Directa con origen DEM hacen lo mismo.
- [ ] `dependence_id` del expediente sigue siendo DEM.
- [ ] Una compra con origen CM conserva CM → TMC; una con origen TMC solo crea TMC → ME.
- [ ] Una Nota con origen DEM conserva jurisdicción → TMC.
- [ ] Un alta DEM sin tema crea DEM → TMC, como hoy.
- [ ] Cambiar el tema después del alta no modifica los pases existentes.
- [ ] Los expedientes ya cargados no cambian y no hay migración.
- [ ] `has_reentry` y el poseedor se comportan igual que antes (el destino del 1er pase sigue siendo TMC).
- [ ] Suite `/me` verde, con evidencia (`... of N tests`, N > 0).
- [ ] Prueba manual de UI: alta de una Licitación DEM y revisión del historial de movimientos.

## Riesgos y preguntas abiertas

- Verificar que ninguna validación de movimientos exija que el origen del 1er pase coincida con
  `dependence_id` o con la última posición (se espera que no, pero hay que comprobarlo antes de codificar).
- Los tests existentes que asumen DEM → TMC en compras deberán ajustarse.
- Si la dependencia `tmc_data.tmc_dependence_comp` no existe en una DB, definir el fallback (se propone
  DEM → TMC como hoy) y no fallar el alta.
- Conviene avisar a `demo-junco` al cerrar; la DB `migracion` carga su propio 1er pase y no depende de esto.

## Tests evidenciados

PENDIENTE USER-RUN.

## Estado / próximo paso

Draft. Falta el OK del usuario a los criterios y asignar la task antes de implementar. Sin código tocado.

## Resultado

(pendiente)
