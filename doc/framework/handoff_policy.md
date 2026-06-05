# Handoff policy

> En odoo-me hay un solo operador (VS Code + Claude). No hay traspaso entre
> herramientas: el "handoff" es entre **fases** de la misma sesión
> (definir → contratar → implementar → verificar → cerrar). La regla de fondo es
> que **la memoria vive en el repo, no en el chat**: lo que un paso produce y el
> siguiente consume tiene que quedar escrito en la task card.

## Cuándo abrir la compuerta de implementación

Pasar a implementación cuando el cambio toque código Odoo real o sensibilidad
funcional, y solo con acceptance criteria claros.

## Regla de lectura única

Leer la documentación metodológica y de proyecto **necesaria** antes de
implementar y condensarla en la task card. No re-leer documentos completos si lo
consolidado alcanza para actuar.

Volver a leer documentación solo cuando:

- el contexto consolidado está incompleto;
- hay contradicción entre task, contrato y documentación;
- el código observado contradice una regla documentada;
- el cambio exige confirmar una regla durable no resumida.

## Persistencia entre fases

Toda salida que sea insumo para un paso posterior debe quedar en la task card
antes de avanzar. El chat no es memoria entre sesiones.

| Salida | Dónde persistir | Paso que la consume |
| --- | --- | --- |
| Contrato técnico definitivo | `## Contrato técnico` en la task card | implementación |
| Execution report | `## Execution report` (o `## Resultado / cierre` según template) | `/test-run`, verificación, `/doc-close` |
| Close gate `Ready` / `Blocked` | `## Verifier / close gate` | `/doc-close` |
| Evidencia o pedido de tests | `## Tests evidenciados` | `/doc-close` |
| Bloqueo detectado | `## Bloqueos` | `/flow`, `/prepare-task` o resolución manual |

Si el contrato, report o close gate no está persistido, el siguiente paso debe
pedir completarlo o bloquear con `PENDIENTE` en vez de reconstruirlo de memoria.

## Contexto consolidado antes de implementar

Antes de tocar código, dejar en la task card un bloque de contexto consolidado con:

- referencia `EPIC-XXX/TASK-YYY`, módulo (`me` / `raa`) y estado de toma;
- objetivo, alcance y no-alcance;
- acceptance criteria verificables;
- reglas de negocio relevantes ya leídas desde `doc/project/<modulo>/business_rules.md`;
- reglas Odoo/framework relevantes ya leídas desde `doc/framework/*`;
- riesgos sensibles: modelos, permisos, workflow, datos, migraciones, auditoría,
  integraciones;
- archivos o áreas esperadas;
- tests esperados y evidencia requerida;
- preguntas abiertas y supuestos permitidos;
- documentos leídos y motivo.

No pegar documentos completos salvo necesidad concreta. Pegar extractos o síntesis
accionables.

## División de validación

Correr primero los checks locales baratos y repetibles cuando estén disponibles:

- `compileall` / parseo Python;
- parseo XML;
- `git diff --check`;
- grep negativo de `attrs`, `states` y `statusbar_colors` cuando aplique;
- revisión de diff contra task/contrato.

La validación runtime (instalación, navegación, creación de registros, constraints,
comportamiento funcional que no se puede verificar de forma estática) es un paso
aparte. Si un check local ya fue ejecutado y documentado, no repetirlo salvo que el
runtime dependa de él.

## Matriz de criticidad y lectura documental

Define qué documentación masticar antes de implementar y cuándo conviene releer.
`Debe releer` no significa leer todo el repo: significa abrir el documento o
sección mínima necesaria para resolver una falta concreta. Las rutas de proyecto
son por módulo (`doc/project/me/...`, `doc/project/raa/...`).

| Área / documento | Criticidad | Antes de implementar | En contrato técnico | En implementación | Regla práctica |
| --- | --- | --- | --- | --- | --- |
| Task card `doc/tasks/EPIC-XXX/TASK-YYY_*` | Alta | Leer completa | Releer si hay contradicción o falta | Releer si necesita confirmar criterios o actualizar execution report | La task es la referencia operativa |
| Epic card `doc/epics/EPIC-XXX_*` | Media | Leer lo necesario para contexto funcional | No salvo contradicción de alcance | No | Resumir el contexto épico relevante |
| `doc/framework/odoo_development_rules.md` | Alta | Leer reglas aplicables | No salvo falta técnica o contradicción con código | No salvo falta técnica o contradicción | Especialmente Odoo 19+ XML, modelos, security, tests y migraciones |
| `doc/project/<modulo>/business_rules.md` | Alta si aplica negocio | Leer secciones aplicables | Releer sección puntual si el contrato depende de una regla no resumida | No salvo contradicción | Las reglas de negocio deben llegar masticadas al contexto consolidado |
| `doc/project/<modulo>/models.md` | Alta si toca modelos/campos | Leer secciones del modelo afectado | Releer sección puntual para contrastar contrato con modelo documentado | No salvo modelo/campo no contemplado | Contrastar doc resumida contra código real, no reanalizar todo |
| `doc/project/<modulo>/security.md` | Alta si toca permisos/security | Leer secciones aplicables | Releer sección puntual si define grupos, ACL o record rules | Releer solo si implementa permisos y falta detalle | Security permite relectura puntual; nunca lectura amplia por default |
| `doc/project/<modulo>/architecture.md` | Media/Alta si afecta diseño | Leer solo si toca arquitectura, módulos o integraciones | Releer sección puntual si hay decisión arquitectónica no resumida | No | Para cambios locales suele quedar N/A |
| `doc/project/<modulo>/tests_plan.md` | Media | Leer si hay tests esperados o comando estándar | No salvo falta de estrategia de test | Releer si necesita ubicar comando o patrón | El contexto debe traer comando o criterio de evidencia |
| `doc/project/<modulo>/migrations.md` | Alta si afecta datos existentes | Leer si hay migración o datos persistentes afectados | Releer sección puntual si define estrategia histórica o compatibilidad | Releer solo si implementa scripts de migración | Migraciones escalan a L/XL |
| `doc/framework/context_policy.md` | Media | Leer o aplicar | No | No | Regla metodológica de bajo contexto |
| `doc/framework/handoff_policy.md` | Media | Leer o aplicar | No | No | Esta política |

## Declaración de modo (opcional)

Cuando ayuda a fijar límites, declarar el modo en el que se trabaja un paso:

```md
Modo: contrato técnico — no implementar.
```

```md
Modo: implementación.
```

```md
Modo: revisión crítica diff-first — no implementar ni cerrar documentación.
```

## Checklist de contexto antes de implementar

```md
Referencia: EPIC-XXX/TASK-YYY
Módulo: me / raa
Modo: XS/S/M/L/XL
Docs leídas:
- doc/framework/odoo_development_rules.md
- doc/framework/language_policy.md
- doc/project/<modulo>/architecture.md
- doc/project/<modulo>/business_rules.md
- doc/project/<modulo>/models.md
- doc/project/<modulo>/security.md
- task card EPIC-XXX/TASK-YYY
Objetivo:
Alcance:
No incluye:
Criterios de aceptación:
Contexto consolidado:
Archivos esperados:
Riesgos:
Tests esperados:
```

## Regla

El objetivo es trabajar con bajo contexto, sin releer todo el repo ni repetir
lectura documental ya hecha y consolidada en la task card.
