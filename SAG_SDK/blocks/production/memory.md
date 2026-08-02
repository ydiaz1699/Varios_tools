# Memoria Persistente y Auto-Mejora (Learning Loop)

> **Cuándo usar este bloque:** Cuando tu agente necesita recordar entre sesiones — lecciones aprendidas, preferencias del usuario, procedimientos exitosos. Aplica a cualquier agente construido con Strands SDK (Python o TypeScript) que se usa repetidamente.

---

## El problema

Un agente Strands es **stateless entre sesiones** por defecto:

```
Sesión 1: "¿por qué emqx no arranca?" → investiga 5 min → resuelve (OOM, subir RAM)
Sesión 2: "emqx caído de nuevo" → empieza DE CERO, investiga de nuevo 5 min
```

Con memoria persistente:

```
Sesión 1: resuelve → remember("emqx requiere ≥512MB") + learn_skill(...)
Sesión 2: recall("emqx caído") → encuentra skill → aplica directo → 30 segundos
```

---

## Arquitectura: 4 archivos Markdown

```
agent/memory/
├── MEMORY.md      ← QUÉ sabe (hechos, lecciones, estado del entorno)
├── USER.md        ← QUIÉN es el usuario (preferencias, estilo, decisiones)
├── SKILLS.md      ← CÓMO hacer las cosas (procedimientos reutilizables)
└── sessions/      ← QUÉ hizo antes (historial resumido)
```

### Principios

1. **Markdown plano** — cualquier LLM lo lee sin parser especial.
2. **Bounded** — cada archivo tiene límite de tamaño (curación automática).
3. **Legible por humanos** — el usuario puede leer/editar la memoria.
4. **Accionable** — cada entrada debe servir para tomar decisiones.

---

## Las 3 capas del "nudge" (cuándo guardar)

Ninguna sola basta. Se combinan:

| Capa | Mecanismo | Cuándo | Propósito |
|------|-----------|--------|-----------|
| **A** | System prompt | Cada interacción | El modelo PUEDE recordar por iniciativa propia |
| **B** | Event-driven | Post-tarea compleja | GARANTIZA que soluciones difíciles se persistan |
| **C** | Schedule | Cada 24h | MANTIENE la calidad (limpia, consolida, verifica) |

```
A genera memoria → B la complementa y garantiza → C la mantiene limpia
```

### Capa A: System Prompt

Agregar al system prompt del agente:

```markdown
## Memoria Persistente

Tienes memoria entre sesiones. Úsala:

### Antes de actuar en un problema:
- `recall("descripción")` → busca si ya lo resolviste antes

### Después de resolver algo complejo o nuevo:
- `remember("lección", category="leccion|patron|entorno")`
- Si fueron >3 pasos → `learn_skill(nombre, procedimiento, trigger)`

### Cuando observes preferencias del usuario:
- `update_user_model("clave", "valor observado")`

### NO guardar: cosas triviales, info duplicada, datos sensibles.
```

### Capa B: Event-Driven

```python
self.register_event(EventHandler(
    event_type="task.completed",
    handler=self._on_task_completed,
))

async def _on_task_completed(self, event):
    is_significant = (
        event.data.get("tool_calls", 0) > 3
        or event.data.get("errors_encountered", False)
        or event.data.get("duration_seconds", 0) > 300
    )
    if is_significant:
        # Guardar resumen + generar skill si aplica
        ...
```

### Capa C: Schedule

```python
self.register_schedule(ScheduleConfig(
    name="curate_memory",
    handler=self._curate_memory,
    interval_minutes=1440,  # 24h
))

async def _curate_memory(self):
    # 1. Eliminar lecciones > 90 días sin uso
    # 2. Consolidar duplicados
    # 3. Verificar skills (¿siguen siendo válidos?)
    # 4. Trim sessions/ viejas
    ...
```

---

## Tools (Python, Strands @tool)

```python
from strands.tools import tool

@tool
def remember(fact: str, category: str = "leccion") -> str:
    """Persiste un hecho en la memoria del agente.
    Categorías: entorno, leccion, patron, pendiente.
    NO guardar: cosas triviales, info duplicada, datos sensibles.

    Args:
        fact: Lo aprendido. Conciso y accionable. Máx 200 chars.
        category: Sección destino.
    """
    return str(MemoryManager.add_to_memory(fact, category, _now()))


@tool
def recall(query: str) -> str:
    """Busca en la memoria: SKILLS (trigger) → MEMORY (keywords) → sessions.
    USAR ANTES de resolver un problema — quizá ya lo resolviste.

    Args:
        query: Qué buscar, ej. "emqx no arranca"
    """
    return str(MemoryManager.recall(query))


@tool
def learn_skill(skill_name: str, procedure: str, trigger: str) -> str:
    """Crea un skill reutilizable basado en una solución exitosa.

    Args:
        skill_name: nombre corto, ej. "diagnosticar-servicio-caido"
        procedure: pasos del procedimiento (markdown)
        trigger: cuándo aplicar, ej. "servicio Docker no responde"
    """
    return str(MemoryManager.add_skill(skill_name, procedure, trigger))


@tool
def update_user_model(key: str, value: str) -> str:
    """Actualiza el perfil del usuario con una preferencia observada.

    Args:
        key: qué actualizar, ej. "estilo", "decision_cifrado"
        value: valor observado, ej. "siempre cifrar"
    """
    return str(MemoryManager.update_user_model(key, value))
```

