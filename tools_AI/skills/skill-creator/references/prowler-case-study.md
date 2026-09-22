# Caso de estudio: cómo Prowler aplica las ideas del video

Conocimiento **destilado** del repo `prowler-cloud/prowler` (verificado en vivo,
2026-09-22), para imitar el patrón al crear skills **sin tener que clonar y leer
el repo entero**. Complementa `case-study-docker-nas.md` (skill compleja de un
solo dominio); este muestra un repo grande multi-área.

> Si necesitas un archivo concreto de Prowler, aquí van las rutas exactas. Leer
> el repo solo para un matiz que esto no cubra.

## Cifras y estructura (lo que confirma el patrón)

- **6 `AGENTS.md`**: raíz + uno por área → `AGENTS.md`, `api/AGENTS.md`,
  `ui/AGENTS.md`, `prowler/AGENTS.md` (el SDK), `mcp_server/AGENTS.md`,
  `docs/AGENTS.md`. Es el patrón del video: **root que enruta + uno por feature**.
- **37 skills** en `skills/<nombre>/SKILL.md`, con `references/` y `assets/`
  opcionales.
- Un `skills/README.md`, un `skills/setup.sh` (multi-agente) y dos meta-skills:
  `skills/skill-creator/` y `skills/skill-sync/`.

## Cómo clasifican las skills (3 familias)

| Familia | Naming | Ejemplos | Idea |
|---|---|---|---|
| Genéricas (reusables en cualquier repo) | `<tecnología>` | `typescript`, `react-19`, `nextjs-16`, `pytest`, `playwright`, `tailwind-4`, `zod-4`, `tdd` | Patrones de una tech, sin nada de Prowler |
| Específicas del proyecto | `prowler-<área/acción>` | `prowler-ui`, `prowler-api`, `prowler-sdk-check`, `prowler-commit`, `prowler-pr`, `prowler-compliance` | Convenciones propias; una skill genérica puede tener `references/` que apunten a docs del proyecto |
| Meta (mantienen el sistema) | acción | `skill-creator`, `skill-sync` | Crear skills / sincronizar auto-invoke |

Regla que usan: si el patrón sirve a cualquier proyecto → skill genérica; si es
propio → `prowler-*`; si una genérica necesita datos del proyecto → NO la
ensucian, le añaden `references/` que apuntan a los docs de Prowler.

## Frontmatter real (ejemplo `prowler-ui/SKILL.md`)

```yaml
---
name: prowler-ui
description: >
  Prowler UI-specific patterns. For generic patterns, see: typescript, react-19, nextjs-16, tailwind-4.
  Trigger: When working inside ui/ on Prowler-specific conventions (...).
license: Apache-2.0
metadata:
  author: prowler-cloud
  version: "1.1"
  scope: [root, ui]                 # una skill puede pertenecer a VARIOS AGENTS.md
  auto_invoke:
    - "Creating/modifying Prowler UI components"
    - "Reviewing Prowler UI components"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---
```

Detalles a imitar (y a NO imitar):
- `description` = **qué hace + `Trigger:` explícito** en el mismo bloque.
- `scope` puede ser **lista** (`[root, ui]`): la skill aparece en varios AGENTS.md.
- `auto_invoke` = lista de acciones; son las filas que van a la tabla auto-invoke.
- `allowed-tools`: **Claude Code lo consume; Kiro NO** → en Kiro no hace daño pero
  no tiene efecto; puedes omitirlo.

## Auto-invoke real (extracto de `ui/AGENTS.md`)

Cada AGENTS.md de área tiene una tabla que ORDENA cargar la skill:

```markdown
## Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action                          | Skill               |
| ------------------------------- | ------------------- |
| App Router / Server Actions     | `nextjs-16`         |
| Creating Zod schemas            | `zod-4`             |
| Committing changes              | `prowler-commit`    |
| Add changelog entry for a PR    | `prowler-changelog` |
```

Confirma por qué existe: los modelos tratan el `Trigger:` como sugerencia; la
tabla lo vuelve una orden. (Ver `auto-invoke-and-metadata.md`.)

## references/ vs assets/ (cómo lo usan)

- `references/` → docs que el LLM lee on-demand: apuntan a archivos LOCALES del
  repo (ej. `docs/developer-guide/*.mdx`), no URLs.
- `assets/` → recursos que el LLM **copia o ejecuta**: plantillas y **código de
  ejemplo real** dentro de la skill. Ejemplos vistos: `prowler-api/assets/`
  (`celery_patterns.py`, `security_patterns.py`), `prowler-sdk-check/assets/`
  (`aws_check.py`, `azure_check.py`, `gcp_check.py`),
  `skill-creator/assets/SKILL-TEMPLATE.md`.

Lección: cuantos más ejemplos concretos en `assets/`, más "one-shot" sale la
tarea (el LLM copia un patrón real en vez de inventarlo).

## skill-sync (automatiza el auto-invoke)

`skills/skill-sync/assets/sync.sh` lee `metadata.scope` y `metadata.auto_invoke`
de cada `SKILL.md` y **regenera las tablas Auto-invoke** de cada AGENTS.md según
el `scope`. Soporta `--dry-run` y `--scope <área>`. Es la alternativa automática
al mantenimiento manual.

## setup.sh (soporte multi-agente)

`skills/setup.sh` crea symlinks para que cada herramienta encuentre las skills en
su ruta: `.claude/skills/` + `CLAUDE.md`, `.gemini/skills/` + `GEMINI.md`,
`.codex/skills/` (usa AGENTS.md nativo), `.github/copilot-instructions.md`. Copia
`AGENTS.md` → `CLAUDE.md`/`GEMINI.md`. Interactivo o `--all`/`--claude`/etc.

## Qué adoptar y qué NO (para tus proyectos en Kiro)

| Pieza de Prowler | ¿Adoptar? | Por qué |
|---|---|---|
| 3 familias de skills (genérica/proyecto/meta) | Sí | Ordena el catálogo de skills |
| `description` con `Trigger:` explícito | Sí | Mejor activación |
| `metadata.scope` + `auto_invoke` + tabla en AGENTS.md | Sí | Ya adoptado (nas-dotfiles) |
| `references/` locales + `assets/` con ejemplos | Sí | Progressive disclosure real |
| Varios AGENTS.md (root + por feature) | **Solo si** el repo es monorepo por áreas | nas-dotfiles no lo es → un solo AGENTS.md |
| `allowed-tools` | Opcional | Kiro no lo consume |
| `skill-sync` (sync.sh) | Diferir | Con pocas skills, manual basta |
| `setup.sh` multi-agente | No (en Kiro) | Solo si soportas Claude/Gemini/Codex a la vez |

## Rutas exactas (si hace falta ir a la fuente)

```text
skills/README.md                        # principios + índice de skills
skills/skill-creator/SKILL.md           # + assets/SKILL-TEMPLATE.md
skills/skill-sync/SKILL.md              # + assets/sync.sh
skills/setup.sh                         # multi-agente
skills/prowler-ui/SKILL.md              # ejemplo skill de proyecto (scope [root, ui])
ui/AGENTS.md                            # ejemplo tabla Auto-invoke real
AGENTS.md                               # root que enruta
```

Repo: https://github.com/prowler-cloud/prowler · Ficha:
`tool_catalog/entries/gentleman-programming/prowler-agent-skills.md` · Video:
`tool_catalog/entries/gentleman-programming/agents-skills-video.md`.
