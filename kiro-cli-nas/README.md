# Instalar Kiro CLI en el NAS (instalación controlada / aislada)

> Guía **reutilizable** para poner Kiro CLI en el NAS Debian y usarlo con cualquier MCP
> (rclone, git, etc.). Pensada para instalación **aislada**, no a nivel de sistema.
>
> Verificado contra el instalador oficial `https://cli.kiro.dev/install` (2026-09-22).
> NAS: Debian x86_64 (Dell PowerEdge T20).

---

## 0. Aclaración importante: Kiro CLI NO es Python ni Node

No hay `venv` ni `pip`/`npm` para esto: **Kiro CLI es un binario compilado** (se descarga, se
verifica por SHA-256 y se copia a un directorio de tu usuario). Por eso "entorno virtual" no aplica
literalmente — pero SÍ se puede instalar de forma **aislada y sin root**, que es el objetivo real.

Tres niveles de aislamiento (elige uno):

| Opción | Borrado sin residuos | Encender/apagar bajo demanda | ¿Toca el host? | Acceso a rclone |
|--------|----------------------|------------------------------|----------------|-----------------|
| **A. Instalador oficial** (`~/.local/bin`) | Medio (borrar 2 binarios + config) | No (siempre disponible) | Deja binario/config en `$HOME` | ✅ directo |
| **B. Prefijo dedicado** (`~/apps/kiro-cli`) | Fácil (`rm -rf` la carpeta) | No | Deja Node/deps en el host | ✅ directo |
| **C. Contenedor Docker** ⭐ | **Total** (`svc down` + borrar carpeta) | **Sí** (`svc up`/`svc stop`) | **No** (todo dentro) | ✅ con `network_mode: host` |

> **Recomendada: C (Docker).** Si tu prioridad es **borrar limpio sin residuos** y **decidir cuándo
> corre** (encender solo cuando lo necesites), Docker es la mejor: `svc up kiro-cli` para usarlo,
> `svc stop` cuando no, y borrado total sin dejar nada en el host. La limitante de red se resuelve con
> `network_mode: host` (§C). B y A siguen documentadas como alternativas más ligeras.

---

## Opción A — Instalador oficial (rápida, ya aislada a tu usuario)

Instala en `~/.local/bin/` sin `sudo`. Es la vía por defecto.

```bash
# 1) Dependencias que exige el instalador en Linux
instal curl unzip                 # 'sha256sum' viene en coreutils (ya presente)

# 2) Instalar (binario a ~/.local/bin del usuario actual)
curl -fsSL https://cli.kiro.dev/install | bash

# 3) PATH (si el instalador avisa que ~/.local/bin no está en PATH)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
reload
kiro-cli --version

# 4) Autenticar + verificar
kiro-cli login                    # imprime una URL → ábrela en el navegador de tu PC (NAS headless)
kiro-cli doctor                   # "Everything looks good!"
```

**Desinstalar:** borra `~/.local/bin/kiro-cli` y `~/.local/bin/kiro-cli-chat`.

---

## Opción B — Prefijo dedicado en `$HOME` (aislada, fácil de quitar) — recomendada

El instalador oficial usa `$HOME/.local/bin` de forma **fija** (no hay flag de directorio). El truco
para aislarlo en su propia carpeta es ejecutar el instalador con `HOME` apuntando a un **prefijo
dedicado**; así todo (binarios, config, credenciales) queda bajo `~/apps/kiro-cli/` y se elimina
borrando esa carpeta — sin ensuciar tu `$HOME` real ni el sistema.

```bash
# 1) Dependencias
instal curl unzip

# 2) Carpeta-prefijo dedicada (primero mkdir, orden real)
mkdir -p $aadm/apps/kiro-cli

# 3) Instalar con HOME redirigido al prefijo → binario en ~/apps/kiro-cli/.local/bin
HOME="$aadm/apps/kiro-cli" curl -fsSL https://cli.kiro.dev/install | HOME="$aadm/apps/kiro-cli" bash

# 4) Wrapper en el PATH normal que lanza el binario aislado con SU home dedicado.
#    Así la config y las credenciales de Kiro viven SOLO en el prefijo.
mkdir -p $aadm/.local/bin
cat > $aadm/.local/bin/kiro-cli <<'EOF'
#!/usr/bin/env bash
export HOME="$HOME/apps/kiro-cli"      # home dedicado para Kiro (config, login, cache)
exec "$HOME/.local/bin/kiro-cli" "$@"
EOF
chmod +x $aadm/.local/bin/kiro-cli

# 5) PATH + verificar
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
reload
kiro-cli --version
kiro-cli login
kiro-cli doctor
```

