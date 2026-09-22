# Guía — MCP de rclone con CONTROL TOTAL en el NAS

> Objetivo: montar en el NAS un servidor **MCP** que dé a un asistente (LobeHub / Cursor / Claude, etc.)
> **control total de rclone** — todas las tools: listar, copiar, sincronizar, montar/desmontar,
> gestionar remotes (config), jobs en background, backend, vfs, serve… **98 endpoints**.
>
> Verificado contra las fuentes reales (2026-09-22):
> - Imagen oficial `rclone/rclone` estable: **1.75.1**
> - MCP base `rclone-mcp-server` (npm): **1.0.3**

---

## 0. TL;DR — la mejor opción

**Control total NO se consigue "fusionando los 4 repos".** Se consigue con **DOS piezas** + un flag:

```
┌─────────────┐   MCP (stdio/http)   ┌──────────────────┐   HTTP RC API   ┌─────────────────┐
│  Cliente    │ ───────────────────▶ │  MCP server      │ ──────────────▶ │  rclone rcd     │ ─▶ remotes
│ (LobeHub…)  │                      │  rclone-mcp-server│  :5572          │  (daemon RC)    │    gdrive:, s3:…
└─────────────┘                      │  TOOLSETS=all     │                 └─────────────────┘
                                     └──────────────────┘
```

- **Pieza A — `rclone rcd`**: el daemon Remote-Control de rclone. Es quien *realmente* ejecuta todo
  y quien lee tu `rclone.conf`. Sin esto el MCP no hace nada.
- **Pieza B — el MCP server** (`rclone-mcp-server`, base de `angenge`): traduce las tools MCP a
  llamadas a la RC API. Con **`RCLONE_TOOLSETS=all`** expone los 98 endpoints = control total.

**Por qué esta base y no "unir los 4":**

| Repo | Qué es | Sirve para control total? |
|------|--------|---------------------------|
| `rclone-ui/rclone-mcp` | Original (Node, RC API) | Sí, pero menos pulido |
| **`angenge/rclone-mcp-server`** | **Refactor del original** (mejores defaults, MCP Resources, docs async jobs) | ✅ **BASE ELEGIDA** |
| `brokenlander/rclone-mcp-readonly` | Fork **read-only** con guards | ❌ es lo contrario a control total (solo como modo seguro opcional) |
| `hyunjae-labs/rclone-drive-mcp` | Python, **solo Google Drive**, por rutas | ❌ no toca mount/sync/config/crypt |

> Los 3 primeros comparten base (Node + RC API). El 4º es otro árbol (Python/Drive).
> Para control total basta **angenge con `TOOLSETS=all`**; "unificar" solo aportaría un modo `--secure`
> opcional (guards de brokenlander) para cuando NO quieras control total.

---

## 1. Decisión de arquitectura para TU NAS

Coherente con el framework nas-dotfiles (Docker + `svc` + `db_net`), la mejor opción es:

- **Pieza A (rclone rcd)** → **contenedor Docker** `rclone/rclone:1.75.1` en `db_net`, con
  **FUSE activo por defecto** (§5.3) para que la tool `mount` proyecte al host = control total real.
  (Alternativa: systemd nativo en el host. Se documenta al final como opción B.)
- **Pieza B (MCP server)** → se lanza vía `npx` desde tu **gateway MCP** (LobeHub), apuntando al
  daemon por `http://rclone-rcd:5572` (misma `db_net`) o `http://${SERVER_IP}:5572`.

**Un solo compose** levanta el daemon. El MCP server no necesita contenedor propio: lo arranca el
cliente MCP con `npx` (stdio) o lo corres en modo `http` si prefieres un endpoint compartido.

### Redes
- `rclone-rcd` va en **`db_net`** (interno, sin exponer al host salvo que quieras).
- Si el MCP corre por `npx` en el host del gateway, expón `5572` a la LAN o mételo también en `db_net`.

---

## 2. Requisito previo: tener un `rclone.conf` con remotes

El daemon necesita un `rclone.conf` con al menos un remote configurado. Si aún no lo tienes,
créalo **una vez** de forma interactiva (en el host):

