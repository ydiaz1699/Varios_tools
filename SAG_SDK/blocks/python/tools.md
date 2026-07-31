# Herramientas con @tool (Python)

> **Cuándo usar este bloque:** Cuando necesitas crear herramientas (tools) que el agente pueda invocar — funciones que leen el sistema, ejecutan comandos, consultan APIs, etc. El decorador `@tool` convierte cualquier función Python en una herramienta que el LLM puede usar.

---

## Tool básico

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

---

## Tool con parámetros

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

## Tool que ejecuta subprocess (patrón safe_run)

**SIEMPRE usar `shell=False`** para evitar inyección de comandos:

```python
def safe_run(args: list[str], timeout: int = 120) -> str:
    """Ejecuta un comando de forma segura (sin shell=True)."""
    result = subprocess.run(
        args,
        shell=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout


@tool
def service_restart(service_name: str) -> str:
    """Reinicia un servicio Docker por nombre.

    Args:
        service_name: Nombre del servicio (ej: "nextcloud")

    Returns:
        str: Resultado de la operación
    """
    import subprocess
    output = safe_run([
        "docker", "compose",
        "-f", f"/docker/{service_name}/compose.yml",
        "restart"
    ])
    return f"Servicio {service_name} reiniciado.\n{output}"
```

---

## Reglas para @tool en Python

1. El **docstring** se convierte en la descripción de la herramienta (el modelo lo lee)
2. Los **type hints** definen el schema de parámetros automáticamente
3. El **return** debe ser `str` (o serializable a string)
4. Errores se manejan devolviendo un string con "ERROR: ..."
5. El decorador `@tool` registra la función automáticamente
6. **Sin docstring = tool invisible** — el LLM no sabrá que existe
7. **NO wrappear** funciones `@tool` con decoradores adicionales (rompe Strands)

---

## Manejo de errores en tools

```python
@tool
def read_config(path: str) -> str:
    """Lee un archivo de configuración.

    Args:
        path: Ruta al archivo

    Returns:
        str: Contenido del archivo o error
    """
    from pathlib import Path
    target = Path(path)
    if not target.exists():
        return f"ERROR: Archivo no encontrado: {path}"
    if not target.is_file():
        return f"ERROR: No es un archivo: {path}"
    try:
        return target.read_text()
    except PermissionError:
        return f"ERROR: Sin permisos para leer: {path}"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"
```

---

## Tools del paquete comunitario

```python
# Herramientas listas para usar del paquete strands-agents-tools
from strands_tools import calculator, python_repl, http_request

agent = Agent(
    model=model,
    tools=[calculator, python_repl, http_request],
)
```

Disponibles en `strands-agents-tools`:
- `calculator` — Operaciones matemáticas
- `python_repl` — Ejecuta código Python
- `http_request` — HTTP GET/POST/etc.
- `file_read` / `file_write` — Leer/escribir archivos
- `shell` — Ejecutar comandos de shell

---

## Estructura recomendada para tools

```
mi-agente/
├── agent/
│   ├── __init__.py
│   ├── mi_agent.py      # Agent + get_model() + system prompt
│   └── tools/
│       ├── __init__.py   # export ALL_TOOLS = [...]
│       └── mis_tools.py  # @tool functions
└── requirements.txt
```
