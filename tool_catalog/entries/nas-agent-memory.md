---
slug: nas-agent-memory
title: nas-agent-memory — diseño de memoria persistente + auto-mejora para un agente
type: pattern
problem: >
  Dar a un agente LLM memoria persistente entre sesiones y un Learning Loop
  (recordar, aprender skills, modelar al usuario, auto-curarse) en vez de ser
  stateless.
applies_to:
  - diseñar memoria persistente para un agente (Strands SDK u otro)
  - implementar un Learning Loop / auto-mejora en un agente propio
  - referencia de arquitectura (memory system, nudge layers)
not_for:
  - agentes sin necesidad de estado entre sesiones
  - proyectos sin componente de agente
tags: [memoria, agente, learning-loop, auto-mejora, strands, nudge, diseño]
reference:
  url: tools_AI/resources/nas-agent-memory/README.md
  kind: web
related:
  - "Destino final — nas-dotfiles agent/ (ydiaz1699/nas-dotfiles)"
  - "Inspiración — Hermes Agent (Nous Research) https://hermes-agent.nousresearch.com/"
status: SOLO_REFERENCIA
evaluated_on: 2026-09-22
---

# nas-agent-memory (recurso de diseño en tools_AI)

## Idea central

Documentación de diseño (pre-implementación) de un sistema de memoria persistente
y auto-mejora para el agente NAS: recordar lecciones/soluciones entre sesiones,
aprender procedimientos de tareas exitosas, modelar al usuario, y auto-curar la
memoria (eliminar obsoleta, consolidar). Incluye docs de sistema de memoria,
capas de "nudge" y guía de implementación, más código de referencia
(`memory.py`, `memory_plugin.py`, `memory_tools.py`).

## Qué problema resuelve

Un agente stateless repite trabajo y olvida contexto entre sesiones; esto lo hace
mejorar con el uso.

## Cuándo SÍ aplica

- Vas a diseñar/implementar memoria o Learning Loop en un agente propio.

## Cuándo NO aplica

- El proyecto no tiene agente, o no necesita estado entre sesiones.

## Qué llevarte si aplica

- `docs/{01-memory-system, 02-nudge-layers, 03-implementation-guide}.md`.
- Código de referencia en `reference/code-base/` (adaptar, no copiar tal cual).

## Referencia

- Recurso: `tools_AI/resources/nas-agent-memory/` (doc de diseño, no producción).
