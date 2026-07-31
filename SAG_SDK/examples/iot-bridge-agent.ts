/**
 * Ejemplo: IoT Bridge — ESP32/Arduino → Strands Agent → Control de dispositivos
 * 
 * El dispositivo envía datos via HTTP al bridge Node.js.
 * El agente Strands interpreta el mensaje y ejecuta acciones.
 * 
 * Setup:
 *   npm install @strands-agents/sdk @google/genai zod express
 *   npm install --save-dev @types/express
 *   export GOOGLE_API_KEY="tu-api-key"
 * 
 * Desde el ESP32 (ejemplo Arduino):
 *   HTTPClient http;
 *   http.begin("http://tu-server:3000/iot/command");
 *   http.addHeader("Content-Type", "application/json");
 *   http.POST("{\"message\": \"enciende la luz\", \"deviceId\": \"esp32-001\"}");
 */

import { Agent, tool } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { z } from 'zod'
import express from 'express'

// --- TOOLS para IoT ---

const controlRelay = tool({
  name: 'control_relay',
  description: 'Enciende o apaga un relay/GPIO del dispositivo IoT',
  inputSchema: z.object({
    deviceId: z.string().describe('ID del dispositivo'),
    pin: z.number().describe('Número de pin GPIO'),
    state: z.enum(['on', 'off']).describe('Estado deseado'),
  }),
  callback: async (input) => {
    // Aquí enviarías el comando al dispositivo via MQTT, HTTP, WebSocket, etc.
    console.log(`[IoT] ${input.deviceId} → GPIO${input.pin} = ${input.state}`)
    // Simular respuesta
    return `Relay en GPIO${input.pin} del dispositivo ${input.deviceId} configurado a: ${input.state}`
  },
})

const readSensor = tool({
  name: 'read_sensor',
  description: 'Lee el valor actual de un sensor conectado al dispositivo',
  inputSchema: z.object({
    deviceId: z.string().describe('ID del dispositivo'),
    sensorType: z.enum(['temperature', 'humidity', 'light', 'motion']).describe('Tipo de sensor'),
  }),
  callback: async (input) => {
    // Aquí leerías el valor real del sensor
    const mockValues = { temperature: '23.5°C', humidity: '65%', light: '850 lux', motion: 'no detectado' }
    return `Sensor ${input.sensorType} en ${input.deviceId}: ${mockValues[input.sensorType]}`
  },
})

const setSchedule = tool({
  name: 'set_schedule',
  description: 'Programa una acción para un horario específico',
  inputSchema: z.object({
    deviceId: z.string(),
    action: z.string().describe('Acción a programar (ej: encender luz)'),
    time: z.string().describe('Hora en formato HH:MM'),
  }),
  callback: (input) => {
    return `Programado: "${input.action}" a las ${input.time} para ${input.deviceId}`
  },
})

// --- AGENT ---

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-3.1-flash-lite',
  params: { temperature: 0.2, maxOutputTokens: 1024 },
})

const agent = new Agent({
  model,
  tools: [controlRelay, readSensor, setSchedule],
  printer: false,
  systemPrompt: `Eres un controlador de dispositivos IoT smart home.
Interpretas comandos en lenguaje natural y ejecutas acciones en los dispositivos.
Responde de forma breve y confirma la acción realizada.
Si no entiendes el comando, pide clarificación.`,
})

// --- HTTP SERVER (recibe comandos del ESP32) ---

const app = express()
app.use(express.json())

app.post('/iot/command', async (req, res) => {
  const { message, deviceId } = req.body

  if (!message) {
    return res.status(400).json({ error: 'message es requerido' })
  }

  const prompt = deviceId
    ? `[Dispositivo: ${deviceId}] ${message}`
    : message

  try {
    const result = await agent.invoke(prompt)
    const response = typeof result === 'string' ? result : result.lastMessage ?? 'OK'
    res.json({ response, deviceId })
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Error' })
  }
})

app.get('/health', (_, res) => res.json({ status: 'ok' }))

app.listen(3000, () => {
  console.log('[IoT Bridge] Servidor escuchando en http://localhost:3000')
  console.log('[IoT Bridge] POST /iot/command — { "message": "...", "deviceId": "..." }')
})
