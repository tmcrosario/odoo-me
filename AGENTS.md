# Odoo Agentic Delivery Framework — Guía global para agentes (odoo-me)

## Rol del framework

Organiza el trabajo con IA en odoo-me (módulos `me` — mesa de entradas — y `raa`).
Separa análisis, especificación, contrato, implementación, verificación, testing y
cierre documental.

## Operación: VS Code + Claude (operador único)

> odoo-me se trabaja **100% con VS Code + Claude**, sin OpenCode ni Cursor. Un solo
> operador recorre todas las fases en la misma sesión. Ver `CLAUDE.md`,
> `doc/framework/tooling_layers.md` y `doc/framework/agents_and_artifacts.md`.

Las fases siguen siendo **compuertas de disciplina**, no límites entre
herramientas: criterios antes de implementar, evidencia antes de declarar tests OK,
y cierre documental como paso explícito y separado del commit.

## Principios

0. **Inicialización persistente**: el proyecto se configura en
   `doc/framework/project_config.md`.
1. **Menor contexto suficiente**: leer solo lo necesario para la tarea.
2. **Escalamiento por riesgo**: no usar el flujo completo para cambios triviales.
3. **Criterios antes de código**: toda implementación debe tener acceptance criteria
   claros.
4. **Código Odoo en el paso de implementación**: cambios en Python/XML/CSV/security/
   tests pasan por la fase de implementación, no por pasos documentales.
5. **Tests con evidencia**: no declarar tests OK sin salida o confirmación explícita.
6. **Docs vivas**: actualizar la task card primero; docs canónicas solo cuando el
   cambio sea durable.
7. **Asignación explícita**: no asumir que una task está libre; revisar responsable y
   estado de toma antes de proponer implementación.
8. **Git seguro**: no commitear ni pushear sin pedido explícito; commit no equivale a
   cierre documental.
9. **Idioma por audiencia**: interfaz humana y metodología en español rioplatense;
   reglas de código en inglés técnico (`doc/framework/language_policy.md`).

## Modos de trabajo

Un solo operador adopta el modo que corresponde a cada fase, expuesto como slash
command en `.claude/commands/`:

- `/flow` — clasifica el pedido y propone el siguiente paso.
- `/new-idea` — decide si una idea abre épica nueva o entra en una existente.
- `/new-task` — crea la task card con el template proporcional al riesgo.
- `/product-spec` — aclara objetivo, alcance y reglas de negocio.
- `/prepare-task` — confirma readiness antes de contrato/implementación.
- `/contract-draft` — fija el diseño/contrato técnico antes de tocar código.
- Implementación — modifica código Odoo siguiendo el contrato.
- Verificación — revisión crítica diff-first; close gate `Ready`/`Blocked`.
- `/test-run` — coordina evidencia de tests.
- `/doc-close` — única ruta para marcar `Done`.
- `/commit-ready` — prepara o ejecuta commits seguros, solo bajo pedido.

## Escalamiento obligatorio

Escalar a revisión crítica (modo L/XL) cuando la tarea toque:

- modelos o campos persistentes;
- permisos, grupos, ACL o record rules;
- workflow, estados o trazabilidad;
- datos XML/CSV, migraciones o datos existentes;
- reglas de negocio ambiguas;
- auditoría, compliance o evidencia institucional;
- integraciones externas;
- cambios L/XL.

## Prohibición metodológica

No inventar reglas de negocio. Lo no especificado queda como pregunta abierta,
riesgo o `N/A` justificado.

## Política de idioma

- Metodología, comandos, skills, task cards, epic cards y docs de proyecto: **español
  rioplatense**.
- `doc/framework/odoo_development_rules.md` y user-visible Odoo strings: **inglés
  técnico** (+ i18n `es_AR` para strings).
- Términos técnicos Odoo/Python pueden quedar en inglés (`recordset`, `domain`,
  `cron`, `model`, `record rules`, etc.).
