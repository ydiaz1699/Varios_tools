# karakeep-mcp como MCP en Kiro CLI (NAS)

> Que **Kiro CLI opere tu biblioteca de bookmarks de Karakeep por lenguaje natural**:
> buscar, crear, leer contenido, etiquetar y organizar en listas los bookmarks de tu
> instancia self-hosted, hablándole en español.
>
> MCP **oficial** de Karakeep (`@karakeep/mcp`, también imagen
> `ghcr.io/karakeep-app/karakeep-mcp`). Habla con la **API REST** de Karakeep.
>
> **NO verificado en runtime todavía** (pendiente de montar Karakeep en el NAS). Las
> tools y la config están extraídas del código y la doc oficiales, no de memoria.

---

## 0. Qué es y cómo encaja

Karakeep es un **único almacén** de bookmarks (en tu NAS, `:3400`) con varias caras.
Este MCP es **una de esas caras**: la que usa el LLM. Las otras son la UI web, el CLI
(`@karakeep/cli`) y la API REST. Visión de conjunto en
`nas-dotfiles/docs/services/karakeep-floccus-architecture.md`.

- Paquete npm: **`@karakeep/mcp`** (se lanza con `npx @karakeep/mcp`). Última: `0.34.0`.
- Imagen Docker alternativa: **`ghcr.io/karakeep-app/karakeep-mcp:latest`**.
- Es un MCP **stdio** en Node; Node ya está en la imagen `kiro-cli-nas:local`.
- Autenticación: una **API key de Karakeep** (Settings → API Keys) + la URL de tu
  instancia. Nada más.

## 1. Arquitectura

```
Kiro CLI (V3, network_mode: host)
   └─ npx @karakeep/mcp   (stdio, efímero, lo lanza Kiro bajo demanda)
        └─ HTTP a la API REST de Karakeep  →  http://192.168.1.200:3400
                                               (contenedor karakeep, publica 3400:3000)
```

- **NO es un contenedor permanente:** es un proceso stdio que Kiro lanza al usarlo y
  mata al terminar. Es solo un bloque en el `mcp.json`. Consumo en reposo: cero.
- El MCP corre **dentro** del contenedor de Kiro CLI (no toca el host).

### GOTCHA de red (por qué IP privada y no `http://karakeep:3400`)

El contenedor kiro-cli usa **`network_mode: host`**, así que **NO está en la red del
compose de Karakeep** y **no resuelve el nombre `karakeep`**. En host mode comparte la
red del NAS y alcanza Karakeep por su **puerto publicado en el host**: `3400:3000`. Por
eso `KARAKEEP_API_ADDR=http://192.168.1.200:3400` (la IP LAN del NAS), no el nombre de
servicio Docker. Mismo patrón que n8n-mcp (ver `n8n-mcp.md` §1).

## 2. Requisitos previos

- Kiro CLI ya montado (imagen `kiro-cli-nas:local`, wrapper `$aadm/.local/bin/kiro`,
  ensamblador `mcp-build`). Ver [`./README.md`](./README.md).
- **Karakeep corriendo** y publicando `3400` (servicio `karakeep` en nas-dotfiles;
  guía `nas-dotfiles/docs/services/karakeep-guide.md`).
- Una **API key de Karakeep**: en la UI de Karakeep → **Settings → API Keys** →
  crear una. (Desde 0.32.0 las API keys pueden ser granulares.)

## 3. Credenciales — `$dkco/kiro-cli/karakeep.env` (chmod 600)

El secreto NO se hardcodea en el `mcp.json`; va en un `.env` que el wrapper inyecta.

```bash
dk kiro-cli
cat > karakeep.env <<'EOF'
KARAKEEP_API_ADDR=http://192.168.1.200:3400
KARAKEEP_API_KEY=PEGA_AQUI_TU_API_KEY_DE_KARAKEEP
EOF
chmod 600 karakeep.env
nano karakeep.env    # pega la API key real donde dice PEGA_AQUI_TU_API_KEY_DE_KARAKEEP
```

Verificar sin exponer el secreto (muestra solo la longitud de la key):

```bash
awk -F= '{print $1"="(($1=="KARAKEEP_API_KEY")?"<oculta, "length($2)" chars>":$2)}' karakeep.env
```

