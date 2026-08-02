# Módulo 3: Rclone Media — Mount FUSE + SA Rotation + Crypt + Jellyfin

> **Tipo**: Plugin del agente NAS + systemd service persistente (24/7)
> **Destino de implementación**: `agent/core/rclone_media.py` + `agent/core/rclone_sa_pool.py` + systemd units
> **Prioridad**: Alta (es el módulo que habilita streaming de medios desde Google Drive)

---

## 1. Propósito

Montar una **biblioteca de medios cifrada** almacenada en Google Drive como filesystem local,
de forma que **Jellyfin** pueda leerla y servirla por streaming como si fuera almacenamiento local.

Características clave:
- **Cifrado end-to-end**: Google no ve contenido ni nombres de archivo (capa `crypt`).
- **Descifrado transparente**: Rclone descifra al vuelo en memoria; Jellyfin ve archivos normales.
- **SA rotation**: 100 Service Accounts rotando para bypass del límite de lectura (~10 TB/día/SA).
- **VFS cache agresivo**: caché local grande para evitar re-descargas y streaming fluido.
- **Mount FUSE 24/7**: persistente, auto-restart, controlado por systemd.
- **Jellyfin compatible**: `--allow-other` para que el proceso de Jellyfin lea el mountpoint.


---

## 2. Cómo funciona el cifrado con Jellyfin

El punto crítico: ¿cómo puede Jellyfin reproducir archivos si están cifrados en Google Drive?

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Google Drive (Shared Drive)                    │
│                                                                      │
│  Contenido CIFRADO:                                                  │
│  ├── q5kj2m8v/                    ← nombre de directorio cifrado     │
│  │   ├── 8fn3x9pq2.bin           ← "Avatar (2009).mkv" cifrado      │
│  │   ├── m2kd7hg4.bin            ← "Inception (2010).mkv" cifrado   │
│  │   └── ...                                                         │
│  Google solo ve: archivos binarios con nombres aleatorios             │
│  Google NO PUEDE: indexar, escanear, ni identificar el contenido     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ rclone mount (FUSE) con crypt remote
                                   │ descifra en RAM al vuelo
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  /mnt/rclone/media/ (mountpoint FUSE)                 │
│                                                                      │
│  Contenido EN CLARO (solo visible localmente):                       │
│  ├── Peliculas/                                                      │
│  │   ├── Avatar (2009).mkv                                           │
│  │   ├── Inception (2010).mkv                                        │
│  │   └── ...                                                         │
│  ├── Series/                                                         │
│  │   ├── Breaking Bad/S01/E01.mkv                                    │
│  │   └── ...                                                         │
│  └── Musica/                                                         │
│                                                                      │
│  Jellyfin lee estos archivos NORMALMENTE — no sabe que hay cifrado   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ Jellyfin lee directamente
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Jellyfin (Docker o nativo)                     │
│                                                                      │
│  Bibliotecas configuradas:                                           │
│  • Películas → /mnt/rclone/media/Peliculas                           │
│  • Series   → /mnt/rclone/media/Series                               │
│  • Música   → /mnt/rclone/media/Musica                               │
│                                                                      │
│  Streaming vía web/apps a cualquier dispositivo                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Clave**: El descifrado ocurre **en RAM** durante la lectura FUSE. Los archivos descifrados
**nunca se escriben a disco** (a menos que el VFS cache los retenga temporalmente como buffer).


---

## 3. SA Rotation para lectura (bypass de cuota de download)

### 3.1 ¿Por qué rotar para lectura?

Google Drive tiene un límite de **~10 TB/día por cuenta** de descarga (API read).
Para una biblioteca de medios con múltiples usuarios de Jellyfin streaming simultáneamente,
una sola SA puede alcanzar el límite. Con 100 SA rotando:

```
100 SA × ~10 TB/día = ~1 PB/día de lectura teórica
```

En la práctica, con un homelab de 3-5 usuarios simultáneos viendo en 4K (~25 Mbps c/u):
- 5 usuarios × 25 Mbps = 125 Mbps = ~1.35 TB/día
- Una sola SA bastaría para uso normal
- La rotation es útil para: picos, scan de biblioteca, múltiples transcodings

### 3.2 Mecanismo de rotación