> **Qué logra esto:** binarios, config (`~/apps/kiro-cli/.kiro/`), login y caché quedan confinados
> en `$aadm/apps/kiro-cli/`. Para desinstalar por completo: `rm -rf $aadm/apps/kiro-cli` y borra el
> wrapper `$aadm/.local/bin/kiro-cli`. Cero rastro en el sistema.
>
> **Nota sobre el wrapper y `$HOME`:** el wrapper fija `HOME` al prefijo ANTES de ejecutar, de modo
> que la config MCP de Kiro vive en `$aadm/apps/kiro-cli/.kiro/settings/mcp.json` (no en tu `$HOME`
> real). Tenlo en cuenta al crear el `mcp.json`: la ruta es la del prefijo.

---

## Opción C — Contenedor Docker (aislamiento total) ⭐ recomendada

Máximo aislamiento: Kiro CLI corre en su propio contenedor con su filesystem, dependencias y
credenciales, **sin tocar el host**. Ventajas para tu caso:

- **Borrado sin residuos:** `svc down kiro-cli` + `rm -rf $dkco/kiro-cli` = no queda NADA en el host
  (ni binario, ni Node, ni config).
- **Bajo demanda:** `svc up kiro-cli` cuando lo necesites, `svc stop kiro-cli` cuando no. Tú decides
  cuándo vive.
- **Red resuelta:** con `network_mode: host` el contenedor ve `localhost:5572` del host → el MCP de
  rclone funciona sin trucos (§C.4).

### C.1 Estructura

```
/docker/kiro-cli/
├── Dockerfile
├── compose.yml
└── data/                         # $HOME persistente del contenedor (login, config, mcp.json)
```

### C.2 Crear carpetas

```bash
mkdir -p $dkco/kiro-cli/data
```

### C.3 Archivos

`Dockerfile` (VERIFICADO en runtime — binario en `/opt/kiro`, fuera del volumen):

```dockerfile
FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip ca-certificates coreutils nodejs npm git \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 kiro

# Instalar Kiro CLI en /opt/kiro (FUERA de /home/kiro, para que el volumen data/ no lo oculte).
# El instalador oficial usa siempre $HOME/.local/bin, asi que se instala con HOME temporal y se copia.
RUN HOME=/tmp/ki bash -c 'curl -fsSL https://cli.kiro.dev/install | bash' \
    && mkdir -p /opt/kiro \
    && cp -a /tmp/ki/.local/bin/. /opt/kiro/ \
    && rm -rf /tmp/ki \
    && chown -R kiro:kiro /opt/kiro

USER kiro
WORKDIR /home/kiro
ENV PATH="/opt/kiro:${PATH}"
ENTRYPOINT ["/opt/kiro/kiro-cli"]
```

> ⚠️ **Gotcha verificado:** si instalas Kiro CLI en `/home/kiro/.local/bin` (el default del
> instalador), el volumen `./data:/home/kiro` **tapa** esa ruta y da
> `exec: "kiro-cli": executable file not found`. Por eso el binario va a `/opt/kiro`.
> `coreutils` se añade para garantizar `sha256sum` (el instalador verifica checksum).

`compose.yml` (con `network_mode: host` de fábrica → ve el daemon rclone en `localhost:5572`):

```yaml
services:
  kiro-cli:
    build: .
    image: kiro-cli-nas:local
    container_name: kiro-cli
    network_mode: host               # ve localhost:5572 del host (MCP de rclone) sin trucos
    stdin_open: true                 # interactivo (TUI)
    tty: true
    volumes:
      - ./data:/home/kiro            # persiste login, config y mcp.json
```

> **Importante:** con `network_mode: host` NO puedes usar a la vez `networks:`, `ports:` ni
> `extra_hosts:` en este servicio (Docker los ignora/rechaza). No hacen falta: en host mode el
> contenedor comparte la red del NAS y llega directo a `127.0.0.1:5572`.

### C.4 Autenticar y usar