## 4. Config MCP — `mcp_tools/karakeep.json`

```json
{
  "mcpServers": {
    "karakeep": {
      "command": "npx",
      "args": ["@karakeep/mcp"],
      "env": {
        "KARAKEEP_API_ADDR": "${KARAKEEP_API_ADDR}",
        "KARAKEEP_API_KEY": "${KARAKEEP_API_KEY}"
      },
      "disabled": false
    }
  }
}
```

- Las variables `${...}` las resuelve el `.env` inyectado por el wrapper (§5).
- Pinear versión: `"args": ["@karakeep/mcp@0.34.0"]` si se quiere fijar (por defecto
  `npx` baja la última).
- **Alternativa Docker** (si prefieres no depender de `npx`):
  `"command": "docker"`, `"args": ["run","-i","--rm","-e","KARAKEEP_API_ADDR","-e","KARAKEEP_API_KEY","ghcr.io/karakeep-app/karakeep-mcp:latest"]`
  (con `network_mode: host` del contenedor kiro-cli, el `docker run` anidado necesita
  acceso al socket; para empezar, `npx` es más simple).

Regenerar el `mcp.json` combinado:

```bash
$aadm/.local/bin/mcp-build     # debe listar karakeep junto a n8n/nextdns/rclone
```

## 5. Wrapper `kiro` — inyectar `karakeep.env`

Añadir la línea `--env-file .../karakeep.env` al wrapper `$aadm/.local/bin/kiro`
(junto a las de nextdns y n8n). Debe quedar así:

```bash
#!/usr/bin/env bash
set -eu
RCPASS="$(grep RCLONE_RC_PASS /docker/rclone-rcd/.env | cut -d= -f2)"
exec docker run -it --rm --network host \
  -e RCLONE_RC_PASS="$RCPASS" \
  --env-file /docker/kiro-cli/nextdns.env \
  --env-file /docker/kiro-cli/n8n.env \
  --env-file /docker/kiro-cli/karakeep.env \
  -v /docker/kiro-cli/data:/home/kiro \
  kiro-cli-nas:local --v3 "$@"
```

Verificar (deben salir TRES líneas `--env-file`):

```bash
grep -n "env-file" $aadm/.local/bin/kiro
```

## 6. Permisos V3 — `permissions.yaml`

Las 34 tools del MCP se clasifican en dos grupos. Precedencia `deny > ask > allow`
(la posición en el archivo no importa). Añadir al final de
`data/.kiro/settings/permissions.yaml`:

```yaml
  # ── karakeep-mcp: lectura/búsqueda → auto ──
  - capability: mcp
    match:
      - "karakeep/search-bookmarks"
      - "karakeep/get-bookmark"
      - "karakeep/get-bookmark-content"
      - "karakeep/get-bookmark-lists"
      - "karakeep/get-lists"
      - "karakeep/get-list"
      - "karakeep/get-list-bookmarks"
      - "karakeep/get-tags"
      - "karakeep/get-tag"
      - "karakeep/get-tag-bookmarks"
      - "karakeep/list-highlights"
      - "karakeep/get-bookmark-highlights"
      - "karakeep/get-highlight"
      - "karakeep/get-asset"
    effect: allow
  # ── karakeep-mcp: crea/modifica/borra/organiza → confirmar ──
  - capability: mcp
    match:
      - "karakeep/create-bookmark"
      - "karakeep/update-bookmark"
      - "karakeep/delete-bookmark"
      - "karakeep/create-list"
      - "karakeep/update-list"
      - "karakeep/delete-list"
      - "karakeep/add-bookmark-to-list"
      - "karakeep/remove-bookmark-from-list"
      - "karakeep/attach-tag-to-bookmark"
      - "karakeep/detach-tag-from-bookmark"
      - "karakeep/update-tag"
      - "karakeep/delete-tag"
      - "karakeep/create-highlight"
      - "karakeep/update-highlight"
      - "karakeep/delete-highlight"
    effect: ask
```

Validar el YAML (no romper las reglas de rclone/nextdns/n8n):

