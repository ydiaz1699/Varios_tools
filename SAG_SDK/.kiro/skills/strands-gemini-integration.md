# Skill: Strands Agents SDK — Multi-Provider (TypeScript + Python)

## Descripción
Guía completa para incorporar Strands Agents SDK en cualquier proyecto, con soporte para múltiples providers (Google Gemini, Amazon Bedrock/Claude, OpenAI, Ollama). Cubre tanto **TypeScript** como **Python**, incluyendo extended thinking, multi-provider dinámico, y patrones reales de producción.

## Cuándo usar esta skill
- Cuando el usuario quiere agregar un agente autónomo a un proyecto existente
- Cuando se necesita integrar herramientas (tools) con un LLM de forma programática
- Cuando se quiere usar Gemini como LLM barato con capacidad de tool-use
- Cuando se necesita conectar a un servidor MCP desde código
- Cuando se quiere crear un bot, CLI, o servicio que use IA con herramientas
- Cuando se necesita un agente que cambie de provider dinámicamente (Gemini/Bedrock/Ollama)
- Cuando se quiere habilitar extended thinking (razonamiento profundo) con Claude

## Fuentes oficiales
- Documentación general: https://strandsagents.com/
- Quickstart TypeScript: https://strandsagents.com/docs/user-guide/quickstart/typescript/
- Quickstart Python: https://strandsagents.com/docs/user-guide/quickstart/python/
- Google Gemini Provider: https://strandsagents.com/docs/user-guide/concepts/model-providers/google/
- MCP Tools: https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/
- GitHub (monorepo): https://github.com/strands-agents/harness-sdk
- GitHub (Python SDK): https://github.com/strands-agents/sdk-python
- PyPI: https://pypi.org/project/strands-agents/
- NPM: @strands-agents/sdk
- Extended Thinking (blog): https://aws.amazon.com/blogs/opensource/using-strands-agents-with-claude-4-interleaved-thinking/

---
---

# PARTE 1: PYTHON

---

## Instalación Python

### Con Gemini (recomendado — barato)
```bash
pip install 'strands-agents[gemini]' strands-agents-tools
```

### Con Bedrock (Claude — mejor razonamiento)
```bash
pip install strands-agents strands-agents-tools
# + aws configure
```

### Con Ollama (local, gratis)
```bash
pip install strands-agents strands-agents-tools
# + ollama serve && ollama pull llama3.1
```

### Versiones compatibles (julio 2026)
- `strands-agents`: >=1.0.0
- `strands-agents-tools`: >=0.1.0
- Python: 3.10+

---

## Provider: Google Gemini (Python)

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

### Variables de entorno
```bash
export GOOGLE_API_KEY="tu-api-key"  # se lee automáticamente
```

Obtener en: https://aistudio.google.com/apikey (tier gratuito disponible)

### Modelos Gemini disponibles (julio 2026)

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

### Desactivar output de streaming (para renderizar con Rich)

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

### Cargar config desde archivo (.env.agent)

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

## Provider: Amazon Bedrock con Extended Thinking (Python)

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

### Qué hace Extended Thinking
- Claude razona **internamente entre tool calls** (no visible al usuario)
- Si una herramienta devuelve un error, lo detecta y corrige en la misma iteración
- Ajusta su estrategia dinámicamente sin loops extra
- `budget_tokens` controla cuánto puede "pensar" (más = más profundo, más caro)

### Variables de entorno
```bash
export AWS_REGION=us-east-1
# Requiere: aws configure (con acceso a Bedrock)
```

---

## Provider: Ollama (Python — local, gratis)

```python
from strands import Agent
from strands.models.ollama import OllamaModel

model = OllamaModel(
    model_id="llama3.1",
    host="http://localhost:11434",
)

agent = Agent(model=model, system_prompt="Eres un asistente.")
result = agent("Lista los archivos en /docker")
```

### Variables de entorno
```bash
export OLLAMA_HOST=http://localhost:11434
# Requiere: ollama serve + ollama pull llama3.1
```

---

## Patrón: Multi-Provider dinámico (Python)

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

## Crear herramientas con @tool (Python)

