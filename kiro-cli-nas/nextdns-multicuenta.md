# NextDNS multi-cuenta como MCP en Kiro CLI (NAS)

> Control de NextDNS por **lenguaje natural** desde Kiro CLI ("bloquea YouTube a papá"),
> con **una cuenta NextDNS por persona** (cada uno su API key, para no agotar los
> límites del plan gratuito de una sola cuenta compartida).
>
> **Verificado en runtime** en el NAS (2026-09-23): lectura y escritura reales
> confirmadas contra la API de NextDNS.

---

## 0. Por qué una cuenta por persona (no perfiles en una cuenta)

El plan gratuito de NextDNS tiene un límite mensual de consultas **por cuenta**. Con
varios perfiles en UNA cuenta, el consumo se suma y puede agotarse (quedándose sin
protección hasta el mes siguiente). Con **una cuenta por persona**, cada uno tiene su
propio cupo holgado. Por eso el modelo es multi-cuenta = multi-API-key.

## 1. Arquitectura

`nextdns-mcp` (dmeiser) es un MCP **stdio** que se arranca con UNA `NEXTDNS_API_KEY`
fija. No acepta "elige la cuenta X" en la llamada → **un server MCP por persona**,
cada uno con su key. Kiro elige el server según a quién nombres (guiado por un steering).

```
Kiro CLI (V3) ──stdio──▶ nextdns-infinix  (API key infinix, perfil 2511f5)
              ──stdio──▶ nextdns-papa      (API key papá,    perfil 2f6df5)
                            │
                            ▼  HTTPS a api.nextdns.io
                        NextDNS (cada cuenta la suya)
```

- **NO son contenedores permanentes:** son procesos stdio efímeros que Kiro CLI
  lanza bajo demanda y mata al terminar. Consumo en reposo: cero. Son solo bloques
  en el `mcp.json`.
- El MCP vive DENTRO de la imagen de Kiro CLI (venv Python 3.14 en `/opt/nextdns-venv`),
  **sin Docker socket** (respeta el principio anti-socket de nas-dotfiles).

## 2. Instalación en la imagen de Kiro CLI (Dockerfile)

`nextdns-mcp` requiere **Python 3.14** y NO está en PyPI (solo GitHub + imagen Docker).
Se instala con `uv` en un venv aislado. Bloque añadido al `Dockerfile` de kiro-cli:

```dockerfile
# uv + nextdns-mcp en venv aislado con Python 3.14 (se lanza como MODULO, no comando)
RUN curl -fsSL https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
    && UV_PYTHON_INSTALL_DIR=/opt/uv-python uv venv --python 3.14 /opt/nextdns-venv \
    && VIRTUAL_ENV=/opt/nextdns-venv UV_PYTHON_INSTALL_DIR=/opt/uv-python uv pip install \
       "nextdns-mcp @ git+https://github.com/dmeiser/nextdns-mcp.git" \
    && chmod -R a+rX /opt/uv-python /opt/nextdns-venv
```

> **Gotchas verificados:**
> - `uv tool install nextdns-mcp` **falla** (`No executables provided`): el paquete es
>   un MÓDULO (`python -m nextdns_mcp.server`), no expone comando. Por eso `uv venv` +
>   `uv pip install`, no `uv tool install`.
> - `UV_PYTHON_INSTALL_DIR=/opt/uv-python` fuerza a que Python 3.14 quede accesible a
>   todos; si se instala en el home de root, el usuario `kiro` (uid 1000) da
>   `Permission denied` al ejecutar el `python` del venv.
> - Invocación final: **`/opt/nextdns-venv/bin/python -m nextdns_mcp.server`**.

Verificar tras el build:
```bash
docker run --rm --entrypoint bash kiro-cli-nas:local -c \
  '/opt/nextdns-venv/bin/python -c "import nextdns_mcp; print(\"OK\")"'
```

## 3. Credenciales — `$dkco/kiro-cli/nextdns.env` (chmod 600)