```bash
# En el NAS (host). Genera/edita el rclone.conf del usuario.
instal rclone            # si no está instalado (usa tu helper 'instal')
rclone config            # n = nuevo remote → sigue el asistente (gdrive, s3, etc.)
rclone listremotes       # verifica que aparezcan tus remotes
```

Guardaremos ese `rclone.conf` en la carpeta del servicio para montarlo en el contenedor.

> Nota crypt/OAuth: los remotes con OAuth (Google Drive, OneDrive…) guardan el `token` dentro del
> propio `rclone.conf`. Con montar ese archivo basta; no hay pasos extra.

---

## 3. Estructura del servicio

```
/docker/rclone-rcd/
├── compose.yml
├── .env                      # SOLO secretos: RC user/pass del daemon
└── config/
    └── rclone.conf           # tu config real de remotes (copiada del host)

/mnt/                         # (en el HOST) donde aparecen los remotes montados por 'mount'
└── gdrive/                   #   ej: /mnt/gdrive tras mount/mount fs=gdrive: (§7)
```

Los montajes **SÍ son visibles en el host**: el compose comparte `/mnt` entre contenedor y host
con propagación `rshared` (§5.3), así que cuando la tool `mount` monta un remote en `/mnt/<nombre>`
dentro del contenedor, ese punto aparece igual en `/mnt/<nombre>` del host — y otros servicios
(Jellyfin, File Browser, etc.) pueden leerlo gracias a `--allow-other`. Esto ya viene activo
por defecto; no hay que añadir nada. Detalle de uso en §7.

---

## 4. Crear carpetas (orden real: primero mkdir)

```bash
mkdir -p $dkco/rclone-rcd/config
mkdir -p /mnt                       # punto base para montajes FUSE visibles en el host (§7)
```

---

## 5. Crear archivos

### 5.1 Copiar tu rclone.conf al servicio

```bash
# Copia la config real de remotes a la carpeta del servicio
cp ~/.config/rclone/rclone.conf $dkco/rclone-rcd/config/rclone.conf
```

### 5.2 `.env` — credenciales del daemon RC (secretos)

Genera una contraseña fuerte para proteger la RC API (evita `--rc-no-auth` si el puerto sale del host):

```bash
# Genera una pass aleatoria y déjala en el .env (no la imprimimos por pantalla)
RC_PASS_TMP="$(openssl rand -hex 24)"
cat > $dkco/rclone-rcd/.env <<EOF
RCLONE_RC_USER=nasadmin
RCLONE_RC_PASS=${RC_PASS_TMP}
EOF
unset RC_PASS_TMP
chmod 600 $dkco/rclone-rcd/.env
```

> Guarda `RCLONE_RC_USER` / `RCLONE_RC_PASS`: el MCP los necesitará (§8).
> Para leerlos luego sin exponerlos en logs: `grep RCLONE_RC $dkco/rclone-rcd/.env`.

### 5.3 `compose.yml` (control total COMPLETO — FUSE/`mount` activo por defecto)

> **Las 98 tools NO dependen de este compose.** Las expone el MCP server (Pieza B) con
> `RCLONE_TOOLSETS=all` (§8). Docker **no limita ninguna tool**. Lo único que este compose
> habilita es que la tool `mount/*` proyecte el montaje al **host** — para eso lleva FUSE
> (`/dev/fuse` + `SYS_ADMIN` + `/mnt:rshared`) **activo por defecto**, que es el control total real.

`dk rclone-rcd` y crea el `compose.yml`:

