"""
agent/tools/memory_tools.py — Tools de memoria persistente para el agente.

Thin wrappers que delegan a agent.core.memory.MemoryManager.
"""

from datetime import datetime
from strands.tools import tool


def _mgr():
    from agent.core.memory import MemoryManager
    return MemoryManager


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@tool
def remember(fact: str, category: str = "leccion") -> str:
    """Persiste un hecho o aprendizaje en la memoria del agente.
    Usar después de resolver un problema o descubrir algo nuevo.

    Categorías: "entorno", "leccion", "patron", "pendiente"
    NO guardar: cosas triviales, info duplicada, datos sensibles.

    Args:
        fact: Lo aprendido. Conciso y accionable. Máx 200 chars.
        category: Sección destino (entorno|leccion|patron|pendiente)
    """
    return str(_mgr().add_to_memory(fact, category, _now()))


@tool
def recall(query: str) -> str:
    """Busca en la memoria información relevante para la consulta.
    Busca en: SKILLS (trigger) → MEMORY (keywords) → sessions.

    USAR ANTES de resolver un problema — quizá ya lo resolviste.

    Args:
        query: Qué buscar, ej. "emqx no arranca"
    """
    return str(_mgr().recall(query))


@tool
def learn_skill(
    skill_name: str, procedure: str, trigger: str
) -> str:
    """Crea un skill reutilizable basado en una solución exitosa.

    Args:
        skill_name: nombre corto, ej. "diagnosticar-servicio-caido"
        procedure: pasos del procedimiento (markdown)
        trigger: cuándo aplicar, ej. "servicio Docker no responde"
    """
    return str(_mgr().add_skill(skill_name, procedure, trigger))


@tool
def update_user_model(key: str, value: str) -> str:
    """Actualiza el perfil del usuario con una preferencia observada.
    Solo hechos OBSERVADOS, nunca suposiciones.

    Args:
        key: qué actualizar, ej. "estilo", "decision_cifrado"
        value: valor observado, ej. "siempre cifrar"
    """
    return str(_mgr().update_user_model(key, value))


@tool
def memory_stats() -> str:
    """Estadísticas del sistema de memoria: tamaño de cada archivo,
    número de skills, sesiones, y espacio usado vs límites."""
    stats = _mgr().get_memory_stats()
    return (
        f"=== MEMORIA DEL AGENTE ===\n\n"
        f"MEMORY.md: {stats['memory_kb']:.1f} KB / 50 KB\n"
        f"USER.md: {stats['user_kb']:.1f} KB / 10 KB\n"
        f"SKILLS.md: {stats['skills_kb']:.1f} KB / 100 KB"
        f" ({stats['skill_count']} skills)\n"
        f"Sessions: {stats['sessions_count']} archivos"
        f" ({stats['sessions_kb']:.1f} KB / 500 KB)\n"
        f"Total: {stats['total_kb']:.1f} KB"
    )
