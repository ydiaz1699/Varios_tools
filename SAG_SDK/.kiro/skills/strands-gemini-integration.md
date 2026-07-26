# Skill: Strands Agents SDK + Google Gemini Integration

## Descripción
Guía completa para incorporar Strands Agents SDK (TypeScript) con el provider de Google Gemini en cualquier proyecto. Esta skill proporciona toda la información necesaria para que un LLM pueda integrar agentes autónomos con tool-use en cualquier tipo de proyecto.

## Cuándo usar esta skill
- Cuando el usuario quiere agregar un agente autónomo a un proyecto existente
- Cuando se necesita integrar herramientas (tools) con un LLM de forma programática
- Cuando se quiere usar Gemini como LLM barato con capacidad de tool-use
- Cuando se necesita conectar a un servidor MCP desde código
- Cuando se quiere crear un bot, CLI, o servicio que use IA con herramientas

## Fuentes oficiales
- Documentación: https://strandsagents.com/docs/user-guide/quickstart/typescript/
- GitHub: https://github.com/strands-agents/harness-sdk (monorepo actual)
- NPM: @strands-agents/sdk
- Modelos Google: https://strandsagents.com/docs/user-guide/concepts/model-providers/google/

---

## Instalación

### Dependencias base
```bash
npm install @strands-agents/sdk @google/genai zod
```

### Dependencias de desarrollo
```bash
npm install --save-dev @types/node typescript tsx
```

### Para usar con MCP servers
```bash
npm install @modelcontextprotocol/sdk
```

### Versiones compatibles (julio 2026)
- `@strands-agents/sdk`: ^1.11.x
- `@google/genai`: ^2.6.0
- `zod`: ^4.1.12 (IMPORTANTE: Strands SDK requiere Zod 4, NO Zod 3)
- `@modelcontextprotocol/sdk`: ^1.12.x
- Node.js: 20+

---

## Configuración del provider Google Gemini

### Variables de entorno
```env
GOOGLE_API_KEY=tu-api-key-de-google-ai-studio
```

Obtener en: https://aistudio.google.com/apikey

### Modelos disponibles (recomendados)
| Modelo | Caso de uso | Costo aprox |
|--------|------------|-------------|
| `gemini-2.5-flash` | Mejor balance rendimiento/costo | ~$0.15/1M input |
| `gemini-2.5-flash-lite` | Más barato posible | Menor que flash |
| `gemini-2.5-pro` | Razonamiento complejo | ~$1.25/1M input |
| `gemini-2.0-flash` | Velocidad máxima | Rápido y barato |

### Import y configuración
```typescript
import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,    // o apiKey directo
  modelId: 'gemini-2.5-flash',           // modelo a usar
  params: {
    temperature: 0.7,                     // creatividad (0-1)
    maxOutputTokens: 4096,                // max tokens de respuesta
    topP: 0.9,                            // nucleus sampling
    topK: 40,                             // top-k sampling
  },
})
```

---

## Crear un agente básico

```typescript
import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-2.5-flash',
})

const agent = new Agent({
  model,
  systemPrompt: 'Eres un asistente experto en...',
})

// Invocar
const result = await agent.invoke('Tu pregunta aquí')
console.log(result.lastMessage)
```

---

## Crear herramientas (tools)

Las herramientas se definen con Zod schemas para validación de tipos:

```typescript
import { tool } from '@strands-agents/sdk'
import { z } from 'zod'

const myTool = tool({
  name: 'nombre_herramienta',
  description: 'Descripción clara de qué hace la herramienta',
  inputSchema: z.object({
    param1: z.string().describe('Descripción del parámetro'),
    param2: z.number().optional().describe('Parámetro opcional'),
  }),
  callback: (input) => {
    // input está tipado según el schema
    // Lógica de la herramienta aquí
    return `Resultado: ${input.param1}`
  },
})

// Asignar al agente
const agent = new Agent({
  model,
  tools: [myTool],
})
```

