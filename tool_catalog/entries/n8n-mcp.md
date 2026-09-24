---
slug: n8n-mcp
title: n8n-mcp (czlonkowski) — que un LLM cree y gestione workflows de n8n
type: repo            # repo | video | dotfiles | tool | article | pattern
problem: >
  Dar a un asistente LLM conocimiento de los ~525 nodos de n8n y capacidad de
  crear/validar/actualizar workflows en la instancia real vía la API REST.
applies_to:
  - que un agente/LLM (Kiro CLI, Claude, Cursor) diseñe y cree workflows de n8n
  - conocer nodos/parámetros de n8n sin memorizarlos ni abrir la UI
  - gestión de workflows por lenguaje natural (list/get/create/update/delete/test)
not_for:
  - ejecutar workflows YA creados desde un LLM (eso es el MCP nativo de n8n, otra cosa)
  - automatizar n8n sin agente/LLM (usar la propia UI/API o cron)
  - Kiro Web (sandbox cloud): sin ruta a la LAN privada; usar Kiro CLI en el NAS
tags: [n8n, mcp, workflows, automatizacion, kiro-cli, nas, api-rest, ssrf]
reference:
  url: https://github.com/czlonkowski/n8n-mcp
  kind: github
related: [rclone-mcp-servers]
status: APLICADO          # montado y verificado en runtime en el NAS (2026-09-24)
evaluated_on: 2026-09-24
---

# n8n-mcp (czlonkowski)

## Idea central

MCP stdio en Node (`npx n8n-mcp`) que da a un LLM dos capas: (1) **documentación**
de los ~525 nodos de n8n (buscar nodos, ver parámetros, validar) y (2) **gestión**
de la instancia real vía la **API REST** de n8n (crear/listar/actualizar/borrar/
probar workflows). No confundir con el MCP nativo de n8n (`Connect a client`,
`/mcp-server/http`), que hace lo contrario: expone workflows YA hechos para
ejecutarlos.

## Qué problema resuelve

Evita escribir un MCP de n8n desde cero y evita que el LLM invente configuraciones
de nodos: conoce los nodos reales y valida antes de crear. Convierte "quiero un
workflow que haga X" en un workflow creado en tu n8n.

## Cuándo SÍ aplica

- Quieres que Kiro CLI (u otro cliente MCP en la LAN) **cree/gestione** workflows.
- Necesitas que el LLM conozca nodos/parámetros correctos de n8n.

## Cuándo NO aplica

- Solo quieres **disparar** workflows existentes desde un LLM → MCP nativo de n8n.
- No hay agente/LLM → usa la UI/API de n8n directamente.
- **Kiro Web** no puede (sandbox sin LAN); sí **Kiro CLI en el NAS**.

## Qué llevarte si aplica

- Paquete npm **`n8n-mcp`** (`npx n8n-mcp`), modo gestión con `N8N_API_URL` +
  `N8N_API_KEY` (la API key REST, no el token del MCP nativo).
- **GOTCHA ESTRELLA:** el guard SSRF bloquea IPs privadas en modo `strict`
  (default). Fix real (verificado en el código, `src/utils/ssrf-protection.ts`):
  `WEBHOOK_SECURITY_MODE=permissive` (NO `ALLOW_PRIVATE_IPS`, que no existe).
- **URL con IP privada** (`http://192.168.1.200:5678`) porque el kiro-cli está en
  `network_mode: host` y no resuelve el nombre `n8n` de `db_net`.
- Obligatorio `MCP_MODE=stdio` + `DISABLE_CONSOLE_OUTPUT=true` (o los logs rompen stdio).
- 27 tools clasificadas allow (lectura/docs/validación) vs ask (crea/modifica/borra).

Guía completa reproducible (compose, `.env`, wrapper, permisos V3, verificación
runtime) en [`../../kiro-cli-nas/n8n-mcp.md`](../../kiro-cli-nas/n8n-mcp.md).
**Leer esa guía ANTES de clonar el repo; clonar solo para un matiz no cubierto.**

## Referencia

- Fuente: https://github.com/czlonkowski/n8n-mcp (npm `n8n-mcp`, v2.89.0 verificada)
- Setup MCP: https://github.com/czlonkowski/n8n-mcp/blob/main/docs/CODEX_SETUP.md
- Leer el repo completo SOLO para un matiz no cubierto por la guía local.
