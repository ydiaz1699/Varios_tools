# Niveles de Estabilidad — SAG_SDK

Cada bloque, ejemplo y patrón tiene un nivel de estabilidad que indica cuánta confianza puedes tener en que funcione sin cambios.

---

## Niveles

| Nivel | Badge | Significado |
|-------|-------|-------------|
| **Stable** | `[stable]` | Verificado en producción. API estable. Cambios solo correctivos. |
| **Experimental** | `[experimental]` | Funciona pero puede cambiar. No probado extensivamente en producción. |
| **Deprecated** | `[deprecated]` | Ya no se mantiene. Puede tener datos desactualizados. Usar alternativa. |

---

## Estado actual por bloque

### Python — `blocks/python/`

| Bloque | Estabilidad | Notas |
|--------|:-----------:|-------|
| `gemini.md` | `[stable]` | Verificado contra panel real jul 2026 |
| `bedrock.md` | `[experimental]` | model_id NO verificado contra docs oficiales |
| `ollama.md` | `[stable]` | API estable, verificado con llama3.1 |
| `multi-provider.md` | `[stable]` | Patrón en producción (NAS Agent) |
| `tools.md` | `[stable]` | @tool API estable desde strands 1.0 |

### TypeScript — `blocks/typescript/`

| Bloque | Estabilidad | Notas |
|--------|:-----------:|-------|
| `gemini.md` | `[stable]` | GoogleModel verificado |
| `tools.md` | `[stable]` | Zod 4 requerido, API estable |
| `mcp.md` | `[stable]` | stdio + SSE verificados |
| `multi-agent.md` | `[experimental]` | Graph/Swarm API puede cambiar entre releases |
| `providers.md` | `[experimental]` | model_ids de OpenAI/Bedrock/Anthropic NO verificados |

### Producción — `blocks/production/`

| Bloque | Estabilidad | Notas |
|--------|:-----------:|-------|
| `credentials.md` | `[stable]` | Patrón en producción (NAS Agent) |
| `session.md` | `[stable]` | FileSessionManager en producción |
| `executive-mode.md` | `[stable]` | Patrón validado con Gemini Flash Lite |
| `core-layer.md` | `[stable]` | Patrón en producción (NAS Agent) |
| `errors.md` | `[stable]` | 8 errores verificados en desarrollo real |
| `testing.md` | `[experimental]` | Patrones correctos, no tiene test suite propio |
| `deployment.md` | `[experimental]` | Patrones de systemd/cron correctos, Docker no probado |
| `checklist.md` | `[stable]` | Validado contra NAS Agent en producción |

### Meta — `blocks/meta/`

| Bloque | Estabilidad | Notas |
|--------|:-----------:|-------|
| `analyze-chat.md` | `[stable]` | Usado repetidamente para extraer patrones |

### Otros

| Archivo | Estabilidad | Notas |
|---------|:-----------:|-------|
| `.kiro/skills/strands-gemini-integration.md` | `[deprecated]` | No se actualiza. Usar blocks/ |
| `prompts/analyze-chat.md` | `[deprecated]` | Duplicado. Usar blocks/meta/analyze-chat.md |
| `examples/*.ts` | `[stable]` | Código funcional verificado |
| `examples/nas-agent-pattern.py` | `[stable]` | Patrón real de producción |

---

## Cómo leer la estabilidad

- **Si es `[stable]`:** Copia-pega con confianza. El patrón funciona.
- **Si es `[experimental]`:** Funciona probablemente, pero verifica datos externos (model_ids, versiones, APIs) contra la documentación oficial antes de producción.
- **Si es `[deprecated]`:** No usar. Existe solo por compatibilidad. La alternativa está indicada.

---

## Cómo promover a stable

Un bloque pasa de `[experimental]` a `[stable]` cuando:
1. Se verifica contra documentación oficial O se usa en producción real
2. Se ejecuta el código de ejemplo sin errores
3. Se actualiza la fecha de "Última verificación" en el bloque
