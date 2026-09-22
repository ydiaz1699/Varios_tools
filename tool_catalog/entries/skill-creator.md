---
slug: skill-creator
title: skill-creator — meta-skill para crear/optimizar skills de agentes LLM
type: tool
problem: >
  Crear skills de agentes LLM bien estructuradas (frontmatter, carga progresiva,
  triggering, auto-invoke) sin reinventar el proceso cada vez.
applies_to:
  - crear una skill nueva para Kiro/Claude Code/Claude.ai
  - mejorar/optimizar una skill existente (description, references, tamaño)
  - entender best practices de authoring de skills
not_for:
  - proyectos sin agentes LLM
tags: [skill, meta-skill, authoring, agent-skills, auto-invoke, kiro]
reference:
  url: tools_AI/skills/skill-creator/SKILL.md
  kind: web
related:
  - "tool_catalog/entries/gentleman-programming/prowler-agent-skills.md (fuente del patrón auto-invoke)"
  - "Aplicado en: nas-dotfiles .kiro/skills/skill-creator"
status: APLICADO
evaluated_on: 2026-09-22
---

# skill-creator (artefacto propio en tools_AI)

## Idea central

Meta-skill que guía el proceso completo de authoring: capturar intent, escribir
`SKILL.md` conciso con carga progresiva, crear `references/`, optimizar la
`description` para triggering, evaluar/iterar, y (Paso 6) añadir auto-invoke +
`metadata.scope/auto_invoke` cuando el proyecto tiene varias skills + AGENTS.md.

## Qué problema resuelve

Evita crear skills monolíticas, con description-phrasebook o sin auto-invoke.
Estandariza cómo se ven las skills en cualquier proyecto propio.

## Cuándo SÍ aplica

- Vas a crear o mejorar una skill en cualquier repo con agentes LLM.

## Cuándo NO aplica

- El proyecto no usa agentes/skills.

## Qué llevarte si aplica

- `SKILL.md` (proceso en 6 pasos) + `assets/SKILL-TEMPLATE.md` (plantilla copiable).
- `references/auto-invoke-and-metadata.md` (scope, auto_invoke, manual vs sync).
- `references/{best-practices, description-optimization, eval-workflow, structure}.md`.

## Referencia

- Artefacto: `tools_AI/skills/skill-creator/` (vive íntegro en este repo).
