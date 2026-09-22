# Las 3 Capas del Nudge: Cuándo y Cómo Guardar Memoria

> **Propósito**: Documentar los 3 mecanismos complementarios que aseguran
> que el agente persiste conocimiento de forma confiable.

---

## 1. Por qué 3 capas (no 1)

Ningún mecanismo solo es suficiente:


| Mecanismo solo | Falla cuando... |
|----------------|-----------------|
| Solo system prompt (A) | El modelo ignora la instrucción en tareas rutinarias |
| Solo event-driven (B) | El agente descubre algo sin "completar una tarea" oficialmente |
| Solo schedule (C) | No genera memoria nueva — solo limpia lo existente |

Combinadas:

```
A genera memoria → B la complementa y garantiza → C la mantiene limpia
```

---

## 2. Capa A: System Prompt (nudge pasivo)

### Qué es

Instrucciones en el system prompt que le dicen al modelo cuándo y cómo usar
las tools de memoria. El modelo decide por sí mismo si algo merece ser recordado.

### Texto a agregar al system prompt

```markdown
## Memoria Persistente

Tienes memoria entre sesiones. Úsala:

### Antes de actuar en un problema:
- `recall("descripción del problema")` → busca si ya lo resolviste antes
- Si hay un skill relevante, APLÍCALO directamente (no reinventes)

### Después de resolver algo complejo o descubrir algo nuevo:
- `remember("lo que aprendiste", category="leccion|patron|entorno")`
- Si resolviste un problema con >3 pasos → `learn_skill(nombre, procedimiento, trigger)`

### Cuando observes preferencias del usuario:
- `update_user_model("clave", "valor observado")`
- Solo hechos OBSERVADOS, nunca suposiciones

### NO guardar:
- Cosas triviales ("listé containers" → no merece memoria)
- Información que ya está en MEMORY.md (verificar con recall primero)
- Datos sensibles (passwords, tokens, IPs externas)
```

### Cuándo se activa

- **Cada interacción** — las instrucciones siempre están presentes.
- El modelo decide si actuar o no basado en la complejidad/novedad de la tarea.

### Ventajas

- Flexible: el modelo puede recordar CUALQUIER cosa que considere útil.
- Creativo: puede conectar patrones que la capa B no detectaría.
- Zero-code extra: solo texto en el system prompt.

### Limitaciones

- Depende de que el modelo "quiera" — no hay garantía.
- Modelos más baratos/rápidos tienden a ignorar instrucciones de memoria.
- Puede generar ruido si el modelo recuerda cosas triviales.

### Costo

- ~200 tokens en system prompt (una vez, fijo).
- ~50-100 tokens por llamada a `remember()` o `recall()` cuando el modelo decide usarlas.

---

## 3. Capa B: Event-Driven (nudge activo)

### Qué es

Un `EventHandler` en el plugin que se dispara automáticamente cuando se
cumplen condiciones específicas. No depende de que el modelo "quiera" — el
sistema OBLIGA la reflexión.

### Eventos que disparan memoria

| Evento | Condición | Acción |
|--------|-----------|--------|
| `task.completed` | tool_calls > 3 | Generar resumen de sesión + auto-skill |
| `task.completed` | involucró troubleshooting (error → fix) | Persistir lección en MEMORY.md |
| `user.correction` | El usuario dijo "no hagas X" / "prefiero Y" | Update USER.md |
| `tool.error_resolved` | Una tool falló → el agente lo arregló | Persistir "cómo se arregló" |
| `session.end` | Sesión con >5 intercambios significativos | Crear resumen en sessions/ |

### Implementación

```python
# agent/plugins/memory_plugin.py (extracto)

class MemoryPlugin(BasePlugin):
    meta = PluginMeta(name="memory", version="1.0.0", ...)

    def setup(self):
        # Tools
        self.register_tool(remember)
        self.register_tool(recall)
        self.register_tool(learn_skill)
        self.register_tool(update_user_model)

        # Capa B: eventos
        self.register_event(EventHandler(
            event_type="task.completed",
            handler=self._on_task_completed,
            description="Evaluar si la tarea merece ser recordada"
        ))
        self.register_event(EventHandler(
            event_type="user.correction",
            handler=self._on_user_correction,
            description="Persistir corrección del usuario en USER.md"
        ))
```

### Flujo de `_on_task_completed`

```python
async def _on_task_completed(self, event):
    tool_calls = event.data.get("tool_calls", 0)
    had_errors = event.data.get("errors_encountered", False)
    duration = event.data.get("duration_seconds", 0)

    # Criterio: ¿fue significativo?
    is_significant = (
        tool_calls > 3
        or had_errors  # troubleshooting = siempre valioso
        or duration > 300  # más de 5 minutos = probablemente complejo
    )

    if not is_significant:
        return  # No contaminar la memoria con ruido

    # Generar resumen de la sesión
    session_summary = await self._generate_session_summary(event)
    self._save_session(session_summary)

    # Si hubo troubleshooting, generar/actualizar skill
    if had_errors:
        skill = await self._generate_skill_from_task(event)
        if skill:
            self._save_skill(skill)
```

