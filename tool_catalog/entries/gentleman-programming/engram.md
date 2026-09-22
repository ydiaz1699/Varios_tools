---
slug: engram
title: Engram — memoria persistente para agentes de código (Go + SQLite/FTS5, MCP)
type: repo
origin: external
problem: >
  Dar memoria persistente y compartible entre sesiones/agentes a un agente de
  código, sin Node/Python/Docker: un solo binario Go con SQLite local vía MCP.
applies_to:
  - dar memoria persistente a un agente (recordar decisiones/lecciones entre sesiones)
  - memoria agent-agnostic vía MCP (Claude Code, OpenCode, Gemini, Codex, Cursor...)
  - alternativa lista-para-usar frente a diseñar memoria propia
not_for:
  - agentes sin necesidad de estado entre sesiones
  - entornos donde no puedes correr un binario local ni MCP
tags: [memoria, engram, mcp, sqlite, fts5, go, agent-agnostic, recall, lazy-loading]
reference:
  url: https://github.com/Gentleman-Programming/engram
  kind: github
related:
  - "Web — https://engram.gentlemanprogramming.com/"
  - "Aparece en el video SDD — tool_catalog/entries/gentleman-programming/sdd-video.md"
  - "Diseño propio equivalente (comparar) — tool_catalog/entries/nas-agent-memory.md"
status: REVISADO_PARCIAL
evaluated_on: 2026-09-22
---

# Engram — memoria persistente para agentes

## Idea central

Un **único binario Go** con **SQLite + FTS5** (búsqueda full-text) expuesto por
CLI, HTTP API, **MCP** y una TUI. Da memoria persistente ("One brain, local or
cloud") **agent-agnostic**: funciona con cualquier agente compatible con MCP
(Claude Code, OpenCode, Gemini CLI, Codex, VS Code/Copilot, Cursor, Windsurf...).
Sin Node/Python/Docker: un binario + un archivo SQLite (`~/.engram/engram.db`).
El contrato para el agente: tratarlo como **memoria curada del proyecto, no un
volcado de transcripción** (guardar decisiones/lecciones con su porqué).

## Qué problema resuelve

Los agentes son stateless entre sesiones; Engram les da recall persistente y
compartible entre distintos agentes, con lazy-loading (recuperar solo lo
relevante, no todo).

## Cuándo SÍ aplica

- Quieres memoria persistente lista-para-usar en un agente compatible con MCP.
- Necesitas compartir memoria entre varios agentes/IDEs.

## Cuándo NO aplica

- El agente no necesita estado entre sesiones.
- No puedes correr un binario local ni configurar MCP.

## Qué llevarte si aplica

- El modelo: SQLite+FTS5 local vía MCP, memoria curada (no transcript sink).
- Docs del repo: `docs/AGENT-SETUP.md`, `docs/ARCHITECTURE.md`, `docs/PLUGINS.md`.
- Comparar con tu diseño propio `nas-agent-memory` (misma meta, otra ejecución).

## Referencia

- Repo: https://github.com/Gentleman-Programming/engram (clonar solo si vas a
  instalarlo o estudiar su arquitectura a fondo).
- Ficha hecha desde el README (REVISADO_PARCIAL); subir a REVISADO_A_FONDO si se
  lee `docs/ARCHITECTURE.md`.
