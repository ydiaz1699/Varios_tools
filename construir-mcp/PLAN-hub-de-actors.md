# PLAN — Hub de "actors" con UN solo conector MCP (Apify self-hosted, por fases)

> **Estado:** planificado, NO desarrollado. Para retomar en un CHAT NUEVO dedicado.
> **Fecha:** 2026-09-28
> **Autor del contexto:** ydiaz1699 (destilado de la sesión donde surgió la idea).
> **Relación:** es un **tercer patrón** de MCP, complementario a los ya anotados en
> [`PROYECTO-guia-construir-mcp.md`](./PROYECTO-guia-construir-mcp.md) (MCP tipo-API) y
> [`PLAN-mcp-indexador-nodos.md`](./PLAN-mcp-indexador-nodos.md) (MCP indexador).

---

## 1. La idea (qué pidió el usuario)

Montar en el NAS una **infraestructura similar a Apify**: **UN solo conector MCP** para el LLM
y, por detrás, **N "actors"** que el usuario va creando (como el de descargar YouTube, subir con
rclone, transcribir…). Añadir un actor nuevo NO debe requerir tocar la configuración de Kiro:
solo escribir el actor y registrarlo.

```
┌─────────────┐   un solo conector MCP   ┌──────────────────────────┐
│  LLM (Kiro) │ ───────────────────────▶ │  Hub MCP (1 server)      │
└─────────────┘                          │   actors/                │
                                         │    ├── rclone_sync       │
                                         │    ├── youtube_download  │
                                         │    ├── transcribe        │
                                         │    └── …(se van añadiendo)│
                                         └──────────────────────────┘
```

### Motivación de origen
El actor `streamers/youtube-video-downloader` de Apify **NO es open source ni self-hostable**:
es un Actor de pago (≈ $0.006/MB, código cerrado, corre en infra de Apify, output temporal ~3 días).
Verificado en su ficha oficial. Lo que SÍ es libre es **yt-dlp** (la herramienta real que hay debajo).
De ahí nace la idea de tener "actors propios" en el NAS.

---

## 2. Distinción de seguridad clave (por qué NO es como el socket de Docker)

El usuario tiene una **regla firme: no usar el socket de Docker** (`/var/run/docker.sock`) por
seguridad. Aclaración importante para no confundir con el modelo Apify:

- **Socket de Docker = peligroso**: es la API del daemon (root en el host). Quien lo controla puede
  pedir montar `/` del host, lanzarse `privileged`… → **acceso al socket ≈ root en el host**.
- **Modelo Apify = seguro con código ajeno** porque **el creador del actor NUNCA toca el daemon**:
  solo aporta CÓDIGO; la **plataforma** decide cómo se ejecuta (sin socket, sin privileged, con
  límites). Además usa **sandbox reforzado** (gVisor / Firecracker microVMs / Kata) = una barrera
  extra sobre el kernel. El actor solo ve su **input** y su **storage** del run; no ve el host ni a
  otros usuarios. La confianza no está en "el creador es bueno", está en "el creador no tiene
  permisos para hacer daño aunque quiera".

**Consecuencia para este proyecto:** en la Fase A todos los actors son **del propio usuario**
(código confiable) → NO hace falta socket ni microVMs. El aislamiento fuerte solo se justifica en
la Fase B (terceros). Y **nunca** con el socket crudo: se hace con namespaces/microVMs.

---

## 3. Las dos arquitecturas (decididas con el usuario)

### Arquitectura A — "actors" = tools de un mismo MCP  ← EMPEZAR AQUÍ
Un solo servidor MCP (Python/FastMCP, patrón ya dominado con nextdns). Cada actor = un módulo con
su **lógica pura** + su registro como tool. Reutiliza el patrón de 2 capas del ecosistema.

- **Ventaja:** simple, un proceso, reusa TODO el patrón de integración a Kiro ya montado.
- **Límite:** todos los actors comparten proceso/entorno Python (aceptable: son del usuario).

### Arquitectura B — "actors" = ejecución aislada (parecido a Apify de verdad)  ← FASE FUTURA
Cada actor corre aislado. **NO con el socket de Docker**. Opciones seguras: **Podman rootless**,
**socket-proxy** (mitiga, no elimina), o un sandbox FaaS dedicado (ver §6).

**Decisión del usuario:** empezar por **A**, pero **diseñar A para poder migrar a B sin reescribir**
(ver §5). Para la Fase B el usuario **cambiará de hardware** (el NAS actual — Dell T20, 2 cores,
8 GB RAM — no da para microVMs por run).

---

## 4. FASE A — Primer actor real: **rclone**

El primer actor es **rclone**, reutilizando lo YA montado y verificado (ver
[`../rclone-mcp-control-total/README.md`](../rclone-mcp-control-total/README.md)):

- Ya existe en el NAS: daemon `rclone rcd` (RC API en `:5572`, imagen `rclone/rclone:1.75.1`,
  red `db_net`) + un MCP server que traduce tools → RC API.
