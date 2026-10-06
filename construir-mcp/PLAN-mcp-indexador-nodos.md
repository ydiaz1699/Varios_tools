# PLAN — Construir un MCP "indexador" (que el LLM conozca nodos/cards de una plataforma)

> **Estado:** plan aprobado, listo para ejecutar por fases. **Fecha:** 2026-09-24
> **Autor del enfoque:** ydiaz1699.
>
> Complementa `PROYECTO-guia-construir-mcp.md` (anatomía general de un MCP, patrón de
> 2 capas de nextdns). Este documento cubre un **tipo concreto** de MCP: el **indexador**,
> como `czlonkowski/n8n-mcp`, que le da al LLM conocimiento de los "nodos" de una
> plataforma para que **genere configuraciones correctas y no las invente**.

---

## 0. El problema que resuelve (motivación real)

Un LLM no conoce de memoria los ~525 nodos de n8n, ni las 19 cards de Mushroom, ni
los paquetes community. Ejemplo vivido: al mejorar un flujo, el asistente **no conocía
OpenWA** hasta que se le pasó el repo. Un **índice consultable** elimina ese problema:
el LLM busca el nodo/card real, lee sus parámetros exactos y genera config válida.

**Dos niveles de utilidad (independientes):**

| Nivel | Qué hace | Requiere API de escritura |
|---|---|---|
| **1 — Índice** | el LLM CONOCE los nodos → genera el JSON/YAML correcto que TÚ pegas | ❌ No |
| **2 — Índice + crear** | además APLICA la config vía API de la plataforma | ✅ Sí |

El **nivel 1 ya aporta ~80% del valor** y es mucho más fácil (no toca API de escritura).
Empezamos siempre por el nivel 1.

> **Nivel 2 — APIs de despliegue verificadas (2026-09-25):** n8n, Node-RED (`POST /flows`)
> y Flowise (`POST /api/v1/chatflows`) tienen API REST para crear/desplegar workflows → el
> Nivel 2 se hace por API, **sin automatizar el navegador**. Detalle y comandos en
> [`./HALLAZGO-apis-despliegue-workflows.md`](./HALLAZGO-apis-despliegue-workflows.md).
> (Descartado chrome-devtools-mcp/WebMCP para este fin; ver ese hallazgo.)

---

## 1. El patrón, leído del código real de n8n-mcp

`czlonkowski/n8n-mcp` (verificado leyendo su repo) usa **3 piezas**:

```
FUENTE (nodos)  →  LOADER  →  PARSER  →  DB (SQLite + FTS5)  →  TOOLS MCP  →  LLM
```

### 1.1 LOADER — de dónde salen los "nodos"
`src/loaders/node-loader.ts`: carga los paquetes npm reales de n8n
(`n8n-nodes-base`, `@n8n/n8n-nodes-langchain`), lee su `package.json` (lista de nodos)
y hace `require()` de cada clase. **No inventa: lee lo que la plataforma ya define.**

### 1.2 PARSER — qué se extrae de cada nodo
`src/parsers/property-extractor.ts` + `node-parser.ts`: de cada nodo saca
`displayName`, `description`, `category`, **`properties`** (parámetros: nombre, tipo,
opciones, default), `operations`, `credentials`, versión, flags (trigger/webhook/AI).
Las **properties** son lo que hace que el LLM sepa configurar el nodo.

### 1.3 DB + BÚSQUEDA — cómo lo consulta el LLM
`src/database/schema.sql`: tabla `nodes` + tabla virtual **`nodes_fts` (FTS5)** con
triggers de sincronización. Búsqueda full-text (BM25). Las tools del MCP
(`search_nodes`, `get_node`) consultan esta DB y devuelven los parámetros exactos.

> **Este patrón NO es exclusivo de n8n.** Es el mismo de Context7, hermes-docs-mcp,
> DOC-Server-MCP y otros: indexar docs/código → SQLite FTS5 → tools de búsqueda. Es un
> patrón establecido, no un invento.

---

## 2. Por qué empezar con Mushroom (piitaya/lovelace-mushroom)

Mushroom (librería de cards Lovelace de Home Assistant) es el **"hola mundo" ideal**
para dominar el patrón antes de escalar:

| Ventaja | Detalle (verificado en el repo) |
|---|---|
| Pequeño | **19 cards** (no 525 nodos) → índice rápido de construir y verificar |
| Fuente ya estructurada | `docs/cards/<card>.md` trae tablas `Configuration variables` (Name/Type/Default/Description) |
| Fuente precisa adicional | `src/cards/<card>/<card>-config.ts` define el esquema exacto (superstruct) |
| Sin API de escritura | las cards van en YAML del dashboard → **solo nivel 1**, sin la parte compleja |
| Estático y re-indexable | `git clone` + parse; re-index con `git pull` + re-run |

