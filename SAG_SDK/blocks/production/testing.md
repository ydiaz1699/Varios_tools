# Testing de Agentes Strands

> **Cuándo usar este bloque:** Cuando necesitas testear tu agente sin hacer requests reales a un LLM, mockear tools, o testear el core layer de forma aislada.

---

## Principio: testear el core, no Strands

No testees que Strands funciona — eso es responsabilidad de la librería. Testea TU lógica:
- Core layer (managers) → testeable sin Strands instalado
- Validación de inputs → puros, sin dependencias
- ToolResult → verificar formato y datos
- Clasificación de queries → puro Python

---

## Testear el core layer (sin Strands)

```python
# tests/test_service_manager.py
from agent.core.service_manager import ServiceManager

def test_restart_nonexistent():
    """Un servicio que no existe debe retornar error."""
    result = ServiceManager.restart("servicio-inventado")
    assert not result.success
    assert "ERROR" in result.message

def test_restart_valid(mocker):
    """Un servicio válido ejecuta docker compose restart."""
    mocker.patch("agent.core.service_manager.safe_run", return_value="OK")
    mocker.patch("agent.core.service_manager.find_compose", return_value="/docker/emqx/compose.yml")
    mocker.patch("agent.core.service_manager.service_exists_or_error", return_value=None)

    result = ServiceManager.restart("emqx")
    assert result.success
    assert "Reiniciado" in result.message
```

**Clave:** El core no importa `strands` — solo usa subprocess, Path, etc. Se testea como cualquier módulo Python.

---

## Testear validación de inputs

```python
# tests/test_validation.py
from agent.tools._shell import validate_service_name

def test_valid_name():
    assert validate_service_name("nextcloud") is None

def test_path_traversal():
    result = validate_service_name("../../etc/passwd")
    assert result is not None
    assert "inválido" in result.lower()

def test_empty_name():
    result = validate_service_name("")
    assert result is not None

def test_special_chars():
    result = validate_service_name("svc;rm -rf /")
    assert result is not None
```

---

## Testear ToolResult

```python
# tests/test_tool_result.py
from agent.core._result import ToolResult

def test_ok():
    r = ToolResult.ok("Todo bien", data={"port": 8080})
    assert r.success
    assert str(r) == "Todo bien"
    assert r.data["port"] == 8080

def test_error():
    r = ToolResult.error("Servicio no encontrado")
    assert not r.success
    assert "ERROR" in str(r)
```

---

## Testear clasificación de queries (prompt dinámico)

```python
# tests/test_classify.py
from agent.nas_agent import _classify_query

def test_diagnostico():
    blocks = _classify_query("revisar emqx")
    assert "diagnostico" in blocks

def test_creacion():
    blocks = _classify_query("instalar vaultwarden")
    assert "creacion" in blocks

def test_backup():
    blocks = _classify_query("backup de plex")
    assert "backup" in blocks

def test_identidad():
    blocks = _classify_query("qué modelo eres")
    assert "identidad" in blocks
    assert "diagnostico" not in blocks

def test_general():
    blocks = _classify_query("hola")
    assert "reglas_core" in blocks
```

---

## Mockear tools para tests de integración

Si necesitas testear el flujo completo sin Docker/subprocess:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def mock_safe_run(mocker):
    """Mock de safe_run para no ejecutar comandos reales."""
    return mocker.patch(
        "agent.tools._shell.safe_run",
        return_value="mocked output"
    )

@pytest.fixture
def mock_docker_running(mocker):
    """Simula que Docker está corriendo con servicios."""
    mocker.patch(
        "agent.tools._shell.safe_run",
        side_effect=lambda args, **kw: (
            "emqx\nnextcloud\nhomeassistant\n"
            if "ps" in args else "OK"
        )
    )
```

---

## Testear sin API key (CI/CD)

```python
# tests/test_agent_creation.py
import os
import pytest

def test_agent_creation_without_key():
    """Verificar que el agente falla gracefully sin API key."""
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ["NAS_AGENT_MODEL"] = "gemini"

    from agent.nas_agent import get_model
    # Debería crear el modelo (la key se valida al hacer request, no al instanciar)
    model = get_model()
    assert model is not None
```

---

## Estructura de tests recomendada

```
tests/
├── conftest.py              # Fixtures compartidos (mocks)
├── test_validation.py       # Validación de inputs (puro)
├── test_tool_result.py      # ToolResult dataclass
├── test_classify.py         # Clasificación de queries
├── test_service_manager.py  # Core layer (con mocks de subprocess)
└── test_compose.py          # Generación de compose (sin Docker)
```

---

## Qué NO testear

- ❌ Que Strands SDK funcione internamente
- ❌ Que el LLM responda correctamente (no determinístico)
- ❌ Que Docker ejecute comandos (eso es integration testing en staging)
- ❌ El output de Rich/UI (frágil, cambia con frecuencia)

---

## pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

---

## Ejecutar tests

```bash
# Todos los tests
pytest

# Solo tests de validación (rápidos, sin mocks)
pytest tests/test_validation.py -v

# Con coverage
pytest --cov=agent --cov-report=term-missing
```

---

## Notas importantes

- El core layer es lo más importante de testear (lógica de negocio)
- Tools son wrappers de 5 líneas — si el core funciona, las tools funcionan
- Clasificación de queries es pura (sin IO) — fácil de testear
- Mocks de subprocess evitan necesitar Docker en CI
- No testear el LLM — es no determinístico y cambia entre providers