- **La "lógica pura" del actor rclone ya está resuelta por la RC API.** El `core.py` del actor
  solo tiene que llamar a la RC API (HTTP a `http://rclone-rcd:5572`) con el input y devolver el
  output. NO reimplementar rclone.

> **PENDIENTE de confirmar con el usuario (arranque de Fase A):** ¿qué hace exactamente el primer
> actor rclone? Candidatos: `sync`/`copy` entre remotes, subir un archivo, listar. El usuario dijo
> "sí" a definirlo pero falta fijar la operación concreta para que `core.py` resuelva algo real.

---

## 5. La clave: hacer A compatible con B SIN reescribir (contrato de actor portable)

Principio (= patrón de 2 capas del usuario): **separar "qué hace el actor" de "quién lo ejecuta".**
El núcleo del actor **nunca cambia**; solo cambia el *adapter* que lo conecta a cada plataforma.

```
core.py  (lógica pura: input dict -> output dict; NO importa mcp ni apify)
   ├── mcp_adapter.py    → Fase A: lo expone como tool MCP
   ├── apify_adapter.py  → Fase B opción 1: Apify SDK  → Crawlee Cloud (drop-in, casi 0 cambios)
   └── http_adapter.py   → Fase B opción 2: handler HTTP → FaaS/microVM (FissionPlane, Orva…)
```

**Regla de oro:** `core.run(input: dict) -> dict`. No importa `mcp`, no importa `apify`. Los
adapters traducen. Migrar = escribir un adapter nuevo, **el core intacto**.

**Extra que ahorra dolor:** describir cada actor con un **`manifest.json`** (input_schema /
output_schema) al estilo del `INPUT_SCHEMA.json` + `.actor/actor.json` de Apify. Así ya "hablas el
idioma de Apify" sin usar Apify todavía → al migrar a Crawlee Cloud el manifest casi se copia.

### Estructura propuesta del hub
```
mi-hub/               # nombre/ubicación a decidir (§8)
├── server.py         # Fase A: FastMCP; carga los mcp_adapter de cada actor (UN conector)
├── actors/
│   └── rclone_sync/
│       ├── core.py       # lógica pura: run(input) -> output  (llama a la RC API de rclone)
│       └── manifest.json # input_schema / output_schema (estilo Apify)
├── adapters/
│   ├── mcp_adapter.py    # Fase A
│   ├── apify_adapter.py  # Fase B → Crawlee Cloud
│   └── http_adapter.py   # Fase B → FaaS/microVM
└── data/             # outputs a un volumen del NAS (sin expiración, a diferencia de Apify)
```

### ¿Cambia el código al migrar?
- **A → Crawlee Cloud:** casi **CERO** cambios si el core lee input/escribe output con el patrón
  Apify SDK (`Actor.getInput()` / `Actor.pushData()`). Crawlee Cloud es **drop-in del Apify SDK**:
  apuntas el SDK a tu servidor y funciona.
- **A → FissionPlane (Firecracker):** cambia el **adapter** (de MCP a handler HTTP), **no el core**.
  FissionPlane es un motor de sandbox genérico (microVMs), no habla "idioma Apify".

---

## 6. FASE B — self-hosted "tipo Apify" (candidatos verificados)

Todos verificados por búsqueda web (2026-09-28). **Ninguno usa el socket de Docker crudo**: el
aislamiento lo dan por diseño con namespaces / microVMs → compatible con la regla anti-socket.

| Proyecto | Qué es | Aislamiento | Nota |
|---|---|---|---|
| **Crawlee Cloud** (`crawlee-cloud/crawlee-cloud`) | **Plataforma** self-hosted estilo Apify (implementa la API de Apify open source, drop-in del Apify SDK) | El que traiga por debajo | **Modelo Actor** que le gusta al usuario. Verificar madurez antes de apostar. |
| **Orva** (`Harsh-2002/Orva`) | FaaS self-hosted (JS/TS/Python) | **nsjail** | Un contenedor da runtime + dashboard + CLI + **MCP server** + AI assistant. Muy alineado. |
| **FissionPlane** (`fissionplane.dev`) | FaaS/sandboxes para agentes | **Firecracker microVMs** | Aislamiento más fuerte (nivel Apify real). Necesita KVM + RAM → hardware nuevo. |
| **HakoRun** (`pardnchiu/HakoRun`) | FaaS en Go | **Bubblewrap** | Sin red saliente, caps dropped. |

### Aclaración importante: Crawlee Cloud vs FissionPlane NO compiten
- **Crawlee Cloud** = **plataforma** (alto nivel: modelo Actor, storages, API compatible Apify).
- **FissionPlane/Firecracker** = **motor de aislamiento** (bajo nivel: solo las cajas seguras).
- Lo ideal es **Crawlee Cloud como plataforma corriendo SOBRE Firecracker** por debajo. No es
  "uno u otro": Firecracker es el suelo, Crawlee Cloud es la casa.

