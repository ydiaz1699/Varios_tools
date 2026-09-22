---
slug: gentleman-dots
title: Gentleman.Dots — entorno de desarrollo (dotfiles) + capa de IA
type: dotfiles
problem: >
  Configurar de una vez un entorno de desarrollo completo (Neovim, shells,
  multiplexores, terminales) y, opcionalmente, una capa de IA para CLIs de LLM.
applies_to:
  - montar/estandarizar un entorno de terminal + Neovim (macOS/Linux/RPi)
  - repos que quieran una capa de IA para Claude Code/OpenCode/Gemini/Cursor
  - referencia de cómo el autor organiza skills/ y AGENTS.md en sus dotfiles
not_for:
  - proyectos que solo necesitan el patrón de skills (para eso, ver prowler-agent-skills)
  - firmware/embebidos o proyectos sin entorno de terminal a estandarizar
tags: [dotfiles, neovim, shell, tmux, zellij, terminal, ai-cli, agent-skills]
reference:
  url: https://github.com/Gentleman-Programming/Gentleman.Dots
  kind: github
related:
  - "Conocimiento destilado (NO clonar el repo): tools_AI/skills/skill-creator/references/gentleman-dots-case-study.md"
  - "Capa IA separada: https://github.com/Gentleman-Programming/gentle-ai"
  - "Mismo autor que el video de Agent Skills (ver gentleman-agents-skills-video / prowler-agent-skills)"
status: REVISADO_A_FONDO
evaluated_on: 2026-09-22
---

# Gentleman.Dots

## Idea central

Dotfiles del autor con un **instalador TUI** (Homebrew o binario) que despliega
un entorno de desarrollo completo: Neovim (LSP, autocompletado), shells (Fish,
Zsh, Nushell), multiplexores (Tmux, Zellij, Herdr) y emuladores (Alacritty,
WezTerm, Kitty, Ghostty). La **capa de IA** (configs de Claude Code/OpenCode/
Gemini/Cursor con memoria persistente, workflow SDD, skills y "persona") ahora
vive en un instalador aparte, `gentle-ai`. El repo incluye además carpetas
`skills/` y `AGENTS.md` propios.

## Qué problema resuelve

Evita configurar a mano decenas de herramientas de terminal; da un entorno
reproducible y una capa de IA lista. Como referencia, muestra cómo el mismo autor
del patrón Agent Skills organiza `skills/` + `AGENTS.md` en un repo real.

## Cuándo SÍ aplica

- Quieres un entorno de terminal/Neovim reproducible en macOS/Linux.
- Buscas una capa de IA para CLIs de LLM (vía `gentle-ai`).
- Quieres un segundo ejemplo real de `skills/` + `AGENTS.md` además de Prowler.

## Cuándo NO aplica

- Solo te interesa el **patrón** de skills/auto-invoke → usa `prowler-agent-skills`
  (más enfocado y ya aplicado en nas-dotfiles). No hace falta leer estos dotfiles.
- Es un proyecto embebido o sin entorno de terminal que estandarizar.

## Qué llevarte si aplica

- El **instalador TUI** como patrón de despliegue de dotfiles multiplataforma.
- **1 solo AGENTS.md** (repo no monorepo) con tabla Auto-invoke que añade una
  columna **"Why"** (la razón de cargar cada skill, no solo el mapeo).
- El **orquestador SDD delegate-only** + subagentes (el patrón del video
  aplicado) y la "identity inheritance" (no perder el tono al delegar).
- Frontmatter de skills **sin `scope`/`auto_invoke`** → auto-invoke manual (la
  misma variante que nas-dotfiles).
- `gentle-ai` como referencia de capa de IA multi-CLI con memoria/skills.

## Referencia

- **Conocimiento ya destilado (leer esto ANTES de clonar):**
  `tools_AI/skills/skill-creator/references/gentleman-dots-case-study.md` —
  estructura real, frontmatter real, tabla Auto-invoke con "Why", orquestador
  SDD/subagentes, y qué adoptar/qué no.
- Repo: https://github.com/Gentleman-Programming/Gentleman.Dots — clonar SOLO
  para un matiz que el caso de estudio no cubra.
