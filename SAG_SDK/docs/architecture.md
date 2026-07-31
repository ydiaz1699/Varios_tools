# Diagramas de Arquitectura — Strands Agents SDK

Referencia visual de cómo se compone un agente Strands y cómo fluyen las interacciones.

---

## 1. Anatomía de un Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                          AGENT                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │  System      │    │   Model      │    │   Session    │     │
│   │  Prompt      │    │  (Provider)  │    │  Manager     │     │
│   │              │    │              │    │              │     │
│   │  Identidad   │    │  Gemini      │    │  Memoria     │     │
│   │  Reglas      │    │  Bedrock     │    │  entre       │     │
│   │  Formato     │    │  Ollama      │    │  invocaciones│     │
│   └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                  │
│   ┌──────────────────────────────────────────────────────┐      │
│   │                    TOOLS                              │      │
│   │                                                      │      │
│   │   @tool         @tool         McpClient              │      │
│   │   list_svc()    backup()     (servidor externo)      │      │
│   │                                                      │      │
│   └──────────────────────────────────────────────────────┘      │
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐                          │
│   │  Callback    │    │  Agent ID    │                          │
│   │  Handler     │    │  (sesión     │                          │
│   │  (output)    │    │   fija)      │                          │
│   └──────────────┘    └──────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Flujo de Tool Use (un turno)

```
Usuario: "¿Qué servicios están corriendo?"
         │
         ▼
┌─────────────────────┐
│  Agent recibe query  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LLM razona:        │
│  "Necesito llamar   │
│   list_services()"  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐      ┌─────────────────────┐
│  Strands ejecuta    │─────▶│  @tool              │
│  la tool            │      │  list_services()    │
└─────────────────────┘      │  → docker ps        │
          │                   └─────────┬───────────┘
          │                             │
          ▼                             ▼
┌─────────────────────┐      ┌─────────────────────┐
│  LLM recibe output  │◀─────│  "emqx: running     │
│  de la tool         │      │   plex: running     │
└─────────┬───────────┘      │   nginx: stopped"   │
          │                   └─────────────────────┘
          ▼
┌─────────────────────┐
│  LLM genera         │
│  respuesta final    │
│  al usuario         │
└─────────────────────┘
          │
          ▼
"Tienes 2 servicios corriendo (emqx, plex) y 1 detenido (nginx)."
```

---

## 3. Multi-tool (encadenamiento en un turno)

```
Usuario: "diagnostica nextcloud"
         │
         ▼
┌─────────────────────────────────────────────────┐
│  LLM razona: necesito 3 tools                    │
└─────────┬───────────────────────────────────────┘
          │
          ├──▶ troubleshoot("nextcloud")   → estado + health
          │
          ├──▶ service_logs("nextcloud")   → últimas 50 líneas
          │
          └──▶ read_compose("nextcloud")   → configuración
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  LLM analiza los 3 resultados juntos:            │
│  "Error: OOMKilled en logs, limit 256MB"         │
│  → Ejecuta service_update("nextcloud")           │
└─────────────────────────────────────────────────┘
          │
          ▼
"Nextcloud estaba crasheando por OOM. Actualicé el contenedor."
```

---

## 4. Arquitectura de capas (producción)

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERFAZ (CLI)                           │
│  main() → Rich UI → Panels/Markdown → Terminal               │
├─────────────────────────────────────────────────────────────┤
│                      AGENT LAYER                             │
│  Agent(model, tools, system_prompt, session_manager)         │
│  Prompt: Thinking + Bloques Dinámicos                        │
├─────────────────────────────────────────────────────────────┤
│                      TOOLS LAYER                             │
│  @tool decorators (5 líneas cada uno, solo delegan)          │
│  ALL_TOOLS = [tool1, tool2, ...]                             │
├─────────────────────────────────────────────────────────────┤
│                      CORE LAYER                              │
│  ServiceManager / BackupManager / ComposeManager             │
│  ToolResult dataclass                                        │
│  safe_run(shell=False)                                       │
├─────────────────────────────────────────────────────────────┤
│                      INFRASTRUCTURE                           │
│  Docker API / Filesystem / Network / subprocess              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Multi-Provider (selección dinámica)

```
                    NAS_AGENT_MODEL=?
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │  Gemini  │ │ Bedrock  │ │  Ollama  │
     │          │ │ (Claude) │ │ (local)  │
     │ $0.08/1M │ │ $3/1M   │ │  Gratis  │
     │ 500 RPD  │ │ Pay/use  │ │ Sin red  │
     │          │ │+thinking │ │          │
     └────┬─────┘ └────┬─────┘ └────┬─────┘
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
              ┌──────────────┐
              │    Agent     │
              │  (misma API) │
              └──────────────┘
```

