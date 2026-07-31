/**
 * Ejemplo: Agente conectado a un MCP Server
 * 
 * Demuestra cómo conectar un agente Strands a un servidor MCP externo
 * que expone herramientas. El agente puede usar todas las tools del MCP.
 * 
 * Setup:
 *   npm install @strands-agents/sdk @google/genai @modelcontextprotocol/sdk zod
 *   export GOOGLE_API_KEY="tu-api-key"
 */

import { Agent, McpClient } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

// --- OPCIÓN A: stdio (lanza el MCP server como subproceso) ---

const mcpClientStdio = new McpClient({
  transport: new StdioClientTransport({
    command: 'npx',
    args: ['tsx', './mi-mcp-server/src/index.ts'],
    env: {
      ...process.env,
      // Variables que necesite tu MCP server
      DATABASE_URL: 'mysql://root:pass@localhost:3306/mydb',
    },
  }),
})

// --- OPCIÓN B: SSE (MCP server ya corriendo) ---
// import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'
// const mcpClientSSE = new McpClient({
//   transport: new SSEClientTransport(new URL('http://localhost:3100/sse')),
// })

// --- OPCIÓN C: Cargar desde config (múltiples servers) ---
// const clients = await McpClient.loadServers({
//   'server1': { command: 'npx', args: ['tsx', './server1/index.ts'] },
//   'server2': { url: 'http://localhost:8080/sse' },
// })

// --- AGENT ---

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
})

const agent = new Agent({
  model,
  tools: [mcpClientStdio],  // El MCP client actúa como ToolProvider
  systemPrompt: 'Eres un asistente con acceso a herramientas externas vía MCP.',
})

const result = await agent.invoke('Lista los archivos en la carpeta raíz')
console.log(result.lastMessage)

// Cleanup
await mcpClientStdio.disconnect()
