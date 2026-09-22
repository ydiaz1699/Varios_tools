---
slug: rclone-mcp-servers
title: Servidores MCP para rclone (control total vía RC API)
type: repo            # repo | video | dotfiles | tool | article | pattern
problem: >
  Dar a un asistente LLM control de rclone (listar/copiar/sync/mount/config de remotes)
  como tools MCP, hablando con un daemon `rclone rcd` (RC API, 98 endpoints).
applies_to:
  - exponer rclone a un agente/LLM por MCP (LobeHub, Cursor, Claude, opencode)
  - control total de almacenamiento cloud desde el NAS sin escribir un MCP propio
  - decidir entre "control total" vs "read-only seguro" para un agente
not_for:
  - automatización de rclone SIN un agente/LLM (usar systemd timers / scripts)
  - solo Google Drive con API nativa por file_id (ver nota hyunjae abajo)
tags: [rclone, mcp, rc-api, control-total, read-only, docker, nas, cloud-storage]
reference:
  url: https://github.com/angenge/rclone-mcp-server
  kind: github
related: []
status: APLICADO          # se generó guía en ../../rclone-mcp-control-total/README.md
evaluated_on: 2026-09-22
---

# Servidores MCP para rclone

## Idea central

Ninguno de estos MCP ejecuta rclone directamente: todos son un **puente a la RC API**
de un daemon `rclone rcd`. El "control total" (todas las tools: config, operations,
sync, mount, vfs, serve, jobs, backend…) se consigue con **`RCLONE_TOOLSETS=all`** (98
endpoints), NO fusionando repos. 3 de los 4 candidatos comparten base Node+RC API; el 4º
es otro árbol (Python, solo Google Drive).

## Qué problema resuelve

Evita escribir un MCP de rclone desde cero. Con un daemon `rcd` + este MCP, un agente
controla todo el almacenamiento cloud del NAS por lenguaje natural. También responde la
duda "¿uno control-total o uno read-only seguro?" (respuesta: son modos del mismo repo base).

## Cuándo SÍ aplica

- Quieres que un LLM gestione rclone (mount, sync, remotes) en el NAS por MCP.
- Necesitas decidir base: **`angenge`** es la elegida para control total.

## Cuándo NO aplica

- No hay agente/LLM en el flujo → usa scripts/systemd, no un MCP.
- Solo Google Drive por API nativa/file_id → el enfoque hyunjae (por rutas) es distinto.
- **Kiro Web NO puede usarlo** (sandbox en la nube, sin ruta a la LAN privada). Sí lo usa un cliente
  que corra en la red: **Kiro CLI en el NAS/PC**, LobeHub en el NAS, o Cursor/Claude Desktop en la LAN.

## Qué llevarte si aplica

Los 4 candidatos y para qué sirve cada uno (no re-leer los repos):

- **`angenge/rclone-mcp-server`** (npm `rclone-mcp-server@1.0.3`, MIT) — **BASE ELEGIDA**.
  Refactor del original con mejores defaults, **MCP Resources** (`rclone://remotes`,
  listado/cat por URI) y docs de `_async`+`job/status`. Control total con `TOOLSETS=all`.
- **`rclone-ui/rclone-mcp`** (npm `rclone-mcp@1.0.0`, MIT) — el **original** (Node, RC API,
  auto-generado desde `rclone-openapi`). Menos pulido que angenge.
- **`brokenlander/rclone-mcp-readonly`** (MIT) — fork **read-only REAL** con guards en
  runtime (`copyfile` solo remoto→local, allowlist en `core/command`, bloquea delete/sync/
  config). Es lo CONTRARIO a control total → úsalo solo como modo seguro opcional.
- **`hyunjae-labs/rclone-drive-mcp`** (Python) — solo Google Drive, API por **rutas**
  (no file_id). No toca mount/sync/config/crypt → descartado como base; solo la idea de "rutas".

Arquitectura para el NAS = 2 piezas: **A)** `rclone/rclone:1.75.1` como `rcd` en `db_net`
con **FUSE activo por defecto** (SYS_ADMIN + /dev/fuse + /mnt:rshared) para que `mount` suba al host
+ **B)** `rclone-mcp-server` (`TOOLSETS=all`) lanzado por el gateway MCP. Las 98 tools las da el MCP
(no el daemon); Docker no limita ninguna. Guía completa (compose, .env, mount FUSE, seguridad, systemd alt.) en
[`../../rclone-mcp-control-total/README.md`](../../rclone-mcp-control-total/README.md).

## Referencia

- Base: https://github.com/angenge/rclone-mcp-server (npm rclone-mcp-server)
- Original: https://github.com/rclone-ui/rclone-mcp
- Read-only: https://github.com/brokenlander/rclone-mcp-readonly
- Drive/rutas: https://github.com/hyunjae-labs/rclone-drive-mcp
- Imagen daemon: `rclone/rclone:1.75.1` · RC API: https://rclone.org/rc/
- Leer los repos completos SOLO para un matiz no cubierto por la guía local.
