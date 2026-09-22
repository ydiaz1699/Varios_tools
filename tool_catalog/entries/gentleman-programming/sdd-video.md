---
slug: sdd-video
title: Video Gentleman — Spec-Driven Development (SDD) de punta a punta
type: video
origin: external
problem: >
  Que la IA no improvise: guiarla con un proceso (spec → diseño → tareas →
  apply/verify) en vez de una prompt vaga o demasiado contexto (ruido).
applies_to:
  - definir un proceso para que un agente no improvise en cambios de código
  - entender SDD (init, preflight, skill registry, strict TDD, fases, PRs encadenadas)
  - diseñar un skill registry / orquestador-subagentes con contexto seleccionado
not_for:
  - proyectos sin agentes LLM
  - cambios triviales que no justifican un proceso formal
tags: [sdd, spec-driven, tdd, skill-registry, orquestador, subagentes, proceso, contexto]
reference:
  url: https://www.youtube.com/watch?v=KILEn2VSXX8
  kind: youtube
related:
  - "Flujo destilado (leer ANTES de releer el video) — tools_AI/skills/skill-creator/references/spec-driven-development.md"
  - "Transcripción (gist) — https://gist.github.com/ydiaz1699/4f29624bf0d0b4806e5269c9d7230013"
  - "SDD aplicado en un repo — tools_AI/skills/skill-creator/references/gentleman-dots-case-study.md"
  - "Memoria del agente que usa — tool_catalog/entries/gentleman-programming/engram.md"
status: REVISADO_A_FONDO
evaluated_on: 2026-09-22
---

# Video Gentleman — Spec-Driven Development (SDD)

## Idea central

SDD es **ingeniería de proceso** (no prompt engineering): el problema no es la
IA sino el contexto vago o excesivo. Se le da "lo justo y necesario" y se le
obliga a seguir un proceso: **SDD Init** (calibrar: detecta stack, preflight,
`openspec/config.yaml`, skill registry, strict TDD) → fases **explore → propose →
spec → design → tasks → apply → verify**, cada una en un **subagente** para no
ensuciar al orquestador. El **Skill Registry** es un índice (skill|trigger|ruta)
del que el orquestador saca los paths exactos y se los pasa al subagente. En
`apply/verify`, **Strict TDD** (test→pasar→edge→evidencia). Si el cambio crece,
**PRs encadenadas** con auto-forecast.

## Qué problema resuelve

Evita que el agente adivine patrones/tradeoffs/constraints que no conoce, y evita
el ruido de meterle todo el contexto de golpe.

## Cuándo SÍ aplica

- Quieres un proceso repetible para que el agente no improvise.
- Vas a diseñar un índice de skills + orquestador/subagentes.

## Cuándo NO aplica

- Proyecto sin agentes, o cambio trivial.

## Qué llevarte si aplica

- El flujo completo y el detalle → `references/spec-driven-development.md` (destilado).
- El **Skill Registry** como validación del patrón de `tool_catalog` + auto-invoke.

## Referencia

- Video: https://www.youtube.com/watch?v=KILEn2VSXX8
- Todo lo accionable ya está destilado en
  `tools_AI/skills/skill-creator/references/spec-driven-development.md`; releer el
  video solo para un matiz no cubierto.