```
                    ┌───────────────────────────┐
                    │     SA Pool Manager        │
                    │                           │
                    │  pool: [SA-051...SA-100]  │  ← 50 SA dedicadas a lectura
                    │  current: SA-067          │
                    │  cooldown: {SA-065: 23h}  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  Detección de error:       │
                    │  • 403 userRateLimitExceeded│
                    │  • 429 Too Many Requests   │
                    │  • Timeout sostenido       │
                    └─────────────┬─────────────┘
                                  │ trigger
                    ┌─────────────▼─────────────┐
                    │  Acción:                   │
                    │  1. Marcar SA actual en    │
                    │     cooldown (24h)         │
                    │  2. Rotar a siguiente SA   │
                    │  3. Reconfigurar rclone    │
                    │     (--drive-service-      │
                    │      account-file)         │
                    │  4. Remount o RC API call  │
                    └───────────────────────────┘
```

### 3.3 Partición del pool de SA

Recomendación: **no compartir SAs** entre upload (9Drive) y read (rclone-media):

| Rango | Uso | Módulo |
|-------|-----|--------|
| SA-001 a SA-050 | Upload (write) | 9Drive / AutoRclone |
| SA-051 a SA-100 | Download (read) | rclone-media |
| SA dedicada | Backup offsite | Módulo 1 (rclone-backup) |

Esto evita conflictos de cuota y simplifica la auditoría.


---

## 4. Configuración de Rclone (remotes)

### 4.1 Remote base (Google Drive con SA)

```ini
# /etc/rclone/rclone.conf (sección relevante — el archivo está cifrado)

[gdrive-media]
type = drive
scope = drive.readonly
service_account_file = /etc/rclone/sa-pool/sa-051.json
team_drive = 0ABCxxxxxxxxxxxxxxxxxx
root_folder_id =
```

**Notas**:
- `scope = drive.readonly`: la SA de lectura NO necesita permiso de escritura.
- `service_account_file`: apunta a la SA activa actual. El rotador cambia este valor.
- `team_drive`: ID del Shared Drive donde está la biblioteca cifrada.

### 4.2 Remote crypt (encima del base)

```ini
[media-crypt]
type = crypt
remote = gdrive-media:media/
filename_encryption = standard
directory_name_encryption = true
password = *** (cifrado dentro de rclone.conf)
password2 = *** (salt, cifrado dentro de rclone.conf)
```

**Notas**:
- `remote = gdrive-media:media/`: apunta al directorio cifrado dentro del Shared Drive.
- `filename_encryption = standard`: nombres de archivo cifrados (Google no puede buscar por nombre).
- `directory_name_encryption = true`: nombres de directorio también cifrados.
- `password` y `password2`: generados con `rclone config password`, almacenados cifrados en rclone.conf.

### 4.3 Generación de passwords de crypt

```bash
# NUNCA inventar passwords a mano — usar el generador de rclone
sudo -u rclone rclone --config /etc/rclone/rclone.conf config password
# Genera passwords criptográficamente seguros y los almacena en el conf
```

**IMPORTANTE**: Si pierdes la password de crypt, **los datos son irrecuperables**.
Guardar un backup de la password (o del rclone.conf descifrado) en un lugar seguro offline.


---

## 5. Unidad systemd: Mount FUSE persistente

### 5.1 Service template: `/etc/systemd/system/rclone-media@.service`

