# Guía de Implementación

> **Propósito**: Archivos a crear, integración con el plugin system,
> modificaciones al system prompt, y orden de ejecución.

---

## 1. Archivos a crear en `nas-dotfiles`

```
agent/
├── core/
│   └── memory.py               ← MemoryManager (CRUD sobre archivos)
├── tools/
│   └── memory_tools.py         ← @tool wrappers
├── plugins/
│   └── memory_plugin.py        ← Plugin: tools + events + schedule
└── memory/                     ← Datos persistentes
    ├── .gitkeep
    ├── MEMORY.md               ← (generado en primera ejecución)
    ├── USER.md                 ← (generado en primera ejecución)
    ├── SKILLS.md               ← (generado en primera ejecución)
    └── sessions/
        └── .gitkeep
```

---

## 2. `agent/core/memory.py` — MemoryManager


### Responsabilidades

- Leer/escribir MEMORY.md, USER.md, SKILLS.md
- Crear/listar/eliminar sesiones en sessions/
- Buscar en toda la memoria (keyword matching + relevancia)
- Verificar tamaños y aplicar límites
- NO toma decisiones sobre QUÉ guardar (eso lo hacen las capas A/B/C)

### Interfaz pública

```python
class MemoryManager:
    """Gestión de archivos de memoria. Métodos estáticos (sin estado)."""

    # ── MEMORY.md ──
    @staticmethod
    def load_memory() -> str
    @staticmethod
    def add_to_memory(fact: str, category: str, timestamp: str) -> ToolResult
    @staticmethod
    def remove_from_memory(fact_substring: str) -> ToolResult

    # ── USER.md ──
    @staticmethod
    def load_user_model() -> str
    @staticmethod
    def update_user_model(key: str, value: str) -> ToolResult

    # ── SKILLS.md ──
    @staticmethod
    def load_skills() -> str
    @staticmethod
    def add_skill(name: str, procedure: str, trigger: str) -> ToolResult
    @staticmethod
    def update_skill_usage(name: str) -> ToolResult
    @staticmethod
    def remove_skill(name: str) -> ToolResult

    # ── Sessions ──
    @staticmethod
    def save_session(title: str, content: str) -> ToolResult
    @staticmethod
    def list_sessions(last_n: int = 10) -> ToolResult
    @staticmethod
    def search_sessions(query: str) -> ToolResult

    # ── Búsqueda cross-file ──
    @staticmethod
    def recall(query: str) -> ToolResult
    # Busca en: SKILLS.md (trigger match) → MEMORY.md → sessions/ (grep)

    # ── Mantenimiento ──
    @staticmethod
    def get_memory_stats() -> dict
    # Retorna: {memory_kb, skills_kb, sessions_count, sessions_total_kb}
    @staticmethod
    def prune_old_entries(max_age_days: int) -> ToolResult
    @staticmethod
    def trim_sessions(max_age_days: int) -> ToolResult
```

---

## 3. `agent/tools/memory_tools.py` — Tools del agente

