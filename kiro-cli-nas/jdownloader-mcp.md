# JDownloader como MCP en Kiro CLI (NAS)

> Control de JDownloader por **lenguaje natural** desde Kiro CLI, usando el MCP
> **propio** `ydiaz1699/proyec_jdw2` (78 tools + auto-solver de captchas) a través
> de la nube **My.JDownloader**.
>
> Complementa el contenedor Docker de JDownloader (servicio `jdownloader` en
> nas-dotfiles, imagen `jlesage/jdownloader-2`) — el contenedor descarga; el MCP lo
> controla. Ambos se conectan a la MISMA cuenta My.JDownloader.
>
> **Montado en esta sesión (2026-09-29):** imagen kiro-cli reconstruida con el MCP
> instalado y verificado (`import` OK). Sigue el mismo patrón que nextdns/rclone/n8n.

---

## 0. Arquitectura (relay/nube, NO red local)

`proyec_jdw2` habla con la **nube My.JDownloader** (modo relay), NO con el contenedor
por la LAN. El contenedor JDownloader y el MCP se conectan a la misma cuenta con las
mismas credenciales. Por eso el MCP funciona desde Kiro CLI en el NAS sin depender de
rutas de red locales.

```
Kiro CLI (V3) ──stdio──▶ jdownloader-mcp (proyec_jdw2, venv /opt/jdownloader-venv)
                            │
                            ▼  HTTPS (relay My.JDownloader)
                        api.jdownloader.org
                            ▲
                            │  el contenedor jlesage/jdownloader-2 (:5800) también
                            │  está vinculado a esta misma cuenta
                        [contenedor JDownloader en el NAS]
```

- **NO es un contenedor permanente:** es un proceso stdio efímero que Kiro CLI lanza
  bajo demanda y mata al terminar. Consumo en reposo: cero. Es solo un bloque en `mcp.json`.
- El MCP vive DENTRO de la imagen de Kiro CLI (venv Python 3.14 en `/opt/jdownloader-venv`),
  sin Docker socket.
- **Conexión lazy:** no hace falta llamar `jd_connect` manual; la primera tool
  auto-conecta leyendo `JD_EMAIL/JD_PASSWORD/JD_DEVICE_NAME` del entorno (ver §5).

## 1. Datos reales del entorno (para no re-preguntar)

| Dato | Valor |
|------|-------|
| Cuenta My.JDownloader | `am2490183@gmail.com` |
| Device Name (vinculado en el contenedor) | `JDownloader@Alex` |
| Contenedor JDownloader | servicio `jdownloader`, imagen `jlesage/jdownloader-2:v26.09.1`, GUI `http://SERVER_IP:5800` |
| Destinos de descarga | `/output` → `/NAS/Descargas` (fijo) · `/usb` → `/NAS/USB` (rshared) |
| MCP repo | https://github.com/ydiaz1699/proyec_jdw2 (paquete `jdownloader-mcp`) |
| venv en la imagen | `/opt/jdownloader-venv` |
| Comando del MCP | `/opt/jdownloader-venv/bin/jdownloader-mcp` (tiene `[project.scripts]`) |

## 2. Instalación en la imagen de Kiro CLI (Dockerfile)

`proyec_jdw2` es un **paquete instalable** (`pyproject.toml` con `[project.scripts]`
`jdownloader-mcp`). A diferencia de nextdns (módulo puro), SÍ expone un comando. Se
instala SIN los extras de captcha ML (torch/easyocr, que son `optional-dependencies`)
→ solo core + NopeCHA (HTTP). Bloque añadido al `Dockerfile` de kiro-cli, **antes de
`USER kiro`**:

```dockerfile
# JDownloader MCP (proyec_jdw2) — venv aislado, patrón nextdns. SIN captcha ML pesado.
# ARG de cache-bust: cambiar su valor reconstruye SOLO esta capa (rebuild en ~2-3 min
# en vez de ~12) sin rehacer apt/kiro/nextdns.
ARG JD_MCP_REF=main
RUN UV_PYTHON_INSTALL_DIR=/opt/uv-python uv venv --python 3.14 /opt/jdownloader-venv \
    && VIRTUAL_ENV=/opt/jdownloader-venv UV_PYTHON_INSTALL_DIR=/opt/uv-python uv pip install \
       "jdownloader-mcp @ git+https://github.com/ydiaz1699/proyec_jdw2.git@main" \
    && chmod -R a+rX /opt/jdownloader-venv
```

### Rebuild

```bash
# Rebuild RÁPIDO (solo la capa del MCP, ~2-3 min) — usar tras actualizar proyec_jdw2:
docker compose -f /docker/kiro-cli/compose.yml build --build-arg JD_MCP_REF=$(date +%s)

# Rebuild completo desde cero (~12 min) — solo si cambian apt/kiro/nextdns:
docker compose -f /docker/kiro-cli/compose.yml build --no-cache
```

> **Por qué el ARG:** Docker cachea por el TEXTO de la instrucción. Como `@main` no
> cambia de texto aunque el contenido de `main` sí, sin el ARG habría que usar
> `--no-cache` (rehace TODO, ~12 min). Cambiar `JD_MCP_REF` invalida solo la capa del
> MCP → rebuild de minutos. Las capas de apt/nodejs/kiro/nextdns quedan cacheadas.

## 3. Bugs encontrados al instalar en limpio y sus fixes (verificados)