```python
from strands import Agent, tool


@tool
def scan_ports() -> str:
    """Escanea puertos en uso en el sistema.

    Returns:
        str: Lista de puertos ocupados y los siguientes disponibles
    """
    import subprocess
    result = subprocess.run(
        ["ss", "-tlnp"],
        capture_output=True, text=True
    )
    return result.stdout


@tool
def disk_usage() -> str:
    """Muestra el uso de disco del sistema.

    Returns:
        str: Resumen de uso de disco por partición
    """
    import subprocess
    result = subprocess.run(
        ["df", "-h", "--type=ext4", "--type=btrfs"],
        capture_output=True, text=True
    )
    return result.stdout


# Agrupar tools y crear agente
ALL_TOOLS = [scan_ports, disk_usage]
agent = Agent(model=model, tools=ALL_TOOLS, system_prompt="...")
```

### Reglas para @tool en Python
1. El **docstring** se convierte en la descripción de la herramienta (el modelo lo lee)
2. Los **type hints** definen el schema de parámetros
3. El **return** debe ser `str` (o serializable a string)
4. Errores se manejan devolviendo un string con "ERROR: ..."
5. El decorador `@tool` registra la función automáticamente

### Tool con parámetros
```python
@tool
def service_logs(service: str, lines: int = 50) -> str:
    """Muestra las últimas N líneas de logs de un servicio Docker.

    Args:
        service: Nombre del servicio (ej: "nextcloud", "plex")
        lines: Número de líneas a mostrar (default: 50)

    Returns:
        str: Últimas líneas de logs del servicio
    """
    import subprocess
    result = subprocess.run(
        ["docker", "compose", "-f", f"/docker/{service}/compose.yml",
         "logs", "--tail", str(lines)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return f"ERROR: {result.stderr}"
    return result.stdout
```

---

## System Prompt con instrucciones de razonamiento (Python)

Para mejorar la calidad de respuestas de cualquier provider, agregar instrucciones
explícitas de razonamiento:

```python
SYSTEM_PROMPT = """
# RAZONAMIENTO

Antes de ejecutar cualquier acción, SIEMPRE razona paso a paso:

1. **Entender** — ¿Qué está pidiendo exactamente el usuario?
2. **Planificar** — ¿Qué información necesito? ¿En qué orden?
3. **Verificar** — Consultar estado actual ANTES de actuar
4. **Evaluar riesgo** — ¿La acción es reversible? ¿Puede causar downtime?
5. **Ejecutar** — Solo actuar después de tener toda la información
6. **Confirmar** — ¿El resultado es el esperado?

## Reglas de razonamiento
- Si la tarea tiene RIESGO: explica tu plan ANTES de ejecutar
- Si hay AMBIGÜEDAD: pregunta antes de asumir
- Si NO SABÉS algo: dilo. Nunca inventes.
- Si algo FALLA: analiza el error, sugiere causa y solución

# MISIÓN
Eres un agente experto en [tu dominio]. Tu trabajo es...
"""

agent = Agent(model=model, tools=ALL_TOOLS, system_prompt=SYSTEM_PROMPT)
```

---

## Strands Agent Tools (paquete comunitario, Python)

```python
# Herramientas listas para usar del paquete strands-agents-tools
from strands_tools import calculator, python_repl, http_request

agent = Agent(
    model=model,
    tools=[calculator, python_repl, http_request],
)
```

Herramientas disponibles en `strands-agents-tools`:
- `calculator` — Operaciones matemáticas
- `python_repl` — Ejecuta código Python
- `http_request` — HTTP GET/POST/etc.
- `file_read` / `file_write` — Leer/escribir archivos
- `shell` — Ejecutar comandos de shell

---

## Comparación de providers (Python)

| Provider | Modelo | RPD (free) | Tool-use | Extended Thinking | Setup |
|----------|--------|:----------:|:--------:|:-----------------:|-------|
| **Gemini** | gemini-3.1-flash-lite | 500 | Bueno | No | Solo API key |
| **Gemini** | gemini-3.5-flash | 20 | Muy bueno | No | Solo API key |
| **Bedrock** | Claude Sonnet 4 | — | El mejor | Sí (interleaved) | AWS credentials |
| **Ollama** | llama3.1 / gemma3:4b | ∞ | Básico | No | Ollama local |

### Recomendación por caso de uso
- **Máxima cuota gratis**: `gemini-3.1-flash-lite` (500 RPD) o `gemini-3.5-flash-lite` (500 RPD)
- **Mejor calidad**: `gemini-3.5-flash` (20 RPD) o `gemini-3.6-flash` (20 RPD)
- **Razonamiento complejo**: Bedrock — extended thinking + mejor tool-use
- **Privacidad / sin internet**: Ollama — gratis, local, sin datos a la nube
- **Cuota agotada**: cambiar a otro modelo (cuotas separadas por modelo)