### Herramientas asíncronas
```typescript
const asyncTool = tool({
  name: 'fetch_data',
  description: 'Obtiene datos de una API',
  inputSchema: z.object({
    url: z.string().url(),
  }),
  callback: async (input) => {
    const response = await fetch(input.url)
    const data = await response.json()
    return JSON.stringify(data)
  },
})
```

---

## Conectar a un servidor MCP

### Via stdio (el bot lanza el servidor como subproceso)
```typescript
import { Agent, McpClient } from '@strands-agents/sdk'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const mcpClient = new McpClient({
  transport: new StdioClientTransport({
    command: 'npx',
    args: ['tsx', 'ruta/al/servidor-mcp/index.ts'],
    env: {
      ...process.env,
      DATABASE_URL: 'mysql://...',
    },
  }),
})

const agent = new Agent({
  model,
  tools: [mcpClient],  // McpClient es un ToolProvider
})
```

### Via SSE (servidor ya corriendo)
```typescript
import { McpClient } from '@strands-agents/sdk'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

const mcpClient = new McpClient({
  transport: new SSEClientTransport(
    new URL('http://localhost:3100/sse')
  ),
})

const agent = new Agent({
  model,
  tools: [mcpClient],
})
```

### Cargar múltiples MCP servers desde config
```typescript
import { McpClient } from '@strands-agents/sdk'

// Desde objeto de configuración
const clients = await McpClient.loadServers({
  'mi-servidor': {
    command: 'npx',
    args: ['tsx', './mcp-server/index.ts'],
  },
  'otro-servidor': {
    url: 'http://localhost:8080/sse',
  },
})

const agent = new Agent({
  model,
  tools: clients,  // Array de McpClient
})
```

---

## Streaming de respuestas

```typescript
// Async iterator
for await (const event of agent.stream('Tu pregunta')) {
  if (event.type === 'modelStreamUpdateEvent') {
    // Chunk de texto parcial
    process.stdout.write(event.data ?? '')
  }
}
```

---

## Plugins y Hooks

```typescript
import { Agent, BeforeToolCallEvent, AfterToolCallEvent } from '@strands-agents/sdk'
import type { Plugin, LocalAgent } from '@strands-agents/sdk'

class MyPlugin implements Plugin {
  get name() { return 'my-plugin' }

  initAgent(agent: LocalAgent) {
    agent.addHook(BeforeToolCallEvent, (event) => {
      console.log(`Calling: ${event.toolUse.name}`)
    })
    agent.addHook(AfterToolCallEvent, (event) => {
      console.log(`Done: ${event.toolUse.name}`)
    })
  }
}

const agent = new Agent({
  model,
  plugins: [new MyPlugin()],
})
```

---

## Multi-Agent: Patrones de orquestación

### Agent-as-tool (un agente usa otro como herramienta)
```typescript
const researcher = new Agent({
  name: 'researcher',
  description: 'Busca información sobre un tema',
  model,
  systemPrompt: 'Eres un investigador experto.',
})

const writer = new Agent({
  model,
  tools: [researcher],
  systemPrompt: 'Usa el researcher para obtener datos y escribe un resumen.',
})
```

### Graph (ejecución secuencial con dependencias)
```typescript
import { Graph } from '@strands-agents/sdk/multiagent'

const graph = new Graph({
  nodes: [
    new Agent({ id: 'step1', model, systemPrompt: 'Paso 1...' }),
    new Agent({ id: 'step2', model, systemPrompt: 'Paso 2...' }),
    new Agent({ id: 'step3', model, systemPrompt: 'Paso 3...' }),
  ],
  edges: [['step1', 'step2'], ['step2', 'step3']],
})

const result = await graph.invoke('Ejecuta el pipeline')
```

