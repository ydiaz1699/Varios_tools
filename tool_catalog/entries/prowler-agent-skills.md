---
slug: prowler-agent-skills
title: Prowler — arquitectura de Agent Skills (AGENTS.md + skills + auto-invoke)
type: repo
problem: >
  Estructurar el contexto de un proyecto para agentes LLM sin saturar tokens:
  AGENTS.md breve + skills cargadas por trigger + auto-invoke obligado.
applies_to:
  - proyectos con .kiro/skills (o .claude/.gemini/.codex)
  - repos donde un agente/LLM colabora y necesita convenciones del proyecto
  - frameworks con muchas guías que conviene cargar bajo demanda
not_for:
  - firmware Arduino/ESP puro sin agentes LLM
  - proyectos pequeños de un solo archivo sin convenciones repetidas
tags: [agent-skills, agents-md, auto-invoke, skill-creator, skill-sync, llm, contexto]
reference:
  url: https://github.com/prowler-cloud/prowler
  kind: github
related:
  - "Video Gentleman: https://www.youtube.com/watch?v=Nvn6s3r9ZAw"
  - "Estándar: https://agentskills.io"
  - "Aplicado en: nas-dotfiles (.kiro/skills/, PRs #148/#149/#150)"
status: APLICADO
evaluated_on: 2026-09-22
---

# Prowler — arquitectura de Agent Skills

## Idea central

Contexto para LLM en 3 niveles para que el agente no alucine por exceso de
contexto: (1) **AGENTS.md** breve (≤250–500 líneas) = "el README para agentes";
(2) **skills** por dominio, cargadas *solo cuando el trigger aplica*, cada una en
`skills/<n>/{SKILL.md,references/,assets/}`; (3) **auto-invoke**: como los modelos
NO activan skills de forma fiable solo con la `description`, una tabla en
AGENTS.md les ORDENA "cuando hagas X, carga la skill Y primero".

## Qué problema resuelve

Evita meter toda la documentación en el prompt (caro y propenso a alucinar) y
evita que el agente ignore las convenciones del proyecto. Onboarding rápido para
humanos y agentes.

## Cuándo SÍ aplica

- Vas a montar/mejorar `.kiro/skills` o equivalentes en un repo.
- Un LLM trabaja en el repo y repite errores por no conocer las convenciones.
- Tienes muchas guías y quieres cargarlas bajo demanda, no todas a la vez.

## Cuándo NO aplica

- Proyecto sin agentes LLM (ej. firmware Arduino) → innecesario, descartar.
- Repo trivial sin convenciones que valga la pena documentar.

## Qué llevarte si aplica

- **Frontmatter enriquecido**: `license` + `metadata.{author,version,scope,auto_invoke}` (`skills/*/SKILL.md`).
- **Meta-skills**: `skills/skill-creator/` (crear skills uniformes) y `skills/skill-sync/assets/sync.sh` (regenera las tablas auto-invoke desde `metadata.scope`/`auto_invoke`).
- **`skills/README.md`**: principios (conciso, progressive disclosure, enlazar-no-duplicar) y la explicación del porqué del auto-invoke.
- **`skills/setup.sh`**: symlinks multi-agente (Claude/Gemini/Codex/Copilot) — solo si necesitas soporte multi-herramienta.

## Referencia

- Repo: https://github.com/prowler-cloud/prowler (carpeta `skills/`)
- Video que lo explica (concepto): https://www.youtube.com/watch?v=Nvn6s3r9ZAw
- Leer el repo completo SOLO si tu proyecto usa agentes/skills. Para el caso
  ya aplicado, ver nas-dotfiles `.kiro/skills/` como implementación adaptada.