Se usa `.env` (NO se hardcodea en el mcp.json). El wrapper lo inyecta al contenedor.

```dotenv
# INFINIX
NEXTDNS_APIKEY_INFINIX=<API_KEY_INFINIX>
NEXTDNS_PROFILE_INFINIX=2511f5
# PAPA (cuenta separada)
NEXTDNS_APIKEY_PAPA=<API_KEY_PAPA>
NEXTDNS_PROFILE_PAPA=2f6df5
```
```bash
chmod 600 $dkco/kiro-cli/nextdns.env
```

> Sobre `.env` vs `profiles.json`: el consejo de "env es frágil" aplica cuando exportas
> variables a tu shell/`.bashrc`. Aquí NO: viven en un archivo `chmod 600` que el wrapper
> lee e inyecta con `--env-file`. Nunca van al shell ni al JSON. El `nextdns-mcp` solo
> lee variables de entorno, así que `.env` es el formato que el MCP espera.

## 4. Config MCP — `mcp_tools/nextdns.json` (un bloque por persona)

```json
{
  "mcpServers": {
    "nextdns-infinix": {
      "command": "/opt/nextdns-venv/bin/python",
      "args": ["-m", "nextdns_mcp.server"],
      "env": {
        "NEXTDNS_API_KEY": "${NEXTDNS_APIKEY_INFINIX}",
        "NEXTDNS_DEFAULT_PROFILE": "${NEXTDNS_PROFILE_INFINIX}",
        "NEXTDNS_WRITABLE_PROFILES": "${NEXTDNS_PROFILE_INFINIX}",
        "NEXTDNS_READABLE_PROFILES": "${NEXTDNS_PROFILE_INFINIX}",
        "FASTMCP_CHECK_FOR_UPDATES": "off"
      },
      "disabled": false
    },
    "nextdns-papa": {
      "command": "/opt/nextdns-venv/bin/python",
      "args": ["-m", "nextdns_mcp.server"],
      "env": {
        "NEXTDNS_API_KEY": "${NEXTDNS_APIKEY_PAPA}",
        "NEXTDNS_DEFAULT_PROFILE": "${NEXTDNS_PROFILE_PAPA}",
        "NEXTDNS_WRITABLE_PROFILES": "${NEXTDNS_PROFILE_PAPA}",
        "NEXTDNS_READABLE_PROFILES": "${NEXTDNS_PROFILE_PAPA}",
        "FASTMCP_CHECK_FOR_UPDATES": "off"
      },
      "disabled": false
    }
  }
}
```
Regenerar el `mcp.json` combinado: `$aadm/.local/bin/mcp-build` (debe decir "2 archivo(s)").

## 5. Wrapper `kiro` — inyecta las keys

```bash
#!/usr/bin/env bash
set -eu
RCPASS="$(grep RCLONE_RC_PASS /docker/rclone-rcd/.env | cut -d= -f2)"
exec docker run -it --rm --network host \
  -e RCLONE_RC_PASS="$RCPASS" \
  --env-file /docker/kiro-cli/nextdns.env \
  -v /docker/kiro-cli/data:/home/kiro \
  kiro-cli-nas:local --v3 "$@"
```

## 6. Steering — mapa de usuarios (`data/.kiro/steering/nextdns-usuarios.md`)

```markdown
# NextDNS — mapa de usuarios
- "yo"/"mi"/"infinix"/"mi teléfono" → server nextdns-infinix (perfil 2511f5)
- "papá"/"mi papá" → server nextdns-papa (perfil 2f6df5)
Usa SOLO las tools del server que corresponde; nunca cambies el perfil de otra persona.
Para bloquear un servicio (YouTube, etc.): manageLists con list_type=parental_services;
si ya existe pero active:false, actívalo con operation=update.
```

## 7. Permisos V3 — `permissions.yaml`

