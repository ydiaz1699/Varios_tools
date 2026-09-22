# Auto-invoke y metadata (scope / auto_invoke)

Patrón tomado del estándar [Agent Skills](https://agentskills.io) y de cómo lo
aplica Prowler (ver ficha `tool_catalog/entries/prowler-agent-skills.md` y el
video https://www.youtube.com/watch?v=Nvn6s3r9ZAw). Resuelve un problema real:
**los modelos NO auto-activan una skill de forma fiable solo con su
`description`** — tratan el trigger como una sugerencia y siguen de largo.

## El problema

Aunque el `description` de la skill describa bien cuándo usarla, el LLM a menudo
no la carga y "barre hacia adelante" con su enfoque por defecto. Esto es
especialmente cierto en repos con muchas skills.

## La solución: obligar desde AGENTS.md

Además del `description`, poner en el `AGENTS.md` del proyecto una sección que
ORDENE cargar la skill antes de actuar:

```markdown
## Auto-invoke Skills

Cuando la acción encaje con una fila, cargar esa skill PRIMERO
(`.kiro/skills/<skill>/SKILL.md`) antes de actuar.

| Cuando la acción sea... | Cargar skill |
|---|---|
| Crear/modificar un componente React | `mi-skill-ui` |
| Escribir un test | `mi-skill-test` |
```

Es un workaround conocido: el `description` sugiere; la tabla de AGENTS.md manda.

## Metadata que habilita el auto-invoke

Añadir al frontmatter de cada skill (campos extra; Kiro/Claude activan por
`name`+`description` y **no** rompen con metadata adicional):

```yaml
---
name: mi-skill
description: >
  Qué hace + cuándo + keywords.
license: MIT
metadata:
  author: TU_USUARIO
  version: "1.0"
  scope: [SCOPE]          # a qué AGENTS.md / dominio pertenece
  auto_invoke:
    - "Acción concreta que debe disparar esta skill"
---
```

- `scope`: a qué `AGENTS.md` pertenece la skill. En un monorepo por features
  Prowler usa `ui`, `api`, `sdk`, `root`. En un proyecto por dominios (no por
  carpetas) se definen scopes propios (ej. nas-dotfiles: `root`, `services`,
  `data`, `mcp`, `docs`) que hoy mapean todos al `AGENTS.md` raíz.
- `auto_invoke`: una o varias acciones. Son las filas que se copian a la tabla
  "Auto-invoke Skills" del AGENTS.md correspondiente.

## Mantenimiento: manual vs sync

Dos formas de mantener la tabla de AGENTS.md sincronizada con la metadata:

- **Manual** (recomendado con pocas skills): al crear/modificar una skill, copiar
  a mano sus entradas `auto_invoke` a la tabla del AGENTS.md. Simple, sin script
  que mantener.
- **Automático** (`skill-sync`): un script (`sync.sh`) que lee `metadata.scope`
  y `metadata.auto_invoke` de cada `SKILL.md` y regenera las tablas de todos los
  AGENTS.md. Referencia: Prowler `skills/skill-sync/assets/sync.sh` (soporta
  `--dry-run` y `--scope`). Vale la pena cuando hay muchas skills y el
  mantenimiento manual se vuelve pesado.

## assets/ vs references/

Prowler distingue dos carpetas de apoyo:

| Carpeta | Para qué |
|---|---|
| `references/` | Documentos que el LLM lee on-demand (guías, contratos). Apuntar a archivos LOCALES, no URLs. |
| `assets/` | Recursos que el LLM **copia o ejecuta**: plantillas (`SKILL-TEMPLATE.md`), schemas, scripts. |

Regla: si el LLM lo lee para entender → `references/`. Si lo copia/ejecuta →
`assets/`. No poner en `assets/` conocimiento operativo que ya vive en una guía.

## Qué NO copiar de Prowler porque no aplica siempre

- `allowed-tools` en el frontmatter: Claude Code lo consume, pero **Kiro no**.
  Incluirlo no rompe, pero no tiene efecto en Kiro.
- `setup.sh` multi-agente (symlinks a `.claude/`, `.gemini/`, `.codex/`,
  Copilot): solo si necesitas soportar varias herramientas a la vez. En un
  entorno solo-Kiro es innecesario.