```ini
[Unit]
Description=Rclone media FUSE mount: %i
Documentation=man:rclone(1)
AssertPathIsDirectory=/mnt/rclone/%i
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=rclone
Group=rclone

Environment=RCLONE_CONFIG=/etc/rclone/rclone.conf
Environment=RCLONE_PASSWORD_COMMAND=/etc/rclone/secrets/get-config-pass.sh

ExecStartPre=/bin/mkdir -p /mnt/rclone/%i
ExecStart=/usr/bin/rclone mount media-crypt: /mnt/rclone/%i \
    --allow-other \
    --uid 1000 \
    --gid 1000 \
    --umask 022 \
    --dir-cache-time 72h \
    --poll-interval 15m \
    --vfs-cache-mode full \
    --vfs-cache-max-size 50G \
    --vfs-cache-max-age 72h \
    --vfs-read-chunk-size 64M \
    --vfs-read-chunk-size-limit 0 \
    --vfs-read-ahead 256M \
    --buffer-size 128M \
    --cache-dir /var/lib/rclone/vfs-cache/%i \
    --drive-chunk-size 64M \
    --drive-acknowledge-abuse \
    --no-modtime \
    --read-only \
    --log-level INFO \
    --log-file /var/log/rclone/media-%i.log

ExecStop=/bin/fusermount -uz /mnt/rclone/%i
Restart=on-failure
RestartSec=10
TimeoutStartSec=30

# ════════════════════════════════════════════════════════════
# SANDBOXING (con FUSE — requiere CAP_SYS_ADMIN)
# ════════════════════════════════════════════════════════════

NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/rclone/vfs-cache/%i /mnt/rclone/%i /var/log/rclone
PrivateTmp=true
PrivateDevices=false
DeviceAllow=/dev/fuse rw
ProtectClock=true
ProtectHostname=true
ProtectKernelLogs=true
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
ProtectProc=invisible
ProcSubset=pid

# FUSE con --allow-other requiere CAP_SYS_ADMIN
AmbientCapabilities=CAP_SYS_ADMIN
CapabilityBoundingSet=CAP_SYS_ADMIN
# Si NO usas --allow-other, eliminar las dos líneas anteriores
# y dejar CapabilityBoundingSet= vacío (más seguro)

RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true
MemoryDenyWriteExecute=true
RemoveIPC=true

SystemCallFilter=@system-service @mount
SystemCallFilter=~@privileged @resources @debug
SystemCallErrorNumber=EPERM
SystemCallArchitectures=native

RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

# Recursos (el VFS cache puede consumir mucha RAM/disco)
LimitNOFILE=65536
TasksMax=256
MemoryMax=4G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

### 5.2 Explicación de flags de rendimiento para Jellyfin

| Flag | Valor | Por qué |
|------|-------|---------|
| `--vfs-cache-mode full` | full | Permite seek (necesario para streaming de video con saltos) |
| `--vfs-cache-max-size 50G` | 50G | Buffer local grande para evitar re-descargas |
| `--vfs-cache-max-age 72h` | 72h | Retener archivos cacheados 3 días (útil para rewatching) |
| `--vfs-read-chunk-size 64M` | 64M | Chunks grandes para menos roundtrips HTTPS |
| `--vfs-read-chunk-size-limit 0` | 0 (sin límite) | Permite que chunks crezcan sin tope |
| `--vfs-read-ahead 256M` | 256M | Prebuffer de 256 MB (streaming fluido en 4K) |
| `--buffer-size 128M` | 128M | Buffer de lectura por archivo |
| `--dir-cache-time 72h` | 72h | Cache de listados de directorio (la biblioteca no cambia cada minuto) |
| `--poll-interval 15m` | 15m | Detectar archivos nuevos cada 15 min |
| `--drive-chunk-size 64M` | 64M | Chunks de descarga del API de Drive |
| `--no-modtime` | — | No consultar modtime (reduce API calls, Jellyfin no lo necesita) |
| `--read-only` | — | Prevenir escrituras accidentales al Drive desde el mount |
| `--allow-other` | — | Jellyfin (otro usuario/container) pueda leer el mountpoint |

### 5.3 Prerequisito: `/etc/fuse.conf`

Para que `--allow-other` funcione, debe estar habilitado en FUSE:

```bash
# /etc/fuse.conf
user_allow_other
```

```bash
sudo sed -i 's/#user_allow_other/user_allow_other/' /etc/fuse.conf
```


---

## 6. Integración con Jellyfin

### 6.1 Jellyfin en Docker

Si Jellyfin corre en Docker, necesita acceso al mountpoint FUSE del host:

```yaml
# docker/jellyfin/compose.yml
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    user: "1000:1000"
    volumes:
      - /docker/jellyfin/config:/config
      - /docker/jellyfin/cache:/cache
      # ↓ MOUNT FUSE del host — requiere propagation
      - /mnt/rclone/media:/media:ro,slave
    devices:
      - /dev/dri:/dev/dri  # hardware transcoding (opcional)
    ports:
      - "8096:8096"
    restart: unless-stopped
    depends_on:
      - rclone-media  # si usas Docker para rclone también (no recomendado)
```

**IMPORTANTE**: El flag `:slave` (o `:rslave`) en el bind mount es necesario para que
Docker vea el contenido del mount FUSE que se monta DESPUÉS de que el container arranca.
Alternativa: asegurar que `rclone-media@.service` arranca ANTES que Jellyfin.

### 6.2 Jellyfin nativo (systemd)

Si Jellyfin corre nativo, asegurarse que:

1. El usuario de Jellyfin pueda leer `/mnt/rclone/media/` (grupo `rclone` o ACL).
2. El servicio de Jellyfin dependa del mount:

```ini
# Override para jellyfin.service
[Unit]
After=rclone-media@media.service
Requires=rclone-media@media.service
```

```bash
sudo systemctl edit jellyfin.service
# Agregar las líneas de arriba
```

### 6.3 Orden de arranque

```
network-online.target
    ↓