Las 8 tools de NextDNS son **agrupadas**: la misma tool lee Y escribe según el
parámetro `operation`. Kiro decide por nombre de tool (no por operación), así que la
política es por tool completa.

| Tool | Naturaleza | Política |
|------|-----------|----------|
| `dohLookup`, `queryAnalytics`, `plotAnalytics` | solo lectura | **allow** (auto) |
| `manageProfiles`, `manageLists`, `manageLogs`, `manageRewrites`, `manageSettings` | pueden escribir/borrar | **ask** (confirmar) |

```yaml
rules:
  - capability: mcp
    match: ["nextdns-infinix/dohLookup","nextdns-infinix/queryAnalytics","nextdns-infinix/plotAnalytics",
            "nextdns-papa/dohLookup","nextdns-papa/queryAnalytics","nextdns-papa/plotAnalytics"]
    effect: allow
  - capability: mcp
    match: ["nextdns-infinix/manageProfiles","nextdns-infinix/manageLists","nextdns-infinix/manageLogs",
            "nextdns-infinix/manageRewrites","nextdns-infinix/manageSettings",
            "nextdns-papa/manageProfiles","nextdns-papa/manageLists","nextdns-papa/manageLogs",
            "nextdns-papa/manageRewrites","nextdns-papa/manageSettings"]
    effect: ask
  # ... (debajo van las reglas de rclone)
```

## 8. Las 8 tools de nextdns-mcp (verificadas)

| Tool | Qué hace |
|------|----------|
| `manageProfiles` | perfiles: list/get/create/update/delete |
| `manageLists` | allow/deny/block lists y **parental_services** (bloquear YouTube, etc.) |
| `manageSettings` | categorías y ajustes (seguridad, privacidad, control parental) |
| `manageLogs` | logs de consultas: get/clear |
| `manageRewrites` | reescrituras DNS |
| `dohLookup` | prueba de resolución DNS-over-HTTPS |
| `queryAnalytics` | métricas de analítica |
| `plotAnalytics` | gráfico PNG de una métrica |

## 9. Gotchas verificados en runtime

- **Bloquear un servicio (YouTube):** va por `manageLists` con `list_type=parental_services`,
  NO por `manageSettings`. Patrón real: el servicio puede estar en la lista pero
  `active:false` (bloqueado pero desactivado) → hay que `operation=update` para
  activarlo. Kiro se auto-corrige: intenta `add` → 400 `duplicate` → `get` → `update`.
- **403 en perfiles ajenos:** con `NEXTDNS_READABLE_PROFILES` limitado, leer un perfil
  fuera de la lista da `403 Read access denied`. Es el aislamiento funcionando, no un fallo.
- Si la API key ve más de un perfil en `list`, Kiro **pregunta cuál** antes de escribir.

## 10. Uso

```
muéstrame las analíticas de mi perfil          # queryAnalytics → auto
bloquea YouTube en mi perfil                    # manageLists → pide confirmación
desbloquea juegos en el perfil de papá          # manageLists → pide confirmación
```

## Proyecto pendiente (portabilidad a nas-agent)

El MCP aquí descrito lo usa **Kiro CLI**. Para que el **nas-agent (Strands SDK)** también
controle NextDNS reutilizando el MISMO código (importando la capa `_impl`/`client` del
paquete, sin MCP), hay un proyecto anotado — NO implementado:
[`./PROYECTO-PENDIENTE-nextdns-en-nas-agent.md`](./PROYECTO-PENDIENTE-nextdns-en-nas-agent.md).

## Referencias
- MCP: https://github.com/dmeiser/nextdns-mcp (Python/FastMCP, imagen `dmeiser/nextdns-mcp`)
- API keys: https://my.nextdns.io/account
- Instalación de Kiro CLI: `./README.md`; MCP rclone: `../rclone-mcp-control-total/README.md`

_Verificado en runtime 2026-09-23. Contenido reescrito/resumido; se enlaza a la fuente._
