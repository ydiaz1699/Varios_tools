# Herramientas con Zod (TypeScript)

> **Cuándo usar este bloque:** Cuando necesitas crear herramientas (tools) para un agente TypeScript. Las tools se definen con la función `tool()` usando Zod para el schema de entrada — pueden ser síncronas o asíncronas.

---

## Tool básico con Zod

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
    return `Resultado: ${input.param1}`
  },
})

const agent = new Agent({
  model,
  tools: [myTool],
})
```

---

## inputSchema con Zod

El schema define los parámetros que el LLM puede pasar a la tool:

```typescript
inputSchema: z.object({
  // String requerido
  name: z.string().describe('Nombre del servicio'),

  // Número con default
  timeout: z.number().default(30).describe('Timeout en segundos'),

  // Enum
  action: z.enum(['start', 'stop', 'restart']).describe('Acción a ejecutar'),

  // Opcional
  verbose: z.boolean().optional().describe('Mostrar detalle'),

  // Array
  tags: z.array(z.string()).describe('Lista de tags'),
})
```

**IMPORTANTE:** Usar Zod 4 (`^4.1.12`). Zod 3 no es compatible con Strands SDK.

---

## Tool con callback síncrono

```typescript
const calculator = tool({
  name: 'calculator',
  description: 'Realiza operaciones matemáticas básicas',
  inputSchema: z.object({
    expression: z.string().describe('Expresión matemática (ej: "2 + 2")'),
  }),
  callback: (input) => {
    try {
      const result = eval(input.expression)  // Solo para ejemplo
      return `Resultado: ${result}`
    } catch (e) {
      return `ERROR: Expresión inválida`
    }
  },
})
```

---

## Tool con callback asíncrono

```typescript
const fetchData = tool({
  name: 'fetch_data',
  description: 'Obtiene datos de una API',
  inputSchema: z.object({
    url: z.string().url().describe('URL de la API'),
  }),
  callback: async (input) => {
    const response = await fetch(input.url)
    const data = await response.json()
    return JSON.stringify(data, null, 2)
  },
})
```

---

## Múltiples tools en un agente

```typescript
import { Agent, tool } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { z } from 'zod'

const listFiles = tool({
  name: 'list_files',
  description: 'Lista archivos en un directorio',
  inputSchema: z.object({
    path: z.string().describe('Ruta del directorio'),
  }),
  callback: async (input) => {
    const { readdir } = await import('fs/promises')
    const files = await readdir(input.path)
    return files.join('\n')
  },
})

const readFile = tool({
  name: 'read_file',
  description: 'Lee el contenido de un archivo',
  inputSchema: z.object({
    path: z.string().describe('Ruta al archivo'),
  }),
  callback: async (input) => {
    const { readFile } = await import('fs/promises')
    return await readFile(input.path, 'utf-8')
  },
})

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-2.5-flash',
})

const agent = new Agent({
  model,
  tools: [listFiles, readFile],
  systemPrompt: 'Eres un asistente que puede explorar el filesystem.',
})
```

---

## Vended Tools (tools pre-hechas del SDK)

```typescript
import { bash } from '@strands-agents/sdk/vended-tools/bash'
import { httpRequest } from '@strands-agents/sdk/vended-tools/http-request'
import { fileEditor } from '@strands-agents/sdk/vended-tools/file-editor'
import { notebook } from '@strands-agents/sdk/vended-tools/notebook'

const agent = new Agent({ model, tools: [bash, httpRequest, fileEditor, notebook] })
```

---

## Notas importantes

- La `description` es lo que el LLM lee para decidir cuándo usar la tool
- Describir claramente qué hace — si la descripción es mala, no se ejecuta
- Los resultados deben ser strings (o serializados a string)
- El callback puede ser sync o async
- Zod 4 es obligatorio (`npm install zod@^4.1.12`)
- `tool()` se importa de `@strands-agents/sdk`