`proyec_jdw2` nunca se había instalado desde cero en un entorno nuevo. Al hacerlo en
el venv de kiro-cli salieron 3 bugs latentes, todos arreglados en el repo (PRs #1-#3):

| # | Síntoma | Causa | Fix (en el repo) |
|---|---------|-------|------------------|
| 1 | `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | `mcp[cli]>=1.0.0` sin tope → `uv` instaló **mcp 2.2.0**, que renombró `FastMCP`→`MCPServer` | Pin `mcp[cli]>=1.0.0,<2` en `pyproject.toml` + `requirements.txt` (PR #2) |
| 2 | `TypeError: FastMCP.__init__() got an unexpected keyword argument 'description'` | mcp 1.x `FastMCP` usa `instructions=`, no `description=` | `description=` → `instructions=` (PR #3) |
| — | (mejora) `jd_connect` manual en cada sesión | conexión eager | Conexión **lazy** desde el entorno (PR #1, idea portada de swe-sanad) |

> **Lección (steering verificar-antes-de-entregar):** `py_compile` NO detecta estos
> errores porque son de runtime/import. Para validar un MCP antes de entregar hay que
> **instalar en limpio (`uv pip install`/`pip install -e .`) e importar el módulo** con
> la versión real de las dependencias. Verificado con mcp 1.30.0: `import
> jdownloader_mcp.server` → OK.

## 4. mcp_tools/jdownloader.json

`/docker/kiro-cli/data/.kiro/settings/mcp_tools/jdownloader.json`:

```json
{
  "mcpServers": {
    "jdownloader": {
      "command": "/opt/jdownloader-venv/bin/jdownloader-mcp",
      "args": [],
      "env": {
        "JD_EMAIL": "${JD_EMAIL}",
        "JD_PASSWORD": "${JD_PASSWORD}",
        "JD_DEVICE_NAME": "${JD_DEVICE_NAME}",
        "JD_LOG_LEVEL": "ERROR",
        "NOPECHA_API_KEY": "${NOPECHA_API_KEY}"
      },
      "disabled": false
    }
  }
}
```

## 5. Secretos: jdownloader.env + wrapper

Secretos NO hardcodeados (patrón nextdns/n8n): van en `/docker/kiro-cli/jdownloader.env`
(chmod 600) y el wrapper `$aadm/.local/bin/kiro` los inyecta con `--env-file`.

`/docker/kiro-cli/jdownloader.env`:
```bash
JD_EMAIL=am2490183@gmail.com
JD_PASSWORD=<la contraseña de My.JDownloader>
JD_DEVICE_NAME=JDownloader@Alex
JD_LOG_LEVEL=ERROR
NOPECHA_API_KEY=          # vacío = free tier NopeCHA (100 req/día)
```

Línea añadida al wrapper `$aadm/.local/bin/kiro` (junto a los otros `--env-file`):
```bash
  --env-file /docker/kiro-cli/jdownloader.env \
```

## 6. Permisos V3 (permissions.yaml)

Las **78 tools** clasificadas: **25 lectura → `allow`**, **53 escritura/control/
destructivas → `ask`**. Añadido a `/docker/kiro-cli/data/.kiro/settings/permissions.yaml`.

- **allow (lectura):** `jd_connection_status`, `jd_list_devices`, `jd_query_links`,
  `jd_query_packages_linkgrabber`, `jd_query_downloads`, `jd_query_packages_downloads`,
  `jd_get_download_state`, `jd_get_speed`, `jd_toolbar_status`, `jd_list_accounts`,
  `jd_list_premium_hosters`, `jd_get_storage_info`, `jd_get_config_value`,
  `jd_list_config_entries`, `jd_get_default_download_folder`, `jd_list_extensions`,
  `jd_list_dialogs`, `jd_get_dialog`, `jd_list_captchas`, `jd_get_captcha`,
  `jd_captcha_solvers_list`, `jd_captcha_daemon_status`, `jd_get_session_info`,
  `jd_system_info`, `jd_poll_events`.
- **ask (todo lo demás):** conexión (`jd_connect/disconnect/reconnect`), añadir/gestionar
  enlaces y paquetes, control de descargas, cuentas, config, extensiones, captchas/dialogs,
  updates. **CRÍTICAS** (apagan JD o el sistema, o ejecutan API cruda):
  `jd_shutdown`, `jd_hibernate`, `jd_standby`, `jd_call_action`.

## 7. Flujo de montaje (orden real)

```bash
# 1. Editar Dockerfile (bloque §2 antes de USER kiro) y rebuild
docker compose -f /docker/kiro-cli/compose.yml build --build-arg JD_MCP_REF=$(date +%s)
# 2. Verificar el MCP en la imagen
docker run --rm --entrypoint /opt/jdownloader-venv/bin/python kiro-cli-nas:local \
  -c "import jdownloader_mcp.server; print('MCP OK')"
# 3. Crear jdownloader.env (§5) + chmod 600
# 4. Crear mcp_tools/jdownloader.json (§4)
# 5. Añadir bloque a permissions.yaml (§6)
# 6. Añadir --env-file jdownloader.env al wrapper kiro (§5)
# 7. Ensamblar mcp.json
$aadm/.local/bin/mcp-build          # debe listar n8n+nextdns+rclone+jdownloader
# 8. Tras tocar data/ como root:
chown -R 1000:1000 /docker/kiro-cli/data
# 9. Probar
$aadm/.local/bin/kiro
# dentro de la sesión: pedir "estado de la conexión de jdownloader"
# → jd_connection_status debe auto-conectar (lazy) a JDownloader@Alex
```

## 8. Gotchas verificados

- **Device Name con `@`:** es `JDownloader@Alex` (con arroba y mayúscula). Debe
  coincidir EXACTO entre la GUI del contenedor y `JD_DEVICE_NAME`.
- **mcp<2 obligatorio:** ver §3. Sin el pin, cualquier reinstalación vuelve a romper.
- **`--no-cache` rehace todo:** usar el ARG cache-bust (§2) para rebuilds rápidos.
- **Kiro Web NO puede usar este MCP** (sandbox cloud sin la cuenta); Kiro CLI en el NAS SÍ.

## Referencias

- MCP propio: https://github.com/ydiaz1699/proyec_jdw2
- Comparado con: https://github.com/swe-sanad/jdownloader-mcp (de ahí la idea lazy + yt-dlp pendiente)
- Contenedor: https://github.com/jlesage/docker-jdownloader-2
- Guía del contenedor en nas-dotfiles: `docs/services/jdownloader-guide.md`
- Patrón base de kiro-cli: [`./README.md`](./README.md)
