# PROYECTO PENDIENTE — NextDNS como tools nativas de nas-agent (Strands SDK)

> **Estado:** anotado, NO implementado. Para retomar en un chat nuevo.
> **Fecha:** 2026-09-23

## Objetivo

Hacer que **NextDNS sea portable entre agentes**: que además de Kiro CLI (que lo usa
como MCP, ya funcionando), el **nas-agent propio (Strands SDK)** de nas-dotfiles pueda
controlar NextDNS **importando el código directamente** (sin MCP, sin stdio), como una
tool nativa más — al lado de sus tools de docker/backup/discovery.

## Por qué es posible (hallazgo verificado)

El código fuente de `dmeiser/nextdns-mcp` está separado en **dos capas**:

- **Capa MCP** (`server.py`): envuelve las tools con `mcp_server.tool()(...)` para stdio/HTTP.
- **Capa de lógica pura** (importable, SIN dependencia de MCP):
  - Funciones `_impl`: `_manage_lists_impl`, `_manage_profiles_impl`, `_manage_settings_impl`,
    `_manage_logs_impl`, `_manage_rewrites_impl`, `_query_analytics_impl`,
    `_plot_analytics_series_impl`, `_dohLookup_impl`.
  - Cliente HTTP: `from nextdns_mcp.client import create_nextdns_client, AccessControlledClient`.

Ambos consumen la MISMA lógica → NO hay que duplicar. Kiro CLI usa la capa MCP; nas-agent
usaría la capa `_impl`/`client`.

## Plan cuando se retome

1. **Leer a fondo** el código real del MCP (firmas exactas, pueden cambiar entre versiones
   porque los `_impl` son API "privada"):
   - `src/nextdns_mcp/tools/{lists,profiles,settings,logs,rewrites,analytics,plots,doh}.py`
   - `src/nextdns_mcp/client.py` (AccessControlledClient, create_nextdns_client)
   - `src/nextdns_mcp/config.py` (get_api_key, NEXTDNS_READABLE/WRITABLE_PROFILES)
2. **Instalar/vendorizar** `nextdns-mcp` como dependencia del nas-agent (git dependency o vendor).
3. **Escribir `agent/tools/nextdns_tools.py`** siguiendo el CONTRIBUTING.md de nas-dotfiles:
   - `@tool` de Strands (docstring = descripción, type hints = schema, return str, "ERROR: ..." en fallos).
   - Usar el patrón `_shell`/`ToolResult`/`readonly_guard` del framework.
   - Multi-cuenta: cada persona su API key (leer de credenciales al estilo nas-runtime-secrets).
   - Tools destructivas (bloquear/borrar) → añadir a `_DESTRUCTIVE_TOOLS` (modo readonly).
4. **Exportar en `agent/tools/__init__.py`** (`ALL_TOOLS`).
5. **Documentar en `agent/nas_agent.py`** (system prompt) y `agent/README.md`.
6. Opcional: plugin `agent/plugins/nextdns_plugin.py` si se quieren tareas periódicas
   (ej. reportes de analítica) o reacción a eventos MQTT.

## Decisiones ya tomadas (no re-discutir)

- **Multi-cuenta** = una cuenta NextDNS/API key por persona (perfiles infinix=2511f5,
  papa=2f6df5), para no agotar el límite de consultas del plan gratuito (es por cuenta).
- **NO Docker socket** (rompe principio anti-socket de nas-dotfiles).
- **Bloquear un servicio** (YouTube) = `manageLists` con `list_type=parental_services`;
  si existe pero `active:false`, `operation=update` para activarlo.
- El MCP para **Kiro CLI ya está montado y funcionando** — este proyecto NO lo reemplaza,
  lo COMPLEMENTA (Kiro CLI = MCP; nas-agent = import directo).

## Riesgos / cuidados

- Las funciones `_impl` son API interna del paquete → pueden cambiar entre versiones.
  Pinear la versión/commit del `nextdns-mcp` y revisar al actualizar.
- Respetar el CONTRIBUTING de nas-dotfiles (safe_run, ToolResult, no subprocess directo,
  secretos en .env + ${VAR}, español en UI).

## Referencias

- MCP funcionando (Kiro CLI): `./nextdns-multicuenta.md`
- Código fuente: https://github.com/dmeiser/nextdns-mcp (rama main, src/nextdns_mcp/)
- Guía de tools del agente: nas-dotfiles `CONTRIBUTING.md` sección 2 ("Nueva tool para el agente Python")
- nas-agent: nas-dotfiles `agent/README.md`, `agent/nas_agent.py`
