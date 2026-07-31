# Provider: Google Gemini (Python)

> **Cuándo usar este bloque:** Cuando necesitas crear un agente con Strands Agents SDK usando Google Gemini como provider. Es el provider más barato (tier gratuito disponible) y más fácil de configurar (solo API key).

---

## Instalación

```bash
pip install 'strands-agents[gemini]' strands-agents-tools
```

Versiones compatibles (julio 2026):
- `strands-agents`: >=1.0.0
- `strands-agents-tools`: >=0.1.0
- Python: 3.10+

---

## Configuración de GeminiModel

```python
from strands import Agent
from strands.models.gemini import GeminiModel

model = GeminiModel(
    model_id="gemini-3.1-flash-lite",  # Recomendado: 500 RPD en free tier
    client_args={"api_key": "tu-key"},  # o usa env GOOGLE_API_KEY
    params={
        "temperature": 0.3,
        "max_output_tokens": 4096,
    },
)

agent = Agent(model=model, system_prompt="Eres un asistente experto.")
result = agent("¿Qué hora es en Tokio?")
print(str(result))  # str(result) extrae el texto de AgentResult
```

---

## Variables de entorno

```bash
export GOOGLE_API_KEY="tu-api-key"  # se lee automáticamente
```

Obtener en: https://aistudio.google.com/apikey (tier gratuito disponible)

---

## Modelos Gemini disponibles (julio 2026)

| Modelo | model_id | RPD (free) | Recomendación |
|--------|----------|:----------:|---------------|
| Gemini 3.1 Flash Lite | `gemini-3.1-flash-lite` | 500 | **Recomendado** — máxima cuota gratis |
| Gemini 3.5 Flash Lite | `gemini-3.5-flash-lite` | 500 | Alta cuota, más nuevo |
| Gemini 3.5 Flash | `gemini-3.5-flash` | 20 | Más capaz, menos cuota |
| Gemini 3.6 Flash | `gemini-3.6-flash` | 20 | Último disponible |
| Gemini 3.1 Pro | `gemini-3.1-pro` | — | Razonamiento complejo |
| Gemini 2.5 Flash | `gemini-2.5-flash` | 20 | Anterior gen |
| Gemini 2.5 Pro | `gemini-2.5-pro` | — | Anterior gen (pro) |
| Gemini 2.0 Flash Lite | `gemini-2.0-flash-lite` | — | Legacy |

**RPD = Requests Per Day** en el tier gratuito.
La cuota es por proyecto (compartida entre modelos de la misma familia).
Recomendación: usar `gemini-3.1-flash-lite` (500 RPD) para desarrollo/uso personal.

---

## Desactivar output de streaming (callback_handler=None)

```python
# callback_handler=None silencia el output de Strands
# Así podés capturar el resultado y renderizarlo vos (ej: con Rich)
agent = Agent(
    model=model,
    tools=[...],
    system_prompt="...",
    callback_handler=None,  # No imprime streaming — vos controlás el output
)

result = agent("tu pregunta")
response_text = str(result)  # Extrae texto del AgentResult
```

**IMPORTANTE:** Usar `callback_handler=None`, NO `printer=False` (API incorrecta).

---

## Cargar config desde archivo (.env.agent)

Patrón para cargar variables desde un archivo sin dependencias extra:

```python
import os
from pathlib import Path

def load_env_file(env_path: Path):
    """Carga key=value de un archivo al entorno."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            if key.strip() and key.strip() not in os.environ:
                os.environ[key.strip()] = value.strip()

# Cargar al inicio del programa
load_env_file(Path("/nas-dotfiles/.env.agent"))
```

---

## Notas importantes

- `GeminiModel` se importa de `strands.models.gemini`
- El agente se invoca como función: `result = agent("tu pregunta")`
- Obtener texto: `str(result)` (NO `result.message`)
- NO wrappear funciones `@tool` con decoradores adicionales (rompe Strands)
- Modelo recomendado: `gemini-3.1-flash-lite` (500 RPD en free tier)
