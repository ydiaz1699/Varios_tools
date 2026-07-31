# Checklist para Agente en Producción

> **Cuándo usar este bloque:** Antes de hacer deploy de un agente Strands a producción. Recorre esta lista para verificar que no falte nada crítico — cada item es un patrón validado en producción real.

---

## Checklist

```
[ ] FileSessionManager para memoria entre invocaciones
[ ] agent_id fijo para ruta de sesión consistente
[ ] System prompt en modo ejecutivo (actuar, no sugerir)
[ ] Sanitización de .env en 3 capas (export, read, scan)
[ ] Core layer separado de @tool
[ ] ToolResult estructurado (no strings crudos)
[ ] safe_run(shell=False) para todo subprocess
[ ] validate_service_name() contra path traversal
[ ] readonly_guard() para modo seguro
[ ] Lista explícita de tools que requieren confirmación
[ ] Repetir reglas críticas en el prompt para modelos lite
[ ] Lazy imports para evitar circular dependencies
```

---

## Detalle de cada item

### FileSessionManager
El agente recuerda entre invocaciones CLI. Sin esto, cada llamada es independiente.
→ Ver bloque: `blocks/production/session.md`

### agent_id fijo
Garantiza que la sesión se guarde en la misma ruta siempre. Sin `agent_id`, la ruta cambia y se pierde el historial.

### System prompt modo ejecutivo
El agente ACTÚA en vez de sugerir. Sin esto, pregunta "¿quieres que...?" para todo.
→ Ver bloque: `blocks/production/executive-mode.md`

### Sanitización de .env en 3 capas
Evita que secrets lleguen al LLM. Tres puntos: export, lectura, output de tools.
→ Ver bloque: `blocks/production/credentials.md`

### Core layer separado
Tools de 5 líneas que delegan a un core testeable. Permite testing sin Strands.
→ Ver bloque: `blocks/production/core-layer.md`

### ToolResult estructurado
Dataclass con `success`, `message`, `data`, `suggestions`. `__str__()` devuelve el mensaje para compatibilidad con Strands.

### safe_run(shell=False)
**NUNCA** usar `shell=True` con input que viene del LLM. Riesgo de inyección de comandos.

```python
def safe_run(args: list[str], timeout: int = 120) -> str:
    result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=timeout)
    return result.stdout
```

### validate_service_name()
Prevenir path traversal — el LLM podría pasar `../../etc/passwd` como nombre de servicio.

```python
def validate_service_name(name: str) -> str | None:
    """Retorna error si el nombre es inválido, None si OK."""
    if "/" in name or ".." in name:
        return f"Nombre inválido: {name}"
    if not Path(f"/docker/{name}").exists():
        return f"Servicio no encontrado: {name}"
    return None
```

### readonly_guard()
Modo seguro donde el agente solo puede leer, no modificar. Útil para demos o testing.

### Lista explícita de tools que requieren confirmación
En el system prompt, listar exactamente qué tools son destructivas (necesitan OK del usuario) vs seguras (ejecutar sin preguntar).

### Repetir reglas críticas
Gemini Flash Lite y otros modelos ligeros ignoran instrucciones largas. Repetir con "⚠️ REPITO:" y dar ejemplos ❌/✅.

### Lazy imports
Evitar `ImportError` por circular dependencies entre tools y core.

```python
def _get_manager():
    from agent.core.manager import Manager
    return Manager
```

---

## Orden recomendado de implementación

1. **Primero:** Core layer + ToolResult (arquitectura base)
2. **Segundo:** Tools con safe_run + validation
3. **Tercero:** Session manager
4. **Cuarto:** System prompt modo ejecutivo
5. **Quinto:** Sanitización de credenciales
6. **Último:** Lazy imports + ajustes para modelos lite
