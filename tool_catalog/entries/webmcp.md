---
slug: webmcp
title: WebMCP — estándar (borrador W3C) para que una web exponga tools a agentes
type: repo
problem: >
  Estándar propuesto para que una WEB exponga sus propias funciones como "tools"
  (document.modelContext.registerTool()) consumibles por agentes/LLM del navegador.
applies_to:
  - vigilar como TENDENCIA futura del web + agentes (no usar hoy)
  - si algún día construyes una web propia y quieres exponer sus acciones a un agente
not_for:
  - controlar webs de TERCEROS (Flowise/Node-RED/etc.) — WebMCP requiere que ESA web lo implemente; no lo hacen
  - cualquier uso en producción hoy (es un explainer/spec en borrador, soporte incipiente)
  - reemplazar MCP backend (sus propios autores dicen que lo COMPLEMENTA, no lo sustituye)
tags: [webmcp, w3c, estandar, borrador, browser-agents, tendencia-futura, registerTool]
reference:
  url: https://github.com/webmachinelearning/webmcp
  kind: github
related: [chrome-devtools-mcp]
status: SOLO_REFERENCIA
evaluated_on: 2026-09-25
---

# WebMCP

## Idea central

Propuesta de estándar (W3C Web Machine Learning CG; impulso de Microsoft + Google) para que
una página web declare tools con `document.modelContext.registerTool({name, description,
inputSchema, execute})` — o de forma declarativa desde `<form>` — y un agente (del navegador,
un iframe o una extensión) las invoque. La idea: adaptar el contenido web, hecho para humanos,
para que lo usen agentes, sin depender de "ver" y clicar la UI.

## Qué problema resuelve

Que un agente actúe sobre una web mediante tools bien definidas (con schema) en vez de
adivinar la UI. PERO solo funciona si **esa web** implementa WebMCP.

## Cuándo SÍ aplica

- Como radar de tendencia: hacia dónde va la interacción web ↔ agentes.
- Si en el futuro construyes una web propia y quieres exponer sus acciones a agentes.

## Cuándo NO aplica

- Controlar webs de terceros (el caso "que el agente maneje Flowise/Node-RED"): esas webs
  NO implementan WebMCP → no sirve. Para eso, sus APIs REST (ver
  `../../construir-mcp/HALLAZGO-apis-despliegue-workflows.md`).
- Hoy, en producción: es spec en BORRADOR, soporte de navegador incipiente.

## Qué llevarte si aplica

- El concepto `registerTool()` imperativo + variante declarativa por `<form>`.
- Se complementa con MCP backend, no lo reemplaza (lo dicen sus autores).
- Estado: seguir el "Implementation Status" del repo antes de considerar usarlo.

## Referencia

- Fuente: https://github.com/webmachinelearning/webmcp (explainer/spec)
- Revisar solo el estado de implementación; no invertir en montarlo aún.
