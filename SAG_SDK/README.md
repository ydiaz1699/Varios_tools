# SAG_SDK — Strands Agents SDK (Python + TypeScript)

Skill de referencia para que cualquier LLM pueda incorporar **Strands Agents SDK** en cualquier proyecto, con soporte multi-provider y ambos lenguajes.

## Arquitectura: Thinking + Bloques Dinámicos

```
LLM necesita integrar Strands
        │
        ▼
┌─ THINKING.md (siempre, entry point) ─────────────┐
│  Razona: ¿qué lenguaje? ¿qué provider?           │
│  ¿qué tipo de agente? ¿es producción?            │
│  → Selecciona bloques relevantes                  │
└───────────────────────────────────────────────────┘
        │
        ▼
┌─ blocks/ (solo los relevantes) ───────────────────┐
│  python/gemini.md    typescript/tools.md           │
│  production/session.md   production/errors.md     │
│  (solo lo que necesitas para ESTA tarea)          │
└───────────────────────────────────────────────────┘
```

**NO cargues todo.** Lee `THINKING.md` → decide qué bloques necesitas → carga solo esos.

## Estructura

```
SAG_SDK/
├── THINKING.md                         ← Entry point (siempre leer primero)
├── blocks/
│   ├── python/
│   │   ├── gemini.md                   ← Provider Gemini (Python)
│   │   ├── bedrock.md                  ← Provider Bedrock + Extended Thinking
│   │   ├── ollama.md                   ← Provider local (gratis)
│   │   ├── multi-provider.md           ← Patrón multi-provider dinámico
│   │   └── tools.md                    ← @tool decorator
│   ├── typescript/
│   │   ├── gemini.md                   ← GoogleModel + agente básico
│   │   ├── tools.md                    ← Zod tools
│   │   ├── mcp.md                      ← Conexión MCP (stdio/SSE)
│   │   ├── multi-agent.md              ← Graph, Swarm, Agent-as-tool
│   │   └── providers.md                ← OpenAI, Bedrock, Anthropic
│   ├── production/
│   │   ├── credentials.md              ← Sanitización en 3 capas
│   │   ├── session.md                  ← FileSessionManager
│   │   ├── executive-mode.md           ← System prompt ejecutivo
│   │   ├── core-layer.md              ← tool → core → shell
│   │   ├── errors.md                   ← 8 errores comunes + fixes
│   │   └── checklist.md                ← Checklist de producción
│   └── meta/
│       └── analyze-chat.md             ← Extraer patrones de chats
├── examples/                           ← Ejemplos ejecutables
│   ├── nas-agent-pattern.py
│   ├── basic-agent.ts
│   ├── agent-with-tools.ts
│   ├── agent-with-mcp.ts
│   ├── telegram-bot-agent.ts
│   ├── multi-agent.ts
│   └── iot-bridge-agent.ts
├── prompts/
│   └── analyze-chat.md                 ← Prompt template (versión legacy)
├── .kiro/skills/
│   └── strands-gemini-integration.md   ← Skill monolítica (legacy, 1182 líneas)
└── README.md
```

## Cómo usarlo

### Opción 1: Bloques dinámicos (recomendado)

1. Lee `THINKING.md` — te dice qué bloques cargar
2. Lee solo los bloques relevantes para tu tarea
3. Implementa

### Opción 2: Skill monolítica (legacy)

Si tu contexto soporta archivos grandes, carga `.kiro/skills/strands-gemini-integration.md` completo (las 4 partes de una vez).

### Opción 3: Ejemplos directos

Revisa `examples/` para código funcional que puedes copiar y adaptar.

## Cobertura

| Lenguaje | Providers | Features |
|----------|-----------|----------|
| **Python** | Gemini, Bedrock (Claude), Ollama | @tool, extended thinking, multi-provider, sesión, seguridad |
| **TypeScript** | Gemini, Bedrock, OpenAI, Anthropic | Zod tools, MCP, multi-agent (Graph/Swarm), structured output |

## Fuentes

