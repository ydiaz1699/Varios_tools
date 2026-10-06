# sawers-mcp

Servidor **MCP** (Model Context Protocol) para consultar el catálogo de la
tienda **Sawers Bolivia** — [tienda.sawers.com.bo](https://tienda.sawers.com.bo/) —
desde un LLM (Kiro, Claude, etc.).

La tienda **no tiene API oficial**, así que este MCP obtiene los datos por
**web scraping** del HTML (la tienda corre sobre **OpenCart**, tema Bootstrap 3,
render del lado del servidor → no hace falta navegador headless).

> Inspirado en el patrón de [anilist-mcp](https://github.com/yuna0x0/anilist-mcp),
> con la diferencia de que allí la fuente es una API GraphQL y aquí es scraping.

## Qué hace

| Tool | Entrada | Devuelve |
|------|---------|----------|
| `search_products` | `query`, `limit?` (1–50) | Lista de productos: `product_id`, `name`, `url`, `image`, `description` |
| `get_product` | `product` (URL, slug o `product_id`) | Detalle: `name`, `image`, `price`, `currency`, `availability`, `description`, `attributes` |
| `list_specials` | `limit?` (1–50) | Productos en oferta (`/especiales`) |
| `login` | `email`, `password` | Inicia sesión para **ver precios** |
| `session_status` | — | Indica si hay sesión iniciada |

Las tools de catálogo son de **solo lectura**; `login` abre sesión en la tienda.

## ⚠️ Importante: los precios requieren login

La tienda **oculta los precios a visitantes anónimos** (muestra
*"Precio - Iniciar Sesión"*). Por eso, **sin** sesión iniciada:

- `price` → `"Requiere iniciar sesion (precio no publico)"`
- `price_requires_login` → `true`

El resto de datos (nombre, descripción, imagen, disponibilidad, atributos) **sí**
están disponibles sin login.

### Cómo ver los precios (login)

Dos formas:

1. **Variables de entorno** (recomendado, login automático al arrancar):

   ```bash
   export SAWERS_EMAIL="tu-correo@ejemplo.com"
   export SAWERS_PASSWORD="tu-contraseña"
   ```

   En Kiro CLI estas variables se inyectan con el `--env-file` del wrapper
   (igual que nextdns/rclone), nunca hardcodeadas en `mcp.json`.

2. **Tool `login`**: el LLM llama `login(email, password)` en caliente. Tras eso,
   `get_product` devuelve el `price` real y `price_requires_login: false`.

> El login usa el endpoint real de OpenCart (`POST /login`) y mantiene la cookie
> de sesión en un cliente HTTP persistente. Credenciales incorrectas → error claro.
> **Necesitas una cuenta registrada y aprobada en la tienda** para que haya precios.

## Instalación y prueba local

```bash
# requiere Python 3.11+ y uv
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -e .

# arrancar el MCP (stdio)
.venv/bin/sawers-mcp
```

Prueba rápida del scraper sin MCP:

```bash
PYTHONPATH=src .venv/bin/python -c \
  "from sawers_mcp import scraper, json; print(scraper.search_products('arduino', 3))"
```

## Integración en Kiro CLI (patrón del NAS)

Este repo incluye en `integration/`:

- `mcp_tools/sawers.json` — bloque para `settings/mcp_tools/` (ensamblar con `mcp-build`).
- `permissions.yaml.snippet` — reglas V3 (todas las tools `allow`, son solo lectura).

Pasos:

1. Copiar `integration/mcp_tools/sawers.json` a `settings/mcp_tools/sawers.json`.
2. Añadir las reglas de `permissions.yaml.snippet` a tu `permissions.yaml`
   (login va como `ask`; el resto `allow`).
3. (Opcional, para ver precios) Poner `SAWERS_EMAIL` y `SAWERS_PASSWORD` en el
   `.env` que inyecta el wrapper `kiro` con `--env-file` (p. ej.
   `$dkco/kiro-cli/sawers.env`, `chmod 600`). El `mcp.json` solo referencia
   `${SAWERS_EMAIL}` / `${SAWERS_PASSWORD}`, nunca los valores.
4. Regenerar `mcp.json` con `mcp-build`.
5. Relanzar Kiro CLI.

> El `command` del `mcp.json` apunta al `python` del venv donde esté instalado
> `sawers-mcp` (igual que nextdns-mcp usa `/opt/nextdns-venv/bin/python`).

## Arquitectura (2 capas)

- `src/sawers_mcp/scraper.py` — **lógica pura**: fetch + parse + selectores CSS.
  Importable y testeable sin MCP. **Todos los selectores viven aquí** → si Sawers
  rediseña la tienda, es el único archivo a tocar.
- `src/sawers_mcp/server.py` — **capa MCP**: envuelve el scraper con FastMCP.

## Notas de robustez / buenas prácticas

- **User-Agent** de navegador real + **rate limiting** (0.7 s entre peticiones)
  para no saturar la tienda ni disparar retos de Cloudflare.
- Detección defensiva de *challenge* de Cloudflare (lanza error claro si aparece).
- Es scraping de una web de terceros: uso **personal/consulta**, peticiones
  espaciadas, respeta `robots.txt` y los términos de la tienda.

## Mejoras futuras

- `list_category(category_path)` para navegar categorías.
- Caché en disco de corta duración.
- Ficha en `tool_catalog` y línea en `repo-index`.

> **Hecho en v0.1:** login opcional para ver precios (sesión con cookies de
> OpenCart), vía tool `login` o variables `SAWERS_EMAIL`/`SAWERS_PASSWORD`.

## Licencia

MIT