```bash
dk kiro-cli
svc build kiro-cli

# La carpeta data/ la crea root, pero el contenedor corre como uid 1000 -> ajustar (obligatorio):
chown -R 1000:1000 $dkco/kiro-cli/data

# Autenticar UNA vez (NAS headless -> device flow, imprime URL+codigo para tu PC):
docker run -it --rm --network host -v $dkco/kiro-cli/data:/home/kiro kiro-cli-nas:local login --use-device-flow

# Sesion normal, en V3 (para que aplique permissions.yaml):
docker run -it --rm --network host -v $dkco/kiro-cli/data:/home/kiro kiro-cli-nas:local --v3
```

> ⚠️ **Gotchas verificados:**
> - **`chown -R 1000:1000 data/`** o el login falla con `Failed to open database: Permission denied`.
> - **`login --use-device-flow`**: el modo navegador falla en el NAS headless; el device flow imprime
>   una URL + código que abres en tu PC.
> - **`--v3`**: obligatorio para que Kiro CLI use `permissions.yaml` (permisos por capacidades). Sin
>   `--v3` corre en V2, que **ignora** `autoApprove`/`permissions.yaml` y pide aprobación a todo.

### C.5 Borrado limpio (sin residuos)

```bash
svc down kiro-cli                   # para y elimina el contenedor
docker image rm kiro-cli-nas:local  # elimina la imagen
rm -rf $dkco/kiro-cli               # elimina Dockerfile, compose y data (login/config/mcp.json)
```

Tras esto **no queda nada** en el host relacionado con Kiro CLI. Ese es el objetivo que buscabas.

> **No añadir a `layers.conf`:** este servicio es bajo demanda, NO debe arrancar en el boot. Si tu
> framework exige listar todos los servicios (`BOOT_ORDER_REQUIRE_ALL=1`), usa `svc no-boot kiro-cli`
> para que el arranque escalonado lo salte sin bloquear su capa.

---

## 📁 Mapa de archivos creados (montaje real — Opción C + MCP rclone)

Inventario COMPLETO de lo que quedó creado en el NAS tras el montaje verificado. Sirve para
reconstruir, auditar o borrar. `[host]` = lo crea root en el host · `[gen]` = generado por script ·
`[cont]` = lo crea Kiro CLI dentro del contenedor (persistido en el volumen).

### En `$dkco/kiro-cli/` (el servicio Docker de Kiro CLI)

```
/docker/kiro-cli/
├── Dockerfile                                  [host] Debian + Node + Kiro CLI (/opt/kiro) + uv + nextdns-mcp (/opt/nextdns-venv)
├── compose.yml                                 [host] network_mode: host, volumen ./data:/home/kiro
├── .no-boot                                    [host] excluye del arranque escalonado (bajo demanda)
├── nextdns.env                                 [host] secretos NextDNS (chmod 600) — API keys por persona
└── data/                                       [cont] = $HOME del contenedor (uid 1000)
    ├── .local/…                                [cont] sesion/credenciales del login (device-flow)
    └── .kiro/
        ├── agents/                             [cont] agentes de Kiro CLI (autogenerado)
        ├── sessions/                           [cont] historial de sesiones
        ├── steering/
        │   ├── idioma.md                       [host] fuerza respuestas en español
        │   └── nextdns-usuarios.md             [host] mapa "papá"→nextdns-papa, "yo"→nextdns-infinix
        └── settings/
            ├── mcp_tools/
            │   ├── rclone.json                 [host] ← EDITAS: MCP rclone (${RCLONE_RC_PASS})
            │   └── nextdns.json                [host] ← EDITAS: MCP nextdns (un bloque por persona)
            ├── mcp.json                        [gen]  ← generado por 'mcp-build' (NO editar a mano)
            └── permissions.yaml                [host] permisos V3 (rclone/* + nextdns-*/* allow/ask)
```

### En `$aadm/.local/bin/` (scripts en el host)

```
/home/aadm/.local/bin/
├── mcp-build                                   [host] ensambla mcp_tools/*.json → mcp.json (jq)
└── kiro                                        [host] wrapper: inyecta RCLONE_RC_PASS del .env y lanza --v3
```

### Dependencia externa (otro servicio, NO parte de kiro-cli)

```
/docker/rclone-rcd/                             el daemon con el que habla el MCP (guia aparte)
├── compose.yml, .env
└── config/rclone.conf                          remotes: mega, gdrive
```