Ejemplo real (`light-card`): type `custom:mushroom-light-card`; campos `entity`
(string, requerido), `icon_color` (string, def `blue`), `show_brightness_control`
(boolean, def false), `tap_action` (action), etc. → el LLM genera el YAML correcto.

---

## 3. FASES DE EJECUCIÓN

> Regla transversal (steering `verificar-antes-de-entregar.md`): verificar SIEMPRE
> contra la fuente real (el repo clonado), no de memoria. Leer archivos completos.

### FASE 0 — Decisiones y scaffold
- [ ] Confirmar lenguaje. **Recomendado: Python + FastMCP** (ya conocido de nextdns; el
      parser aquí lee markdown/TS como texto, no necesita ejecutar JS). Alternativa
      Node/TS si se quiere `require()` real de nodos (necesario para n8n, no para Mushroom).
- [ ] Crear subcarpeta del proyecto: `Varios_tools/mcp-indexador/` (o `mcp-hacs-cards/`).
      Respeta la regla: cada proyecto en su subcarpeta, nada suelto en la raíz.
- [ ] Estructura inicial:
      ```
      mcp-indexador/
      ├── README.md
      ├── pyproject.toml           # deps: fastmcp
      ├── indexer/
      │   ├── loader.py            # localiza las fuentes (docs/cards/*.md, *-config.ts)
      │   ├── parser.py            # extrae {type, name, desc, config_vars[], ejemplo}
      │   └── build_db.py          # crea SQLite + FTS5 y puebla
      ├── server.py                # MCP FastMCP: search_cards / get_card / list_cards
      └── data/
          └── cards.db             # generado (no versionar si es grande)
      ```

### FASE 1 — LOADER (localizar la fuente)
- [ ] `git clone --depth 1 https://github.com/piitaya/lovelace-mushroom` en una ruta temporal.
- [ ] `loader.py`: recorrer `docs/cards/*.md` (fuente principal) y, si se quiere precisión
      extra, casar cada uno con `src/cards/<card>/<card>-config.ts`.
- [ ] Salida del loader: lista de rutas de card + su nombre base.

### FASE 2 — PARSER (extraer parámetros)
- [ ] `parser.py`: de cada `docs/cards/<card>.md` extraer:
      - `type` YAML (ej. `custom:mushroom-<card>-card`) — verificar el nombre exacto en el .md.
      - `display_name`, `description` (encabezado + sección Description).
      - `config_variables[]`: parsear la tabla markdown → `{name, type, default, required, description}`.
      - `example_yaml`: si el .md trae bloque de ejemplo, guardarlo.
- [ ] Verificación: comparar 2-3 cards contra su `-config.ts` para confirmar que no falta ningún campo.

### FASE 3 — DB + FTS5 (imitando el schema de n8n-mcp)
- [ ] `build_db.py`: crear SQLite con:
      ```sql
      CREATE TABLE cards (
        card_type TEXT PRIMARY KEY,    -- custom:mushroom-light-card
        display_name TEXT, description TEXT, category TEXT,
        config_variables TEXT,         -- JSON: [{name,type,default,required,description}]
        example_yaml TEXT, source_url TEXT, updated_at DATETIME
      );
      CREATE VIRTUAL TABLE cards_fts USING fts5(
        card_type, display_name, description, config_variables,
        content=cards, content_rowid=rowid
      );
      -- + triggers insert/update/delete para sincronizar cards_fts (como n8n-mcp)
      ```
- [ ] Poblar desde el parser. Verificar: `SELECT count(*)` == 19.

### FASE 4 — SERVER MCP (las tools que consulta el LLM)
- [ ] `server.py` con FastMCP y 3 tools (todas **solo lectura** → permisos `allow`):
      - `list_cards()` → las 19 con nombre+descripción (overview).
      - `search_cards(query)` → FTS5/BM25 sobre nombre+desc+config → cards candidatas.
      - `get_card(card_type)` → toda la config de esa card (campos, tipos, defaults, ejemplo).
- [ ] Aplicar el patrón de 2 capas (de la guía general): lógica pura `_impl` + envoltorio
      `@mcp.tool` → así el indexador se puede reutilizar sin MCP más adelante.

### FASE 5 — INTEGRAR A KIRO CLI (patrón ya dominado)
- [ ] `mcp_tools/mushroom.json` (command=python del venv, args=server.py o `-m`).
- [ ] `mcp-build` → regenerar `mcp.json`.
- [ ] `permissions.yaml`: las 3 tools → `allow` (solo lectura, sin riesgo).
- [ ] Si el server vive dentro de la imagen kiro-cli: venv aislado (como nextdns en
      `/opt/...`), verificar que el uid 1000 lo puede ejecutar.