```yaml
services:
  rclone-rcd:
    image: rclone/rclone:1.75.1
    container_name: rclone-rcd
    restart: on-failure:5              # convención nas-dotfiles (systemd controla el orden en boot)
    env_file:
      - ../.env                        # hereda SERVER_IP y TZ globales
      - .env                           # RCLONE_RC_USER / RCLONE_RC_PASS (secretos)
    command:
      - rcd
      - --rc-addr=:5572
      - --rc-user=${RCLONE_RC_USER}
      - --rc-pass=${RCLONE_RC_PASS}
      - --rc-serve                     # permite servir archivos por HTTP si se necesita
      - --rc-web-gui=false             # sin GUI web embebida (la controlas por MCP)
      - --config=/config/rclone.conf
      - --allow-other                  # que otros usuarios/servicios del host lean el mount
      - --log-level=INFO
    volumes:
      - ./config/rclone.conf:/config/rclone.conf   # tu config de remotes
      - /mnt:/mnt:rshared                          # montajes visibles en el HOST (mount FUSE)
    networks:
      - db_net
    ports:
      - "127.0.0.1:5572:5572"        # expone SOLO a localhost del NAS (para Kiro CLI en el NAS, §8.4)
    #   - "${SERVER_IP}:5572:5572"   # alternativa: exponer a la LAN (Kiro CLI/MCP en otro PC) — menos seguro
    # --- FUSE: necesario para que la tool mount/* funcione y suba al host (control total) ---
    cap_add:
      - SYS_ADMIN
    devices:
      - /dev/fuse
    security_opt:
      - apparmor:unconfined
    healthcheck:
      test: ["CMD", "rclone", "rc", "--rc-addr=:5572",
             "--user=${RCLONE_RC_USER}", "--pass=${RCLONE_RC_PASS}", "core/version"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  db_net:
    external: true
```

> `env_file: [../.env, .env]` sigue tu regla de heredar `SERVER_IP`/`TZ` del `.env` global.
> Si tu `db_net` no está declarada `external`, ajusta el bloque `networks` a tu convención.
>
> **Sobre FUSE activo por defecto:** `SYS_ADMIN` + `/dev/fuse` + `/mnt:rshared` dan a la tool
> `mount` control real sobre el host. Es el precio de "control total": es un contenedor
> privilegiado en la práctica, así que mantenlo en `db_net` y **no expongas** `5572` a redes
> no confiables. Si algún día NO necesitas `mount`, puedes quitar el bloque FUSE y el volumen
> `/mnt` — las otras 90+ tools seguirán funcionando igual.

---

## 6. Levantar y verificar (orden real: al final)

```bash
dk rclone-rcd
svc up rclone-rcd
svc health                 # rclone-rcd debe salir healthy
svc logs rclone-rcd        # ver que arranca sin errores

# Probar la RC API directamente (desde el host, si expusiste el puerto o entrando al contenedor):
svc exec rclone-rcd rclone rc --rc-addr=:5572 \
  --user=nasadmin --pass=TU_RC_PASS core/version

# Listar remotes vía RC API (confirma que ve tu rclone.conf):
svc exec rclone-rcd rclone rc --rc-addr=:5572 \
  --user=nasadmin --pass=TU_RC_PASS config/listremotes
```

> Sustituye `TU_RC_PASS` por el valor real (`grep RCLONE_RC_PASS $dkco/rclone-rcd/.env`).
> NO lo pegues en chats ni lo dejes en el historial; úsalo solo en tu terminal local.

---

## 7. Usar `mount` — montar remotes como carpetas del host

El bloque FUSE ya va **activo por defecto** en el compose (§5.3), así que la tool `mount`
funciona sin tocar nada. Prueba a montar un remote (por MCP o directamente por RC):

```bash
svc exec rclone-rcd rclone rc --rc-addr=:5572 --user=nasadmin --pass=TU_RC_PASS \
  mount/mount fs=gdrive: mountPoint=/mnt/gdrive

# Verifica que el montaje subió al HOST:
ls /mnt/gdrive
mount | grep /mnt/gdrive

# Desmontar:
svc exec rclone-rcd rclone rc --rc-addr=:5572 --user=nasadmin --pass=TU_RC_PASS \
  mount/unmount mountPoint=/mnt/gdrive
```

> `:rshared` es imprescindible para que el montaje del contenedor "suba" al host (misma técnica que
> File Browser en tu framework). Sin `SYS_ADMIN` + `/dev/fuse` (ya presentes en el compose), `mount`
> falla. El `mountPoint` debe estar bajo `/mnt` (el path que se comparte con el host).
> Si NO vas a usar `mount`, puedes quitar el bloque FUSE + el volumen `/mnt` del compose; el resto
> del control total (config, operations, sync, vfs, serve, jobs…) sigue igual.

