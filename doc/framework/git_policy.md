# Política Git

## Propósito

Definir un workflow de commit seguro guiado por agentes para proyectos Odoo.

## Principios

- No hacer commit salvo pedido explícito del usuario.
- No hacer push salvo pedido explícito del usuario.
- No usar `--no-verify`, `--no-gpg-sign` ni bypasses de hooks salvo pedido explícito.
- No hacer amend de commits salvo pedido explícito y verificación de seguridad.
- No commitear secretos, credenciales, archivos `.env` ni ruido generado.
- Un commit **no es lo mismo que `Done` documental**.
- Un commit no reemplaza tests, verifier ni close gate.

## Checklist de readiness para commit

Antes de commitear, revisar:

1. `git status` incluyendo archivos untracked.
2. Diff staged y unstaged.
3. Estilo de commits recientes.
4. Referencia `EPIC-XXX/TASK-YYY` cuando aplique.
5. Estado de tests / verifier cuando hubo cambios de código.
6. Archivos sospechosos: secretos, configs locales, assets generados, caches, logs.

## Estilo de mensaje de commit

Formato recomendado para la primera línea:

```text
[TYPE] resumen imperativo breve
```

Tipos sugeridos:

- `[ADD]` nueva feature o capacidad;
- `[IMP]` mejora a comportamiento existente;
- `[FIX]` bugfix;
- `[REF]` refactor sin cambio funcional;
- `[REM]` eliminación;
- `[MIG]` migración;
- `[DOC]` solo documentación;
- `[TEST]` solo tests;
- `[CHORE]` tooling / framework / configuración.

Mantener la primera línea concisa. Preferir un cambio lógico por commit.

## Naming de branches

Formato estricto:

```text
<tipo>/EPIC-XXX-TASK-YYY-slug
```

Tipos: `feature`, `fix`, `hotfix`, `refactor`, `docs`, `chore`.

Ejemplos:

- `feature/EPIC-001-TASK-004-add-due-date-field`
- `fix/EPIC-002-TASK-007-recompute-deadline`

CI puede extraer la referencia para validar contra `doc/tasks/EPIC-XXX/TASK-YYY_*.md` cuando se active.

## Flujo guiado por agente

1. El usuario pide `prepare commit` o `commit`.
2. El agente revisa `status` / diff / log.
3. El agente resume cambios incluidos y riesgos.
4. El agente propone mensaje de commit y un comentario breve para GitHub.
5. Si el usuario pidió commit explícitamente, el agente hace `git add` de los archivos relevantes y `git commit`.
6. El agente reporta el hash de commit y el estado final del working tree.

## Seguridad

Si hay cambios de código sin tests, reportarlo claramente. El usuario puede pedir el commit de todas formas, pero el reporte debe preservar el riesgo.
