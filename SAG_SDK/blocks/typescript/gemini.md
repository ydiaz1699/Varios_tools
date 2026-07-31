# Provider: Google Gemini + Agente Básico (TypeScript)

> **Cuándo usar este bloque:** Cuando necesitas crear un agente con Strands Agents SDK en TypeScript usando Google Gemini como provider. Incluye instalación, configuración del modelo, y creación de un agente básico.

---

## Instalación

```bash
# Dependencias base
npm install @strands-agents/sdk @google/genai zod

# Dependencias de desarrollo
npm install --save-dev @types/node typescript tsx
```

### Versiones compatibles (julio 2026)

- `@strands-agents/sdk`: ^1.11.x
- `@google/genai`: ^2.6.0
- `zod`: ^4.1.12 (**IMPORTANTE: Strands SDK requiere Zod 4, NO Zod 3**)
- Node.js: 20+

---

## Variables de entorno

```env
GOOGLE_API_KEY=tu-api-key-de-google-ai-studio
```

Obtener en: https://aistudio.google.com/apikey

---

## Modelos disponibles

| Modelo | Caso de uso | RPD (free) |
|--------|------------|:----------:|
| `gemini-3.1-flash-lite` | Máxima cuota gratis, bueno para tool-use | 500 |
| `gemini-3.5-flash-lite` | Alta cuota, más nuevo | 500 |
| `gemini-3.5-flash` | Mejor balance rendimiento/cuota | 20 |
| `gemini-3.6-flash` | Último disponible | 20 |
| `gemini-2.5-flash` | Anterior gen | 20 |
| `gemini-2.5-pro` | Razonamiento complejo | — |

---

## Configuración del modelo

```typescript
import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const model = new GoogleModel({
  apiKey: process.env.GOOGLE_API_KEY,
  modelId: 'gemini-2.5-flash',
  params: {
    temperature: 0.7,
    maxOutputTokens: 4096,
    topP: 0.9,
    topK: 40,
  },
})
```

---

## Agente básico

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

const result = await agent.invoke('Tu pregunta aquí')
console.log(result.lastMessage)
```

---

## package.json mínimo

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

## Notas importantes

- `GoogleModel` se importa de `@strands-agents/sdk/models/google`
- Siempre usar `"type": "module"` en package.json (imports ESM)
- **Zod 4 es obligatorio** — no usar Zod 3 con Strands SDK
- El agente maneja el loop de tool-use automáticamente
- El `systemPrompt` define el comportamiento — hazlo claro y específico