rclone-media@media.service (mount FUSE)
    ↓ (After=, Requires=)
jellyfin.service (o docker container)
    ↓
Jellyfin escanea /mnt/rclone/media/ → encuentra archivos → sirve streaming
```

### 6.4 Configuración de bibliotecas en Jellyfin

Una vez montado, configurar en Jellyfin Dashboard → Libraries:

| Biblioteca | Ruta | Tipo |
|------------|------|------|
| Películas | `/media/Peliculas` (o `/mnt/rclone/media/Peliculas`) | Movies |
| Series | `/media/Series` | Shows |
| Música | `/media/Musica` | Music |
| Anime | `/media/Anime` | Shows (con metadata provider específico) |

**Recomendaciones de scan**:
- Desactivar "Real time monitoring" (FUSE no soporta inotify de forma confiable).
- Scan programado cada 6-12h (o manual después de subir contenido nuevo vía 9Drive).
- NFO files y artwork local mejoran la experiencia (evitan API calls de metadata).


---

## 7. Módulo del agente NAS: `rclone_media.py` + `rclone_sa_pool.py`

### 7.1 `agent/core/rclone_sa_pool.py` — Gestión del pool de SA

```python
"""
Responsabilidades:
- Listar SA disponibles en /etc/rclone/sa-pool/
- Rastrear cuál SA está activa y cuáles están en cooldown
- Rotar a la siguiente SA disponible cuando se detecta rate limit
- Health check: verificar que cada SA tiene acceso al Shared Drive
- Persistir estado de rotación (cuál SA está activa, cooldowns)
"""

# Estructura de datos:
SA_POOL_DIR = Path("/etc/rclone/sa-pool/")           # 100 JSONs
SA_STATE_FILE = Path("/var/lib/rclone/sa-state.json") # estado de rotación

# Estado ejemplo:
{
    "active_sa": "sa-067.json",
    "partition": "read",           # "read" o "write"
    "last_rotation": "2026-08-01T03:45:00Z",
    "cooldowns": {
        "sa-065.json": "2026-08-01T02:30:00Z",  # expira en ~22h
        "sa-066.json": "2026-08-01T03:00:00Z"
    },
    "rotation_count_today": 3,
    "errors_today": {"sa-065.json": 2, "sa-066.json": 1}
}
```

### 7.2 `agent/core/rclone_media.py` — Lifecycle del mount

```python
"""
Responsabilidades:
- Instalar la unidad systemd rclone-media@.service
- Iniciar/detener/reiniciar el mount
- Monitorear salud del mount (¿está montado? ¿responde? ¿errores de cuota?)
- Trigger de SA rotation cuando detecta errores 403/429 en logs
- Reportar estadísticas: cache hit ratio, ancho de banda, SA activa
- Integración con Jellyfin: verificar que Jellyfin puede leer el mountpoint
"""

# Tools que expone:
# rclone_media_status()       → estado del mount + SA activa + cache stats
# rclone_media_start()        → inicia el mount FUSE
# rclone_media_stop()         → desmonta (fusermount -uz)
# rclone_media_rotate_sa()    → fuerza rotación manual de SA
# rclone_media_cache_clear()  → limpia VFS cache
# rclone_media_health()       → ¿mount responde? ¿Jellyfin puede leer?
```

### 7.3 Tools para el agente

```python
# agent/tools/rclone_media_tools.py

@tool
def rclone_media_status() -> str:
    """Estado completo del mount FUSE de media: si está montado, SA activa,
    estadísticas de VFS cache (tamaño usado, hit ratio), ancho de banda actual,
    y si Jellyfin puede leer el mountpoint."""

@tool
def rclone_media_start(mount_name: str = "media") -> str:
    """Inicia el mount FUSE de media. Requiere que la unidad systemd
    rclone-media@.service esté instalada. Verifica automáticamente
    que la SA activa tiene acceso al Shared Drive antes de montar."""

@tool
def rclone_media_stop(mount_name: str = "media") -> str:
    """Detiene el mount FUSE de media (fusermount -uz). Safe: espera a que
    no haya lecturas activas antes de desmontar. Si Jellyfin está usando
    archivos, advierte pero NO fuerza (a menos que force=True)."""