---

## 8. Conectar el MCP server (Pieza B)

El MCP server se lanza desde tu **gateway MCP** (LobeHub) o cualquier cliente. Con
`RCLONE_TOOLSETS=all` obtienes **control total (98 tools)**.

### 8.1 Opción stdio (el cliente lanza el MCP con npx) — recomendada

Config del cliente MCP (formato genérico `mcpServers`):

```json
{
  "mcpServers": {
    "rclone": {
      "command": "npx",
      "args": ["-y", "rclone-mcp-server"],
      "env": {
        "RCLONE_URL": "http://rclone-rcd:5572",
        "RCLONE_USER": "nasadmin",
        "RCLONE_PASS": "TU_RC_PASS",
        "RCLONE_TOOLSETS": "all"
      }
    }
  }
}
```

> `RCLONE_URL`:
> - Usa `http://rclone-rcd:5572` si el proceso MCP corre **dentro de `db_net`**.
> - Usa `http://${SERVER_IP}:5572` si corre en el host y expusiste el puerto (§5.3 `ports`).

### 8.2 Opción HTTP (un MCP compartido para varios clientes)

```bash
RCLONE_URL=http://rclone-rcd:5572 \
RCLONE_USER=nasadmin RCLONE_PASS=TU_RC_PASS \
RCLONE_TOOLSETS=all \
npx rclone-mcp-server http --port 3000
# Endpoint: http://<host>:3000/mcp
```

⚠️ El endpoint `/mcp` **no tiene auth propia** y con `TOOLSETS=all` incluye borrado/sync/config.
No lo expongas a redes no confiables sin un reverse-proxy con autenticación.

### 8.3 Toolsets disponibles (control total = `all`)

| Toolset | Qué controla |
|---------|--------------|
| `core` / `core_advanced` | versión, stats, comandos rc genéricos |
| `config_read` / `config_admin` | listar/leer remotes / crear/editar/borrar remotes |
| `operations` / `operations_advanced` | list, stat, copy/move/mkdir/deletefile / rmdir, purge, delete |
| `sync` | copy, move, sync (bidireccional, destructivo) |
| `jobs` | jobs en background (`_async` + `job/status`) |
| `mount` | montar/desmontar remotes (requiere §7) |
| `vfs` | caché VFS, refresh, forget |
| `serve` | servir remotes por HTTP/WebDAV/FTP/etc. |
| `cache` / `fscache` | control de cache |
| `backend` | comandos específicos del backend |
| `options` / `plugins` | opciones globales / plugins |
| `sharing` | `operations/publiclink` (enlaces públicos) |
| `debug` | perfilado/gc |

Especiales: `RCLONE_TOOLSETS=default` (mínimo seguro) · **`all` (control total, 98 tools)**.

### 8.4 Usar con **Kiro CLI en el NAS** (control total + auto-aprobación selectiva) — recomendado

> **Kiro Web NO puede** usar este MCP: corre en un sandbox en la nube, sin ruta a tu LAN privada.
> **Kiro CLI SÍ**, porque se ejecuta en tu máquina. Aquí lo instalamos **en el propio NAS**.

Idea: control total (`TOOLSETS=all`) pero con **`autoApprove`** para que las tools **no
destructivas** (leer, listar, copiar, subir, descargar, `sync_copy` aditivo, crear carpeta) se
ejecuten solas, y las **destructivas** (borrar, purgar, mirror `sync_sync`, mover, crear/borrar
remotes, montar/desmontar) **pidan confirmación**.

**Requisitos en el NAS:**
- Node.js instalado (para `npx`): `instal nodejs npm` (o vía nvm).
- Exponer el puerto del daemon **solo a localhost del NAS** (Kiro CLI habla por `localhost`, no está
  en `db_net`). En el `compose.yml` (§5.3) descomenta y usa:
  ```yaml
      ports:
        - "127.0.0.1:5572:5572"     # solo localhost del NAS — NO lo abras a la LAN
  ```
  y `svc recreate rclone-rcd`.

