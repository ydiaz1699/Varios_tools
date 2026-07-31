# Errores Comunes con Strands y Cómo Evitarlos

> **Cuándo usar este bloque:** Cuando encuentras un error trabajando con Strands Agents SDK y necesitas un diagnóstico rápido. Cubre los 8 errores más comunes en producción con síntomas y fixes.

---

## Error 1: Agente sin memoria (stateless por defecto)

**Síntoma:** El agente olvida todo entre invocaciones CLI.

**Fix:** `FileSessionManager` con `session_id` fijo + `agent_id` fijo.

```python
from strands.session.file_session_manager import FileSessionManager

session_manager = FileSessionManager(
    session_id="mi-agente-main",
    storage_dir=str(Path.home() / ".mi-agente" / "sessions"),
)
agent = Agent(model=model, tools=tools, session_manager=session_manager, agent_id="mi-agente")
```

---

## Error 2: Agente que sugiere en vez de actuar

**Síntoma:** "¿Quieres que ejecute X?" para operaciones de lectura.

**Fix:** System prompt en modo ejecutivo con lista explícita de permisos.

```
# MODO EJECUTIVO
- Operaciones de LECTURA: EJECUTAR INMEDIATAMENTE. NO preguntar.
- Operaciones SEGURAS: EJECUTAR directamente.
- Operaciones DESTRUCTIVAS: pedir confirmación.
```

---

## Error 3: Credenciales enviadas al LLM

**Síntoma:** El agente lee `.env` y envía passwords a la API del provider.

**Fix:** Sanitizar archivos `.env` ANTES de que el LLM los vea (capa 2).

```python
if path.endswith(".env"):
    return sanitize_env_for_llm(content)  # Reemplaza valores con ***REDACTED***
```

---

## Error 4: Agente muestra comandos crudos

**Síntoma:** "Ejecuta: docker compose -f ... down" en vez de usar tools.

**Fix:** Regla en prompt: "NUNCA muestres comandos. SIEMPRE usa tus tools." + Mapeo explícito de acción → tool.

---

## Error 5: Circular imports con core layer

**Síntoma:** `ImportError: cannot import name X from partially initialized module`

**Fix:** Lazy imports en tools:

```python
def _get_service_manager():
    from agent.core.service_manager import ServiceManager
    return ServiceManager

@tool
def service_restart(name: str) -> str:
    """Reinicia un servicio Docker."""
    return str(_get_service_manager().restart(name))
```

---

## Error 6: Sección ACTIVACIÓN confunde al agente con sesión

**Síntoma:** Agente muestra menú de bienvenida cuando ya hay historial.

**Fix:** Condicionar la activación en el prompt:

```
Cuando recibas el primer mensaje DE UNA SESIÓN NUEVA (sin historial previo),
responde con bienvenida. Si ya hay mensajes anteriores, NO lo hagas.
```

---

## Error 7: Provider Gemini Flash Lite ignora instrucciones largas

**Síntoma:** El agente no sigue todas las reglas del prompt.

**Fix:** Repetir las reglas críticas con "⚠️ REPITO:" y dar ejemplos concretos de correcto vs incorrecto en el prompt.

```
⚠️ REPITO: NUNCA preguntes si quieres que ejecute una operación de lectura.

❌ INCORRECTO: "¿Quieres que lea los logs?"
✅ CORRECTO: *ejecuta service_logs()* → "Los logs muestran..."
```

---

## Error 8: shell=True en subprocess (seguridad)

**Síntoma:** Posible inyección de comandos si el LLM pasa input malicioso.

**Fix:** SIEMPRE `shell=False` + validación de inputs:

```python
def safe_run(args: list[str], timeout: int = 120) -> str:
    """Ejecuta comando de forma segura."""
    result = subprocess.run(
        args,
        shell=False,          # NUNCA shell=True
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout
```

---

## Tabla rápida de errores de instalación/runtime

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError: google.genai` | Falta dependencia | `pip install 'strands-agents[gemini]'` |
| `No module named pip` | Debian sin pip | `apt install python3-pip python3.X-venv` |
| `GOOGLE_API_KEY not set` | Falta variable | `export GOOGLE_API_KEY=...` |
| `429 Too Many Requests` | Quota agotada | Cambiar modelo o esperar |
| `404 models/X not found` | Model ID incorrecto | Verificar en tabla de modelos |
| `botocore.exceptions.NoCredentialsError` | Sin AWS config | `aws configure` |
| `ConnectionRefusedError` (Ollama) | Ollama no corre | `ollama serve` |
| `ModelThrottledException` | Rate limit (RPM) | Esperar 60s |
| Tool no se ejecuta | Docstring vacío | @tool NECESITA docstring |
| `got unexpected keyword argument 'printer'` | API incorrecta | Usar `callback_handler=None` |
| `unrecognized tool specification` | Tool wrapeada | No wrappear @tool con decoradores extra |
| `peer zod@"^4.1.12"` (TS) | Zod 3 instalado | `npm install zod@^4.1.12` |
