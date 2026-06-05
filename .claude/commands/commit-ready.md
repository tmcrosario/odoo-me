---
description: Prepara o ejecuta un commit seguro; no commitea ni pushea sin pedido explícito
argument-hint: [prepare | commit]
---

Prepará o ejecutá un commit seguro guiado.

Modo pedido: $ARGUMENTS

## Reglas de seguridad

- No hacer commit salvo pedido explícito del usuario.
- No hacer push salvo pedido explícito del usuario.
- No usar `--no-verify`, `--no-gpg-sign` ni bypasses salvo pedido explícito.
- No commitear secretos, credenciales, `.env`, caches, logs o archivos locales sospechosos.
- No asumir tests OK sin evidencia.
- Commit no equivale a `Done` documental.
- Si hay código Odoo y docs canónicas pendientes, advertirlo antes de commitear.

## Procedimiento

1. Ejecutar `git status --short`.
2. Revisar staged + unstaged diff.
3. Revisar últimos commits para estilo.
4. Identificar archivos relevantes y archivos sospechosos.
5. Verificar referencia `EPIC-XXX/TASK-YYY` si aplica.
6. Verificar estado de tests/verifier si hay código Odoo.
7. Verificar si la task registra `Docs canónicas pendientes de consolidación`.
8. Si hay código Odoo y docs pendientes, incluir riesgo explícito en el output.
9. Proponer mensaje de commit y un comentario breve para GitHub.
10. Si el usuario pidió commit explícitamente, hacer `git add` de archivos relevantes y `git commit`.
11. Ejecutar `git status --short` al final.

## Output

```md
Commit mode: prepare-only / executed
Reference: EPIC-XXX/TASK-YYY / N/A
Files included:
Files excluded/suspicious:
Tests/verifier status:
Docs canónicas pendientes:
Risks:
Commit message:
Comentario breve para GitHub:
Commit hash: ... / N/A
Final status:
```

## Mensaje sugerido

```text
[TYPE] resumen imperativo breve
```

Tipos: `[ADD]`, `[IMP]`, `[FIX]`, `[REF]`, `[REM]`, `[MIG]`, `[DOC]`, `[TEST]`, `[CHORE]`. Sin atribución AI.
