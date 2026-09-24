# PROYECTO PENDIENTE — Guía "Cómo construir un MCP propio"

> **Estado:** anotado, NO desarrollado. Para retomar en un CHAT NUEVO dedicado.
> **Fecha:** 2026-09-23
> **Motivación del usuario (ydiaz1699):** le gustó cómo se incorporó el MCP a Kiro
> (patrón limpio de dotfiles: mcp_tools + permissions.yaml + steering + wrapper) y quiere
> aprender a **construir sus propios MCP** en el futuro, basándose en lo aprendido con
> `dmeiser/nextdns-mcp`.

---

## ⚠️ El hilo de la idea — NO perder esto

### Aclaración clave: "construir un MCP" son DOS cosas distintas

**Opción A — Construir un MCP server nuevo (escribir el CÓDIGO del MCP).**
Como hizo dmeiser con nextdns-mcp: escribir un servidor MCP en Python (FastMCP) que
exponga tools de algún servicio/API. Lo relevante es la **estructura interna del código**
(las 2 capas, FastMCP, etc.). ← **ESTO es lo que el usuario quiere aprender.**

**Opción B — Incorporar/integrar un MCP a Kiro con el patrón limpio.**
Reutilizar el patrón de integración ya montado (mcp_tools + mcp-build + permissions.yaml
+ steering + wrapper) para cualquier MCP. ← Esto YA está documentado en `../kiro-cli-nas/`.

> El objetivo de ESTE proyecto es la **Opción A** (construir el server), complementada con
> la B (cómo incorporarlo a Kiro, que ya sabemos).

### Corrección importante (para no partir de un error)

El usuario cree que el MCP "no se incorpora mediante JSON, sino por dotfiles". **NO es así:**
registrar un MCP en Kiro SIEMPRE es mediante JSON (`mcp.json` con command/args/env). Lo que
le gustó no es "sin JSON" — es el **patrón limpio de dotfiles alrededor** (JSON por trozos +
permissions.yaml + steering + wrapper). El registro base es JSON. Aclararlo al construir el suyo.

---

## Propuesta: crear la guía "Cómo construir un MCP propio"

Documento a crear (en esta carpeta `construir-mcp/`) que cubra:

1. **Anatomía de un MCP** (basado en el análisis real de nextdns-mcp):
   - Patrón de **2 capas**: lógica pura (`_impl`, hace la llamada HTTP/acción, SIN MCP) +
     envoltorio MCP (`mcp_server.tool()(...)`). Por qué separarlas → **portabilidad**: la
     misma lógica sirve como MCP (para un LLM) Y como import directo (para código/otro agente,
     ej. nas-agent Strands). Este patrón es el hallazgo estrella.
   - **FastMCP** como framework (o alternativas: el SDK oficial de MCP `modelcontextprotocol`).
   - Transportes **stdio vs HTTP** (streamable); cómo se declaran **tools, prompts, resources**.
   - Manejo de argumentos (nextdns-mcp usa StripExtraFieldsMiddleware + coerción de tipos
     porque los clientes LLM mandan campos extra — patrón útil).
   - Config por variables de entorno (`.env` + `load_dotenv`), validación, access control.
2. **Cómo se incorpora a Kiro** (fase JSON, ya documentada en kiro-cli-nas):
   - `mcp.json` (command/args/env) + el patrón limpio: `mcp_tools/*.json` + `mcp-build`
     (jq) + `permissions.yaml` (allow/ask/deny por capacidad) + steering + wrapper que
     inyecta secretos. Kiro CLI V3 usa permissions.yaml, no autoApprove.
3. **Checklist de construcción** — reutilizar el steering
   `nas-dotfiles/.kiro/steering/verificar-antes-de-entregar.md` (¿paquete en registro?
   ¿comando o módulo? ¿volumen tapa ruta? ¿permisos/UID? leer config completa).

---

## Plan cuando se retome (en chat nuevo)

1. **Leer a fondo el código real de referencia** (NO de memoria — solo vimos `server.py`):
   - `dmeiser/nextdns-mcp`: un `src/nextdns_mcp/tools/*.py` COMPLETO (ej. lists.py: ver cómo
     es `manageLists` público vs `_manage_lists_impl` puro), `client.py` (AccessControlledClient,
     create_nextdns_client), `openapi.py` (create_mcp_server, middleware), `config.py`, `coercion.py`.
   - El **SDK oficial de MCP** (modelcontextprotocol/python-sdk) y **FastMCP** (jlowin/fastmcp)
     como referencia canónica del framework — verificar contra la doc oficial, no de memoria.
2. **Decidir el caso de ejemplo**: construir un MCP mínimo propio que funcione (ej. un MCP
   de una API sencilla que el usuario quiera), aplicando el patrón de 2 capas desde el inicio.
3. **Escribir la guía** `construir-mcp/README.md` (anatomía + incorporación a Kiro + checklist).
4. **Construir el MCP de ejemplo** paso a paso, verificándolo en runtime (como se hizo con todo).
5. Opcional: una **plantilla/scaffold** reutilizable (estructura de carpetas + FastMCP básico +
   el patrón _impl/envoltorio + Dockerfile + mcp_tools.json de ejemplo).

## Decisiones / contexto ya conocido (no re-descubrir)

- El patrón de 2 capas (`_impl` + `mcp_server.tool()`) YA está verificado en nextdns-mcp
  (ver `../kiro-cli-nas/PROYECTO-PENDIENTE-nextdns-en-nas-agent.md`).
- La incorporación a Kiro (mcp_tools + mcp-build + permissions.yaml + steering + wrapper) YA
  está montada y documentada (`../kiro-cli-nas/`, `../rclone-mcp-control-total/`).
- Kiro CLI V3: permisos por `permissions.yaml` (allow/ask/deny), NO autoApprove del mcp.json.
- nextdns-mcp: Python 3.14 + FastMCP, stdio, config por env, NO está en PyPI (solo git/imagen).
- Respetar CONTRIBUTING de nas-dotfiles si el MCP se integra ahí; respetar estructura de
  Varios_tools (cada proyecto en su subcarpeta).

## Referencias

- Ejemplo real analizado: https://github.com/dmeiser/nextdns-mcp (Python/FastMCP)
- FastMCP: https://github.com/jlowin/fastmcp
- SDK oficial MCP: https://github.com/modelcontextprotocol/python-sdk
- Spec MCP: https://modelcontextprotocol.io
- Integración a Kiro (ya hecha): `../kiro-cli-nas/`, `../rclone-mcp-control-total/`
- Checklist previo: `nas-dotfiles/.kiro/steering/verificar-antes-de-entregar.md`
