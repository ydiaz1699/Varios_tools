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

| Opción | Qué aísla | ¿Root? | Sirve para el MCP de rclone (host) | Esfuerzo |
|--------|-----------|--------|-------------------------------------|----------|
| **A. Instalador oficial** (`~/.local/bin`) | Tu usuario | No | ✅ Sí | Mínimo |
| **B. Prefijo dedicado** (`$HOME` apuntado a `~/apps/kiro-cli`) | Carpeta propia, fácil de borrar | No | ✅ Sí | Bajo |
| **C. Contenedor Docker** | Total (FS, red, deps) | No (usa Docker) | ⚠️ Limitado — ver §C.4 | Medio |

> **Para controlar rclone** (que corre en el host del NAS), lo natural es **B** (o A).
> **C (Docker)** aísla más pero complica el acceso a `localhost:5572` y a `rclone.conf` del host.

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

## Opción C — Contenedor Docker (aislamiento total)

Máximo aislamiento: Kiro CLI corre en su propio contenedor, con su filesystem, sus dependencias y
sus credenciales, sin tocar el host. Encaja con el framework nas-dotfiles.

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

`Dockerfile`:

```dockerfile
FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip ca-certificates nodejs npm git \
    && rm -rf /var/lib/apt/lists/*
# Usuario no-root con HOME persistible
RUN useradd -m -u 1000 kiro
USER kiro
WORKDIR /home/kiro
# Instalar Kiro CLI (a ~/.local/bin del usuario kiro)
RUN curl -fsSL https://cli.kiro.dev/install | bash || true
ENV PATH="/home/kiro/.local/bin:${PATH}"
ENTRYPOINT ["kiro-cli"]
```

`compose.yml`:

```yaml
services:
  kiro-cli:
    build: .
    image: kiro-cli-nas:local
    container_name: kiro-cli
    stdin_open: true                 # interactivo (TUI)
    tty: true
    volumes:
      - ./data:/home/kiro            # persiste login, config y mcp.json
    # Para que el MCP de rclone alcance el daemon del host (§C.4):
    # extra_hosts:
    #   - "host.docker.internal:host-gateway"
    # network_mode: host             # alternativa: ve localhost:5572 del host directamente
```

Uso:

```bash
dk kiro-cli
svc build kiro-cli
docker run -it --rm -v $dkco/kiro-cli/data:/home/kiro kiro-cli-nas:local login   # autenticar una vez
docker run -it --rm -v $dkco/kiro-cli/data:/home/kiro kiro-cli-nas:local          # sesión normal
```

### C.4 ⚠️ Limitación para el caso rclone

Un Kiro CLI **dentro de Docker** tiene el MISMO problema de red que Kiro Web: por defecto NO ve
`localhost:5572` del host ni el `rclone.conf` del host. Para que el MCP de rclone funcione desde el
contenedor tienes que **darle ruta al daemon**:

- **`network_mode: host`** → el contenedor comparte la red del host y `RCLONE_URL=http://localhost:5572`
  funciona. Es lo más simple, pero reduce el aislamiento de red.
- o **`extra_hosts: host.docker.internal:host-gateway`** + `RCLONE_URL=http://host.docker.internal:5572`
  (con el puerto expuesto en el compose de rclone).
- o meter este contenedor en **`db_net`** y usar `RCLONE_URL=http://rclone-rcd:5572` (misma red que el
  daemon) — la opción más limpia si ya usas `db_net`.

> Por esta fricción, **para controlar rclone recomiendo la opción B** (Kiro CLI en el host). Usa C si
> tu prioridad es el aislamiento total y aceptas configurar la red.

---

## Después de instalar: configurar un MCP

Con Kiro CLI ya instalado (A, B o C), la config de un MCP va en `mcp.json`:

- **Opción A:** `~/.kiro/settings/mcp.json`
- **Opción B:** `$aadm/apps/kiro-cli/.kiro/settings/mcp.json` (el `$HOME` dedicado del wrapper)
- **Opción C:** `$dkco/kiro-cli/data/.kiro/settings/mcp.json` (el volumen del contenedor)

Verifica dentro de la sesión con `/mcp`.

Para el **MCP de rclone con control total y auto-aprobación selectiva**, ver la guía dedicada:
[`../rclone-mcp-control-total/README.md`](../rclone-mcp-control-total/README.md) (§8.4.2).

---

## Referencias

- Instalador oficial: https://cli.kiro.dev/install (binario Rust, SHA-256, `~/.local/bin`)
- Docs setup Kiro CLI: https://kiro.dev/docs/cli/setup
- Docs MCP config: https://kiro.dev/docs/mcp

_Contenido reescrito/resumido a partir de la documentación oficial; se enlaza a la fuente._