**Config** en `~/.kiro/settings/mcp.json` (global) del NAS:

```json
{
  "mcpServers": {
    "rclone": {
      "command": "npx",
      "args": ["-y", "rclone-mcp-server"],
      "env": {
        "RCLONE_URL": "http://localhost:5572",
        "RCLONE_USER": "nasadmin",
        "RCLONE_PASS": "${RCLONE_RC_PASS}",
        "RCLONE_TOOLSETS": "all"
      },
      "disabled": false,
      "autoApprove": [
        "core_version", "core_stats", "core_about",
        "config_listremotes", "config_get", "config_dump",
        "operations_list", "operations_stat", "operations_size", "operations_check",
        "operations_fsinfo", "operations_publiclink",
        "operations_mkdir",
        "operations_copyfile", "operations_copyurl",
        "sync_copy",
        "job_status", "job_list", "vfs_refresh", "vfs_list"
      ]
    }
  }
}
```

Exporta el secreto en la shell antes de lanzar la CLI (no lo pongas en claro en el JSON):
```bash
export RCLONE_RC_PASS="$(grep RCLONE_RC_PASS $dkco/rclone-rcd/.env | cut -d= -f2)"
kiro-cli            # dentro de la sesión: /mcp  → verifica que 'rclone' cargó y lista las tools
```

**Clasificación aplicada** (destructividad real de rclone):

| Se ejecuta SOLO (autoApprove) | Pide CONFIRMACIÓN (no está en la lista) |
|-------------------------------|------------------------------------------|
| Leer/listar: version, stats, about, listremotes, get, dump, list, stat, size, check, fsinfo, publiclink | `sync_sync` / `sync_bisync` / `sync_resync` (MIRROR, **borran**) |
| Crear carpeta: `operations_mkdir` | `operations_deletefile` / `delete` / `purge` / `rmdir` / `rmdirs` |
| Copiar/subir/descargar: `operations_copyfile`, `operations_copyurl`, `sync_copy` (aditivo) | **Mover**: `operations_movefile`, `sync_move` (borran del origen) |
| Jobs y VFS de solo lectura: `job_status`, `job_list`, `vfs_refresh`, `vfs_list` | Remotes/unidades: `config_create` / `config_update` / `config_delete` |
|  | Montaje: `mount_mount`, `mount_unmount` |

> **Decisiones tomadas:** `sync_copy` (aditivo) va en auto porque NO borra; `sync_sync` (mirror) va a
> confirmación porque borra en destino. **Mover** va a confirmación (borra del origen tras copiar).
> Nombres de tool = endpoint RC en snake_case (`/operations/copyfile` → `operations_copyfile`),
> verificado en el paquete `rclone-mcp-server@1.0.3`.
>
> Alternativa: `disabledTools` oculta tools por completo (ni con confirmación). `autoApprove: ["*"]`
> aprobaría TODO (incluido borrar) — **no recomendado** con `TOOLSETS=all`.

---

## 9. Patrón para operaciones largas (sync / copy de árboles)

Copiar o sincronizar árboles completos puede exceder el timeout del request. **Siempre** usa
`_async: true` y luego consulta el job:

```jsonc
// sync_copy — copia aditiva src→dst (sin borrados)
{ "srcFs": "origen:", "dstFs": "gdrive:", "_async": true }   // devuelve { jobid }

// sync_sync — MIRROR (DESTRUCTIVO: borra en dst lo que no esté en src)
{ "srcFs": "gdrive:", "dstFs": "origen:", "_async": true }

// job_status — poll hasta finished:true
{ "jobid": 17 }
```

Aceptan `_async`: `sync_copy`, `sync_move`, `sync_sync`, `operations_copyfile`,
`operations_movefile`, `operations_size`, `operations_purge`, `operations_delete`,
`operations_copyurl`, `operations_check`.

Convención de rutas en la RC API: los remotes llevan **dos puntos finales** (`gdrive:`),
y siempre **lista antes de adivinar** una ruta.

---

