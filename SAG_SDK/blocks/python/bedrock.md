# Provider: Amazon Bedrock con Extended Thinking (Python)

> **Cuándo usar este bloque:** Cuando necesitas el mejor razonamiento disponible (Claude via Bedrock) con capacidad de extended thinking — ideal para diagnósticos complejos, debugging profundo, o tareas que requieren corrección mid-stream.

---

## Instalación

```bash
pip install strands-agents strands-agents-tools
# + aws configure (requiere acceso a Bedrock)
```

---

## Configuración de BedrockModel

```python
import os
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14"],
        "thinking": {
            "type": "enabled",
            "budget_tokens": 10000,  # tokens para razonamiento interno
        },
    },
)

agent = Agent(model=model, system_prompt="Razona paso a paso.")
result = agent("Diagnostica por qué nextcloud está lento")
```

---

## Qué hace Extended Thinking

- Claude razona **internamente entre tool calls** (no visible al usuario)
- Si una herramienta devuelve un error, lo detecta y corrige en la misma iteración
- Ajusta su estrategia dinámicamente sin loops extra
- `budget_tokens` controla cuánto puede "pensar" (más = más profundo, más caro)

---

## budget_tokens — Guía de ajuste

| budget_tokens | Caso de uso | Costo aprox. |
|:-------------:|-------------|--------------|
| 5000 | Tareas simples con verificación | Bajo |
| 10000 | Diagnósticos estándar (recomendado) | Medio |
| 20000 | Razonamiento complejo multi-paso | Alto |
| 50000+ | Solo si realmente necesitas análisis profundo | Muy alto |

---

## Variables de entorno

```bash
export AWS_REGION=us-east-1
# Requiere: aws configure (con acceso a Bedrock)
```

---

## Ejemplo: Multi-provider con Bedrock

```python
import os
from strands.models.bedrock import BedrockModel

def get_bedrock_model():
    thinking_budget = int(os.environ.get("NAS_AGENT_THINKING_BUDGET", "10000"))
    return BedrockModel(
        model_id=os.environ.get("NAS_AGENT_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
        additional_request_fields={
            "anthropic_beta": ["interleaved-thinking-2025-05-14"],
            "thinking": {"type": "enabled", "budget_tokens": thinking_budget},
        },
    )
```

---

## Notas importantes

- `BedrockModel` se importa de `strands.models.bedrock`
- Extended thinking se habilita via `additional_request_fields`
- El campo `anthropic_beta` activa la feature de interleaved thinking
- Requiere credenciales AWS configuradas (`aws configure`)
- Es el provider con mejor tool-use y razonamiento, pero tiene costo
- No tiene tier gratuito — cada request se cobra por tokens