- [Strands Agents Docs](https://strandsagents.com/)
- [GitHub — Python SDK](https://github.com/strands-agents/sdk-python)
- [GitHub — Monorepo](https://github.com/strands-agents/harness-sdk)
- [PyPI](https://pypi.org/project/strands-agents/)
- [NPM](https://www.npmjs.com/package/@strands-agents/sdk)

## Cobertura

| Lenguaje | Providers | Features |
|----------|-----------|----------|
| **Python** | Gemini, Bedrock (Claude), Ollama | @tool, extended thinking, multi-provider dinámico |
| **TypeScript** | Gemini, Bedrock, OpenAI, Anthropic | Zod tools, MCP, multi-agent (Graph/Swarm) |

## Cómo usarlo

1. Coloca esta carpeta en tu workspace (o repo de herramientas)
2. Cuando trabajes con un LLM, referenciá el archivo `.kiro/skills/strands-gemini-integration.md`
3. El LLM tendrá toda la información para agregar Strands a cualquier proyecto

## Contenido

```
SAG_SDK/
├── .kiro/skills/
│   └── strands-gemini-integration.md   ← Skill completa (referencia principal)
├── examples/
│   ├── nas-agent-pattern.py            ← Multi-provider + @tool + reasoning (PYTHON)
│   ├── basic-agent.ts                  ← Agente básico con Gemini
│   ├── agent-with-tools.ts             ← Agente con herramientas custom
│   ├── agent-with-mcp.ts              ← Agente conectado a MCP server
│   ├── telegram-bot-agent.ts           ← Bot de Telegram con agente
│   ├── multi-agent.ts                  ← Orquestación multi-agente
│   └── iot-bridge-agent.ts            ← IoT bridge (ESP32 → Agente)
└── README.md
```

## Qué cubre la skill

### Python (PARTE 1)
- Instalación (`pip install 'strands-agents[gemini]'`)
- Provider Gemini (barato, default)
- Provider Bedrock + Extended Thinking (Claude razona internamente)
- Provider Ollama (local, gratis)
- Patrón multi-provider dinámico (selección por env var)
- Crear herramientas con `@tool` decorator
- System prompt con instrucciones de razonamiento
- Herramientas comunitarias (`strands-agents-tools`)
- Comparación de providers (costo, calidad, setup)
- Errores comunes y soluciones

### TypeScript (PARTE 2)
- Instalación (npm + Zod 4 obligatorio)
- Provider Gemini con configuración
- Crear herramientas con Zod schemas
- Conectar a MCP servers (stdio + SSE)
- Multi-Agent: Agent-as-tool, Graph, Swarm
- Structured Output
- Otros providers (OpenAI, Bedrock, Anthropic)
- Vended Tools (bash, httpRequest, fileEditor)
- package.json y tsconfig.json recomendados

### Patrones de integración (PARTE 3)
- Recomendación de stack por tipo de proyecto
- Errores comunes unificados
- Resumen de imports (Python + TypeScript)
- Notas para LLMs que lean la skill

### Patrones de producción (PARTE 4) — NUEVO
- Protección de credenciales (3 capas: export, read, scan)
- Sesión persistente entre invocaciones CLI (FileSessionManager)
- System prompt en modo ejecutivo (actuar, no sugerir)
- Core layer: separar @tool de la lógica de negocio
- ToolResult estructurado (no strings crudos)
- 8 errores comunes con Strands y cómo evitarlos
- Checklist para agente en producción

## Para qué sirve

- **En Kiro/Claude Desktop/Cursor:** El LLM lee la skill y sabe exactamente cómo agregar Strands
- **En cualquier chat con LLM:** Pega el contenido de la skill como contexto
- **Como referencia personal:** Todo sobre Strands multi-provider en un solo lugar

## Ejemplo rápido — Python (5 líneas)

```python
from strands import Agent
from strands.models.gemini import GeminiModel

agent = Agent(
    model=GeminiModel(model_id="gemini-2.5-flash"),
    system_prompt="Eres un experto en Docker."
)
result = agent("¿Cómo veo contenedores corriendo?")
```

## Ejemplo rápido — TypeScript (5 líneas)

```typescript
import { Agent } from '@strands-agents/sdk'
import { GoogleModel } from '@strands-agents/sdk/models/google'

const agent = new Agent({
  model: new GoogleModel({ modelId: 'gemini-2.5-flash' }),
  systemPrompt: 'Eres un experto en Docker.',
})
const result = await agent.invoke('¿Cómo veo contenedores corriendo?')
```

## Fuentes

- [Strands Agents Docs](https://strandsagents.com/)
- [Python Quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/)
- [TypeScript Quickstart](https://strandsagents.com/docs/user-guide/quickstart/typescript/)
- [Google Gemini Provider](https://strandsagents.com/docs/user-guide/concepts/model-providers/google/)
- [Extended Thinking (blog)](https://aws.amazon.com/blogs/opensource/using-strands-agents-with-claude-4-interleaved-thinking/)
- [MCP Tools Integration](https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/)
- [GitHub — Python SDK](https://github.com/strands-agents/sdk-python)
- [GitHub — Monorepo](https://github.com/strands-agents/harness-sdk)
- [PyPI](https://pypi.org/project/strands-agents/)
- [NPM](https://www.npmjs.com/package/@strands-agents/sdk)