@tool
def rclone_media_rotate_sa() -> str:
    """Fuerza rotación manual de Service Account. Útil si la SA actual
    muestra errores sostenidos. Pone la SA actual en cooldown 24h y
    activa la siguiente disponible. Requiere remount."""

@tool
def rclone_media_cache_stats() -> str:
    """Estadísticas del VFS cache: espacio usado, archivos cacheados,
    espacio libre antes de alcanzar el límite, y archivos más accedidos."""

@tool
def rclone_media_cache_clear() -> str:
    """Limpia el VFS cache local. ADVERTENCIA: el próximo acceso a cualquier
    archivo requerirá descarga completa desde Google Drive. Usar solo si
    hay archivos corruptos en cache o para liberar espacio en disco."""
```


---

## 8. Automatización de SA rotation

### 8.1 Detección de rate limit

El rotador monitorea los logs del mount buscando patrones de error:

```python
# Patrones que disparan rotación:
RATE_LIMIT_PATTERNS = [
    "googleapi: Error 403: User Rate Limit Exceeded",
    "googleapi: Error 403: Rate Limit Exceeded",
    "googleapi: Error 429",
    "backend is rate limited",
]
```

### 8.2 Estrategia de rotación

```
1. Detectar error de cuota en logs (o vía RC API si el mount usa rcd)
2. Marcar SA actual en cooldown (24h)
3. Seleccionar siguiente SA disponible (no en cooldown)
4. Actualizar rclone.conf: service_account_file = /etc/rclone/sa-pool/sa-NNN.json
5. Opción A: Remount completo (systemctl restart rclone-media@media)
   Opción B: RC API call para cambiar backend on-the-fly (si soportado)
6. Log: "Rotated from SA-065 to SA-067 (reason: 403 rate limit)"
7. Si todas las SA están en cooldown → alerta al usuario, esperar
```

### 8.3 Implementación con systemd path unit (alternativa)

En vez de un daemon que parsea logs, se puede usar un `systemd.path` que vigila el log:

```ini
# /etc/systemd/system/rclone-media-watchdog.path
[Unit]
Description=Watch rclone media logs for rate limit errors

[Path]
PathChanged=/var/log/rclone/media-media.log
Unit=rclone-media-rotate.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/rclone-media-rotate.service
[Unit]
Description=Rotate SA on rate limit detection

[Service]
Type=oneshot
ExecStart=/usr/local/bin/rclone-sa-rotate.sh
```

### 8.4 gclone como alternativa simplificada

[gclone](https://github.com/l3v11/gclone) es un fork de rclone con SA rotation **nativa**:

```ini
# rclone.conf para gclone
[gdrive-media]
type = drive
scope = drive.readonly
service_account_file = /etc/rclone/sa-pool/sa-051.json
service_account_file_path = /etc/rclone/sa-pool/
# ↑ gclone rota automáticamente entre TODOS los JSON de este directorio
team_drive = 0ABCxxxxxxxxxxxxxxxxxx
```

**Ventajas de gclone**:
- Rotación automática sin código custom
- Drop-in replacement de rclone (misma CLI, mismos flags)
- No necesita watchdog/scripts

**Desventajas de gclone**:
- Es un fork: puede quedarse atrás respecto a rclone oficial
- Menos mantenido (último release puede estar desactualizado)
- No se puede usar con `rclone-mcp` (que espera rclone oficial)


---

## 9. VFS Cache: diseño y sizing

### 9.1 ¿Por qué cache-mode full?

| Modo | Seek | Write | Uso de disco | Para Jellyfin |
|------|------|-------|--------------|---------------|
| `off` | No | No | 0 | ❌ No funciona (no puede seek en video) |
| `minimal` | No | Sí | Bajo | ❌ No funciona |
| `writes` | No | Sí | Bajo | ❌ No funciona |
| `full` | Sí | Sí | Alto | ✅ Necesario para streaming de video |

Jellyfin necesita **seek** (saltar a un punto del video), lo cual requiere `full`.

### 9.2 Sizing del cache

```
Cálculo para una biblioteca de streaming:

Escenario: 5 usuarios viendo en 4K simultáneamente
- 4K Remux: ~60-80 Mbps → ~30 GB por película de 2h
- Cache "caliente" deseable: últimas 5-10 películas vistas = 150-300 GB
- Mínimo funcional: 50 GB (3-4 películas en cache)
- Recomendado: 100-200 GB (si tienes espacio en el NAS)

