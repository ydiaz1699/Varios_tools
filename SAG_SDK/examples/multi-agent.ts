/**
 * Ejemplo: Multi-Agent con Strands (Graph + Swarm)
 * 
 * Setup:
 *   npm install @strands-agents/sdk @google/genai zod
 *   export GOOGLE_API_KEY="tu-api-key"
 */

import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { Graph, Swarm } from '@strands-agents/sdk/multiagent'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
})

// --- PATRÓN 1: Agent-as-tool ---
const researcher = new Agent({
  name: 'researcher',
  description: 'Investiga un tema y devuelve hechos',
  model,
  systemPrompt: 'Eres un investigador. Encuentra datos.',
})

const writer = new Agent({
  model,
  tools: [researcher],
  systemPrompt: 'Usa el researcher y escribe un resumen.',
})

// --- PATRÓN 2: Graph (pipeline secuencial) ---
const graph = new Graph({
  nodes: [
    new Agent({ id: 'analyze', model, systemPrompt: 'Analiza.' }),
    new Agent({ id: 'summarize', model, systemPrompt: 'Resume.' }),
  ],
  edges: [['analyze', 'summarize']],
})

// --- PATRÓN 3: Swarm (routing dinámico) ---
const swarm = new Swarm({
  nodes: [
    new Agent({ id: 'triage', model, systemPrompt: 'Enruta.' }),
    new Agent({ id: 'tech', model, systemPrompt: 'Soporte técnico.' }),
    new Agent({ id: 'billing', model, systemPrompt: 'Facturación.' }),
  ],
  start: 'triage',
})

const result = await writer.invoke('Escribe sobre agentes IA')
console.log(result.lastMessage)
