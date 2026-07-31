# Core Layer: Separar @tool de la lógica

> **Cuándo usar este bloque:** Cuando tu agente tiene tools complejas y necesitas que la lógica sea testeable sin Strands, evitar circular imports, y mantener las tools de pocas líneas. El patrón es: tool → core → shell.

---

## El problema

Error común: meter toda la lógica dentro del `@tool`. Consecuencias:
- No se puede testear sin Strands instalado
- Se acopla la interfaz al negocio
- Circular imports cuando el core necesita cosas del agente

---

## Patrón correcto: tool → core → shell

```
@tool (5 líneas)  →  Core (lógica de negocio)  →  Shell (subprocess/IO)
    ↓                         ↓                          ↓
 Solo delega          Testeable sin Strands         safe_run()
```

---

## Implementación

### Core layer (lógica de negocio)

```python
# agent/core/service_manager.py
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    success: bool
    message: str          # Lo que ve el LLM (str())
    data: dict = field(default_factory=dict)       # Datos estructurados (para lógica)
    suggestions: list = field(default_factory=list)  # Siguientes pasos sugeridos
    elapsed_ms: float = None

    def __str__(self) -> str:
        return self.message  # Backward compat con Strands

    @classmethod
    def ok(cls, message: str, **kwargs):
        return cls(success=True, message=message, **kwargs)

    @classmethod
    def error(cls, message: str, **kwargs):
        return cls(success=False, message=f"ERROR: {message}", **kwargs)


def safe_run(args: list[str], timeout: int = 120) -> str:
    """Ejecuta comando de forma segura (shell=False)."""
    import subprocess
    result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=timeout)
    return result.stdout


class ServiceManager:
    @staticmethod
    def restart(service_name: str) -> ToolResult:
        """Reinicia un servicio Docker."""
        error = service_exists_or_error(service_name)
        if error:
            return ToolResult.error(error)
        compose = find_compose(service_name)
        import time
        start = time.time()
        output = safe_run(["docker", "compose", "-f", str(compose), "restart"])
        elapsed = (time.time() - start) * 1000
        return ToolResult.ok(f"Reiniciado.\n{output}", elapsed_ms=elapsed)

    @staticmethod
    def logs(service_name: str, lines: int = 50) -> ToolResult:
        """Obtiene logs de un servicio."""
        error = service_exists_or_error(service_name)
        if error:
            return ToolResult.error(error)
        compose = find_compose(service_name)
        output = safe_run([
            "docker", "compose", "-f", str(compose),
            "logs", "--tail", str(lines)
        ])
        return ToolResult.ok(output)
```

### Tools layer (delegación pura)

```python
# agent/tools/docker_tools.py
from strands import tool


@tool
def service_restart(service_name: str) -> str:
    """Reinicia un servicio Docker.

    Args:
        service_name: Nombre del servicio (ej: "nextcloud")

    Returns:
        str: Resultado de la operación
    """
    return str(_get_service_manager().restart(service_name))


@tool
def service_logs(service_name: str, lines: int = 50) -> str:
    """Muestra las últimas N líneas de logs de un servicio.

    Args:
        service_name: Nombre del servicio
        lines: Número de líneas (default: 50)

    Returns:
        str: Logs del servicio
    """
    return str(_get_service_manager().logs(service_name, lines))
```

---

## ToolResult dataclass

```python
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    success: bool
    message: str          # Lo que ve el LLM (via __str__)
    data: dict = field(default_factory=dict)       # Datos estructurados
    suggestions: list = field(default_factory=list)  # Siguientes pasos
    elapsed_ms: float = None

    def __str__(self) -> str:
        return self.message  # Strands usa str() para leer el resultado

    @classmethod
    def ok(cls, message: str, **kwargs):
        return cls(success=True, message=message, **kwargs)

    @classmethod
    def error(cls, message: str, **kwargs):
        return cls(success=False, message=f"ERROR: {message}", **kwargs)
```

Beneficios:
- `str(result)` devuelve el mensaje (compatible con Strands)
- `result.success` permite lógica condicional
- `result.data` lleva datos estructurados sin contaminar el mensaje
- `result.suggestions` permite sugerir acciones al agente

---

## Lazy imports (evitar circular dependencies)

```python
# agent/tools/docker_tools.py

def _get_service_manager():
    """Lazy import para evitar circular dependencies."""
    from agent.core.service_manager import ServiceManager
    return ServiceManager


@tool
def service_restart(name: str) -> str:
    """Reinicia un servicio Docker."""
    return str(_get_service_manager().restart(name))
```

**Por qué:** Si `core` importa algo de `tools` (o viceversa via un módulo común), Python falla con `ImportError: cannot import name X from partially initialized module`. Lazy imports rompen el ciclo.

---

## Estructura de directorios

```
mi-agente/
├── agent/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── service_manager.py   # Lógica de negocio
│   │   └── tool_result.py       # ToolResult dataclass
│   ├── tools/
│   │   ├── __init__.py          # ALL_TOOLS = [...]
│   │   └── docker_tools.py      # @tool (solo delegación)
│   └── mi_agent.py              # Agent + get_model()
└── tests/
    └── test_service_manager.py  # Testea core SIN Strands
```

---

## Test sin Strands

```python
# tests/test_service_manager.py
from agent.core.service_manager import ServiceManager

def test_restart_nonexistent():
    result = ServiceManager.restart("servicio-fake")
    assert not result.success
    assert "ERROR" in result.message

def test_logs():
    result = ServiceManager.logs("nextcloud", lines=10)
    assert result.success or "ERROR" in result.message
```

No necesitas Strands instalado para testear el core. Solo la lógica de negocio.

---

## Notas importantes

- Tools deben ser de ~5 líneas (solo delegan al core)
- Core es testeable sin Strands
- `ToolResult.__str__()` es la clave de compatibilidad con Strands
- Lazy imports evitan circular dependencies
- `safe_run(shell=False)` siempre — nunca `shell=True`