### Qué contiene cada archivo clave (resumen)

| Archivo | Rol | Editable a mano |
|---------|-----|-----------------|
| `Dockerfile` | Instala Kiro CLI en `/opt/kiro` (fuera del volumen) | Sí |
| `compose.yml` | `network_mode: host` + volumen `data/` | Sí |
| `settings/mcp_tools/rclone.json` | Bloque `mcpServers.rclone` (command npx, env, `${RCLONE_RC_PASS}`) | **Sí (fuente)** |
| `settings/mcp.json` | Combinado de todos los `mcp_tools/*.json` | **No (generado)** |
| `settings/permissions.yaml` | Reglas V3: `rclone/*`=allow, destructivas=ask | Sí |
| `steering/idioma.md` | Responder en español | Sí |
| `$aadm/.local/bin/mcp-build` | Regenera `mcp.json` desde los trozos | Sí |
| `$aadm/.local/bin/kiro` | Lanza el contenedor con la pass inyectada y `--v3` | Sí |

### Flujo de mantenimiento

- **Añadir un MCP:** crear `settings/mcp_tools/<nuevo>.json` → `mcp-build` → relanzar `kiro`.
- **Editar rclone:** editar `settings/mcp_tools/rclone.json` → `mcp-build` → relanzar.
- **Cambiar permisos:** editar `settings/permissions.yaml` → relanzar (no requiere `mcp-build`).
- **Tras tocar archivos en `data/` como root:** `chown -R 1000:1000 $dkco/kiro-cli/data`.
- **Borrar TODO sin residuos:** `svc down kiro-cli` + `docker image rm kiro-cli-nas:local` +
  `rm -rf $dkco/kiro-cli` + (opcional) borrar `$aadm/.local/bin/{kiro,mcp-build}`.

---

## Después de instalar: configurar un MCP

Con Kiro CLI ya instalado (A, B o C), la config de un MCP va en `mcp.json`:

- **Opción A:** `~/.kiro/settings/mcp.json`
- **Opción B:** `$aadm/apps/kiro-cli/.kiro/settings/mcp.json` (el `$HOME` dedicado del wrapper)
- **Opción C:** `$dkco/kiro-cli/data/.kiro/settings/mcp.json` (el volumen del contenedor)

Verifica dentro de la sesión con `/mcp`.

### Puntos verificados en runtime (importantes)

- **Permisos (V3):** el `autoApprove` del `mcp.json` **NO** controla las aprobaciones en Kiro CLI V3.
  El control real es `settings/permissions.yaml` con reglas `capability: mcp` y `effect` allow/ask/deny
  (`deny > ask > allow`). Hay que lanzar **con `--v3`**.
- **`mcp.json` limpio (estilo !include):** Kiro no soporta include; se emula con `settings/mcp_tools/<mcp>.json`
  (uno por MCP) + un script `mcp-build` (jq) que los ensambla en `mcp.json`.
- **Secretos:** el `mcp.json` usa `"${VAR}"` y un wrapper inyecta la variable al `docker run` (`-e VAR=...`),
  leyéndola del `.env` del servicio correspondiente. Nunca hardcodear el secreto en el JSON.
- **Idioma:** `settings/../steering/idioma.md` para respuestas en español (la UI sigue en inglés).

Para el **MCP de rclone con control total y auto-aprobación selectiva** (con el `permissions.yaml`,
`mcp-build` y wrapper ya escritos y probados), ver la guía dedicada:
[`../rclone-mcp-control-total/README.md`](../rclone-mcp-control-total/README.md) — sección
"✅ Verificado en runtime" (R5–R8).

Para el **MCP de NextDNS multi-cuenta** (una cuenta/API key por persona, control por lenguaje
natural tipo "bloquea YouTube a papá", con Python 3.14 en venv aislado dentro de la imagen):
[`./nextdns-multicuenta.md`](./nextdns-multicuenta.md) — verificado en runtime.

---

## Referencias

- Instalador oficial: https://cli.kiro.dev/install (binario Rust, SHA-256, `~/.local/bin`)
- Docs setup Kiro CLI: https://kiro.dev/docs/cli/setup
- Docs MCP config: https://kiro.dev/docs/mcp

_Contenido reescrito/resumido a partir de la documentación oficial; se enlaza a la fuente._
