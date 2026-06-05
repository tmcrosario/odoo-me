# Plan de tests — módulo `me` (Mesa de Entradas)

> **Stub.** No había plan de tests previo. El relevamiento de la suite real (qué
> existe en `me/tests/`, cobertura, gaps) se cierra en EPIC-001.

## Comando canónico

Desde la raíz del stack `odoo-docker-stack/`:

```bash
docker compose -f develop.yml run --rm odoo odoo -d <TEST_DB> -u me --test-tags /me --stop-after-init --log-level=test
```

## Política

- Tests user-run por default. No declarar `OK` sin salida pegada.
- En M/L/XL, el bloque "Tests evidenciados" de la task card es obligatorio.
- Áreas que requieren test (o `N/A + motivo`): reglas de negocio, workflow/movimientos,
  security/permisos, modelos/campos persistentes, migraciones, bugfixes con riesgo de
  regresión. Ver `doc/framework/odoo_development_rules.md` y `doc/framework/testing_policy.md`.

## Pendiente de baseline (EPIC-001)

- [ ] Inventariar `me/tests/` (qué se prueba hoy).
- [ ] Medir cobertura de las reglas activas de `business_rules.md` y los workflows.
- [ ] Identificar gaps prioritarios (movimientos automáticos, poseedor, duplicados,
  bypass de fecha, reingreso institucional).
- [ ] Confirmar disponibilidad de CI.
