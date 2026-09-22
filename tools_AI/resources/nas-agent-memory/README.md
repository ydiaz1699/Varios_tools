# NAS Agent Memory — Sistema de Auto-Mejora (Learning Loop)

> **Estado**: Documentación de diseño (pre-implementación)
> **Destino final**: `agent/` en [ydiaz1699/nas-dotfiles](https://github.com/ydiaz1699/nas-dotfiles)
> **Inspirado en**: [Hermes Agent](https://hermes-agent.nousresearch.com/) (Nous Research) — adaptado para Strands Agents SDK
> **Fecha**: 2026-08-01

---

## Resumen Ejecutivo

Este módulo agrega un **sistema de memoria persistente y auto-mejora** al agente NAS,
permitiéndole:

- **Recordar** lecciones, soluciones y contexto entre sesiones.
- **Aprender** procedimientos (skills) de las tareas que resuelve exitosamente.
- **Modelar al usuario** (preferencias, nivel técnico, decisiones).
- **Auto-curarse** eliminando memoria obsoleta y consolidando conocimiento.

El resultado es un agente que **mejora con el uso** — cada problema resuelto
lo hace más efectivo la próxima vez que se enfrenta a algo similar.

---

## ¿Por qué?

### El problema hoy

El agente NAS (Strands SDK) es **stateless entre sesiones**:

```
Sesión 1: usuario pregunta "¿por qué emqx no arranca?" → agente investiga → resuelve (OOM)
Sesión 2: usuario pregunta "emqx caído de nuevo" → agente empieza DE CERO (no recuerda la solución)
```

### Con memoria

```
Sesión 1: resuelve OOM → remember("emqx requiere ≥512MB") + learn_skill("diagnosticar-emqx-oom")
Sesión 2: recall("emqx caído") → encuentra skill → aplica directamente → resuelto en segundos
```

---

## Arquitectura del Learning Loop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LEARNING LOOP                                     │
│                                                                          │
│   ┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐   │
│   │  ACTUAR │─────►│REFLEXIONAR│─────►│ PERSISTIR│─────►│  CURAR   │   │
│   │         │      │           │      │          │      │          │   │
│   │ Resolver│      │ ¿Fue útil?│      │ Guardar  │      │ Limpiar  │   │
│   │ el      │      │ ¿Nuevo?   │      │ en       │      │ obsoleto │   │
│   │ problema│      │ ¿Complejo?│      │ MEMORY/  │      │ cada 24h │   │
│   └─────────┘      └──────────┘      │ SKILLS   │      └─────┬────┘   │
│        ▲                              └──────────┘            │        │
│        │                                                      │        │
│        │              ┌──────────┐                            │        │
│        └──────────────│ RECORDAR │◄───────────────────────────┘        │
│                       │          │                                      │
│                       │ Antes de │                                      │
│                       │ actuar:  │                                      │
│                       │ recall() │                                      │
│                       └──────────┘                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Las 3 capas del "nudge" (cuándo guardar)

El sistema usa **3 mecanismos complementarios** para asegurar que la memoria se
popula de forma confiable:

| Capa | Mecanismo | Cuándo | Propósito |
|------|-----------|--------|-----------|
| **A** | System prompt | Cada interacción | El modelo PUEDE recordar por iniciativa propia |
| **B** | Event-driven | Post-tarea compleja | GARANTIZA que soluciones difíciles se persistan |
| **C** | Schedule | Cada 24h | MANTIENE la calidad, elimina ruido, consolida |

**A** = "el modelo puede recordar"
**B** = "el sistema obliga a recordar cuando importa"
**C** = "el sistema limpia y mantiene la calidad"

Detalle completo: [`docs/02-nudge-layers.md`](docs/02-nudge-layers.md)

---

## Componentes del sistema de memoria

```
agent/memory/                      ← directorio de estado persistente
├── MEMORY.md                      ← conocimiento del agente (entorno, lecciones, patrones)
├── USER.md                        ← modelo del usuario (preferencias, nivel, decisiones)
├── SKILLS.md                      ← procedimientos aprendidos (cómo resolvió X)
└── sessions/                      ← historial resumido de sesiones pasadas
    ├── 2026-08-01_backup-fix.md
    ├── 2026-08-02_emqx-oom.md
    └── ...
```

| Archivo | Propósito | Quién lo escribe | Cuándo se lee |
|---------|-----------|------------------|---------------|
| `MEMORY.md` | Hechos, lecciones, estado del entorno | Tools `remember()` + curación | Inicio de sesión + `recall()` |
| `USER.md` | Preferencias y perfil del usuario | Tool `update_user_model()` | Inicio de cada sesión (system prompt) |
| `SKILLS.md` | Procedimientos reutilizables paso a paso | Tool `learn_skill()` + auto-skill (capa B) | `recall()` cuando un problema matchea |
| `sessions/` | Resúmenes de sesiones pasadas | Capa B (al finalizar sesión) | `recall()` para búsqueda full-text |

Detalle completo: [`docs/01-memory-system.md`](docs/01-memory-system.md)

---

## Integración con el agente NAS

### Archivos a crear en `nas-dotfiles`

```
agent/
├── core/
│   └── memory.py              ← MemoryManager (CRUD sobre archivos de memoria)
├── tools/
│   └── memory_tools.py        ← @tool: remember, recall, learn_skill, update_user_model
├── plugins/
│   └── memory_plugin.py       ← Registra tools + events (capa B) + schedule (capa C)
└── memory/                    ← Datos persistentes (gitignored o versionados, tu decisión)
    ├── MEMORY.md
    ├── USER.md
    ├── SKILLS.md
    └── sessions/
```

### Patrón que sigue

Idéntico al resto del agente:
- **MemoryManager** (core) → métodos estáticos, retorna `ToolResult`
- **memory_tools.py** (tools) → `@tool` wrappers que delegan al Manager
- **MemoryPlugin** (plugin) → auto-descubierto por `PluginLoader`, registra tools + events + schedules

### Dependencias

- **Ninguna dependencia externa nueva** — solo lectura/escritura de archivos Markdown.
- Opcional (futuro): `sqlite3` para FTS5 full-text search sobre `sessions/`.
- Compatible con el `EventBus` y `ScheduleConfig` existentes.

Detalle completo: [`docs/03-implementation-guide.md`](docs/03-implementation-guide.md)

---

## Diferencias con Hermes Agent

| Aspecto | Hermes (built-in) | Este diseño (Strands SDK) |
|---------|-------------------|---------------------------|
| Formato de memoria | Markdown (MEMORY.md) | Markdown (igual) |
| Búsqueda | FTS5 SQLite nativo | Simple grep/keyword → FTS5 opcional |
| Auto-skill creation | Automático (el modelo crea skills sin pedir) | Semi-auto (capa B sugiere, modelo confirma) |
| Curación | Built-in, opaco | Explícito, auditable (schedule visible) |
| Modelo del usuario | USER.md + Honcho + plugins de memoria | USER.md (simple, suficiente para homelab) |
| Cross-session recall | Búsqueda sobre historial completo | Resúmenes en `sessions/` + grep |
| Complejidad | Alta (muchas capas, memory providers) | Baja-Media (solo archivos + 3 tools) |

**Filosofía**: Hermes es un producto terminado con muchas capas. Este diseño busca
el **80% del valor con el 20% de la complejidad** — archivos Markdown planos que
cualquier LLM futuro puede leer directamente.

---

## Estado de la documentación

| Documento | Contenido |
|-----------|-----------|
| [`docs/01-memory-system.md`](docs/01-memory-system.md) | Diseño de MEMORY.md, USER.md, SKILLS.md, sessions/ |
| [`docs/02-nudge-layers.md`](docs/02-nudge-layers.md) | Las 3 capas (A+B+C) con ejemplos completos |
| [`docs/03-implementation-guide.md`](docs/03-implementation-guide.md) | Archivos a crear, integración, system prompt, tests |
| [`reference/code-base/`](reference/code-base/) | Código Python de referencia listo para integrar |

---

## Orden de implementación recomendado

| Paso | Complejidad | Impacto | Descripción |
|------|-------------|---------|-------------|
| 1 | Baja | Alto | Crear archivos `MEMORY.md`, `USER.md`, `SKILLS.md` (vacíos con estructura) |
| 2 | Baja | Alto | Implementar `memory_tools.py` (`remember`, `recall`, `learn_skill`) |
| 3 | Baja | Medio | Agregar instrucciones al system prompt (capa A) |
| 4 | Media | Alto | Implementar `MemoryPlugin` con EventHandler (capa B) |
| 5 | Media | Medio | Agregar ScheduleConfig para curación (capa C) |
| 6 | Alta | Medio | (Opcional) FTS5 index sobre sessions/ para búsqueda avanzada |

---

## Referencias

- [Hermes Agent — Memory System](https://hermes-agent.nousresearch.com/docs/user-guide/features/overview)
- [Hermes Agent — Skills System](https://hermes-agent.nousresearch.com/docs/)
- [Strands Agents SDK](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)
- [agentskills.io](https://agentskills.io) — estándar abierto de skills (compatible con Hermes)
