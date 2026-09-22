# Caso de estudio: Gentleman.Dots (skills + AGENTS.md + orquestador SDD)

Conocimiento **destilado** del repo `Gentleman-Programming/Gentleman.Dots`
(verificado en vivo, 2026-09-22), para no clonar el repo entero. Es un segundo
ejemplo del patrón del video, más **simple** que Prowler pero con un extra: el
**orquestador de subagentes** (SDD) que el video menciona, aquí aplicado de
verdad.

> Para el patrón grande/multi-área, ver `prowler-case-study.md`. Este es el caso
> "un solo AGENTS.md + orquestador con subagentes".

## Estructura real

- **1 solo `AGENTS.md`** en la raíz (NO es multi-área como Prowler). Confirma:
  si el repo no es un monorepo por features, un AGENTS.md raíz basta.
- **6 skills** en `skills/<n>/SKILL.md`: `gentleman-bubbletea`,
  `gentleman-installer`, `gentleman-system`, `gentleman-trainer`,
  `gentleman-e2e`, `go-testing`. Todas específicas del repo (TUI en Go/Bubbletea,
  instalador, trainer de Vim, E2E). No hay familia "genérica reutilizable".
- `skills/setup.sh` (multi-agente) y `skills/setup_test.sh`.
- Las skills de USUARIO (React, TypeScript, SDD) se movieron a un repo aparte,
  `gentle-ai`; este repo solo conserva las de SU codebase.

## Diferencia clave con Prowler: frontmatter SIN scope/auto_invoke

Ejemplo real (`gentleman-installer/SKILL.md`):

```yaml
---
name: gentleman-installer
description: >
  Installation step patterns for Gentleman.Dots TUI installer.
  Trigger: When editing installer.go, adding installation steps, or modifying the installation flow.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---
```

- **No usan `metadata.scope` ni `metadata.auto_invoke`.** Solo `name`,
  `description` con `Trigger:`, `license`, `author`, `version`.
- Consecuencia: la tabla Auto-invoke del AGENTS.md se mantiene **a MANO** (no hay
  `skill-sync` que la genere desde metadata). Es la variante "auto-invoke manual"
  — la misma que decidimos para nas-dotfiles.

## Tabla Auto-invoke real (con columna "Why")

En `AGENTS.md`, la tabla añade una tercera columna que explica el porqué:

```markdown
## Auto-invoke Skills

When performing these actions, **ALWAYS** invoke the corresponding skill FIRST:

| Action | Invoke First | Why |
|--------|--------------|-----|
| Adding new TUI screen  | `gentleman-bubbletea` | Screen constants, Model state, Update handlers |
| Adding installation step | `gentleman-installer` | Step registration, OS handling, error wrapping |
| Writing Go tests | `go-testing` | Table-driven tests, teatest patterns |
| Creating new skill | `skill-creator` | Skill structure, naming, frontmatter |
```

Mejora a imitar: la columna **"Why"** da al LLM la razón de cargar la skill, no
solo el mapeo. Barato y útil.

## El extra valioso: orquestador SDD con subagentes

`AGENTS.md` incluye un **"Spec-Driven Development (SDD) Orchestrator"** que es el
patrón subagente/orquestador del video, aplicado:

- El agente principal es el **ORCHESTRATOR**; modo **"Delegate-only: NEVER execute
  phase work inline"** → lanza sub-agentes (vía Task tool) para el trabajo pesado
  y solo **rastrea estado y decisiones** del usuario (se mantiene lightweight).
- Comandos `/sdd-*` mapean a skills (`/sdd-init`→`sdd-init`,
  `/sdd-new`→`sdd-explore` luego `sdd-propose`, etc.). Los `/sdd-new|continue|ff`
  son **meta-comandos del orquestador**, NO skills que se invocan.
- **Identity Inheritance**: al entrar en modo SDD, el orquestador MANTIENE su
  personalidad/tono (mentor), no cambia a "voz genérica de orquestador". Las
  reglas SDD son una **capa (overlay)**, no un reemplazo de personalidad.

Esto confirma en la práctica lo de `agents-md-and-subagents.md`: orquestador
lightweight + subagentes con contexto aislado que devuelven resultado.

## Contributing (cómo añaden una skill, del propio AGENTS.md)

1. Leer la skill `skill-creator` primero.
2. Crear el directorio bajo `skills/`.
3. Añadir `SKILL.md` siguiendo la plantilla.
4. Registrarla en `AGENTS.md` bajo "Gentleman.Dots Specific".
5. Ejecutar `./skills/setup.sh --all` para regenerar (symlinks multi-agente).

## Qué llevarte (y qué no) para tus proyectos en Kiro

| Pieza | ¿Adoptar? | Por qué |
|---|---|---|
| Un solo AGENTS.md (repo no monorepo) | Sí | Valida no dividir sin necesidad |
| Columna **"Why"** en la tabla Auto-invoke | Sí | Da la razón al LLM, no solo el mapeo |
| Auto-invoke **manual** (sin scope/auto_invoke) | Opción válida | Es lo que ya hacemos en nas-dotfiles |
| Orquestador **delegate-only** + subagentes | Sí, para tareas multi-fase | Mantiene el contexto principal limpio |
| **Identity inheritance** en modo orquestador | Sí | El agente no debe perder su tono al delegar |
| `setup.sh --all` multi-agente | No (en Kiro) | Solo si soportas Claude/Gemini/Codex a la vez |
| Skills de usuario en repo aparte (`gentle-ai`) | Contexto | Separan skills de codebase vs de usuario |

## Rutas exactas (si hace falta ir a la fuente)

```text
AGENTS.md                              # 1 solo; tabla Auto-invoke + SDD Orchestrator
skills/gentleman-installer/SKILL.md    # ejemplo frontmatter (sin scope/auto_invoke)
skills/setup.sh                        # multi-agente (--all)
```

Repo: https://github.com/Gentleman-Programming/Gentleman.Dots · Ficha:
`tool_catalog/entries/gentleman-programming/gentleman-dots.md` · Capa IA de usuario:
https://github.com/Gentleman-Programming/gentle-ai