Regla práctica:
- SSD: 100-200 GB de cache (seek instantáneo)
- HDD: 50-100 GB (seek más lento pero funcional)
- NVMe: 200-500 GB si puedes (experiencia premium)
```

### 9.3 Estructura del cache en disco

```
/var/lib/rclone/vfs-cache/media/
├── .cache-state.json          ← metadata del cache (qué archivos, cuándo se accedieron)
├── Peliculas/
│   ├── Avatar (2009).mkv      ← archivo parcialmente cacheado (sparse file)
│   └── Inception (2010).mkv
└── Series/
    └── Breaking Bad/S01/E01.mkv
```

### 9.4 Políticas de evicción

Rclone evicta del cache cuando:
1. Se alcanza `--vfs-cache-max-size` (50G en nuestra config)
2. Un archivo no se ha accedido en `--vfs-cache-max-age` (72h)
3. Se usa LRU (Least Recently Used) para decidir qué evictar primero

### 9.5 Monitoreo del cache

```bash
# Tamaño actual del cache
du -sh /var/lib/rclone/vfs-cache/media/

# Archivos más recientes en cache (lo que se está viendo)
find /var/lib/rclone/vfs-cache/media/ -type f -mmin -60

# Vía RC API (si el mount usa rcd):
# POST /vfs/stats → cache size, items, hits, misses
```


---

## 10. Subir contenido nuevo a la biblioteca cifrada

### 10.1 El problema

Si la biblioteca en Google Drive está cifrada con `crypt`, no puedes simplemente subir
archivos vía la interfaz web de Google Drive (estarían en claro y romperían la estructura).

**Solo rclone puede escribir archivos cifrados correctamente.**

### 10.2 Flujo de upload de media nueva

```
Descargar/obtener archivo localmente
    ↓
rclone copy /path/local media-crypt:Peliculas/
    ↓ (rclone cifra automáticamente al escribir via crypt remote)
Google Drive recibe el archivo CIFRADO
    ↓ (después de --poll-interval o scan manual)
El mount FUSE ve el archivo nuevo descifrado
    ↓
Jellyfin detecta archivo nuevo en próximo scan
```

### 10.3 Tool del agente para upload de media

```python
@tool
def rclone_media_upload(local_path: str, destination: str = "") -> str:
    """Sube un archivo/directorio local a la biblioteca cifrada de media.
    El archivo se cifra automáticamente al escribir (capa crypt).
    
    Requiere usar una SA del pool de ESCRITURA (SA-001 a SA-050).
    
    Args:
        local_path: ruta local del archivo, ej. "/tmp/Avatar (2009).mkv"
        destination: subdirectorio destino, ej. "Peliculas" o "Series/Breaking Bad/S01"
    """
```

### 10.4 Integración con 9Drive para upload

Flujo alternativo: usar 9Drive para subir y luego rclone-media para servir.

**Problema**: 9Drive sube archivos en CLARO (no cifrados). Para mantener privacidad:

- **Opción A**: 9Drive sube a un directorio temporal → script rclone mueve al crypt remote → borra el original.
- **Opción B**: Modificar 9Drive para llamar a rclone copy (con crypt) en vez de upload directo al Drive API.
- **Opción C**: No usar 9Drive para media cifrada; usar solo rclone CLI/agente para uploads.

**Recomendación**: Opción C para simplicidad. 9Drive para uploads no-cifrados (compartir con otros);
rclone directo para la biblioteca privada cifrada de Jellyfin.


---

## 11. Troubleshooting

### 11.1 Problemas comunes

| Problema | Causa | Solución |
|----------|-------|----------|
| Jellyfin no ve archivos | Mount no está activo o `--allow-other` faltante | `mountpoint /mnt/rclone/media` + verificar `user_allow_other` en fuse.conf |
| Buffering constante en 4K | VFS cache insuficiente o chunks muy pequeños | Subir `--vfs-cache-max-size`, `--vfs-read-ahead`, `--buffer-size` |
| Error "transport endpoint not connected" | Mount FUSE crasheó sin limpieza | `fusermount -uz /mnt/rclone/media && systemctl restart rclone-media@media` |
| 403 Rate Limit Exceeded | SA alcanzó cuota diaria | Rotation automática o manual: `rclone_media_rotate_sa()` |
| Mount lento al inicio | dir-cache vacío, primera carga | Normal: esperar `--dir-cache-time` se popule. Considerar `rclone lsd` previo |
| Jellyfin scan muy lento | Biblioteca enorme + sin cache de listados | Reducir frecuencia de scan, usar NFO files locales |
| "Permission denied" en container Docker | UID mismatch entre rclone mount y Jellyfin | Usar `--uid`/`--gid` en mount para matchear el usuario de Jellyfin |

### 11.2 Verificación del mount

```bash
# ¿Está montado?
mountpoint -q /mnt/rclone/media && echo "OK" || echo "NO MONTADO"

