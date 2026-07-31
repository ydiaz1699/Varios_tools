# Otros Providers (TypeScript)

> **Cuándo usar este bloque:** Cuando necesitas usar un provider distinto a Google Gemini en TypeScript — OpenAI, Amazon Bedrock (Claude), o Anthropic directo.

---

## OpenAI

```typescript
import { Agent } from '@strands-agents/sdk'
import { OpenAIModel } from '@strands-agents/sdk/models/openai'

const model = new OpenAIModel({
  apiKey: process.env.OPENAI_API_KEY,
  modelId: 'gpt-4o',
})

const agent = new Agent({
  model,
  systemPrompt: 'Eres un asistente experto.',
})

const result = await agent.invoke('Tu pregunta')
console.log(result.lastMessage)
```

### Variables de entorno

```bash
export OPENAI_API_KEY=sk-...
```

---

## Amazon Bedrock (Claude)

```typescript
import { Agent } from '@strands-agents/sdk'
import { BedrockModel } from '@strands-agents/sdk/models/bedrock'

const model = new BedrockModel({
  modelId: 'global.anthropic.claude-sonnet-4-6',
  region: 'us-east-1',
})

const agent = new Agent({
  model,
  systemPrompt: 'Eres un asistente experto.',
})

const result = await agent.invoke('Tu pregunta')
console.log(result.lastMessage)
```

### Variables de entorno

```bash
export AWS_REGION=us-east-1
# Requiere: aws configure (con acceso a Bedrock)
```

---

## Anthropic (directo)

```typescript
import { Agent } from '@strands-agents/sdk'
import { AnthropicModel } from '@strands-agents/sdk/models/anthropic'

const model = new AnthropicModel({
  apiKey: process.env.ANTHROPIC_API_KEY,
  modelId: 'claude-sonnet-4-20250514',
})

const agent = new Agent({
  model,
  systemPrompt: 'Eres un asistente experto.',
})

const result = await agent.invoke('Tu pregunta')
console.log(result.lastMessage)
```

### Variables de entorno

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Resumen de imports

```typescript
// OpenAI
import { OpenAIModel } from '@strands-agents/sdk/models/openai'

// Bedrock
import { BedrockModel } from '@strands-agents/sdk/models/bedrock'

// Anthropic
import { AnthropicModel } from '@strands-agents/sdk/models/anthropic'

// Google (para referencia)
import { GoogleModel } from '@strands-agents/sdk/models/google'
```

---

## Comparación rápida

| Provider | Import | Requiere | Costo |
|----------|--------|----------|-------|
| Google Gemini | `GoogleModel` | `GOOGLE_API_KEY` | Free tier (500 RPD) |
| OpenAI | `OpenAIModel` | `OPENAI_API_KEY` | Pay per token |
| Bedrock | `BedrockModel` | AWS credentials | Pay per token |
| Anthropic | `AnthropicModel` | `ANTHROPIC_API_KEY` | Pay per token |

---

## Notas importantes

- Todos los modelos usan la misma interfaz `Agent` — solo cambia el model
- `BedrockModel` usa credenciales AWS (no API key)
- La API es consistente: `new Agent({ model, tools, systemPrompt })`
- Puedes cambiar de provider sin modificar la lógica del agente
