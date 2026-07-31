# Provider: Ollama (Python — local, gratis)

> **Cuándo usar este bloque:** Cuando necesitas privacidad total (sin datos a la nube), quieres evitar costos de API, o estás en un entorno sin acceso a internet. Ollama corre modelos localmente en tu hardware.

---

## Instalación

```bash
pip install strands-agents strands-agents-tools
# + ollama serve && ollama pull llama3.1
```

Requisitos previos:
- Ollama instalado: https://ollama.ai
- Un modelo descargado: `ollama pull llama3.1`
- Ollama corriendo: `ollama serve`

---

## Configuración de OllamaModel

```python
from strands import Agent
from strands.models.ollama import OllamaModel

model = OllamaModel(
    model_id="llama3.1",
    host="http://localhost:11434",
)

agent = Agent(model=model, system_prompt="Eres un asistente.")
result = agent("Lista los archivos en /docker")
print(str(result))
```

---

## Variables de entorno

```bash
export OLLAMA_HOST=http://localhost:11434
# Requiere: ollama serve + ollama pull llama3.1
```

---

## Configuración de host remoto

Si Ollama corre en otra máquina de tu red:

```python
model = OllamaModel(
    model_id="llama3.1",
    host="http://192.168.1.100:11434",  # IP de la máquina con GPU
)
```

---

## Modelos recomendados para tool-use

| Modelo | Tamaño | Tool-use | Notas |
|--------|--------|:--------:|-------|
| `llama3.1` | 8B | Básico | Buen balance velocidad/calidad |
| `gemma3:4b` | 4B | Básico | Muy ligero, rápido |
| `qwen2.5:7b` | 7B | Bueno | Mejor tool-use entre modelos pequeños |

**Nota:** El tool-use en modelos locales es significativamente inferior al de Gemini o Claude. Usar para tareas simples o cuando la privacidad es prioritaria.

---

## Notas importantes

- `OllamaModel` se importa de `strands.models.ollama`
- Ollama debe estar corriendo antes de crear el agente
- No hay costo por request — limitado solo por tu hardware
- Tool-use es básico comparado con Gemini/Claude
- Ideal para: desarrollo local, pruebas, privacidad, sin internet