## 10. Seguridad (con control total, importa más)

- **Autenticación del daemon**: usa `--rc-user/--rc-pass` (nunca `--rc-no-auth` si el puerto sale del host).
- **No exponer 5572 a la LAN** salvo necesidad: mantén daemon y MCP en `db_net`.
- **rclone.conf montado read-only** si NO usas `config_admin`:
  cambia el volumen a `./config/rclone.conf:/config/rclone.conf:ro`.
- **Modo seguro opcional** (guards estilo `brokenlander`): si en algún momento quieres exponerlo a un
  agente con menos privilegios, arranca un **segundo** MCP con `RCLONE_TOOLSETS=default` + `RCLONE_READ_ONLY=1`
  (solo browse/cat/download). Puedes tener ambos: uno "control total" interno y uno "read-only" expuesto.

---

## 11. Añadir al arranque escalonado (layers.conf)

Regla del framework: al **crear** un servicio, añádelo a `layers.conf` en la capa correcta.
`rclone-rcd` es infraestructura de datos → misma capa que las DBs / antes de los servicios que lo usen.

```bash
# editar $dkco/scripts/layers.conf y añadir rclone-rcd en la capa adecuada
```

Para detenerlo a propósito sin que el reboot lo reviva ni bloquee su capa: `svc no-boot rclone-rcd`.

---

## Opción B (alternativa) — `rclone rcd` como systemd nativo en el host

Si prefieres no dockerizar el daemon (p. ej. para que `mount` sea más natural en el host):

```bash
# 1) Config protegida por root
sudo mkdir -p /etc/rclone
sudo cp ~/.config/rclone/rclone.conf /etc/rclone/rclone.conf
sudo chmod 600 /etc/rclone/rclone.conf

# 2) Servicio systemd
sudo tee /etc/systemd/system/rclone-rcd.service >/dev/null <<'EOF'
[Unit]
Description=Rclone RC daemon (for MCP)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/rclone rcd \
  --rc-addr=127.0.0.1:5572 \
  --rc-user=nasadmin --rc-pass=CAMBIAR_ESTA_PASS \
  --config=/etc/rclone/rclone.conf
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 3) Aplicar permisos y arrancar (orden real)
sudo systemctl daemon-reload
sudo systemctl enable --now rclone-rcd
systemctl status rclone-rcd --no-pager | head -5
```

Luego el MCP apunta a `RCLONE_URL=http://127.0.0.1:5572` (o `http://${SERVER_IP}:5572`).

> **Docker (A) vs systemd (B):** ambos dan las 98 tools (eso lo decide `TOOLSETS=all` en el MCP, no
> el daemon) y ambos soportan `mount`. Docker es más coherente con nas-dotfiles (`svc`, layers.conf,
> backups) y con FUSE activo por defecto (§5.3) ya cubre `mount` en el host — sin ventaja real de
> systemd. **Recomendación: A (Docker) en `db_net`.** systemd solo si prefieres no dockerizar el binario.

---

## Checklist de placeholders a reemplazar

- `TU_RC_PASS` → el valor real de `RCLONE_RC_PASS` (de `$dkco/rclone-rcd/.env`).
- `nasadmin` → el usuario RC que prefieras.
- `gdrive:` / `origen:` → tus remotes reales (con `:` final).
- `CAMBIAR_ESTA_PASS` (opción B) → una contraseña fuerte real.
- `${SERVER_IP}` → lo hereda del `.env` global; no lo hardcodees.

## Fuentes

- MCP base (control total, toolsets, MCP Resources, async): `angenge/rclone-mcp-server` — npm `rclone-mcp-server@1.0.3` (MIT, refactor de `rclone-ui/rclone-mcp`).
- Modo seguro opcional (guards runtime): `brokenlander/rclone-mcp-readonly` (MIT).
- Imagen del daemon: `rclone/rclone:1.75.1` (Docker Hub).
- RC API de rclone: documentación oficial rclone (`rc`, toolsets por prefijo de path).

_Contenido de las fuentes reescrito y resumido; se enlaza a cada repo/imagen para el detalle completo._
