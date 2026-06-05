# Delivery modes

## Clasificación

| Modo | Uso | Documentación | Verificación |
| --- | --- | --- | --- |
| XS | typo, texto, ajuste trivial | nota mínima | N/A o visual |
| S | cambio chico seguro | task compacta | manual/test puntual |
| M | cambio funcional normal | task estándar | tests + verifier según caso |
| L | permisos, modelo, workflow, datos, lógica sensible | flujo completo | verifier crítico obligatorio |
| XL | arquitectura, migración, integración mayor | flujo completo extendido | revisión crítica + plan explícito |

## Regla de escalamiento

Si hay duda entre dos modos, elegir el más alto solo cuando el riesgo sea real. No escalar por costumbre.

## Sensibilidad Odoo

Escalar automáticamente a L/XL si toca:

- `models/` con campos persistentes o constraints;
- `security/`, grupos, ACL o record rules;
- `data/` con datos durables;
- workflow de estados;
- contabilidad, permisos, auditoría o datos críticos;
- migraciones;
- integraciones externas.

## Documentación canónica

Actualizar docs canónicas solo si el cambio agrega una regla durable o altera el contrato del sistema. Para cambios XS/S, preferir `N/A` o consolidación diferida.