---

## 6. Thinking + Bloques Dinámicos (prompt assembly)

```
agent "revisar emqx"
         │
         ▼
┌─────────────────────────────────────────────┐
│  Python: _classify_query("revisar emqx")     │
│  → Tipo: diagnóstico                         │
│  → Bloques: [identidad, reglas_core,         │
│              herramientas, diagnostico,       │
│              formato]                         │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  _assemble_prompt(bloques):                  │
│                                              │
│  ┌─────────────────────────────┐            │
│  │  THINKING_PROMPT            │  ← siempre │
│  │  "Confirma, planifica,      │            │
│  │   ejecuta"                  │            │
│  └─────────────────────────────┘            │
│  ┌─────────────────────────────┐            │
│  │  BLOCK_IDENTIDAD            │            │
│  │  BLOCK_REGLAS_CORE          │            │
│  │  BLOCK_HERRAMIENTAS         │  ← según  │
│  │  BLOCK_DIAGNOSTICO          │    query   │
│  │  BLOCK_FORMATO              │            │
│  └─────────────────────────────┘            │
└─────────────────────────────────────────────┘
         │
         ▼
    System Prompt ensamblado
    (solo lo relevante para ESTA tarea)
```

---

## 7. Sesión persistente (FileSessionManager)

```
Invocación 1:
  agent "revisar tasmoadmin"
         │
         ▼
  ┌──────────────┐     ┌─────────────────────┐
  │    Agent     │────▶│  ~/.nas-agent/       │
  │  diagnostica │     │  sessions/           │
  └──────────────┘     │  session_meta.json   │
                       └─────────────────────┘

Invocación 2 (minutos después):
  agent "sí reiniciar"
         │
         ▼
  ┌──────────────┐     ┌─────────────────────┐
  │    Agent     │◀────│  Lee sesión previa:  │
  │  recuerda    │     │  "hablaban de        │
  │  tasmoadmin  │     │   tasmoadmin"        │
  └──────────────┘     └─────────────────────┘
         │
         ▼
  service_restart("tasmoadmin")

30 min sin actividad → auto-reset
```

---

## 8. Seguridad (3 capas de credenciales)

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1: Export (para git/portabilidad)                      │
│  .env real → .env.example con __pega_aqui__                  │
├─────────────────────────────────────────────────────────────┤
│  CAPA 2: Lectura (lo que ve el LLM)                         │
│  read_file(".env") → valores sensibles = ***REDACTED***      │
├─────────────────────────────────────────────────────────────┤
│  CAPA 3: Output de tools (scan_compose, troubleshoot)        │
│  Variables en output → ***REDACTED***                        │
└─────────────────────────────────────────────────────────────┘

Resultado: las credenciales NUNCA llegan a la API del LLM
```

---

## 9. MCP (Model Context Protocol)

```
┌──────────────┐         ┌──────────────────────┐
│    Agent     │         │   MCP Server         │
│              │         │   (proceso aparte)    │
│  tools: [    │         │                      │
│    mcpClient │◀═══════▶│   Expone tools:      │
│  ]           │  stdio  │   - query_db()       │
│              │  o SSE  │   - list_tables()    │
└──────────────┘         │   - run_migration()  │
                         └──────────────────────┘

El agente descubre las tools del MCP server automáticamente.
Un agente puede conectar a múltiples MCP servers.
```

---

## 10. Multi-Agent (TypeScript)

```
┌─────────────────────────────────────────────────────────────┐
│  PATRÓN 1: Agent-as-tool                                     │
│                                                              │
│  Writer Agent                                                │
│    tools: [Researcher Agent]                                 │
│                                                              │
│  Writer decide cuándo usar al Researcher como herramienta    │
├─────────────────────────────────────────────────────────────┤
│  PATRÓN 2: Graph (pipeline)                                  │
│                                                              │
│  [Analyze] ──▶ [Summarize] ──▶ [Review]                     │
│                                                              │
│  Output de cada nodo pasa al siguiente (DAG)                 │
├─────────────────────────────────────────────────────────────┤
│  PATRÓN 3: Swarm (routing dinámico)                          │
│                                                              │
│         ┌──▶ [Billing Agent]                                │
│  [Triage] ──▶ [Support Agent]                               │
│         └──▶ [Sales Agent]                                  │
│                                                              │
│  Triage decide a quién enviar (LLM routing)                  │
└─────────────────────────────────────────────────────────────┘
```