```python
from strands.tools import tool

def _mgr():
    from agent.core.memory import MemoryManager
    return MemoryManager

@tool
def remember(fact: str, category: str = "leccion") -> str:
    """Persiste un hecho o aprendizaje en la memoria del agente (MEMORY.md).
    Usar después de resolver un problema o descubrir algo nuevo sobre el entorno.

    Categorías válidas: "entorno", "leccion", "patron", "pendiente"
    NO guardar: cosas triviales, info que ya existe, datos sensibles.

    Args:
        fact: Lo que se aprendió. Claro, conciso, accionable. Máximo 200 chars.
        category: Sección donde guardar (entorno|leccion|patron|pendiente)
    """
    return str(_mgr().add_to_memory(fact, category, timestamp=_now()))

@tool
def recall(query: str) -> str:
    """Busca en la memoria del agente información relevante para la consulta.
    Busca en: SKILLS.md (por trigger) → MEMORY.md (por keyword) → sessions/ (grep).

    USAR ANTES de resolver un problema — quizá ya lo resolviste antes.

    Args:
        query: Qué buscar, ej. "emqx no arranca", "cómo hice backup de jellyfin"
    """
    return str(_mgr().recall(query))

@tool
def learn_skill(skill_name: str, procedure: str, trigger: str) -> str:
    """Crea un skill (procedimiento reutilizable) basado en una solución exitosa.
    El skill se aplicará automáticamente la próxima vez que el trigger matchee.

    Args:
        skill_name: nombre corto, ej. "diagnosticar-servicio-caido"
        procedure: pasos del procedimiento (markdown, paso a paso)
        trigger: cuándo aplicar, ej. "servicio Docker no responde"
    """
    return str(_mgr().add_skill(skill_name, procedure, trigger))

@tool
def update_user_model(key: str, value: str) -> str:
    """Actualiza el modelo del usuario (USER.md) con una preferencia o
    decisión observada. Solo hechos OBSERVADOS, nunca suposiciones.

    Args:
        key: qué actualizar, ej. "estilo", "decision_cifrado", "nivel_tecnico"
        value: valor observado, ej. "directo sin rodeos", "siempre cifrar"
    """
    return str(_mgr().update_user_model(key, value))

@tool
def memory_stats() -> str:
    """Muestra estadísticas del sistema de memoria: tamaño de cada archivo,
    número de skills, sesiones guardadas, y espacio usado vs límites."""
    stats = _mgr().get_memory_stats()
    return (
        f"=== MEMORIA DEL AGENTE ===\n\n"
        f"MEMORY.md: {stats['memory_kb']:.1f} KB / 50 KB\n"
        f"USER.md: {stats['user_kb']:.1f} KB / 10 KB\n"
        f"SKILLS.md: {stats['skills_kb']:.1f} KB / 100 KB ({stats['skill_count']} skills)\n"
        f"Sessions: {stats['sessions_count']} archivos ({stats['sessions_kb']:.1f} KB / 500 KB)\n"
        f"Total: {stats['total_kb']:.1f} KB"
    )
```

---

## 4. `agent/plugins/memory_plugin.py` — Plugin completo

```python
from agent.plugins.base import BasePlugin, PluginMeta, EventHandler, ScheduleConfig

class MemoryPlugin(BasePlugin):
    meta = PluginMeta(
        name="memory",
        version="1.0.0",
        description="Memoria persistente y auto-mejora (Learning Loop)",
        dependencies=[],  # sin dependencias — se carga primero
    )

    def setup(self):
        from agent.tools.memory_tools import (
            remember, recall, learn_skill, update_user_model, memory_stats
        )

        # Tools
        self.register_tool(remember)
        self.register_tool(recall)
        self.register_tool(learn_skill)
        self.register_tool(update_user_model)
        self.register_tool(memory_stats)

        # Capa B: event-driven
        self.register_event(EventHandler(
            event_type="task.completed",
            handler=self._on_task_completed,
            description="Evaluar si la tarea merece persistir en memoria"
        ))
        self.register_event(EventHandler(
            event_type="user.correction",
            handler=self._on_user_correction,
            description="Actualizar USER.md cuando el usuario corrige"
        ))

        # Capa C: curación periódica
        self.register_schedule(ScheduleConfig(
            name="curate_memory",
            handler=self._curate_memory,
            interval_minutes=1440,  # 24h
            enabled=True,
            run_on_start=False,
        ))
```

---

## 5. Modificaciones al system prompt

### Dónde agregar

En el system prompt del agente (el que se pasa a Strands al crear el Agent),
agregar DESPUÉS de las instrucciones de tools pero ANTES del contexto dinámico:

### Texto exacto (Capa A)

```markdown
## Memoria Persistente

Tienes memoria entre sesiones almacenada en archivos locales.

### Reglas de uso:
1. **ANTES de resolver un problema**: usa `recall("descripción")` para verificar
   si ya tienes un skill o lección relevante. Aplicar skills existentes es 10x más rápido.
2. **DESPUÉS de resolver algo complejo o nuevo**: usa `remember("lección", category)`.
3. **Si creaste un procedimiento de >3 pasos**: usa `learn_skill(nombre, pasos, trigger)`.
4. **Si observas una preferencia del usuario**: usa `update_user_model(clave, valor)`.

### NO guardar:
- Tareas triviales (listar containers, leer un archivo)
- Info que ya existe en memoria (verificar con recall primero)
- Datos sensibles (passwords, tokens, claves)
- Suposiciones no confirmadas sobre el usuario
```

### Inyección dinámica de contexto

Al inicio de cada sesión, inyectar DESPUÉS del system prompt estático:

```python
# En el flujo de inicio del agente:
user_model = MemoryManager.load_user_model()
env_section = MemoryManager.load_memory_section("Entorno")

dynamic_context = f"""
## Contexto del usuario (de sesiones anteriores)
{user_model}

## Estado conocido del entorno
{env_section}
"""
# Agregar al system prompt antes de la primera interacción
```

