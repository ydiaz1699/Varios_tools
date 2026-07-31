# Multi-Agent (TypeScript)

> **Cuándo usar este bloque:** Cuando necesitas coordinar múltiples agentes — ya sea como herramientas entre sí (Agent-as-tool), en pipelines secuenciales (Graph), o con routing dinámico (Swarm).

---

## Patrón 1: Agent-as-tool

Un agente puede usar a otro agente como si fuera una herramienta. Ideal para separar responsabilidades:

```typescript
import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
})

// Agente especializado en investigación
const researcher = new Agent({
  name: 'researcher',
  description: 'Busca información sobre un tema',
  model,
  systemPrompt: 'Eres un investigador experto. Busca y sintetiza información.',
})

// Agente principal que usa al researcher como tool
const writer = new Agent({
  model,
  tools: [researcher],
  systemPrompt: 'Usa el researcher para obtener datos y escribe un resumen claro.',
})

const result = await writer.invoke('Escribe un resumen sobre Kubernetes')
console.log(result.lastMessage)
```

**Cómo funciona:** El agente `writer` puede invocar al agente `researcher` como si fuera una tool. El `name` y `description` del sub-agente son lo que el LLM lee para decidir cuándo usarlo.

---

## Patrón 2: Graph (pipeline secuencial)

Ejecuta agentes en un orden definido por edges (aristas). Ideal para pipelines multi-paso:

```typescript
import { Agent } from '@strands-agents/sdk'
import { Graph } from '@strands-agents/sdk/multiagent'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
})

const graph = new Graph({
  nodes: [
    new Agent({
      id: 'step1',
      model,
      systemPrompt: 'Analiza el input y extrae los puntos clave.',
    }),
    new Agent({
      id: 'step2',
      model,
      systemPrompt: 'Toma los puntos clave y redacta un resumen ejecutivo.',
    }),
    new Agent({
      id: 'step3',
      model,
      systemPrompt: 'Revisa el resumen y sugiere mejoras.',
    }),
  ],
  edges: [
    ['step1', 'step2'],
    ['step2', 'step3'],
  ],
})

const result = await graph.invoke('Analiza este reporte de ventas Q3...')
console.log(result.lastMessage)
```

**Cómo funciona:** El output de cada nodo se pasa como input al siguiente según las edges. Es un DAG (Directed Acyclic Graph).

---

## Patrón 3: Swarm (routing dinámico)

Un agente de triage decide a qué especialista enviar cada request. Ideal para sistemas de soporte o routing:

```typescript
import { Agent } from '@strands-agents/sdk'
import { Swarm } from '@strands-agents/sdk/multiagent'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
})

const swarm = new Swarm({
  nodes: [
    new Agent({
      id: 'triage',
      model,
      systemPrompt: `Eres un router. Analiza el mensaje del usuario y decide:
        - Si es sobre facturación → transfiere a "billing"
        - Si es sobre soporte técnico → transfiere a "support"
        Responde SOLO con el ID del agente destino.`,
    }),
    new Agent({
      id: 'billing',
      model,
      systemPrompt: 'Eres un especialista en facturación. Ayuda con cobros, facturas y pagos.',
    }),
    new Agent({
      id: 'support',
      model,
      systemPrompt: 'Eres un especialista en soporte técnico. Diagnostica y resuelve problemas.',
    }),
  ],
  start: 'triage',
})

const result = await swarm.invoke('Mi factura del mes pasado tiene un error')
console.log(result.lastMessage)
```

**Cómo funciona:** El nodo `start` recibe el input inicial y decide a qué otro nodo transferir el control. El routing es dinámico (el LLM decide).

---

## Comparación de patrones

| Patrón | Caso de uso | Coordinación |
|--------|------------|:------------:|
| **Agent-as-tool** | Un agente necesita consultar a otro | Manual (el LLM decide) |
| **Graph** | Pipeline fijo de N pasos | Secuencial por edges |
| **Swarm** | Routing dinámico a especialistas | LLM de triage decide |

---

## Imports necesarios

```typescript
// Core
import { Agent } from '@strands-agents/sdk'

// Multi-agent
import { Graph, Swarm } from '@strands-agents/sdk/multiagent'
```

---

## Notas importantes

- `Graph` y `Swarm` se importan de `@strands-agents/sdk/multiagent`
- Agent-as-tool no requiere imports extra — solo pasar un Agent como tool
- El `name` y `description` son obligatorios para un agente usado como tool
- En Graph, el `id` de cada agente debe ser único
- En Swarm, el campo `start` indica qué nodo recibe el input inicial
