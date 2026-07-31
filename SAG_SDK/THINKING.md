# SAG_SDK — Thinking Prompt (Entry Point)

## Qué es esto

Eres un LLM que necesita integrar **Strands Agents SDK** en un proyecto.
Este archivo es tu punto de entrada — te dice qué bloques cargar según lo que necesites.

NO necesitas leer TODO. Lee este archivo y luego SOLO los bloques relevantes.

---

## Razonamiento (ejecutar siempre)

Antes de implementar, responde estas preguntas:

1. **¿Qué lenguaje?** → Python o TypeScript
2. **¿Qué provider?** → Gemini (barato) / Bedrock (inteligente) / Ollama (local) / Multi-provider
3. **¿Qué tipo de agente?**
   - Agente simple con tools → `blocks/{lang}/tools`
   - Agente con MCP server → `blocks/typescript/mcp`
   - Multi-agente (pipeline/routing) → `blocks/typescript/multi-agent`
   - Agente CLI con sesión → `blocks/production/session`
   - Bot (Telegram/Discord) → ver ejemplos
4. **¿Es producción?** → cargar `blocks/production/` relevantes

---

## Mapa de bloques

### Python

| Bloque | Archivo | Cuándo cargar |
|--------|---------|---------------|
| Gemini provider | `blocks/python/gemini.md` | Usar Gemini como LLM |
| Bedrock provider | `blocks/python/bedrock.md` | Usar Claude con extended thinking |
| Ollama provider | `blocks/python/ollama.md` | LLM local gratis |
| Multi-provider | `blocks/python/multi-provider.md` | Cambiar provider por env var |
| Tools (@tool) | `blocks/python/tools.md` | Crear herramientas custom |

### TypeScript

| Bloque | Archivo | Cuándo cargar |
|--------|---------|---------------|
| Gemini provider | `blocks/typescript/gemini.md` | Usar Gemini como LLM |
| Tools (Zod) | `blocks/typescript/tools.md` | Herramientas con schema Zod |
| MCP | `blocks/typescript/mcp.md` | Conectar a MCP server |
| Multi-agent | `blocks/typescript/multi-agent.md` | Graph, Swarm, Agent-as-tool |
| Otros providers | `blocks/typescript/providers.md` | OpenAI, Bedrock, Anthropic |

### Producción (ambos lenguajes)

| Bloque | Archivo | Cuándo cargar |
|--------|---------|---------------|
| Credenciales | `blocks/production/credentials.md` | Manejar secrets/API keys |
| Sesión | `blocks/production/session.md` | Memoria entre invocaciones |
| System prompt | `blocks/production/executive-mode.md` | Que el agente ACTÚE sin preguntar |
| Core layer | `blocks/production/core-layer.md` | Separar @tool de lógica |
| Errores comunes | `blocks/production/errors.md` | Debugging / troubleshooting |
| Testing | `blocks/production/testing.md` | Testear el agente sin llamadas reales al LLM |
| Deployment | `blocks/production/deployment.md` | Correr el agente en producción (systemd, cron, Docker) |

### Meta

| Bloque | Archivo | Cuándo cargar |
|--------|---------|---------------|
| Analizar chat | `blocks/meta/analyze-chat.md` | Extraer patrones de una conversación |
| Checklist | `blocks/production/checklist.md` | Verificar agente antes de producción |

---

## Reglas transversales (siempre aplican)

1. **Python:** `@tool` REQUIERE docstring con Args/Returns — sin eso el LLM no sabe qué hace
2. **TypeScript:** Zod 4 OBLIGATORIO (`npm install zod@^4`) — Zod 3 no funciona
3. **Gemini:** `GOOGLE_API_KEY` como env var — obtener en https://aistudio.google.com/apikey
4. **Return type:** Tools SIEMPRE retornan `str` (Python) o `string` (TypeScript)
5. **shell=False:** NUNCA usar `shell=True` en subprocess — riesgo de inyección
6. **Streaming:** `callback_handler=None` para desactivar output de Strands y renderizar tú
7. **Model IDs y cuotas:** los `model_id` y valores de RPD/RPM/TPM listados en los bloques de Gemini fueron verificados contra un panel real (jul 2026), pero **cambian por cuenta y con el tiempo**. Antes de usar en producción, confirmar en el panel de cuotas de Google AI Studio. Para Bedrock/Anthropic/OpenAI, los `model_id` en esta skill NO están verificados de la misma forma — chequear siempre contra la documentación oficial del provider.

---

## Ejemplo de flujo

```
Usuario: "Quiero agregar un agente con Gemini a mi proyecto Python que administre Docker"

Tu razonamiento:
  1. Lenguaje: Python ✓
  2. Provider: Gemini ✓
  3. Tipo: Agente con tools (Docker commands)
  4. Producción: sí (CLI con sesión)

Bloques a cargar:
  → blocks/python/gemini.md
  → blocks/python/tools.md
  → blocks/production/session.md
  → blocks/production/executive-mode.md
```

---

## Skill completa (DEPRECADA)

> ⚠️ El archivo `.kiro/skills/strands-gemini-integration.md` está **deprecado**.
> Se mantiene por compatibilidad con contextos que solo soportan un archivo,
> pero NO se actualiza activamente. La fuente de verdad son los `blocks/`.
>
> Si necesitas todo junto, carga todos los bloques de la categoría que necesites.

Los bloques individuales son la fuente de verdad. El monolito puede tener datos desactualizados.
