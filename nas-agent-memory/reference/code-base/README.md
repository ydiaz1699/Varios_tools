# Código de referencia: Memory Plugin para el Agente NAS

> **Estado**: Listo para integrar (requiere ajuste de imports al mover a nas-dotfiles)
> **Destino final**: `agent/` en [ydiaz1699/nas-dotfiles](https://github.com/ydiaz1699/nas-dotfiles)

## Archivos

| Archivo | Capa | Descripción |
|---------|------|-------------|
| `memory.py` | Core | MemoryManager — CRUD sobre MEMORY.md, USER.md, SKILLS.md, sessions/ |
| `memory_tools.py` | Tools | `@tool` wrappers: remember, recall, learn_skill, update_user_model, memory_stats |
| `memory_plugin.py` | Plugin | Registra tools + events (Capa B) + schedule (Capa C) |

## Patrón

```
MemoryManager (core) → memory_tools.py (@tool wrappers) → MemoryPlugin (registro)
```

Idéntico a: `BackupManager` → `backup_tools.py` → `BackupPlugin`

## Dependencias

- **Ninguna externa** — solo `pathlib`, `re`, `datetime` (stdlib)
- Interna: `agent.core._result.ToolResult`, `agent.plugins.base.*`

## Para integrar

1. Copiar `memory.py` → `agent/core/memory.py`
2. Copiar `memory_tools.py` → `agent/tools/memory_tools.py`
3. Copiar `memory_plugin.py` → `agent/plugins/memory_plugin.py`
4. Crear directorio `agent/memory/` (o configurar `NAS_AGENT_MEMORY_DIR`)
5. Agregar instrucciones de Capa A al system prompt (ver docs/03)
6. El PluginLoader lo descubre automáticamente