### Recomendación por hardware
- **NAS actual (8 GB, sin holgura para KVM):** el aislamiento correcto NO es Firecracker
  (sobreingeniería + no cabe). Sería **nsjail/bubblewrap** (Orva/HakoRun) — "suficientemente
  fuerte" sin microVMs.
- **Hardware nuevo (plan del usuario para Fase B):** ahí sí **Firecracker** (nivel Apify real),
  idealmente con **Crawlee Cloud** encima como plataforma de actors.

---

## 7. Plan cuando se retome (Fase A)

1. **Confirmar la operación del actor rclone** (§4): sync / copy / upload / list — fijar una.
2. **Leer contra fuente real** (no de memoria): la RC API de rclone que usará el core
   (`../rclone-mcp-control-total/README.md` + doc oficial rclone rc), FastMCP (`jlowin/fastmcp`),
   y el formato `INPUT_SCHEMA.json` / `.actor/actor.json` de Apify (para el manifest portable).
3. **Escribir el hub** con la estructura de §5: `core.py` agnóstico + `manifest.json` + `mcp_adapter`
   + `server.py` (FastMCP). Contrato `run(input) -> output`.
4. **Integrar a Kiro CLI del NAS** con el patrón YA montado (mcp_tools/*.json + mcp-build +
   permissions.yaml + wrapper --env-file). Permisos V3: rclone lectura → `allow`; destructivas
   (delete/purge/sync/move/mount/config) → `ask` (reutilizar la clasificación ya hecha para rclone).
5. **Verificar en runtime** (como todo el ecosistema).
6. Repetir para el 2º actor (youtube_download con yt-dlp) reusando el mismo molde.

## 8. Decisiones pendientes con el usuario (antes de codificar)
- **Operación concreta del actor rclone** (§4).
- **Nombre y ubicación** del subproyecto: `Varios_tools/mi-hub-mcp/` o `Varios_tools/actor-hub/`
  (respetar regla: cada proyecto en su subcarpeta; nada suelto en la raíz de Varios_tools).
- **Dónde corre el hub:** Kiro CLI del NAS (donde ya vive el MCP de rclone). Kiro Web NO puede
  (sandbox cloud, sin ruta a la LAN privada — igual que rclone/n8n/nextdns).
- Confirmar destino de Fase B: **Crawlee Cloud** como plataforma (drop-in Apify) + **Firecracker**
  como aislamiento en el hardware nuevo.

---

---

## 8-bis. Patrón de referencia: Docker MCP Gateway (con su gotcha del socket)

El repo **`MariyaSha/Docker_MCPGUIApp`** (codebase del video que motivó la sesión) implementa el
mismo concepto "**un conector → N cosas**": una app Python habla con **UN** `docker/mcp-gateway`
que federa varios MCP servers (DuckDuckGo local, HuggingFace/Stripe remotos) declarados en un
**`catalog.yaml`**. Ficha: [`../tool_catalog/entries/docker-mcp-gateway-app.md`](../tool_catalog/entries/docker-mcp-gateway-app.md).

**Qué tomar de él:**
- La idea del **`catalog.yaml`** = registro declarativo de servers/actors → inspira el registro
  del hub (declarar actors en YAML en vez de hardcodearlos).
- La separación **app ↔ 1 gateway** (no la app contra cada server) = misma filosofía del contrato
  de actor portable (§5).

**Qué NO tomar (gotcha crítico):**
- Su compose monta **`/var/run/docker.sock`** en los dos gateways → **viola la regla anti-socket**.
  El Docker MCP Gateway lo necesita porque lanza cada MCP server como contenedor bajo demanda
  (controla el daemon). El hub propio logra "un conector → N" **sin** socket, con FastMCP + registry.
- Es un **federador** de MCPs que ya existen, **no un creador de actors** con lógica propia (que es
  lo que busca el hub). Docker federa; el hub fabrica.

> Moraleja: el Docker MCP Gateway resuelve "muchos MCPs, un endpoint" **a costa del socket**. El
> hub quiere lo mismo **sin** socket → por eso la Fase A es un MCP propio, no este gateway.

---

## 9. Referencias (verificar contra fuente real al retomar)
- Actor Apify (cerrado, de pago) que motivó todo: https://apify.com/streamers/youtube-video-downloader
- Herramienta libre real debajo: yt-dlp — https://github.com/yt-dlp/yt-dlp
- Plataforma self-hosted estilo Apify: https://github.com/crawlee-cloud/crawlee-cloud
- FaaS self-hosted con MCP integrado (nsjail): https://github.com/Harsh-2002/Orva
- FaaS/sandboxes microVM (Firecracker): https://fissionplane.dev/
- FaaS con Bubblewrap: https://github.com/pardnchiu/HakoRun
- rclone ya montado en el NAS: `../rclone-mcp-control-total/README.md`
- FastMCP: https://github.com/jlowin/fastmcp
- Patrón 2 capas / integración a Kiro: `./PROYECTO-guia-construir-mcp.md`, `../kiro-cli-nas/`
