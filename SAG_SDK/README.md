# SAG_SDK — Strands Agents SDK + Gemini (Agent Skill)

Skill de referencia para que cualquier LLM (Claude, GPT, Gemini, etc.) pueda incorporar **Strands Agents SDK con Google Gemini** en cualquier proyecto, de forma nativa.

## Qué es esto

Es una **knowledge base / skill** — no es un proyecto ejecutable. Es documentación estructurada que un LLM puede leer para saber cómo integrar Strands en tu proyecto sin tener que buscar información en internet.

## Cómo usarlo

1. Coloca esta carpeta en tu workspace (o repo de herramientas)
2. Cuando trabajes con un LLM, referencía el archivo `.kiro/skills/strands-gemini-integration.md`
3. El LLM tendrá toda la información para agregar Strands + Gemini a cualquier proyecto

## Contenido

```
SAG_SDK/
├── .kiro/skills/
│   └── strands-gemini-integration.md   ← Skill completa (la referencia principal)
├── examples/
│   ├── basic-agent.ts                  ← Agente básico con Gemini
│   ├── agent-with-tools.ts             ← Agente con herramientas custom
│   ├── agent-with-mcp.ts               ← Agente conectado a MCP server
│   ├── telegram-bot-agent.ts           ← Bot de Telegram con agente
│   └── multi-agent.ts                  ← Orquestación multi-agente
└── README.md
```

## Para qué sirve

- **En Claude Desktop/Cursor/Kiro:** El LLM lee la skill y sabe exactamente cómo agregar Strands a tu proyecto
- **En cualquier chat con LLM:** Pega el contenido de la skill como contexto
- **Como referencia personal:** Todo lo que necesitas sobre Strands + Gemini en un solo lugar

## Fuentes

- [Strands Agents Docs](https://strandsagents.com/docs/user-guide/quickstart/typescript/)
- [Google Gemini Provider](https://strandsagents.com/docs/user-guide/concepts/model-providers/google/)
- [MCP Tools Integration](https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/)
- [GitHub (monorepo)](https://github.com/strands-agents/harness-sdk)

Content was rephrased for compliance with licensing restrictions.
