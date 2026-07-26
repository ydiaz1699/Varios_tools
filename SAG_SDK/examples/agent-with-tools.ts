/**
 * Ejemplo: Agente con herramientas custom
 * 
 * Demuestra cómo crear tools tipadas con Zod y asignarlas al agente.
 * El agente decide autónomamente cuándo usar cada herramienta.
 * 
 * Setup:
 *   npm install @strands-agents/sdk @google/genai zod
 *   export GOOGLE_API_KEY="tu-api-key"
 */

import { Agent, tool } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { z } from 'zod'

// --- TOOLS ---

const getWeather = tool({
  name: 'get_weather',
  description: 'Obtiene el clima actual de una ciudad',
  inputSchema: z.object({
    city: z.string().describe('Nombre de la ciudad'),
    country: z.string().optional().describe('Código de país (ej: US, ES, AR)'),
  }),
  callback: async (input) => {
    // Aquí iría tu lógica real (API call, etc.)
    return `El clima en ${input.city} es 22°C, parcialmente nublado.`
  },
})

const calculateDistance = tool({
  name: 'calculate_distance',
  description: 'Calcula la distancia entre dos puntos geográficos',
  inputSchema: z.object({
    from: z.string().describe('Ciudad de origen'),
    to: z.string().describe('Ciudad de destino'),
  }),
  callback: (input) => {
    // Ejemplo simplificado
    return `La distancia entre ${input.from} y ${input.to} es aproximadamente 500 km.`
  },
})

const searchDatabase = tool({
  name: 'search_database',
  description: 'Busca registros en la base de datos local',
  inputSchema: z.object({
    query: z.string().describe('Término de búsqueda'),
    limit: z.number().default(10).describe('Máximo de resultados'),
  }),
  callback: async (input) => {
    // Tu lógica de DB aquí
    return JSON.stringify({ results: [], total: 0, query: input.query })
  },
})

// --- AGENT ---

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-2.5-flash',
  params: { temperature: 0.3 },
})

const agent = new Agent({
  model,
  tools: [getWeather, calculateDistance, searchDatabase],
  systemPrompt: `Eres un asistente que puede consultar el clima, calcular distancias y buscar en la base de datos. 
Usa las herramientas cuando sea necesario para responder de forma precisa.`,
})

// El agente decide qué tool usar basándose en la pregunta
const result = await agent.invoke('¿Qué clima hace en Madrid y qué tan lejos está de Barcelona?')
console.log(result.lastMessage)
