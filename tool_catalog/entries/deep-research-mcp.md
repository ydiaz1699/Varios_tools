---
slug: deep-research-mcp
title: MCP de deep research (GPT Researcher y alternativas)
type: repo
problem: >
  Dar a un LLM investigación web PROFUNDA e iterativa (busca, scrapea, sintetiza informe con
  citas) en vez de una búsqueda simple — para explorar temas nuevos a fondo.
applies_to:
  - investigar un tema nuevo a fondo (informe con fuentes citadas), no una búsqueda puntual
  - alimentar de contexto externo la skill de ideación (idea-forge) cuando falta info
not_for:
  - búsquedas puntuales (Kiro ya trae web search integrado; no hace falta un MCP)
  - Kiro Web (si el MCP corre en el NAS, mismo límite de red que los otros MCP locales)
tags: [mcp, deep-research, web-search, gpt-researcher, investigacion, tavily, research-agent]
reference:
  url: https://github.com/assafelovic/gptr-mcp
  kind: github
related: [idea-forge, chrome-devtools-mcp]
status: SOLO_REFERENCIA
evaluated_on: 2026-09-25
---

# MCP de deep research

## Idea central

MCP servers que convierten a un LLM en un asistente de **investigación profunda**: en vez de
devolver resultados crudos de búsqueda, hacen búsqueda ITERATIVA (buscan → leen → refinan →
vuelven a buscar) y entregan un **informe sintetizado con citas**. El más establecido es
**GPT Researcher MCP** (`assafelovic/gptr-mcp`); hay varias alternativas equivalentes.

## Qué problema resuelve

Investigar un tema a fondo sin gastar el context window en resultados irrelevantes. Útil como
"músculo de investigación" cuando la skill de ideación (`idea-forge`) necesita traer
conocimiento externo que no está en el catálogo.

## Cuándo SÍ aplica

- Investigar un tema nuevo en profundidad, con informe y fuentes.
- Complementar la ideación cuando falta información externa.

## Cuándo NO aplica

- Una búsqueda puntual: Kiro ya trae web search integrado (no necesitas un MCP para eso).
- Si valoras cero configuración: casi todos piden su propia API key (Tavily/OpenAI/Gemini/
  OpenRouter) → otra credencial + posible coste. Evaluar si compensa.

## Qué llevarte si aplica

- **Candidato principal:** `assafelovic/gptr-mcp` (GPT Researcher, el proyecto de research más
  maduro; deep research vía MCP).
- **Alternativas** (mismo concepto, distinto motor/dependencias) para comparar antes de elegir:
  - `ssdeanx/deep-research-mcp-server` — usa Gemini 2.5 Flash + Google Search grounding, SIN
    scraping (menos dependencias).
  - `pinkpixel-dev/deep-research-mcp` — usa Tavily Search + Crawl.
  - `yoloshii/gigaxity-deep-research` — Qwen3 vía OpenRouter, síntesis multi-fuente con citas.
  - `mzxrai/mcp-webresearch` — más ligero, con prompt "agentic-research".
- Criterio de elección: qué motor/LLM usa (y su coste), si requiere scraping, y si su API key
  encaja con lo que ya tienes. Verificar en vivo antes de montar (regla verificar-antes-de-entregar).

## Referencia

- Principal: https://github.com/assafelovic/gptr-mcp
- Comparar alternativas arriba antes de montar; casi todas requieren API key propia.
- Se relaciona con la skill `idea-forge` (ideación): el research es su "brazo externo".