# ¿Responde? (debe listar archivos)
ls -la /mnt/rclone/media/ | head -5

# ¿Jellyfin puede leer? (como su usuario)
sudo -u jellyfin ls /mnt/rclone/media/Peliculas/ | head -3

# Estado del servicio systemd
systemctl status rclone-media@media.service

# Últimos errores en log
grep -i "error\|403\|429" /var/log/rclone/media-media.log | tail -20

# SA activa actual
cat /var/lib/rclone/sa-state.json | jq .active_sa
```

### 11.3 Recovery automático

La unidad systemd ya tiene `Restart=on-failure` con `RestartSec=10`, pero para
el caso específico de "transport endpoint not connected" (mount zombie):

```ini
# Agregar al [Service] del unit:
ExecStartPre=-/bin/fusermount -uz /mnt/rclone/%i
# El "-" significa "ignorar error si no está montado"
```


---

## 12. Seguridad específica de este módulo

### 12.1 Diferencias con Módulo 1 (backup)

| Aspecto | Módulo 1 (backup) | Este módulo (media) |
|---------|-------------------|---------------------|
| CAP_SYS_ADMIN | No (vacío) | Sí (FUSE requiere) |
| PrivateDevices | true | false (/dev/fuse) |
| DeviceAllow | — | /dev/fuse rw |
| Duración | Oneshot (minutos) | 24/7 persistente |
| MemoryMax | 1G | 4G (VFS cache en RAM) |
| Superficie de ataque | Baja (short-lived) | Media (long-running, FUSE) |

### 12.2 Protección de SA keys

```bash
/etc/rclone/sa-pool/
├── sa-051.json  (root:rclone, 0640) ← solo el grupo rclone puede leer
├── sa-052.json
│   ...
└── sa-100.json