### Swarm (routing dinámico entre agentes)
```typescript
import { Swarm } from '@strands-agents/sdk/multiagent'

const swarm = new Swarm({
  nodes: [
    new Agent({ id: 'triage', model, systemPrompt: 'Enruta al especialista.' }),
    new Agent({ id: 'billing', model, systemPrompt: 'Resuelve temas de facturación.' }),
    new Agent({ id: 'support', model, systemPrompt: 'Soporte técnico.' }),
  ],
  start: 'triage',
})
```

---

## Structured Output (respuestas tipadas)

```typescript
import { z } from 'zod'

const MovieSchema = z.object({
  title: z.string(),
  rating: z.number().min(1).max(10),
  genre: z.string(),
  summary: z.string(),
})

const result = await agent.structured_output(
  MovieSchema,
  'Analiza la película The Matrix'
)
// result está tipado como { title: string, rating: number, ... }
```

---

## package.json mínimo para un proyecto con Strands + Gemini

```json
{
  "name": "mi-agente",
  "type": "module",
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@strands-agents/sdk": "^1.11.0",
    "@google/genai": "^2.6.0",
    "zod": "^4.1.12"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "tsx": "^4.19.0",
    "typescript": "^5.7.0"
  }
}
```

### Si necesitas MCP, agregar:
```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.12.0"
  }
}
```

---

## tsconfig.json recomendado

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Patrones de integración por tipo de proyecto

### Bot de Telegram
```
Bot Framework (grammy/telegraf) → Strands Agent (Gemini) → Tools/MCP
```

### CLI tool
```
Commander/Inquirer → Strands Agent (Gemini) → Tools locales
```

### API REST/Backend
```
Express/Fastify endpoint → Strands Agent (Gemini) → Tools/MCP → Response
```

### IoT / Arduino / ESP32 (via bridge)
```
Dispositivo → MQTT/HTTP → Node.js Bridge → Strands Agent (Gemini) → Tools → Respuesta al dispositivo
```

### Cron job / Automatización
```
Scheduler (node-cron) → Strands Agent (Gemini) → Tools/MCP → Resultado
```

### Browser (client-side)
```
React/Vue/Svelte component → Strands Agent (Gemini) → Tools → UI update
```

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `peer zod@"^4.1.12"` | Zod 3 instalado | `npm install zod@^4.1.12` |
| `peerOptional @google/genai@"^2.6.0"` | Versión vieja de genai | `npm install @google/genai@^2.6.0` |
| `GOOGLE_API_KEY not set` | Falta la variable | Setear en .env o pasarla en `apiKey` |
| `Tool validation failed` | Schema de Zod no coincide | Verificar que el input match el schema |
| `MCP connection refused` | Servidor MCP no corre | Verificar que el MCP server esté activo |

---

## Notas para LLMs que lean esta skill

1. **Siempre usar `type: "module"`** en package.json (imports ESM)
2. **Zod 4 es obligatorio** — no usar Zod 3 con Strands SDK
3. **GoogleModel se importa de** `@strands-agents/sdk/models/google`
4. **McpClient se importa de** `@strands-agents/sdk` (no de otro paquete)
5. **StdioClientTransport** se importa de `@modelcontextprotocol/sdk/client/stdio.js`
6. **SSEClientTransport** se importa de `@modelcontextprotocol/sdk/client/sse.js`
7. El agente maneja el **loop de tool-use automáticamente** — no necesitas implementarlo
8. Para que el agente use herramientas, solo tienes que **describirlas bien** — Gemini decide cuándo usarlas
9. Los resultados de tools deben ser **strings** (o serializados a string)
10. El `systemPrompt` define el comportamiento — hazlo claro y específico


---

## Vended Tools (herramientas built-in del SDK)

El SDK incluye herramientas listas para usar:

```typescript
import { bash } from '@strands-agents/sdk/vended-tools/bash'
import { httpRequest } from '@strands-agents/sdk/vended-tools/http-request'
import { fileEditor } from '@strands-agents/sdk/vended-tools/file-editor'
import { notebook } from '@strands-agents/sdk/vended-tools/notebook'

const agent = new Agent({
  model,
  tools: [bash, httpRequest, fileEditor, notebook],
})
```

