# HALLAZGO — APIs de despliegue de workflows (n8n / Node-RED / Flowise)

> **Fecha:** 2026-09-25 · **Estado:** verificado contra docs oficiales.
> **Relación:** insumo para el **Nivel 2** del `PLAN-mcp-indexador-nodos.md` (índice + CREAR).

---

## El problema que resuelve

Idea original del usuario (ydiaz1699): los MCP del mercado para **Flowise/Node-RED**
pueden GENERAR el JSON del workflow, pero **no lo importan/despliegan** en la instancia
para ejecutarlo (a diferencia de n8n, cuyo `n8n-mcp` sí lo crea directo vía API). La
hipótesis era usar automatización de navegador (chrome-devtools-mcp / WebMCP) para que
el agente hiciera el "importar" en la UI.

## Conclusión (verificada): NO hace falta el navegador

**Node-RED y Flowise SÍ tienen API REST para crear/desplegar workflows**, igual que n8n.
La brecha "genero pero no despliego" se cierra con la **API de cada plataforma**, que es
mucho más fiable que arrastrar nodos en la UI por automatización de navegador (frágil,
depende de la UI, consume tokens en screenshots). El navegador solo tendría sentido para
webs **sin** API — no es el caso aquí.

## Las 3 APIs de despliegue

| Plataforma | Endpoint de creación/despliegue | Auth | Fuente |
|---|---|---|---|
| **n8n** | (ya lo usa `n8n-mcp`: `n8n_create_workflow` vía API REST) | API key REST (Settings → n8n API) | docs.n8n.io |
| **Node-RED** | `POST /flows` (Admin HTTP API) — acepta el flow JSON completo | según settings (admin auth) | nodered.org/docs/api/admin/methods/post/flows |
| **Flowise** | `POST /api/v1/chatflows` | `Authorization: Bearer <token>` | docs.flowiseai.com/api-reference/chatflows |

Ejemplos verificados:
```bash
# Node-RED — desplegar un flow completo
curl -X POST http://localhost:1880/flows \
  -H "Content-Type: application/json" \
  -H "Node-RED-API-Version: v2" \
  --data "@myflow.json"
# Cabeceras útiles: 'Node-RED-Deployment-Type: nodes' evita reiniciar nodos sin cambios;
# conservar 'rev' hace que rechace un edit obsoleto con HTTP 409.

# Flowise — crear un chatflow
curl -X POST http://<host>:3000/api/v1/chatflows \
  -H "Authorization: Bearer <FLOWISE_API_KEY>" \
  -H "Content-Type: application/json" \
  --data "@chatflow.json"
```

> Verificar la ruta/campos exactos contra la doc de la VERSIÓN instalada antes de construir
> (regla del steering `verificar-antes-de-entregar`): Flowise y Node-RED cambian entre
> versiones. No dar por buenos estos comandos sin confirmarlos en la instancia real.

## Qué significa para el MCP indexador (Nivel 2)

- El **Nivel 2** ("índice + crear") es viable para Node-RED y Flowise **sin navegador**:
  el MCP genera el flow (con el conocimiento del índice, Nivel 1) y lo despliega con un
  `POST` a la API de la plataforma — exactamente el patrón de `n8n_create_workflow`.
- Por tanto, la tool de "crear" del indexador (ej. `nodered_deploy_flow`,
  `flowise_create_chatflow`) debe llamar a estas APIs, NO automatizar la UI.
- Sigue aplicando: empezar por **Nivel 1** (índice, genera y el usuario pega), y añadir
  Nivel 2 (crear vía API) cuando el índice funcione. Las tools de escritura → `ask` en
  `permissions.yaml`.

## Descartado: chrome-devtools-mcp / WebMCP para ESTE objetivo

- **chrome-devtools-mcp**: MCP válido y útil, pero para debug/performance web y
  automatizar webs SIN API — NO como forma de crear workflows (la API es superior).
  Catalogado aparte en `tool_catalog/entries/chrome-devtools-mcp.md`.
- **WebMCP**: es un ESTÁNDAR EN BORRADOR (W3C) para que una web exponga SUS PROPIAS tools
  a un agente — requiere que la web lo implemente (Flowise/Node-RED NO lo hacen) y no está
  en producción. No sirve para controlar webs ajenas. Catalogado como tendencia futura.

## Referencias
- Node-RED Admin API: https://nodered.org/docs/api/admin/methods/post/flows
- Flowise Chatflows API: https://docs.flowiseai.com/api-reference/chatflows
- Plan del indexador: `./PLAN-mcp-indexador-nodos.md` (Nivel 2)
- Fichas de los recursos de navegador: `../tool_catalog/entries/chrome-devtools-mcp.md`, `../tool_catalog/entries/webmcp.md`