---

## Ejecutar como módulo Python

```bash
# Estructura recomendada
mi-agente/
├── agent/
│   ├── __init__.py
│   ├── mi_agent.py      # Agent + get_model() + system prompt
│   └── tools/
│       ├── __init__.py   # export ALL_TOOLS = [...]
│       └── mis_tools.py  # @tool functions
└── requirements.txt

# Ejecutar
cd mi-agente
python -m agent.mi_agent "tu pregunta"
```

---

## Errores comunes (Python)

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError: google.genai` | Falta dependencia Gemini | `pip install 'strands-agents[gemini]'` |
| `No module named pip` | Debian sin pip | `apt install python3-pip python3.X-venv` |
| `GOOGLE_API_KEY not set` | Falta variable | `export GOOGLE_API_KEY=...` o poner en `.env.agent` |
| `429 Too Many Requests` | Quota diaria agotada | Cambiar modelo (ej: `gemini-3.1-flash-lite`) o esperar |
| `404 models/X not found` | Model ID incorrecto | Verificar ID exacto en la tabla de modelos |
| `botocore.exceptions.NoCredentialsError` | Sin AWS config | `aws configure` |
| `ConnectionRefusedError` (Ollama) | Ollama no corre | `ollama serve` |
| `ModelThrottledException` | Rate limit (RPM) | Esperar 60s y reintentar |
| Tool no se ejecuta | Docstring vacío | El @tool NECESITA docstring para que el modelo lo entienda |
| `got an unexpected keyword argument 'printer'` | API incorrecta | Usar `callback_handler=None` (no `printer=False`) |
| `unrecognized tool specification` | Tool wrapeada | No wrappear funciones @tool con decoradores extra |

---
---

# PARTE 2: TYPESCRIPT

---

## Instalación TypeScript

### Dependencias base
```bash
npm install @strands-agents/sdk @google/genai zod
```

### Dependencias de desarrollo
```bash
npm install --save-dev @types/node typescript tsx
```

### Para usar con MCP servers
```bash
npm install @modelcontextprotocol/sdk
```

### Versiones compatibles (julio 2026)
- `@strands-agents/sdk`: ^1.11.x
- `@google/genai`: ^2.6.0
- `zod`: ^4.1.12 (IMPORTANTE: Strands SDK requiere Zod 4, NO Zod 3)
- `@modelcontextprotocol/sdk`: ^1.12.x
- Node.js: 20+

---

## Configuración del provider Google Gemini (TypeScript)

### Variables de entorno
```env
GOOGLE_API_KEY=tu-api-key-de-google-ai-studio
```

### Modelos disponibles (recomendados)
| Modelo | Caso de uso | RPD (free) |
|--------|------------|:----------:|
| `gemini-3.1-flash-lite` | Máxima cuota gratis, bueno para tool-use | 500 |
| `gemini-3.5-flash-lite` | Alta cuota, más nuevo | 500 |
| `gemini-3.5-flash` | Mejor balance rendimiento/cuota | 20 |
| `gemini-3.6-flash` | Último disponible | 20 |
| `gemini-2.5-flash` | Anterior gen | 20 |
| `gemini-2.5-pro` | Razonamiento complejo | — |

### Import y configuración
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

## Crear un agente básico (TypeScript)

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

## Crear herramientas con Zod (TypeScript)

```typescript
import { tool } from '@strands-agents/sdk'
import { z } from 'zod'

const myTool = tool({
  name: 'nombre_herramienta',
  description: 'Descripción clara de qué hace la herramienta',
  inputSchema: z.object({
    param1: z.string().describe('Descripción del parámetro'),
    param2: z.number().optional().describe('Parámetro opcional'),
  }),
  callback: (input) => {
    return `Resultado: ${input.param1}`
  },
})

