/**
 * Ejemplo: Bot de Telegram con Strands Agent + Gemini
 * 
 * Patrón completo para crear un bot de Telegram que use un agente
 * autónomo con herramientas. Aplicable a cualquier proyecto.
 * 
 * Setup:
 *   npm install @strands-agents/sdk @google/genai grammy zod
 *   export GOOGLE_API_KEY="tu-api-key"
 *   export TELEGRAM_BOT_TOKEN="tu-token-de-botfather"
 */

import { Agent, tool } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { Bot } from 'grammy'
import { z } from 'zod'

// --- CONFIG ---
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN!
const ALLOWED_USERS = (process.env.ALLOWED_USER_IDS ?? '').split(',')

// --- TOOLS (ejemplo: herramientas para tu proyecto específico) ---
const myProjectTool = tool({
  name: 'do_something',
  description: 'Hace algo específico de tu proyecto',
  inputSchema: z.object({
    action: z.string().describe('Acción a realizar'),
  }),
  callback: async (input) => {
    // Tu lógica aquí
    return `Acción "${input.action}" completada`
  },
})

// --- AGENT ---
const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-2.5-flash',
  params: { temperature: 0.3, maxOutputTokens: 4096 },
})

const agent = new Agent({
  model,
  tools: [myProjectTool],
  systemPrompt: 'Eres un asistente de Telegram. Responde de forma concisa.',
})

// --- BOT ---
const bot = new Bot(BOT_TOKEN)

// Auth middleware
bot.use(async (ctx, next) => {
  const userId = ctx.from?.id?.toString()
  if (!userId || !ALLOWED_USERS.includes(userId)) {
    await ctx.reply('⛔ No autorizado')
    return
  }
  await next()
})

// Manejar mensajes de texto
bot.on('message:text', async (ctx) => {
  await ctx.api.sendChatAction(ctx.chat.id, 'typing')

  try {
    const result = await agent.invoke(ctx.message.text)
    const response = typeof result === 'string' ? result : result.lastMessage ?? 'Sin respuesta'
    await ctx.reply(response)
  } catch (error) {
    await ctx.reply(`❌ Error: ${error instanceof Error ? error.message : 'Desconocido'}`)
  }
})

// Start
bot.start({ onStart: (info) => console.log(`Bot @${info.username} online`) })