---

## 6. Registro de tools destructivas

En `agent/tools/_shell.py`, agregar al `_DESTRUCTIVE_TOOLS` frozenset:

```python
# NO agregar memory tools como destructivas — la memoria es interna del agente,
# no es una acción sobre el sistema del usuario.
# remember(), learn_skill(), etc. son SIEMPRE seguras de ejecutar.
```

**Excepción**: si agregas una tool `forget(fact)` que elimina memoria, ESA sí
podría considerarse destructiva (pero solo afecta al agente, no al sistema).

---

## 7. Inicialización (primera ejecución)

Cuando el agente arranca por primera vez y no existe `agent/memory/`:

```python
# En memory.py o en el setup del plugin:
MEMORY_DIR = Path("/path/to/agent/memory")

def ensure_memory_initialized():
    """Crea los archivos de memoria con estructura base si no existen."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_DIR / "sessions").mkdir(exist_ok=True)

    if not (MEMORY_DIR / "MEMORY.md").exists():
        (MEMORY_DIR / "MEMORY.md").write_text(MEMORY_TEMPLATE)
    if not (MEMORY_DIR / "USER.md").exists():
        (MEMORY_DIR / "USER.md").write_text(USER_TEMPLATE)
    if not (MEMORY_DIR / "SKILLS.md").exists():
        (MEMORY_DIR / "SKILLS.md").write_text(SKILLS_TEMPLATE)
```

Templates: ver `docs/01-memory-system.md` para el contenido inicial de cada archivo.

---

## 8. Emisión de eventos (para Capa B)

El agente necesita emitir eventos cuando corresponda. Esto puede requerir
un wrapper en el loop principal o hooks en Strands:

```python
# Ejemplo: emitir evento al finalizar una sesión
from agent.events.bus import EventBus

# Al finalizar interacción:
EventBus.emit("task.completed", {
    "tool_calls": len(tools_used),
    "errors_encountered": any_errors,
    "duration_seconds": elapsed,
    "summary": brief_summary,
    "tools_used": [t.name for t in tools_used],
})

# Cuando el usuario corrige:
# Detección: si el usuario dice "no", "prefiero", "siempre haz X", "nunca hagas Y"
EventBus.emit("user.correction", {
    "correction": user_message,
    "context": what_agent_did_wrong,
})
```

**Nota**: la detección de `user.correction` puede ser simple (keyword matching)
o sofisticada (pedirle al modelo que clasifique si el mensaje es una corrección).

---

## 9. Testing

### Tests unitarios recomendados

```python
# tests/test_memory.py
def test_remember_adds_to_memory():
    """remember() agrega una línea con timestamp a MEMORY.md"""

def test_recall_finds_skill_by_trigger():
    """recall('servicio caído') encuentra skill con trigger 'servicio no responde'"""

def test_recall_searches_sessions():
    """recall() busca en sessions/ si MEMORY y SKILLS no tienen resultado"""

def test_memory_size_limit():
    """add_to_memory() rechaza si MEMORY.md superaría 50 KB"""

def test_learn_skill_creates_entry():
    """learn_skill() crea entrada con formato correcto en SKILLS.md"""

def test_update_user_model_replaces():
    """update_user_model() reemplaza valor existente, no duplica"""

def test_prune_removes_old():
    """prune_old_entries(90) elimina lecciones con fecha > 90 días"""
```

---

## 10. Orden de implementación

| Paso | Archivo | Tiempo estimado | Dependencias |
|------|---------|-----------------|--------------|
| 1 | `agent/memory/` + templates | 10 min | Ninguna |
| 2 | `agent/core/memory.py` | 1-2h | Paso 1 |
| 3 | `agent/tools/memory_tools.py` | 30 min | Paso 2 |
| 4 | System prompt (Capa A) | 10 min | Paso 3 |
| 5 | `agent/plugins/memory_plugin.py` (solo tools) | 30 min | Paso 3 |
| 6 | Event handlers (Capa B) | 1-2h | Paso 5 + EventBus |
| 7 | Schedule (Capa C) | 1h | Paso 5 + Scheduler |
| 8 | Tests | 1h | Todo lo anterior |

**Total estimado**: 5-8 horas de implementación.
**Complejidad real**: Media (no hay dependencias externas, solo archivos + tools).