| Tool | Qué hace |
|------|----------|
| `bash` | Ejecuta comandos de shell |
| `httpRequest` | Hace HTTP requests (GET, POST, etc.) |
| `fileEditor` | Lee, escribe y edita archivos |
| `notebook` | Bloc de notas persistente para el agente |

---

## Conversation Management (historial)

### Acceder a mensajes previos
```typescript
const result = await agent.invoke('Hola')
console.log(agent.messages) // Array de mensajes del conversation

// Invocar de nuevo — mantiene contexto
const result2 = await agent.invoke('¿Qué te dije antes?')
```

### Sliding Window (limitar contexto)
```typescript
const agent = new Agent({
  model,
  conversationManager: {
    strategy: 'slidingWindow',
    windowSize: 20, // Mantener últimos 20 mensajes
  },
})
```

### Summarization (resumir historial largo)
```typescript
const agent = new Agent({
  model,
  conversationManager: {
    strategy: 'summarization',
    maxMessages: 50, // Cuando supere 50, resume los viejos
  },
})
```

### Reiniciar conversación
```typescript
agent.messages = [] // Limpiar historial
```

---

## Session Persistence (guardar estado)

### Guardar en archivo
```typescript
import { FileSessionStore } from '@strands-agents/sdk/sessions'

const agent = new Agent({
  model,
  sessionStore: new FileSessionStore({ directory: './sessions' }),
  sessionId: 'user-123', // Identificador único de la sesión
})
```

### Guardar en S3
```typescript
import { S3SessionStore } from '@strands-agents/sdk/sessions'

const agent = new Agent({
  model,
  sessionStore: new S3SessionStore({
    bucket: 'my-agent-sessions',
    prefix: 'sessions/',
    region: 'us-east-1',
  }),
  sessionId: 'user-123',
})
```

---

## Cancellation (AbortSignal)

```typescript
const controller = new AbortController()

// Cancelar después de 30 segundos
setTimeout(() => controller.abort(), 30_000)

try {
  const result = await agent.invoke('Tarea larga...', {
    signal: controller.signal,
  })
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('Invocación cancelada')
  }
}
```

---

## Error Handling

```typescript
import { ModelThrottledException } from '@strands-agents/sdk'

try {
  const result = await agent.invoke('...')
} catch (error) {
  if (error instanceof ModelThrottledException) {
    // Rate limit — esperar y reintentar
    console.log('Rate limited, esperando...')
    await new Promise(r => setTimeout(r, 5000))
    // Reintentar...
  } else {
    console.error('Error:', error.message)
  }
}
```

### Manejo de errores en tools
```typescript
const safeTool = tool({
  name: 'safe_operation',
  description: 'Operación que puede fallar',
  inputSchema: z.object({ id: z.string() }),
  callback: async (input) => {
    try {
      const result = await riskyOperation(input.id)
      return JSON.stringify(result)
    } catch (error) {
      // Devolver error como string — el agente lo interpreta
      return `ERROR: ${error.message}. No se pudo completar la operación.`
    }
  },
})
```

---

## Observability (Traces & Metrics)

### Acceder a métricas de ejecución
```typescript
const result = await agent.invoke('...')

// Métricas disponibles en el resultado
console.log(result.metrics) // { inputTokens, outputTokens, duration, toolCalls }
```

### OpenTelemetry integration
```typescript
import { OtelPlugin } from '@strands-agents/sdk/plugins/otel'

const agent = new Agent({
  model,
  plugins: [new OtelPlugin({
    serviceName: 'my-agent',
    endpoint: 'http://localhost:4318/v1/traces',
  })],
})
```

---

## Otros Model Providers (no solo Gemini)

### OpenAI / GPT
```typescript
import { OpenAIModel } from '@strands-agents/sdk/models/openai'

const model = new OpenAIModel({
  apiKey: process.env.OPENAI_API_KEY,
  modelId: 'gpt-4o',  // o 'gpt-4o-mini' para más barato
})
```

