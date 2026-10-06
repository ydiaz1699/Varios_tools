---
slug: chrome-devtools-mcp
title: chrome-devtools-mcp — control de Chrome real para un agente (MCP)
type: repo
problem: >
  Dar a un LLM control de un Chrome real (navegar, clicar, screenshots, red, consola,
  performance) vía Puppeteer, para automatizar/depurar webs — sobre todo las que NO tienen API.
applies_to:
  - depurar/analizar una web (performance, red, consola, DOM) desde el agente
  - automatizar una web que NO expone API REST (scraping, rellenar formularios)
  - probar tu propio frontend (E2E, screenshots) con un LLM
not_for:
  - crear workflows en n8n/Node-RED/Flowise → usar sus APIs REST (ver construir-mcp/HALLAZGO-apis-despliegue-workflows.md); la UI por navegador es frágil
  - tareas donde exista una API oficial (la API siempre es más fiable que manejar la UI)
tags: [mcp, chrome, devtools, puppeteer, browser-automation, debug, performance, scraping]
reference:
  url: https://github.com/ChromeDevTools/chrome-devtools-mcp
  kind: github
related: [n8n-mcp, rclone-mcp-servers, webmcp]
status: REVISADO_A_FONDO
evaluated_on: 2026-09-25
---

# chrome-devtools-mcp

## Idea central

MCP server oficial de Chrome DevTools que expone un Chrome real (vía Puppeteer) a un
agente de código (Claude, Cursor, Copilot, Kiro CLI…). El LLM puede navegar, clicar,
tomar screenshots, inspeccionar red/consola con stack traces mapeados y grabar trazas de
performance. Se lanza con `npx -y chrome-devtools-mcp@latest` (Node + Chrome estable). Trae
modo `--slim`/`--headless` para tareas básicas.

## Qué problema resuelve

Le da a un LLM "manos y ojos" en un navegador real: automatizar/depurar cualquier web,
especialmente las que NO tienen API. Para debug web y performance es de primera.

## Cuándo SÍ aplica

- Depurar una web (por qué va lenta, qué peticiones falla, qué logea la consola).
- Automatizar una web SIN API (rellenar/leer una UI que no ofrece otra vía).
- Probar tu propio frontend con el agente.

## Cuándo NO aplica

- Crear workflows en n8n/Node-RED/Flowise: esas plataformas tienen API REST de despliegue
  (ver `../../construir-mcp/HALLAZGO-apis-despliegue-workflows.md`); manejar su canvas por
  navegador es frágil, lento y caro en tokens. La API gana siempre.
- Cualquier tarea con API oficial disponible.

## Qué llevarte si aplica

- Config MCP mínima: `{"command":"npx","args":["-y","chrome-devtools-mcp@latest"]}`.
  Para el NAS/Kiro CLI necesitaría Chrome en el contenedor (pieza pesada) — valorar antes.
- Flags útiles: `--slim`, `--headless`, `--isolated`, `--no-usage-statistics`.
- Es de Google/ChromeDevTools, soporta oficialmente Chrome y Chrome for Testing.

## Referencia

- Fuente: https://github.com/ChromeDevTools/chrome-devtools-mcp
- Leer el Tool Reference completo solo si vas a montarlo para debug/automatización web.
