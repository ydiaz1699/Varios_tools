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
- [Google Gemini Provider](https://strandsagents.com/docs/user-guide/concepts/model-providers/google/)
- [Extended Thinking (blog)](https://aws.amazon.com/blogs/opensource/using-strands-agents-with-claude-4-interleaved-thinking/)
- [MCP Tools Integration](https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/)