const agent = new Agent({
  model,
  tools: [myTool],
})
```

### Herramientas asíncronas
```typescript
const asyncTool = tool({
  name: 'fetch_data',
  description: 'Obtiene datos de una API',
  inputSchema: z.object({ url: z.string().url() }),
  callback: async (input) => {
    const response = await fetch(input.url)
    const data = await response.json()
    return JSON.stringify(data)
  },
})
```

---

## Conectar a un servidor MCP (TypeScript)

### Via stdio
```typescript
import { Agent, McpClient } from '@strands-agents/sdk'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const mcpClient = new McpClient({
  transport: new StdioClientTransport({
    command: 'npx',
    args: ['tsx', 'ruta/al/servidor-mcp/index.ts'],
    env: { ...process.env, DATABASE_URL: 'mysql://...' },
  }),
})

const agent = new Agent({ model, tools: [mcpClient] })
```

### Via SSE (servidor ya corriendo)
```typescript
import { McpClient } from '@strands-agents/sdk'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

const mcpClient = new McpClient({
  transport: new SSEClientTransport(new URL('http://localhost:3100/sse')),
})

const agent = new Agent({ model, tools: [mcpClient] })
```

---

## Multi-Agent (TypeScript)

### Agent-as-tool
```typescript
const researcher = new Agent({
  name: 'researcher',
  description: 'Busca información sobre un tema',
  model,
  systemPrompt: 'Eres un investigador experto.',
})

const writer = new Agent({
  model,
  tools: [researcher],
  systemPrompt: 'Usa el researcher y escribe un resumen.',
})
```

### Graph (pipeline secuencial)
```typescript
import { Graph } from '@strands-agents/sdk/multiagent'

const graph = new Graph({
  nodes: [
    new Agent({ id: 'step1', model, systemPrompt: 'Paso 1...' }),
    new Agent({ id: 'step2', model, systemPrompt: 'Paso 2...' }),
  ],
  edges: [['step1', 'step2']],
})

const result = await graph.invoke('Ejecuta el pipeline')
```

### Swarm (routing dinámico)
```typescript
import { Swarm } from '@strands-agents/sdk/multiagent'

const swarm = new Swarm({
  nodes: [
    new Agent({ id: 'triage', model, systemPrompt: 'Enruta al especialista.' }),
    new Agent({ id: 'billing', model, systemPrompt: 'Facturación.' }),
    new Agent({ id: 'support', model, systemPrompt: 'Soporte técnico.' }),
  ],
  start: 'triage',
})
```

---

## Structured Output (TypeScript)

```typescript
import { z } from 'zod'

const MovieSchema = z.object({
  title: z.string(),
  rating: z.number().min(1).max(10),
  genre: z.string(),
  summary: z.string(),
})

const result = await agent.structured_output(MovieSchema, 'Analiza The Matrix')
```

---

## Otros Providers (TypeScript)

```typescript
// OpenAI
import { OpenAIModel } from '@strands-agents/sdk/models/openai'
const model = new OpenAIModel({ apiKey: process.env.OPENAI_API_KEY, modelId: 'gpt-4o' })

// Amazon Bedrock
import { BedrockModel } from '@strands-agents/sdk/models/bedrock'
const model = new BedrockModel({ modelId: 'global.anthropic.claude-sonnet-4-6', region: 'us-east-1' })

// Anthropic directo
import { AnthropicModel } from '@strands-agents/sdk/models/anthropic'
const model = new AnthropicModel({ apiKey: process.env.ANTHROPIC_API_KEY, modelId: 'claude-sonnet-4-20250514' })
```

---

## Vended Tools (TypeScript)

```typescript
import { bash } from '@strands-agents/sdk/vended-tools/bash'
import { httpRequest } from '@strands-agents/sdk/vended-tools/http-request'
import { fileEditor } from '@strands-agents/sdk/vended-tools/file-editor'
import { notebook } from '@strands-agents/sdk/vended-tools/notebook'

