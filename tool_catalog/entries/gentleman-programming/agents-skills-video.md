---
slug: gentleman-agents-skills-video
title: Video Gentleman Programming — arquitectura AGENTS.md + skills + subagentes
type: video
origin: external
problem: >
  Entender la arquitectura de contexto para agentes LLM (AGENTS.md + skills por
  trigger + auto-invoke + subagentes) sin releer la transcripción completa.
applies_to:
  - diseñar el contexto para agentes en un repo (AGENTS.md + skills)
  - decidir tamaño/división de AGENTS.md (uno vs varios por feature)
  - saber cuándo delegar en subagentes para no ensuciar el contexto
not_for:
  - proyectos sin agentes LLM (firmware Arduino/ESP, etc.)
tags: [agent-skills, agents-md, auto-invoke, subagentes, orquestador, contexto, video]
reference:
  url: https://www.youtube.com/watch?v=Nvn6s3r9ZAw
  kind: youtube
related:
  - "Transcripción (gist): https://gist.github.com/ydiaz1699/39b3288dabc5df14ccbcb3dfb8fb2ad9"
  - "Ejemplo del video: tool_catalog/entries/gentleman-programming/prowler-agent-skills.md"
  - "Aplicado en: tools_AI/skills/skill-creator (Paso 6 + references/)"
status: REVISADO_A_FONDO
evaluated_on: 2026-09-22
---

# Video Gentleman Programming — AGENTS.md + skills + subagentes

## Idea central

Arquitectura de contexto en 3 niveles para que el agente no alucine por exceso de
contexto: (1) **AGENTS.md** = "el README para agentes" (arquitectura, dónde va
cada cosa; ~250 líneas, máx ~500); si el repo es grande, **varios AGENTS.md por
feature + un root que enruta**. (2) **Skills** cargadas por trigger, cada una en
`skills/<n>/{SKILL.md,references/,assets/}`; como los modelos no auto-activan de
forma fiable, se refuerza con una tabla **auto-invoke** en AGENTS.md. (3)
**Subagentes**: para tareas repetitivas/paralelas, el **orquestador** delega en
subagentes con **contexto aislado** que devuelven solo un **resumen**, así el
orquestador no se ensucia.

## Qué problema resuelve

Evita meter toda la doc/código en el prompt (caro, alucina) y evita que el agente
ignore las convenciones. Da una arquitectura reutilizable para cualquier repo con
agentes.

## Cuándo SÍ aplica

- Vas a montar/mejorar AGENTS.md + skills en un repo.
- Dudas si dividir el AGENTS.md o cuándo usar subagentes.

## Cuándo NO aplica

- Proyecto sin agentes LLM → no lo mires.

## Qué llevarte si aplica

- El **límite de tamaño** y la división de AGENTS.md (root que enruta).
- El patrón **auto-invoke** (ya en `skill-creator/references/auto-invoke-and-metadata.md`).
- El patrón **subagente/orquestador** (ya en `skill-creator/references/agents-md-and-subagents.md`).
- El repo de ejemplo: ver ficha `prowler-agent-skills`.

## Referencia

- Video: https://www.youtube.com/watch?v=Nvn6s3r9ZAw
- Transcripción propia (gist): https://gist.github.com/ydiaz1699/39b3288dabc5df14ccbcb3dfb8fb2ad9
- Leer la transcripción completa SOLO si necesitas un matiz que las references de
  `skill-creator` no cubran; el patrón ya está extraído y aplicado ahí.
