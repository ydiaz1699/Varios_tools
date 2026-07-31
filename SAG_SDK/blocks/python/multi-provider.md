# Patrón: Multi-Provider dinámico (Python)

> **Cuándo usar este bloque:** Cuando tu agente debe poder cambiar de provider (Gemini/Bedrock/Ollama) en runtime según una variable de entorno — por ejemplo, usar Gemini en desarrollo y Bedrock en producción, o Ollama cuando no hay internet.

---

## El patrón get_model()

Seleccionar provider en runtime según variable de entorno. Este es el patrón
usado en producción en el NAS Agent:

```python
import os
from strands import Agent


def get_model():
    """Selecciona modelo según NAS_AGENT_MODEL (gemini|bedrock|ollama)."""
    proveedor = os.environ.get("NAS_AGENT_MODEL", "gemini").lower()
    model_id_override = os.environ.get("NAS_AGENT_MODEL_ID")

    if proveedor == "gemini":
        from strands.models.gemini import GeminiModel
        return GeminiModel(
            model_id=model_id_override or "gemini-2.5-flash",
            client_args={"api_key": os.environ.get("GOOGLE_API_KEY")} if os.environ.get("GOOGLE_API_KEY") else None,
            params={"temperature": 0.3, "max_output_tokens": 4096},
        )

    elif proveedor == "bedrock":
        from strands.models.bedrock import BedrockModel
        thinking_budget = int(os.environ.get("NAS_AGENT_THINKING_BUDGET", "10000"))
        return BedrockModel(
            model_id=model_id_override or "us.anthropic.claude-sonnet-4-20250514-v1:0",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            additional_request_fields={
                "anthropic_beta": ["interleaved-thinking-2025-05-14"],
                "thinking": {"type": "enabled", "budget_tokens": thinking_budget},
            },
        )

    elif proveedor == "ollama":
        from strands.models.ollama import OllamaModel
        return OllamaModel(
            model_id=model_id_override or "llama3.1",
            host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        )

    else:
        raise ValueError(f"Provider '{proveedor}' no soportado. Opciones: gemini, bedrock, ollama")


# Uso:
model = get_model()
agent = Agent(model=model, tools=[...], system_prompt="...")
```

---

## Variables de entorno

```bash
# Selección de provider
export NAS_AGENT_MODEL=gemini          # opciones: gemini, bedrock, ollama

# Override de modelo (opcional)
export NAS_AGENT_MODEL_ID=gemini-3.5-flash  # sobreescribe el default del provider

# Provider-specific
export GOOGLE_API_KEY=tu-key           # para gemini
export AWS_REGION=us-east-1            # para bedrock
export NAS_AGENT_THINKING_BUDGET=10000 # para bedrock (extended thinking)
export OLLAMA_HOST=http://localhost:11434  # para ollama
```

---

## Por qué lazy imports

Los imports de cada provider están **dentro** del if/elif correspondiente:

```python
if proveedor == "gemini":
    from strands.models.gemini import GeminiModel  # Solo se importa si se usa
```

Beneficios:
- No necesitas instalar TODOS los providers
- Con `pip install 'strands-agents[gemini]'` solo necesitas la dependencia de Gemini
- Evita errores de import si no tienes boto3 (Bedrock) o ollama instalado

---

## Ejemplo de uso completo

```python
import os
from pathlib import Path
from strands import Agent

# Cargar config
def load_env_file(env_path: Path):
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

load_env_file(Path("/nas-dotfiles/.env.agent"))

# Crear agente con el provider que indique el env
model = get_model()
agent = Agent(
    model=model,
    tools=[...],
    system_prompt="...",
    callback_handler=None,
)

result = agent("tu pregunta")
print(str(result))
```

---

## Recomendación por caso de uso

| Caso | Provider | Razón |
|------|----------|-------|
| Desarrollo / testing | gemini | Gratis (500 RPD), rápido |
| Producción (tareas complejas) | bedrock | Mejor razonamiento + thinking |
| Sin internet / privacidad | ollama | Local, sin datos a la nube |
| Cuota agotada | Cambiar provider | Cuotas son independientes |