---

## MemoryManager (Core)

```python
from pathlib import Path
import re, os
from datetime import datetime

MEMORY_DIR = Path(os.environ.get("AGENT_MEMORY_DIR", "agent/memory"))
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
USER_FILE = MEMORY_DIR / "USER.md"
SKILLS_FILE = MEMORY_DIR / "SKILLS.md"
SESSIONS_DIR = MEMORY_DIR / "sessions"

MAX_MEMORY_KB = 50
MAX_SKILLS_KB = 100


class MemoryManager:
    @staticmethod
    def add_to_memory(fact, category, timestamp):
        """Agrega línea a la sección correspondiente de MEMORY.md."""
        ...

    @staticmethod
    def recall(query):
        """Busca en SKILLS (trigger) → MEMORY (keyword) → sessions (grep)."""
        keywords = query.lower().split()
        results = []

        # 1. Skills por trigger
        for skill in _parse_skills():
            if any(kw in skill["trigger"].lower() for kw in keywords):
                results.append(f"📚 SKILL: {skill['name']}\n{skill['procedure']}")

        # 2. Memory por keyword
        for line in MEMORY_FILE.read_text().splitlines():
            if line.startswith("- ") and any(kw in line.lower() for kw in keywords):
                results.append(f"🧠 {line}")

        # 3. Sessions por grep
        for f in sorted(SESSIONS_DIR.glob("*.md"), reverse=True)[:20]:
            if any(kw in f.read_text().lower() for kw in keywords):
                results.append(f"📝 Sesión: {f.name}")

        return results or "Nada encontrado — problema nuevo."

    @staticmethod
    def add_skill(name, procedure, trigger):
        """Crea entrada en SKILLS.md con formato estándar."""
        ...

    @staticmethod
    def update_user_model(key, value):
        """Actualiza o agrega key:value en USER.md."""
        ...
```

---

## Formato de MEMORY.md

```markdown
# Memoria del Agente
> Última actualización: 2026-08-01T15:30:00

## Entorno
- OS: Debian 12, kernel 6.1
- Docker: v24.0.7

## Lecciones aprendidas
- [2026-07-15] Los permisos de /var/lib/rclone deben ser 0750
- [2026-08-01] emqx requiere al menos 512MB de RAM

## Patrones que funcionaron
- Backup: tar.gz local → rclone sync → rclone check
```

## Formato de SKILLS.md

```markdown
## skill: diagnosticar-servicio-caido
> Aprendido: 2026-07-10 | Usado: 5 veces
> Trigger: "servicio no responde", "container down"

### Procedimiento
1. `docker compose ps` → ¿está up?
2. `docker compose logs --tail 50` → ¿errores?
3. Si OOMKilled: aumentar mem_limit
4. Si restart loop: verificar volúmenes
```

## Formato de USER.md

```markdown
# Perfil del Usuario

## Preferencias
- Estilo: directo, sin rodeos
- Idioma: español (código en inglés)

## Decisiones técnicas
- No usar cron (solo systemd timers)
- Siempre cifrar datos en la nube
```

---

## Inyección en system prompt (inicio de sesión)

```python
# Al crear el Agent de Strands:
user_model = MemoryManager.load_user_model()
env_info = MemoryManager.load_memory_section("Entorno")

system_prompt = f"""
{STATIC_SYSTEM_PROMPT}

## Contexto del usuario
{user_model}

## Estado del entorno
{env_info}

## Memoria Persistente
[instrucciones de Capa A aquí]
"""

agent = Agent(model=model, tools=tools, system_prompt=system_prompt)
```

---

## Límites y sizing

| Archivo | Límite | Inyectado en prompt |
|---------|--------|---------------------|
| MEMORY.md | 50 KB | Solo sección "Entorno" (~2 KB) |
| USER.md | 10 KB | Completo (~3-5 KB) |
| SKILLS.md | 100 KB | Solo vía recall() (on-demand) |
| sessions/ | 500 KB total | Solo vía recall() |

Impacto en context window: **~5-7 KB** por sesión (< 2000 tokens). Mínimo.

---

## Checklist de implementación

1. [ ] Crear directorio `agent/memory/` con templates vacíos
2. [ ] Implementar `MemoryManager` (CRUD sobre archivos)
3. [ ] Crear tools: `remember`, `recall`, `learn_skill`, `update_user_model`
4. [ ] Agregar instrucciones Capa A al system prompt
5. [ ] Registrar EventHandler para Capa B (post-tarea)
6. [ ] Registrar Schedule para Capa C (curación 24h)
7. [ ] (Opcional) FTS5 index para búsqueda avanzada en sessions/

---

## Inspiración

- [Hermes Agent (Nous Research)](https://hermes-agent.nousresearch.com/) — learning loop completo
- [agentskills.io](https://agentskills.io) — estándar abierto de skills portables