### Cuándo se activa

- **Automáticamente** después de que el agente completa una tarea.
- NO requiere decisión del modelo — es una red de seguridad.

### Ventajas

- **Garantiza** que las soluciones difíciles se persistan (el modelo no puede "olvidar").
- Genera skills automáticamente (el modelo no necesita hacerlo explícitamente).
- Detecta correcciones del usuario y actualiza USER.md.

### Limitaciones

- Requiere que el sistema de eventos esté funcionando (EventBus).
- Necesita criterios claros de "significativo" (evitar falsos positivos).
- La generación del resumen/skill consume una llamada extra al modelo.

### Costo

- 1 llamada al modelo por tarea significativa (~500-1000 tokens para generar resumen).
- Solo se activa en ~20% de las interacciones (las complejas).

---

## 4. Capa C: Schedule de Curación (mantenimiento)

### Qué es

Un `ScheduleConfig` que corre cada 24h y revisa/limpia/consolida la memoria.
No genera memoria nueva — mantiene la calidad de lo existente.

### Tareas de curación

| Tarea | Qué hace | Por qué |
|-------|----------|---------|
| **Eliminar obsoleto** | Borrar lecciones > 90 días sin referencia | Evitar acumulación infinita |
| **Consolidar duplicados** | Fusionar lecciones similares | "emqx OOM 512MB" + "emqx necesita más RAM" → 1 entrada |
| **Verificar skills** | ¿El skill sigue siendo válido? (tools existen, paths correctos) | Evitar aplicar procedimientos rotos |
| **Actualizar contadores** | Marcar skills no usados en >60 días | Candidatos a eliminación |
| **Verificar entorno** | ¿Los datos de "Entorno" en MEMORY.md siguen siendo correctos? | Docker se actualizó, IP cambió, etc. |
| **Trim sessions/** | Eliminar sesiones > 90 días | Liberar espacio; lecciones ya consolidadas |

### Implementación

```python
# agent/plugins/memory_plugin.py (extracto)

    def setup(self):
        # ... (tools y eventos) ...

        # Capa C: curación periódica
        self.register_schedule(ScheduleConfig(
            name="curate_memory",
            handler=self._curate_memory,
            interval_minutes=1440,  # cada 24h
            enabled=True,
            run_on_start=False,
        ))

    async def _curate_memory(self):
        """Curación diaria de la memoria."""
        memory = MemoryManager.load_memory()

        # 1. Eliminar lecciones viejas sin uso
        memory = self._prune_old_entries(memory, max_age_days=90)

        # 2. Consolidar duplicados (pedir al modelo que identifique similares)
        memory = await self._consolidate_duplicates(memory)

        # 3. Verificar skills (¿los paths/tools referenciados existen?)
        skills = MemoryManager.load_skills()
        skills = self._verify_skills(skills)

        # 4. Trim sessions viejas
        self._trim_old_sessions(max_age_days=90)

        # 5. Actualizar sección "Entorno" (verificar con comandos reales)
        await self._refresh_environment_info(memory)

        # 6. Persistir
        MemoryManager.save_memory(memory)
        MemoryManager.save_skills(skills)
```

### Cuándo se activa

- **Cada 24h** (configurable).
- `run_on_start=False`: no cursar al arrancar (podría ser lento).
- Si el agente estuvo apagado, se ejecuta en la próxima oportunidad.

### Ventajas

- Previene crecimiento infinito de la memoria.
- Mantiene skills actualizados (no aplica procedimientos obsoletos).
- Consolida automáticamente (menos ruido, más señal).
- Refresca info del entorno (detecta si Docker se actualizó, etc.).

### Limitaciones

- Consume una llamada al modelo para consolidación y verificación (~1000-2000 tokens).
- Puede eliminar algo que aún era útil (mitigación: ser conservador en eliminación).
- Solo mantiene, no crea.

### Costo

- 1 ejecución diaria: ~1000-2000 tokens (consolidación + verificación).
- Si no hay nada que curar: ~200 tokens (solo verificación rápida).

---

## 5. Diagrama de interacción entre las 3 capas

```
┌─── SESIÓN DEL AGENTE ───────────────────────────────────────────────┐
│                                                                      │
│  [Inicio]                                                            │
│     │                                                                │
│     ▼                                                                │
│  Cargar USER.md → system prompt                                      │
│  Cargar MEMORY.md (sección Entorno) → system prompt                  │
│  Incluir instrucciones de Capa A → system prompt                     │
│     │                                                                │
│     ▼                                                                │
│  ┌────────────────────────────────────────────────┐                  │
│  │ INTERACCIÓN                                     │                  │
│  │                                                 │                  │
│  │  Usuario: "emqx no arranca"                     │                  │
│  │     │                                           │                  │
│  │     ▼ [Capa A: modelo decide]                   │                  │
│  │  recall("emqx no arranca") ──► SKILLS.md        │                  │
│  │     │ → encuentra skill "diagnosticar-emqx-oom" │                  │
│  │     ▼                                           │                  │
│  │  Aplica el skill → resuelve rápido              │                  │
│  │     │                                           │                  │
│  │     ▼ [Capa A: modelo decide]                   │                  │
│  │  remember("emqx OOM de nuevo, misma causa")     │                  │
│  │  → actualiza contador en skill (+1 uso)         │                  │
│  └────────────────────────────┬───────────────────┘                  │
│                               │                                      │
│  [Fin de tarea]               ▼                                      │
│                    ┌──────────────────────┐                          │
│                    │ CAPA B: evento       │                          │
│                    │ task.completed       │                          │
│                    │ tool_calls=4 ✓       │                          │
│                    │ → generar resumen    │                          │
│                    │ → verificar skill    │                          │
│                    │   (ya existía, OK)   │                          │
│                    │ → save session       │                          │
│                    └──────────────────────┘                          │
└──────────────────────────────────────────────────────────────────────┘

┌─── FUERA DE SESIÓN (cada 24h) ──────────────────────────────────────┐
│                                                                      │
│  ┌──────────────────────────────────────┐                            │
│  │ CAPA C: curación                     │                            │
│  │                                      │                            │
│  │ • MEMORY.md: 45 KB → OK (< 50 KB)   │                            │
│  │ • Lecciones > 90 días: 2 → eliminar  │                            │
│  │ • Duplicados: "emqx OOM" × 3 → 1    │                            │
│  │ • Skills sin uso 60d: 0 → OK         │                            │
│  │ • Sessions > 90d: 5 → eliminar       │                            │
│  │ • Entorno: Docker 24.0.7 → 25.0.1   │                            │
│  │   (actualizar)                       │                            │
│  └──────────────────────────────────────┘                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 6. Configuración y tuning

### Umbrales de la capa B

```python
# Cuándo se considera "significativo"
SIGNIFICANCE_THRESHOLDS = {
    "min_tool_calls": 3,        # ≥3 tools usadas
    "min_duration_seconds": 300, # ≥5 minutos de sesión
    "errors_always_save": True,  # cualquier error resuelto = siempre guardar
}
```

### Parámetros de la capa C

```python
# Curación
CURATION_CONFIG = {
    "max_memory_kb": 50,         # límite de MEMORY.md
    "max_skills_kb": 100,        # límite de SKILLS.md
    "max_session_age_days": 90,  # eliminar sesiones antiguas
    "max_lesson_age_days": 90,   # eliminar lecciones sin uso reciente
    "skill_unused_warning_days": 60,  # marcar skill para revisión
    "curation_interval_minutes": 1440, # cada 24h
}
```

### Desactivar capas individualmente

```yaml
# agent/config/defaults.yml (sección de memoria)
memory:
  enabled: true
  layer_a:  # system prompt
    enabled: true
  layer_b:  # event-driven
    enabled: true
    min_tool_calls: 3
  layer_c:  # curación
    enabled: true
    interval_minutes: 1440
```

---

## 7. Ejemplo completo: primera vez vs segunda vez

### Primera vez (sin memoria)

```
Usuario: "jellyfin no muestra la biblioteca"
Agente:
  1. recall("jellyfin biblioteca") → NADA encontrado
  2. Investiga: docker logs, mountpoint, permisos...
  3. Descubre: /mnt/rclone/media no está montado (FUSE crasheó)
  4. Fix: fusermount -uz + systemctl restart rclone-media@media
  5. Verifica: Jellyfin ve archivos de nuevo
  6. [Capa A] remember("Si Jellyfin no ve biblioteca: verificar mount FUSE primero")
  7. [Capa A] learn_skill("jellyfin-sin-biblioteca", "1. mountpoint... 2. fusermount...")
  8. [Capa B] task.completed (tools=6, errors=true)
     → genera sesión en sessions/2026-08-01_jellyfin-mount.md
     → confirma que el skill se creó (ya lo hizo Capa A)
```

### Segunda vez (con memoria)

```
Usuario: "jellyfin no muestra la biblioteca de nuevo"
Agente:
  1. recall("jellyfin biblioteca") → ENCONTRADO: skill "jellyfin-sin-biblioteca"
  2. Aplica directamente:
     - mountpoint /mnt/rclone/media → "not a mountpoint" ✓ (confirmado)
     - fusermount -uz + restart
     - Verificar: Jellyfin ve archivos
  3. [Capa A] remember actualiza contador del skill (+1 uso)
  4. Resuelto en 30 segundos (vs 5 minutos la primera vez)
```

**Resultado**: El agente es ~10x más rápido la segunda vez. Con cada uso, el ratio mejora.
