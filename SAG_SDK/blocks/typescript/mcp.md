# Conexión MCP (TypeScript)

> **Cuándo usar este bloque:** Cuando necesitas conectar tu agente TypeScript a un servidor MCP (Model Context Protocol) — ya sea via stdio (lanzar el server como proceso hijo) o SSE (conectar a un server ya corriendo en red).

---

## Instalación

```bash
npm install @strands-agents/sdk @modelcontextprotocol/sdk
```

Versiones compatibles:
- `@modelcontextprotocol/sdk`: ^1.12.x

---

## Conexión via stdio (lanzar server como subproceso)

El transporte stdio es ideal cuando el servidor MCP es un script local que quieres lanzar como proceso hijo del agente:

```typescript
import { Agent, McpClient } from '@strands-agents/sdk'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const mcpClient = new McpClient({
  transport: new StdioClientTransport({
    command: 'npx',
    args: ['tsx', 'ruta/al/servidor-mcp/index.ts'],
    env: { ...process.env, DATABASE_URL: 'mysql://...' },
  }),
})

const agent = new Agent({ model, tools: [mcpClient] })
const result = await agent.invoke('Lista las tablas de la base de datos')
```

### Parámetros de StdioClientTransport

- `command`: El ejecutable a lanzar (`npx`, `node`, `python`, etc.)
- `args`: Argumentos del comando
- `env`: Variables de entorno para el subproceso (pasar `...process.env` + las extras)

---

## Conexión via SSE (servidor ya corriendo)

El transporte SSE es ideal cuando el servidor MCP ya está corriendo como servicio en la red:

```typescript
import { Agent, McpClient } from '@strands-agents/sdk'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

const mcpClient = new McpClient({
  transport: new SSEClientTransport(new URL('http://localhost:3100/sse')),
})

const agent = new Agent({ model, tools: [mcpClient] })
const result = await agent.invoke('Ejecuta la query...')
```

---

## McpClient como tool del agente

El `McpClient` se pasa directamente en el array de `tools`. El agente descubre automáticamente las herramientas que expone el servidor MCP:

```typescript
import { Agent, McpClient } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
})

// MCP server que expone herramientas de base de datos
const dbMcp = new McpClient({
  transport: new StdioClientTransport({
    command: 'npx',
    args: ['tsx', './mcp-servers/db-server.ts'],
    env: { ...process.env },
  }),
})

// MCP server que expone herramientas de filesystem
const fsMcp = new McpClient({
  transport: new SSEClientTransport(new URL('http://localhost:3200/sse')),
})

// El agente tiene acceso a TODAS las tools de ambos servers
const agent = new Agent({
  model,
  tools: [dbMcp, fsMcp],
  systemPrompt: 'Eres un asistente con acceso a DB y filesystem.',
})
```

---

## Imports clave

```typescript
// McpClient del SDK de Strands
import { McpClient } from '@strands-agents/sdk'

// Transportes del SDK de MCP
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'
```

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `MCP connection refused` | Server MCP no está corriendo | Verificar que el MCP esté activo |
| `Cannot find module` | Ruta incorrecta al server | Verificar `args` en StdioClientTransport |
| `ENOENT` | Comando no encontrado | Verificar que `command` existe en PATH |

---

## Notas importantes

- `McpClient` se importa de `@strands-agents/sdk`
- `StdioClientTransport` de `@modelcontextprotocol/sdk/client/stdio.js`
- `SSEClientTransport` de `@modelcontextprotocol/sdk/client/sse.js`
- Un agente puede tener múltiples McpClients (cada uno expone sus tools)
- El agente descubre las tools del MCP server automáticamente