### FASE 6 — VERIFICAR EN RUNTIME
- [ ] En Kiro CLI: `/mcp` lista el server mushroom con 3 tools.
- [ ] Prueba: "hazme una tarjeta Mushroom para mi luz con control de brillo" →
      el LLM debe llamar `search_cards`/`get_card` y generar YAML con
      `type: custom:mushroom-light-card` + `show_brightness_control: true` (campo real, no inventado).
- [ ] Confirmar que un campo inexistente NO aparece (el LLM se ciñe al índice).

### FASE 7 — DOCUMENTAR Y CATALOGAR
- [ ] `README.md` del proyecto (instalación + cómo re-indexar con `git pull` + run).
- [ ] Ficha en `tool_catalog/entries/` (patrón enlazar-no-duplicar).
- [ ] Registrar aprendizajes (gotchas del parser, del FTS5, de la integración).

---

## 4. Escalado tras dominar Mushroom (mismo motor, otras fuentes)

El **motor** (PARSER → DB+FTS5 → tools) se reutiliza; solo cambia el LOADER/PARSER por
la forma de cada plataforma:

| Plataforma | Fuente de "nodos" | Dificultad | Nivel |
|---|---|---|---|
| **Mushroom** (primero) | `docs/cards/*.md` + `*-config.ts` | 🟢 baja | 1 (índice) |
| **Otras librerías HACS** | mismo patrón de docs de cards | 🟢 baja | 1 |
| **Node-RED** | paquetes npm: `package.json` (`node-red.nodes`) + `.html` (props) + `.js` | 🟡 media | 1 (y 2 vía Admin API) |
| **Flowise** | clases TS en `flowise-components` con `inputs[]` | 🟡 media-alta | 1 (2 vía API chatflows) |
| **n8n (community)** | `require()` de paquetes npm + `.description` (lo que hace n8n-mcp) | 🟠 alta | 1 y 2 (ya existe base) |

> Node-RED es más fácil que Flowise para el índice (cada nodo trae props + docs estándar).
> Para n8n community ya existe base en n8n-mcp (`fetch:community`); estudiarla antes de rehacer.

---

## 5. Otros ejemplos del mismo patrón (para estudiar, verificados)

Referencias de MCPs indexadores de docs/código (mismo patrón LOADER→PARSER→DB+FTS5):

- **czlonkowski/n8n-mcp** — el caso base con nodos (SQLite + FTS5). Fuente principal de este plan.
- **Context7** (`context7-mcp`) — docs de librerías al día para LLMs (`get-library-docs`).
- **hermes-docs-mcp** — docs desde markdown del repo upstream → SQLite FTS5, re-index con 1 comando.
- **DOC-Server-MCP** — FTS5 + sqlite-vec (híbrido full-text + vectorial), versionado por librería.
- **mcp-context-server** — FTS integrado por defecto.

> Nota de evolución posible: n8n-mcp y estos usan **FTS5** (léxico). Para búsqueda
> semántica se puede añadir **sqlite-vec** (embeddings) como hace DOC-Server-MCP. No es
> necesario para empezar; FTS5 basta para el nivel 1.

---

## 6. Checklist de arranque (lo que falta decidir con el usuario)

- [ ] Lenguaje del MCP: **Python/FastMCP** (recomendado) vs Node/TS.
- [ ] Nombre/ubicación del proyecto: `Varios_tools/mcp-indexador/` o `mcp-hacs-cards/`.
- [ ] ¿El server corre dentro de la imagen kiro-cli (venv aislado) o como proceso npx/uvx?
- [ ] Confirmar que se empieza por **Mushroom nivel 1** (índice, sin API de escritura).

## Referencias

- Patrón base (código real): https://github.com/czlonkowski/n8n-mcp
  (`src/loaders/node-loader.ts`, `src/parsers/property-extractor.ts`, `src/database/schema.sql`)
- Librería a indexar primero: https://github.com/piitaya/lovelace-mushroom
  (`docs/cards/*.md`, `src/cards/*/*-config.ts`)
- Node-RED (escalado): https://nodered.org/docs/creating-nodes/properties y
  https://nodered.org/docs/creating-nodes/packaging
- FastMCP: https://github.com/jlowin/fastmcp · SDK MCP: https://github.com/modelcontextprotocol/python-sdk
- Anatomía general de un MCP (2 capas, integración a Kiro): `./PROYECTO-guia-construir-mcp.md`
- Integración a Kiro ya montada: `../kiro-cli-nas/`

_Contenido verificado contra los repos reales (n8n-mcp y lovelace-mushroom clonados y
leídos) y búsquedas de patrones equivalentes; se enlaza a la fuente. 2026-09-24._
