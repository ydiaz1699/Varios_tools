---
slug: idea-forge
title: idea-forge — formular ideas, conectar el ecosistema e investigar
type: tool
problem: >
  Formular ideas fundadas en lo que el usuario YA tiene: cruza tool_catalog + repo-index para
  proponer combinaciones nuevas, evita reinventar, e investiga afuera solo si falta.
applies_to:
  - lluvia de ideas / "¿qué construyo o mejoro con lo que tengo?"
  - conectar dos proyectos/herramientas del ecosistema entre sí
  - evaluar un recurso nuevo frente a lo que ya existe
  - investigar un tema y aterrizarlo al caso del usuario
not_for:
  - crear la skill/artefacto en sí (usar skill-creator)
  - unificar drafts/notas dispersas (usar unificador-skill)
  - construir un MCP (usar construir-mcp/)
  - implementar/ejecutar la idea (lo hace la skill o proyecto específico)
tags: [ideacion, brainstorming, research, conectar, catalogo, repo-index, procedencia]
reference:
  url: tools_AI/skills/idea-forge/SKILL.md
  kind: web
related: [skill-creator, unificador-skill, deep-research-mcp, nas-agent-memory]
status: APLICADO
evaluated_on: 2026-09-25
---

# idea-forge

## Idea central

Skill de **ideación con procedencia**: en vez de inventar ideas al aire, mira primero el
ecosistema del usuario (tool_catalog + repo-index + construir-mcp + nas-dotfiles), cruza las
piezas que ya existen para proponer combinaciones nuevas, avisa si algo ya existe (no
duplicar), y solo investiga hacia afuera cuando falta contexto — aterrizando lo investigado a
su caso, no dejando un informe genérico.

## Qué problema resuelve

"Tengo muchas piezas (repos, MCPs, servicios) pero no veo cómo unirlas / qué construir".
idea-forge las conecta y prioriza ideas concretas con piezas reales.

## Cuándo SÍ aplica

- Pedir brainstorming: "¿qué puedo construir/mejorar con lo que tengo?"
- Conectar dos herramientas/proyectos entre sí.
- Evaluar un recurso nuevo frente al ecosistema.
- Investigar un tema y aterrizarlo.

## Cuándo NO aplica

- Crear la skill en sí → `skill-creator`. Unificar drafts → `unificador-skill`.
  Construir un MCP → `construir-mcp/`. Ejecutar la idea → la skill/proyecto específico.

## Qué llevarte si aplica

- Orden obligatorio: **adentro (ecosistema) → conectar → afuera (solo si falta)**.
- Salida: 2–4 ideas priorizadas, cada una con piezas EXISTENTes + qué falta + esfuerzo, y
  siguiente paso; ofrecer catalogar lo nuevo.
- Su "brazo externo" de investigación profunda es el MCP de deep research (`deep-research-mcp`),
  opcional.

## Referencia

- Fuente: `tools_AI/skills/idea-forge/SKILL.md`