const agent = new Agent({ model, tools: [bash, httpRequest, fileEditor, notebook] })
```

---

## package.json mínimo (TypeScript)

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
---

# PARTE 3: PATRONES DE INTEGRACIÓN

---

## Por tipo de proyecto

| Proyecto | Stack recomendado | Provider |
|----------|------------------|----------|
| CLI sysadmin (NAS, Docker) | Python + @tool | Gemini (barato) o Bedrock (complejo) |
| Bot de Telegram | TypeScript + grammy | Gemini |
| API REST/Backend | TypeScript + Express/Fastify | Gemini |
| IoT / ESP32 (via bridge) | TypeScript + Express + MQTT | Gemini |
| Cron job / Automatización | Python | Gemini |
| Privacidad total | Python + Ollama | Ollama (local) |
| Razonamiento complejo | Python + Bedrock | Bedrock + thinking |

---

## Errores comunes (ambos lenguajes)

| Error | Causa | Solución |
|-------|-------|----------|
| `peer zod@"^4.1.12"` (TS) | Zod 3 instalado | `npm install zod@^4.1.12` |
| `ModuleNotFoundError: google.genai` (Py) | Falta gemini extra | `pip install 'strands-agents[gemini]'` |
| `GOOGLE_API_KEY not set` | Falta variable | Setear en .env o shell |
| `ModelThrottledException` | Rate limit | Esperar + reintentar |
| `MCP connection refused` (TS) | Server no corre | Verificar que el MCP esté activo |
| Tool no se ejecuta (Py) | Sin docstring | `@tool` NECESITA docstring |
| Tool no se ejecuta (TS) | Mala description | Describir claramente qué hace |

---

## Notas para LLMs que lean esta skill

### Python
1. Instalar con `pip install 'strands-agents[gemini]'` para Gemini
2. En Debian 13+: necesita `apt install python3-pip python3.X-venv` primero
3. `@tool` decorator convierte funciones en herramientas — el docstring es la descripción
4. Type hints definen el schema de parámetros automáticamente
5. El return de un @tool debe ser `str`
6. `GeminiModel` se importa de `strands.models.gemini`
7. `BedrockModel` se importa de `strands.models.bedrock`
8. Extended thinking se habilita via `additional_request_fields` en BedrockModel
9. El agente se invoca como función: `result = agent("tu pregunta")`
10. Obtener texto de la respuesta: `str(result)` (NO `result.message`)
11. Silenciar streaming: `callback_handler=None` (NO `printer=False`)
12. NO wrappear funciones `@tool` con decoradores adicionales (rompe Strands)
13. Multi-provider se resuelve con un `get_model()` que lee env vars
14. Modelo recomendado: `gemini-3.1-flash-lite` (500 RPD en free tier)
15. Cargar config desde archivo: leer `.env.agent` con `load_env_file()` al inicio

### TypeScript
1. Siempre usar `type: "module"` en package.json (imports ESM)
2. **Zod 4 es obligatorio** — no usar Zod 3 con Strands SDK
3. `GoogleModel` se importa de `@strands-agents/sdk/models/google`
4. `McpClient` se importa de `@strands-agents/sdk`
5. `StdioClientTransport` de `@modelcontextprotocol/sdk/client/stdio.js`
6. `SSEClientTransport` de `@modelcontextprotocol/sdk/client/sse.js`
7. El agente maneja el loop de tool-use automáticamente
8. Los resultados de tools deben ser strings (o serializados a string)
9. El `systemPrompt` define el comportamiento — hazlo claro y específico

### General
- Para que el agente use herramientas, solo hay que **describirlas bien**
- El modelo decide cuándo usar cada herramienta basándose en la descripción
- Instrucciones de razonamiento en el system prompt mejoran TODOS los providers
- Extended thinking (solo Bedrock/Claude) permite corrección mid-stream sin loops extra

---

## Resumen de imports principales

### Python
```python
from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands.models.bedrock import BedrockModel
from strands.models.ollama import OllamaModel
from strands.types.exceptions import ModelThrottledException
from strands_tools import calculator, python_repl, http_request
```

### TypeScript
```typescript
// Core
import { Agent, tool, McpClient } from '@strands-agents/sdk'

// Models
import { GoogleModel } from '@strands-agents/sdk/models/google'
import { OpenAIModel } from '@strands-agents/sdk/models/openai'
import { BedrockModel } from '@strands-agents/sdk/models/bedrock'
import { AnthropicModel } from '@strands-agents/sdk/models/anthropic'

// Multi-agent
import { Graph, Swarm } from '@strands-agents/sdk/multiagent'

// Vended tools
import { bash } from '@strands-agents/sdk/vended-tools/bash'
import { httpRequest } from '@strands-agents/sdk/vended-tools/http-request'
import { fileEditor } from '@strands-agents/sdk/vended-tools/file-editor'

// MCP transports
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

// Events
import { BeforeToolCallEvent, AfterToolCallEvent } from '@strands-agents/sdk'
import type { Plugin, LocalAgent } from '@strands-agents/sdk'
```