```bash
python3 -c "import yaml; yaml.safe_load(open('data/.kiro/settings/permissions.yaml')); print('OK')"
```

> Cambiar `permissions.yaml` NO requiere `mcp-build` (solo relanzar `kiro`).

## 7. Arrancar y verificar

```bash
$aadm/.local/bin/kiro
```

Dentro de la sesión:

```
/mcp
```

Debe listar **karakeep** (junto a rclone, nextdns, n8n). La primera vez aparece
`◌ loading` porque `npx` descarga el paquete; espera unos segundos o invoca una tool
para forzar la carga.

Prueba de conexión (lectura → allow, corre sola):

```
busca en karakeep mis bookmarks sobre docker
```

## 8. Uso

```
busca en karakeep mis bookmarks sobre homelab            # search-bookmarks → auto (allow)
guárdame este enlace en karakeep: https://ejemplo.com    # create-bookmark → PIDE CONFIRMACIÓN (ask)
etiqueta ese bookmark como "leer-luego"                  # attach-tag-to-bookmark → ask
crea una lista "Proyectos NAS" y mete ahí los últimos 5  # create-list + add-bookmark-to-list → ask
```

- Búsqueda/lectura corren solas (allow).
- Crear/modificar/borrar/organizar piden confirmación (ask).

## 9. Las tools (verificadas del código oficial)

Extraídas de `apps/mcp/src/*.ts` del repo `karakeep-app/karakeep`.

**Lectura/búsqueda (allow):** `search-bookmarks`, `get-bookmark`,
`get-bookmark-content`, `get-bookmark-lists`, `get-lists`, `get-list`,
`get-list-bookmarks`, `get-tags`, `get-tag`, `get-tag-bookmarks`, `list-highlights`,
`get-bookmark-highlights`, `get-highlight`, `get-asset`.

**Escritura/organización (ask):** `create-bookmark`, `update-bookmark`,
`delete-bookmark`, `create-list`, `update-list`, `delete-list`,
`add-bookmark-to-list`, `remove-bookmark-from-list`, `attach-tag-to-bookmark`,
`detach-tag-from-bookmark`, `update-tag`, `delete-tag`, `create-highlight`,
`update-highlight`, `delete-highlight`.

## 10. Mantenimiento

- **Editar config del MCP:** `mcp_tools/karakeep.json` → `mcp-build` → relanzar `kiro`.
- **Cambiar permisos:** editar `permissions.yaml` → relanzar (sin `mcp-build`).
- **Rotar API key:** editar `$dkco/kiro-cli/karakeep.env` → relanzar `kiro`.
- **Tras tocar `data/` como root:** `chown -R 1000:1000 $dkco/kiro-cli/data`.

## 11. Notas operativas

- `mcp-build` y `kiro` viven en `$aadm/.local/bin`; como root ese dir no está en PATH →
  invócalos por ruta absoluta o añade `export PATH="/home/aadm/.local/bin:$PATH"` a
  `/root/.bashrc`.
- `npx @karakeep/mcp` requiere salida a internet la primera vez (host mode la tiene).
- **Kiro Web (sandbox cloud) NO puede usar este MCP** (sin ruta a la LAN privada).
  Kiro CLI en el NAS SÍ.
- **Pendiente de verificación en runtime** una vez Karakeep esté levantado: `/mcp`
  lista `karakeep`, y un `search-bookmarks` devuelve resultados contra `:3400`.

## Referencias

- MCP oficial: https://docs.karakeep.app/mcp · paquete npm `@karakeep/mcp`
- Código de las tools: `apps/mcp/src/{bookmarks,lists,tags,highlights,assets}.ts` del
  repo https://github.com/karakeep-app/karakeep
- Arquitectura del conjunto: `nas-dotfiles/docs/services/karakeep-floccus-architecture.md`
- Servicio Karakeep (UI/CLI/API): `nas-dotfiles/docs/services/karakeep-guide.md`
- Instalación de Kiro CLI: [`./README.md`](./README.md) · MCP n8n: [`./n8n-mcp.md`](./n8n-mcp.md)

_Contenido reescrito/resumido a partir de la documentación y el código oficiales; se
enlaza a la fuente. Tools verificadas contra el código, no de memoria._
