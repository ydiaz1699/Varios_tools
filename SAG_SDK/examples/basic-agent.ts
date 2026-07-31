/**
 * Ejemplo: Agente básico con Strands + Gemini
 * 
 * Setup:
 *   npm install @strands-agents/sdk @google/genai zod
 *   export GOOGLE_API_KEY="tu-api-key"
 */

import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
  params: {
    temperature: 0.7,
    maxOutputTokens: 2048,
  },
})

const agent = new Agent({
  model,
  systemPrompt: 'Eres un asistente útil y conciso. Responde en español.',
})

// Uso simple
const result = await agent.invoke('¿Qué es TypeScript y por qué es útil?')
console.log(result.lastMessage)
