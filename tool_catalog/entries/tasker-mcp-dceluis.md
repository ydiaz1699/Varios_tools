---
slug: tasker-mcp-dceluis
title: dceluis/tasker-mcp — MCP que EJECUTA tareas de Tasker en vivo (Go + XTP)
type: repo
origin: external
problem: >
  Dar a un LLM control en vivo del teléfono exponiendo tareas de Tasker como tools MCP,
  hablando por HTTP con el propio Tasker (no genera XML, dispara acciones reales).
applies_to:
  - controlar el teléfono en vivo desde un LLM (flash, SMS, wifi, foto, ubicación...)
  - convertir tareas Tasker existentes en tools MCP sin escribir código por tool
  - patrón "tarea Tasker → tool MCP" leyendo comentario + TaskVariables del .prj.xml
not_for:
  - generar XML de Tasker importable offline (para eso está tu propio Tasker_mcp, Python)
  - entornos sin Tasker corriendo y accesible por HTTP (necesita el server HTTP de Tasker)
  - quien no quiera compilar Go / usar binarios precompilados en el teléfono (Termux)
tags: [tasker, mcp, android, go, xtp, wasm, ejecucion-en-vivo, sse, stdio]
reference:
  url: https://github.com/dceluis/tasker-mcp
  kind: github
related:
  - "Espejo de seguridad propio — https://github.com/ydiaz1699/tasker-mcp-dceluis"
  - "Tu MCP propio (genera XML, Python) — https://github.com/ydiaz1699/Tasker_mcp"
  - "Control Android por ADB (ecosistema) — https://github.com/ydiaz1699/android_agent_bridge"
status: REVISADO_A_FONDO
evaluated_on: 2026-09-25
---

# dceluis/tasker-mcp

MIT · Go (+ JS util) · 49 ⭐ · último push 2025-03-10 · autor Luis Sanchez.

## Idea central

Un servidor MCP escrito en Go que **no genera** configuraciones de Tasker: **ejecuta**
tareas que ya existen en el teléfono. Cada tarea de Tasker marcada como "MCP" se expone
como una tool MCP; cuando el LLM la llama, el server hace un `POST /run_task` al servidor
HTTP del propio Tasker (puerto 1821) y devuelve el resultado. Es el enfoque opuesto al de
tu `Tasker_mcp` propio (que produce XML importable sin tocar el teléfono).

## Qué problema resuelve

Que un LLM controle el teléfono en tiempo real (mandar SMS, encender wifi, sacar foto,
leer batería/ubicación, hablar por TTS, etc.) reusando la lógica que ya tienes montada en
Tasker, **sin escribir un handler por cada acción**: el schema de cada tool se deduce
automáticamente de la tarea Tasker.

## Cómo funciona (el truco que vale la pena)

1. En Tasker, una tarea se vuelve tool si tiene **comentario** (→ descripción de la tool) y
   sus **TaskVariables** cumplen: `Configure on Import`=off, `Immutable`=on, valor vacío.
   El tipo (`number`/`string`/`onoff`) y el `Prompt` de la variable definen el JSON schema;
   `Same as Value` (clearout) marca el argumento como requerido.
2. Exportas el proyecto (`mcp_server.prj.xml`) y `utils/xml-to-tools.js` lo convierte en
   `toolDescriptions.json` (lista de tools con inputSchema JSON). — esta es la pieza más
   reutilizable del repo (parser XML→schema MCP genérico, ~120 líneas).
3. El binario Go (`cli/main.go`) carga ese JSON, registra cada entrada como tool MCP
   genérica, y al invocarla hace `POST http://<tasker-host>:1821/run_task` con auth Bearer.
   Transportes: `stdio` o `sse`. Una acción especial `MCP#parse_args` en Tasker desempaqueta
   los argumentos (Tasker solo pasa `par1`/`par2` posicionales).
4. También hay un **plugin XTP/WASM** (`plugin/`, TinyGo → wasip1) como empaquetado alterno.

Tools de ejemplo ya incluidas (`dist/toolDescriptions.json`, 22): set/get volume, print,
clipboard, list files, lamp on/off, play music, battery, location, take photo, call, create
task, say, set alarm, flashlight, contacts, send SMS, toggle wifi, flash text, browse URL,
screenshot.

## Cuándo SÍ aplica

- Quieres que un agente ejecute acciones reales en el teléfono vía Tasker.
- Ya tienes tareas Tasker y no quieres codificar una tool por cada una.
- Buscas el patrón "config declarativa (XML/comentarios) → tools MCP con schema".

## Cuándo NO aplica

- Solo quieres GENERAR archivos `.tsk.xml`/`.prf.xml`/`.prj.xml` (ahí gana tu Tasker_mcp).
- No tienes Tasker corriendo ni su server HTTP alcanzable (requiere el teléfono en red).
- No quieres binarios Go en el teléfono (Termux) ni compilar / cross-compilar.

## Qué llevarte si aplica

- `utils/xml-to-tools.js` — parser XML de Tasker → JSON schema de tools MCP (la joya).
- El **convenio TaskVariable→argumento** (immutable + no-configure + vacío) documentado en el
  README; sirve para "descubrir" tools desde datos declarativos.
- `cli/main.go` — patrón de **tool handler genérico** en Go (una función maneja N tools; el
  schema viene de datos, no de código). Útil como referencia para MCPs data-driven.
- La idea de dos empaquetados: binario CLI (stdio/sse) y plugin XTP/WASM.

## Referencia

- Fuente: https://github.com/dceluis/tasker-mcp (MIT). Leer completo solo si vas a montar
  ejecución en vivo o a reusar el parser XML→tools. Para generar XML, tu repo propio ya cubre.
- **Espejo de seguridad:** https://github.com/ydiaz1699/tasker-mcp-dceluis (copia propia
  por si el original —inactivo desde 2025-03— se borra; ver su `UPSTREAM.md`).