### Amazon Bedrock (Claude)
```typescript
import { BedrockModel } from '@strands-agents/sdk/models/bedrock'

const model = new BedrockModel({
  modelId: 'global.anthropic.claude-sonnet-4-6',
  region: 'us-east-1',
})
// Requiere AWS credentials configuradas
```

### Anthropic directo
```typescript
import { AnthropicModel } from '@strands-agents/sdk/models/anthropic'

const model = new AnthropicModel({
  apiKey: process.env.ANTHROPIC_API_KEY,
  modelId: 'claude-sonnet-4-20250514',
})
```

### Comparación de providers
| Provider | Modelo recomendado | Costo/1M input | Tool-use |
|----------|-------------------|----------------|----------|
| Google | gemini-2.5-flash | ~$0.15 | Excelente |
| OpenAI | gpt-4o-mini | ~$0.15 | Excelente |
| Bedrock | claude-sonnet-4 | ~$3.00 | El mejor |
| Anthropic | claude-sonnet-4 | ~$3.00 | El mejor |

---

## Patrón completo: IoT Bridge (Arduino/ESP32 → Agente)

Para dispositivos que no pueden correr Node.js directamente:

```typescript
/**
 * Bridge: Dispositivo IoT envía datos via MQTT/HTTP
 * → Node.js recibe → Strands Agent procesa → Responde al dispositivo
 */
import { Agent, tool } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { z } from 'zod'
import express from 'express'

// Tool que controla el dispositivo
const controlDevice = tool({
  name: 'control_device',
  description: 'Envía un comando al dispositivo IoT',
  inputSchema: z.object({
    deviceId: z.string(),
    action: z.enum(['on', 'off', 'set_value']),
    value: z.number().optional(),
  }),
  callback: async (input) => {
    // Enviar comando via MQTT, HTTP, o serial
    await sendToDevice(input.deviceId, input.action, input.value)
    return `Comando ${input.action} enviado a ${input.deviceId}`
  },
})

const readSensor = tool({
  name: 'read_sensor',
  description: 'Lee el valor actual de un sensor',
  inputSchema: z.object({
    sensorId: z.string(),
  }),
  callback: async (input) => {
    const value = await getSensorValue(input.sensorId)
    return `Sensor ${input.sensorId}: ${value}`
  },
})

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-2.5-flash',
})

const agent = new Agent({
  model,
  tools: [controlDevice, readSensor],
  systemPrompt: 'Controlas dispositivos IoT. Responde con acciones concretas.',
})

// HTTP endpoint que recibe datos del ESP32
const app = express()
app.post('/iot/command', async (req, res) => {
  const { message } = req.body // ej: "enciende la luz del salón"
  const result = await agent.invoke(message)
  res.json({ response: result.lastMessage })
})
```

---

## Deshabilitando output de consola

Por defecto Strands imprime el razonamiento en consola. Para desactivar:

```typescript
const agent = new Agent({
  model,
  printer: false, // Sin output a consola
})
```

---

## Resumen de imports principales

```typescript
// Core
import { Agent, tool, McpClient } from '@strands-agents/sdk'

// Models
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { OpenAIModel } from '@strands-agents/sdk/models/openai'
import { BedrockModel } from '@strands-agents/sdk/models/bedrock'
import { AnthropicModel } from '@strands-agents/sdk/models/anthropic'

// Multi-agent
import { Graph, Swarm } from '@strands-agents/sdk/multiagent'

// Vended tools
import { bash } from '@strands-agents/sdk/vended-tools/bash'
import { httpRequest } from '@strands-agents/sdk/vended-tools/http-request'
import { fileEditor } from '@strands-agents/sdk/vended-tools/file-editor'

// MCP transports
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

// Events (para plugins)
import { BeforeToolCallEvent, AfterToolCallEvent } from '@strands-agents/sdk'

// Types
import type { Plugin, LocalAgent } from '@strands-agents/sdk'
```
