# Protección de Credenciales — 3 Capas

> **Cuándo usar este bloque:** Cuando tu agente tiene tools que leen archivos del sistema (especialmente `.env`) y necesitas evitar que secretos se envíen al LLM. Implementa sanitización en 3 puntos para máxima seguridad.

---

## El problema

Un agente con tools que leen archivos del sistema PUEDE enviar secretos al LLM sin querer. Si tienes un tool `read_file` y el agente lee un `.env`, los passwords viajan a la API del provider (Gemini, Bedrock, etc.).

---

## Regla de oro

- `.env` REAL → solo vive en el servidor, nunca en git ni en la API del LLM
- `.env.example` → para git, con `__pega_aqui__` en vez de valores reales
- Lo que ve el LLM → siempre `***REDACTED***` en variables sensibles

---

## Patrones sensibles (detectar estos en keys)

```python
SENSITIVE_PATTERNS = [
    "password", "secret", "token", "cookie", "key", "pass",
    "user", "username", "login", "credential", "auth",
    "api_key", "apikey", "private",
]
SAFE_EXCEPTIONS = ["allow_anonymous", "allow_user"]
```

---

## Capa 1: Exportación (para git/portabilidad)

Cuando exportas `.env` a un catálogo o repositorio:

```python
def sanitize_env_for_export(env_content: str) -> str:
    """Reemplaza valores sensibles con placeholders."""
    lines = []
    for line in env_content.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            key_lower = key.strip().lower()
            if any(pat in key_lower for pat in SENSITIVE_PATTERNS) and value.strip():
                if not any(exc in key_lower for exc in SAFE_EXCEPTIONS):
                    lines.append(f"{key.strip()}=__pega_aqui__")
                    continue
        lines.append(line)
    return "\n".join(lines)
```

---

## Capa 2: Lectura por el agente (lo que ve el LLM)

Sanitizar ANTES de que el contenido llegue al modelo:

```python
@tool
def read_file(path: str) -> str:
    """Lee un archivo. Si es .env, sanitiza antes de enviar al LLM."""
    content = Path(path).read_text()

    # NUNCA enviar secretos al LLM
    if path.endswith(".env"):
        return sanitize_env_for_llm(content)
    return content

def sanitize_env_for_llm(content: str) -> str:
    """Reemplaza valores sensibles con ***REDACTED***."""
    lines = []
    for line in content.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            if any(pat in key.strip().lower() for pat in SENSITIVE_PATTERNS):
                if value.strip():
                    lines.append(f"{key.strip()}=***REDACTED***")
                    continue
        lines.append(line)
    return "\n".join(lines)
```

---

## Capa 3: Output de herramientas (scan_compose, troubleshoot)

En cualquier tool que muestre variables de entorno como parte de su output:

```python
# En cualquier tool que muestre variables de entorno
env_safe = [
    e.split("=")[0] + "=***REDACTED***"
    if any(pat in e.lower() for pat in SENSITIVE_PATTERNS)
    else e
    for e in env_list
]
```

---

## Ejemplo completo integrado

```python
from pathlib import Path
from strands import tool

SENSITIVE_PATTERNS = [
    "password", "secret", "token", "cookie", "key", "pass",
    "user", "username", "login", "credential", "auth",
    "api_key", "apikey", "private",
]
SAFE_EXCEPTIONS = ["allow_anonymous", "allow_user"]


def sanitize_env_for_llm(content: str) -> str:
    """Capa 2: Lo que ve el LLM."""
    lines = []
    for line in content.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            key_lower = key.strip().lower()
            if any(pat in key_lower for pat in SENSITIVE_PATTERNS):
                if value.strip() and not any(exc in key_lower for exc in SAFE_EXCEPTIONS):
                    lines.append(f"{key.strip()}=***REDACTED***")
                    continue
        lines.append(line)
    return "\n".join(lines)


@tool
def read_file(path: str) -> str:
    """Lee un archivo del sistema.

    Args:
        path: Ruta al archivo

    Returns:
        str: Contenido (sanitizado si es .env)
    """
    target = Path(path)
    if not target.exists():
        return f"ERROR: No existe: {path}"

    content = target.read_text()

    # Capa 2: sanitizar .env antes de enviar al LLM
    if path.endswith(".env"):
        return sanitize_env_for_llm(content)

    return content
```

---

## Checklist de seguridad

```
[ ] SENSITIVE_PATTERNS cubre todos tus secrets
[ ] Capa 1 (export): .env.example tiene __pega_aqui__
[ ] Capa 2 (read): tool de lectura sanitiza .env
[ ] Capa 3 (scan): tools que listan env vars redactan valores
[ ] .env real NUNCA está en git (.gitignore)
[ ] .env real NUNCA llega a la API del LLM
```
