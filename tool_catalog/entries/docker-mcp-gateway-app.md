---
slug: docker-mcp-gateway-app
title: Docker MCP Gateway GUI App (MariyaSha) — 1 gateway federando N MCP servers
type: repo
problem: >
  Un solo endpoint (Docker MCP Gateway) que federa varios MCP servers locales y
  remotos vía un catalog.yaml; app Python (Streamlit) + Docker Model Runner.
applies_to:
  - entender el patrón "un conector -> N MCP servers" (federación por catalog.yaml)
  - diseñar el registro declarativo de actors del hub MCP propio (construir-mcp/PLAN-hub-de-actors.md)
  - conectar Claude/Cursor/una app Python a MCPs existentes (Stripe, HuggingFace, DuckDuckGo)
not_for:
  - montarlo tal cual en el NAS (usa /var/run/docker.sock -> viola la regla anti-socket del usuario)
  - crear actors PROPIOS con lógica nueva (el gateway federa MCPs existentes, no los fabrica)
  - entornos headless sin Docker Desktop / Model Runner
tags: [docker, mcp, gateway, catalog, federacion, streamlit, socket-gotcha]
reference:
  url: https://github.com/MariyaSha/Docker_MCPGUIApp
  kind: github
related:
  - "Plan del hub de actors (mismo patrón, sin socket) — construir-mcp/PLAN-hub-de-actors.md"
  - "Video fuente (= el que se descargó en la sesión) — https://youtu.be/DO3wPYJKpxk"
  - "MCP de rclone ya montado — entries/rclone-mcp-servers.md"
status: REVISADO_PARCIAL
evaluated_on: 2026-09-28
---

# Docker MCP Gateway GUI App (MariyaSha)

## Idea central

Template del patrón **Docker MCP Gateway + Catalog**: una app Python (Streamlit) habla con
**UN solo gateway** (`docker/mcp-gateway`) y ese gateway unifica el acceso a varios MCP servers
—locales (DuckDuckGo) y remotos (Hugging Face, Stripe)— declarados en un `catalog.yaml`. Es el
patrón "un conector → N cosas" resuelto por Docker. Es el codebase del video de YouTube
"Stop Sharing API Keys with LLMs - Use Docker MCP Catalog Instead!".

## Qué problema resuelve

No repartir API keys entre clientes ni cablear cada MCP server a mano: Docker gestiona auth,
endpoints y descubrimiento de tools tras un único gateway, con los servers declarados en un YAML.

## Cuándo SÍ aplica

- Para **entender/referenciar** el patrón de federación "1 gateway → N MCP servers".
- Para inspirar el **registro declarativo (catalog.yaml)** del hub de actors propio.
- Si aceptas Docker Desktop + Model Runner y el socket, para conectar apps/Claude/Cursor a MCPs.

## Cuándo NO aplica

- **Gotcha crítico:** los dos gateways montan `/var/run/docker.sock` en el compose → **viola la
  regla anti-socket del usuario**. No copiar el mecanismo tal cual al NAS.
- Es un **federador** de MCPs que ya existen, NO un **creador de actors** con lógica propia (que
  es lo que busca el hub del usuario). Docker federa; el hub quiere fabricar actors.
- Entornos headless sin Docker Desktop.

## Qué llevarte si aplica

- El **concepto de `catalog.yaml`** (registro declarativo de servers/actors) → imitar como
  registro del hub MCP propio, pero SIN socket.
- La idea de **app ↔ 1 gateway** (no la app contra cada server) = misma separación
  "quién ejecuta" vs "qué hace" del contrato de actor portable.
- Archivos clave: `complete_app/docker-compose.yaml` (ver el `docker.sock` — el gotcha),
  `complete_app/catalog.yaml` (registry de remotos), `complete_app/app.py`.

## Referencia

- Fuente: https://github.com/MariyaSha/Docker_MCPGUIApp
- Video: https://youtu.be/DO3wPYJKpxk
- Leer completo SOLO para el matiz del catalog.yaml o del gateway; el mecanismo (socket) NO se
  adopta en el NAS.
