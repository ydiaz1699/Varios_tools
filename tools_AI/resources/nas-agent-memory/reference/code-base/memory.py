"""
agent/core/memory.py — MemoryManager: gestión de archivos de memoria persistente.

Patrón: métodos estáticos, retorna ToolResult, lee/escribe archivos Markdown.
No toma decisiones sobre QUÉ guardar — eso lo hacen las capas A/B/C.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from agent.core._result import ToolResult, Timer

# ─── Configuración ───────────────────────────────────────────────────────────

MEMORY_DIR = Path(os.environ.get(
    "NAS_AGENT_MEMORY_DIR",
    str(Path(__file__).parent.parent / "memory")
))
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
USER_FILE = MEMORY_DIR / "USER.md"
SKILLS_FILE = MEMORY_DIR / "SKILLS.md"
SESSIONS_DIR = MEMORY_DIR / "sessions"

# Límites
MAX_MEMORY_KB = 50
MAX_USER_KB = 10
MAX_SKILLS_KB = 100
MAX_SESSIONS_TOTAL_KB = 500

VALID_CATEGORIES = {"entorno", "leccion", "patron", "pendiente"}


class MemoryManager:
    """Gestión CRUD de archivos de memoria. Sin estado."""

    # ── Inicialización ──────────────────────────────────────────────────

    @staticmethod
    def ensure_initialized():
        """Crea estructura de memoria si no existe."""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        SESSIONS_DIR.mkdir(exist_ok=True)

        if not MEMORY_FILE.exists():
            MEMORY_FILE.write_text(
                "# Memoria del Agente NAS\n"
                f"> Última actualización: {_now()}\n\n"
                "## Entorno\n\n"
                "## Lecciones aprendidas\n\n"
                "## Patrones que funcionaron\n\n"
                "## Estado pendiente\n",
                encoding="utf-8",
            )
        if not USER_FILE.exists():
            USER_FILE.write_text(
                "# Perfil del Usuario\n"
                f"> Última actualización: {_now()}\n\n"
                "## Preferencias de interacción\n\n"
                "## Decisiones técnicas\n\n"
                "## Proyectos activos\n",
                encoding="utf-8",
            )
        if not SKILLS_FILE.exists():
            SKILLS_FILE.write_text(
                "# Skills del Agente NAS\n"
                f"> Total: 0 skills | Última actualización: {_now()}\n",
                encoding="utf-8",
            )

    # ── MEMORY.md ───────────────────────────────────────────────────────

    @staticmethod
    def load_memory() -> str:
        """Carga MEMORY.md completo."""
        MemoryManager.ensure_initialized()
        return MEMORY_FILE.read_text(encoding="utf-8")

    @staticmethod
    def load_memory_section(section: str) -> str:
        """Carga solo una sección de MEMORY.md (ej: 'Entorno')."""
        content = MemoryManager.load_memory()
        pattern = rf"## {re.escape(section)}\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def add_to_memory(fact: str, category: str, timestamp: str) -> ToolResult:
        """Agrega un hecho a la sección correspondiente de MEMORY.md."""
        MemoryManager.ensure_initialized()

        if category not in VALID_CATEGORIES:
            return ToolResult.error(
                f"Categoría '{category}' inválida. Válidas: {VALID_CATEGORIES}",
                tool_name="remember",
            )

        if len(fact) > 200:
            return ToolResult.error(
                "El hecho es demasiado largo (máx 200 chars). Sé conciso.",
                tool_name="remember",
            )

        # Verificar tamaño
        current_size = MEMORY_FILE.stat().st_size / 1024
        if current_size >= MAX_MEMORY_KB:
            return ToolResult.warn(
                f"MEMORY.md alcanzó {current_size:.1f} KB (límite: {MAX_MEMORY_KB} KB). "
                "Ejecutar curación antes de agregar más.",
                tool_name="remember",
            )

        section_map = {
            "entorno": "## Entorno",
            "leccion": "## Lecciones aprendidas",
            "patron": "## Patrones que funcionaron",
            "pendiente": "## Estado pendiente",
        }

        content = MEMORY_FILE.read_text(encoding="utf-8")
        section_header = section_map[category]
        entry = f"- [{timestamp[:10]}] {fact}\n"

        # Insertar después del header de sección
        idx = content.find(section_header)
        if idx == -1:
            content += f"\n{section_header}\n{entry}"
        else:
            insert_pos = content.find("\n", idx) + 1
            content = content[:insert_pos] + entry + content[insert_pos:]

        # Actualizar timestamp global
        content = re.sub(
            r"> Última actualización: .*",
            f"> Última actualización: {timestamp}",
            content,
        )

        MEMORY_FILE.write_text(content, encoding="utf-8")

        return ToolResult.ok(
            f"✅ Guardado en MEMORY.md [{category}]: {fact}",
            data={"category": category, "fact": fact},
            tool_name="remember",
        )

    # ── USER.md ─────────────────────────────────────────────────────────

    @staticmethod
    def load_user_model() -> str:
        """Carga USER.md completo."""
        MemoryManager.ensure_initialized()
        return USER_FILE.read_text(encoding="utf-8")

    @staticmethod
    def update_user_model(key: str, value: str) -> ToolResult:
        """Actualiza o agrega una preferencia en USER.md."""
        MemoryManager.ensure_initialized()

        content = USER_FILE.read_text(encoding="utf-8")

        # Buscar si la key ya existe (formato: "- Key: valor")
        pattern = rf"^- {re.escape(key)}:.*$"
        new_line = f"- {key}: {value}"

        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
            action = "actualizado"
        else:
            # Agregar al final de "Decisiones técnicas" o al final
            if "## Decisiones técnicas" in content:
                idx = content.find("## Decisiones técnicas")
                next_section = content.find("\n## ", idx + 1)
                insert_pos = next_section if next_section != -1 else len(content)
                content = content[:insert_pos] + f"{new_line}\n" + content[insert_pos:]
            else:
                content += f"\n{new_line}\n"
            action = "agregado"

        # Actualizar timestamp
        content = re.sub(
            r"> Última actualización: .*",
            f"> Última actualización: {_now()}",
            content,
        )

        USER_FILE.write_text(content, encoding="utf-8")

        return ToolResult.ok(
            f"✅ USER.md {action}: {key} = {value}",
            data={"key": key, "value": value, "action": action},
            tool_name="update_user_model",
        )

    # ── SKILLS.md ───────────────────────────────────────────────────────

    @staticmethod
    def load_skills() -> str:
        """Carga SKILLS.md completo."""
        MemoryManager.ensure_initialized()
        return SKILLS_FILE.read_text(encoding="utf-8")

    @staticmethod
    def add_skill(name: str, procedure: str, trigger: str) -> ToolResult:
        """Crea un skill nuevo en SKILLS.md."""
        MemoryManager.ensure_initialized()

        content = SKILLS_FILE.read_text(encoding="utf-8")

        # Verificar duplicado
        if f"## skill: {name}" in content:
            return ToolResult.warn(
                f"Skill '{name}' ya existe. Usa update_skill() para modificarlo.",
                tool_name="learn_skill",
            )

        # Verificar tamaño
        current_size = SKILLS_FILE.stat().st_size / 1024
        if current_size >= MAX_SKILLS_KB:
            return ToolResult.warn(
                f"SKILLS.md alcanzó {current_size:.1f} KB. Curar antes de agregar.",
                tool_name="learn_skill",
            )

        timestamp = _now()[:10]
        skill_entry = (
            f"\n---\n\n"
            f"## skill: {name}\n"
            f"> Aprendido: {timestamp} | Usado: 0 veces | Último uso: nunca\n"
            f"> Trigger: \"{trigger}\"\n\n"
            f"### Procedimiento\n{procedure}\n"
        )

        content += skill_entry

        # Actualizar contador en header
        skill_count = content.count("## skill: ")
        content = re.sub(
            r"> Total: \d+ skills",
            f"> Total: {skill_count} skills",
            content,
        )

        SKILLS_FILE.write_text(content, encoding="utf-8")

        return ToolResult.ok(
            f"✅ Skill '{name}' creado (trigger: \"{trigger}\")",
            data={"name": name, "trigger": trigger},
            tool_name="learn_skill",
        )

    # ── Sessions ────────────────────────────────────────────────────────

    @staticmethod
    def save_session(title: str, content: str) -> ToolResult:
        """Guarda un resumen de sesión en sessions/."""
        MemoryManager.ensure_initialized()

        date = _now()[:10]
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:50]
        filename = f"{date}_{slug}.md"
        filepath = SESSIONS_DIR / filename

        filepath.write_text(content, encoding="utf-8")

        return ToolResult.ok(
            f"✅ Sesión guardada: sessions/{filename}",
            data={"file": filename},
            tool_name="save_session",
        )

    # ── Búsqueda (recall) ───────────────────────────────────────────────

    @staticmethod
    def recall(query: str) -> ToolResult:
        """Busca en toda la memoria por relevancia."""
        MemoryManager.ensure_initialized()

        results = []
        query_lower = query.lower()
        keywords = query_lower.split()

        # 1. Buscar en SKILLS (por trigger — máxima prioridad)
        skills_content = MemoryManager.load_skills()
        for skill_block in skills_content.split("## skill: ")[1:]:
            lines = skill_block.strip().split("\n")
            skill_name = lines[0].strip()
            trigger_line = next((l for l in lines if "Trigger:" in l), "")
            if any(kw in trigger_line.lower() or kw in skill_name.lower() for kw in keywords):
                results.append(f"📚 SKILL: {skill_name}\n{''.join(lines[:15])}")

        # 2. Buscar en MEMORY.md (por keyword)
        memory_content = MemoryManager.load_memory()
        for line in memory_content.splitlines():
            if line.startswith("- ") and any(kw in line.lower() for kw in keywords):
                results.append(f"🧠 MEMORIA: {line.strip()}")

        # 3. Buscar en sessions/ (grep simple)
        if SESSIONS_DIR.exists():
            for session_file in sorted(SESSIONS_DIR.glob("*.md"), reverse=True)[:20]:
                session_content = session_file.read_text(encoding="utf-8")
                if any(kw in session_content.lower() for kw in keywords):
                    # Extraer título
                    first_line = session_content.splitlines()[0] if session_content else ""
                    results.append(f"📝 SESIÓN ({session_file.name}): {first_line}")

        if not results:
            return ToolResult.ok(
                f"No encontré nada relevante para: \"{query}\"\n"
                "Esto es un problema nuevo — resuélvelo y usa remember()/learn_skill() después.",
                data={"found": False, "query": query},
                tool_name="recall",
            )

        return ToolResult.ok(
            f"=== RESULTADOS PARA: \"{query}\" ===\n\n"
            + "\n\n".join(results[:10]),
            data={"found": True, "count": len(results), "query": query},
            tool_name="recall",
        )

    # ── Stats ───────────────────────────────────────────────────────────

    @staticmethod
    def get_memory_stats() -> dict:
        """Retorna estadísticas del sistema de memoria."""
        MemoryManager.ensure_initialized()

        memory_kb = MEMORY_FILE.stat().st_size / 1024 if MEMORY_FILE.exists() else 0
        user_kb = USER_FILE.stat().st_size / 1024 if USER_FILE.exists() else 0
        skills_kb = SKILLS_FILE.stat().st_size / 1024 if SKILLS_FILE.exists() else 0

        skills_content = SKILLS_FILE.read_text(encoding="utf-8") if SKILLS_FILE.exists() else ""
        skill_count = skills_content.count("## skill: ")

        sessions = list(SESSIONS_DIR.glob("*.md")) if SESSIONS_DIR.exists() else []
        sessions_kb = sum(f.stat().st_size for f in sessions) / 1024

        return {
            "memory_kb": memory_kb,
            "user_kb": user_kb,
            "skills_kb": skills_kb,
            "skill_count": skill_count,
            "sessions_count": len(sessions),
            "sessions_kb": sessions_kb,
            "total_kb": memory_kb + user_kb + skills_kb + sessions_kb,
        }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