# Directorio
chmod 0750 /etc/rclone/sa-pool/
chown root:rclone /etc/rclone/sa-pool/
```

Cada JSON contiene una **clave privada RSA** — si se filtra, esa SA puede acceder
al Shared Drive. Mitigación:
- Permisos 0640 (solo root y grupo rclone leen)
- Las SA tienen scope `drive.readonly` — incluso comprometidas, no pueden borrar/modificar
- Rotar keys periódicamente (gcloud iam service-accounts keys create nuevo + delete viejo)

### 12.3 Riesgo del VFS cache en disco

El VFS cache escribe archivos **descifrados** a disco (`/var/lib/rclone/vfs-cache/`).
Esto es un tradeoff de rendimiento vs seguridad:

- **Sin cache**: descifrado solo en RAM, más seguro, pero streaming imposible (no hay seek)
- **Con cache**: archivos en claro en disco, menos seguro, pero streaming funciona

**Mitigaciones**:
1. El directorio de cache tiene permisos `0750 rclone:rclone` — otros usuarios no leen
2. Usar **cifrado de disco completo** (LUKS) en la partición/disco donde vive el cache
3. El cache se evicta automáticamente (72h max age, 50G max size)
4. En caso de robo del NAS: el disco está cifrado con LUKS → el cache es ilegible

### 12.4 Impacto de compromiso

Si un atacante compromete el proceso rclone-media:
- **Puede leer**: archivos descifrados del mount y del VFS cache
- **NO puede**: escribir al Google Drive (mount es `--read-only`)
- **NO puede**: acceder a otros servicios del NAS (ProtectSystem=strict, namespaces)
- **NO puede**: escalar privilegios (NoNewPrivileges, CapabilityBoundingSet limitado)
- **NO puede**: ver procesos de otros usuarios (ProtectProc=invisible)


---

## 13. Requisitos de hardware

### 13.1 Mínimos

| Recurso | Mínimo | Recomendado | Para qué |
|---------|--------|-------------|----------|
| RAM | 4 GB libres | 8 GB+ | VFS cache en RAM + buffer de lectura |
| Disco (cache) | 50 GB SSD | 200 GB NVMe | VFS cache persistente (seek performance) |
| Red (WAN) | 50 Mbps | 200+ Mbps | Download desde Google Drive |
| Red (LAN) | 1 Gbps | 2.5 Gbps | Streaming a clientes Jellyfin |
| CPU | 2 cores | 4+ cores | Descifrado AES + transcoding (si aplica) |

### 13.2 Notas sobre transcoding

Si Jellyfin hace transcoding (h265→h264 para clientes incompatibles):
- El transcoding necesita leer el archivo → VFS cache ayuda enormemente
- Hardware transcoding (Intel QuickSync, NVIDIA NVENC) reduce carga de CPU
- Sin transcoding (direct play): CPU casi irrelevante, solo importa red

---

## 14. Diagrama de arquitectura completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                              NAS                                      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    systemd service (24/7)                       │  │
│  │                    rclone-media@media.service                   │  │
│  │                                                                │  │
│  │  ┌──────────┐    ┌──────────┐    ┌─────────────────────────┐  │  │
│  │  │ SA Pool  │───►│ rclone   │───►│ /mnt/rclone/media/      │  │  │
│  │  │ Manager  │    │ mount    │    │ (FUSE, descifrado)       │  │  │
│  │  │          │    │ +crypt   │    │                          │  │  │
│  │  │ 50 SA    │    │ +FUSE    │    │  Peliculas/              │  │  │
│  │  │ (read)   │    │          │    │  Series/                 │  │  │
│  │  └──────────┘    └────┬─────┘    │  Musica/                 │  │  │
│  │                       │           └────────────┬────────────┘  │  │
│  │                       │ VFS cache              │                │  │
│  │                       ▼                        │ reads          │  │
│  │  ┌─────────────────────────┐                   │                │  │
│  │  │ /var/lib/rclone/        │                   │                │  │
│  │  │ vfs-cache/media/        │                   │                │  │
│  │  │ (50-200 GB SSD)         │                   │                │  │
│  │  └─────────────────────────┘                   │                │  │
│  └────────────────────────────────────────────────┼────────────────┘  │
│                                                   │                    │
│  ┌────────────────────────────────────────────────▼────────────────┐  │
│  │                         Jellyfin                                 │  │
│  │                         (Docker o nativo)                        │  │
│  │                                                                  │  │
│  │  Lee /mnt/rclone/media/ como si fuera local                     │  │
│  │  Sirve streaming a clientes (web, apps, TV)                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │ HTTPS (Google Drive API)
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        Google Shared Drive                                 │
│                                                                           │
│  media/  (directorio raíz del crypt remote)                               │
│  ├── q5kj2m8v/8fn3x9pq2.bin    ← "Peliculas/Avatar (2009).mkv" cifrado  │
│  ├── m3nz7k/p2x8hd.bin         ← "Series/..." cifrado                    │
│  └── ...                                                                  │
│                                                                           │
│  Google ve: archivos binarios con nombres aleatorios                      │
│  Google NO puede: escanear, indexar, reclamar copyright, ni ver contenido │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Decisiones pendientes

- [ ] ¿Rclone oficial con rotation custom, o gclone con rotation nativa?
- [ ] ¿Tamaño exacto del VFS cache? (depende del disco disponible en el NAS)
- [ ] ¿Backup de la password de crypt? (offline en USB cifrado? en password manager?)
- [ ] ¿Cifrado LUKS del disco del NAS? (mitiga riesgo del VFS cache en claro)
- [ ] ¿Partition del pool: 50/50 o diferente ratio read/write?
- [ ] ¿Usar rclone rcd también para el media mount? (permite RC API stats sin journalctl)
- [ ] ¿Jellyfin en Docker o nativo? (afecta la integración con el mountpoint)

---

## 16. Referencias

- [Rclone FUSE mount docs](https://rclone.org/commands/rclone_mount/)
- [Rclone VFS cache](https://rclone.org/commands/rclone_mount/#vfs-file-caching)
- [Rclone crypt backend](https://rclone.org/crypt/)
- [Jellyfin remote storage guide](https://jellyfin.org/docs/general/server/storage)
- [gclone (SA rotation fork)](https://github.com/l3v11/gclone)
- [FUSE user_allow_other](https://man7.org/linux/man-pages/man8/mount.fuse3.8.html)
