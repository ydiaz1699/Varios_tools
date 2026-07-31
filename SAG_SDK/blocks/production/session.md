# Sesión Persistente entre Invocaciones CLI

> **Cuándo usar este bloque:** Cuando tu agente CLI necesita recordar contexto entre invocaciones — por ejemplo, que en la llamada anterior se diagnosticó un servicio y ahora el usuario quiere actuar sobre ese diagnóstico.

---

## El problema

Por defecto, cada invocación de un agente CLI es **stateless**. Si el usuario hace:

```bash
mi-agente "revisar servicio nextcloud"   # Diagnostica
mi-agente "sí reiniciar"                 # ¿Reiniciar qué? No recuerda
```

---

## Solución: FileSessionManager

```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager
from pathlib import Path

# Sesión fija — el agente recuerda entre invocaciones
session_manager = FileSessionManager(
    session_id="mi-agente-main",
    storage_dir=str(Path.home() / ".mi-agente" / "sessions"),
)

agent = Agent(
    model=model,
    tools=tools,
    system_prompt=prompt,
    session_manager=session_manager,
    agent_id="mi-agente",  # ID fijo para ruta consistente
)

# Primera invocación:
agent("revisar servicio X")  # Diagnostica

# Segunda invocación (otro proceso):
agent("sí reiniciar")  # Recuerda que hablaban de X
```

---

## Auto-reset por timeout

Para evitar que el contexto sea infinito (y costoso), resetear la sesión si pasó mucho tiempo:

```python
import time
import json
from pathlib import Path

SESSION_TIMEOUT_MIN = 30


def session_expired(meta_path: Path) -> bool:
    """True si pasaron más de N minutos sin actividad."""
    if not meta_path.exists():
        return False
    meta = json.loads(meta_path.read_text())
    elapsed = (time.time() - meta.get("last_active", 0)) / 60
    return elapsed > SESSION_TIMEOUT_MIN


def update_session_meta(meta_path: Path):
    """Actualiza timestamp de última actividad."""
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps({"last_active": time.time()}))


# Uso:
meta_path = Path.home() / ".mi-agente" / "session_meta.json"

if session_expired(meta_path):
    # Crear nueva sesión (resetear)
    session_manager = FileSessionManager(
        session_id=f"session-{int(time.time())}",
        storage_dir=str(Path.home() / ".mi-agente" / "sessions"),
    )
else:
    # Reusar sesión existente
    session_manager = FileSessionManager(
        session_id="mi-agente-main",
        storage_dir=str(Path.home() / ".mi-agente" / "sessions"),
    )

update_session_meta(meta_path)
```

---

## Flags CLI recomendados

```bash
mi-agente --new "query"    # Nueva sesión limpia (ignora historial)
mi-agente --clear          # Borrar memoria / todas las sesiones
mi-agente --status         # Ver sesión actual (ID, mensajes, última actividad)
```

### Implementación

```python
import sys

args = sys.argv[1:]

if "--new" in args:
    args.remove("--new")
    session_manager = FileSessionManager(
        session_id=f"session-{int(time.time())}",
        storage_dir=str(Path.home() / ".mi-agente" / "sessions"),
    )
elif "--clear" in args:
    import shutil
    shutil.rmtree(Path.home() / ".mi-agente" / "sessions", ignore_errors=True)
    print("Sesiones borradas.")
    sys.exit(0)
elif "--status" in args:
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        elapsed = (time.time() - meta.get("last_active", 0)) / 60
        print(f"Sesión activa. Última actividad: hace {elapsed:.0f} min")
    else:
        print("Sin sesión activa.")
    sys.exit(0)
```

---

## Notas importantes

- `FileSessionManager` se importa de `strands.session.file_session_manager`
- `session_id` debe ser fijo para reusar sesión entre procesos
- `agent_id` fija la ruta del archivo de sesión
- El timeout evita contextos infinitos (y costos de tokens)
- Sin session manager, cada `agent("...")` es independiente
- El storage_dir puede ser cualquier ruta con permisos de escritura
