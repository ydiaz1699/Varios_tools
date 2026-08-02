# Módulo 1: Rclone Backup Offsite con Hardening Systemd

> **Tipo**: Plugin del agente NAS (`nas-dotfiles`)
> **Destino de implementación**: `agent/core/rclone_*.py` + `agent/tools/rclone_*.py` + `agent/plugins/rclone_plugin.py`
> **Prioridad**: Alta (es el módulo más maduro, código base ya existe)

---

## 1. Propósito

Respaldar datos críticos del NAS a almacenamiento cloud (Google Drive, S3, B2, cualquier remote de Rclone) de forma:

- **Cifrada**: capa `crypt` de Rclone — el proveedor cloud no ve contenido ni nombres de archivo.
- **Aislada**: usuario de sistema dedicado, sin login, sin acceso a otros datos del NAS.
- **Hardened**: unidades systemd con sandboxing agresivo (namespaces, seccomp, capabilities vacías).
- **Automatizada**: systemd timers (no cron), con persistencia y jitter aleatorio.
- **Auditable**: logs centralizados en journald, puntuación de seguridad verificable.

---

## 2. Filosofía de seguridad (Defense in Depth)

```
Capa 1: IDENTIDAD
    └── Usuario de sistema "rclone" (nologin, UID < 1000, sin home real)

Capa 2: FILESYSTEM
    └── Permisos 0700/0600, separación binario/config/datos/logs

Capa 3: SECRETOS
    └── rclone.conf cifrado AES-256 + password maestra en systemd-creds (TPM/host key)

Capa 4: EJECUCIÓN
    └── Unidades systemd con ProtectSystem=strict, NoNewPrivileges,
        CapabilityBoundingSet vacío, SystemCallFilter, MemoryMax

Capa 5: AUTOMATIZACIÓN
    └── systemd timers con Persistent=true, RandomizedDelaySec, LoadCredential
```

---

## 3. Estructura de archivos en el NAS

```
/usr/bin/rclone                    → binario (root:root, 0755, inmutable con chattr +i)
/etc/rclone/                       → configuración (root:rclone, 0750)
/etc/rclone/rclone.conf            → config cifrada AES-256 (rclone:rclone, 0600)
/etc/rclone/secrets/               → scripts de password-command (root:rclone, 0750)
/etc/rclone/secrets/config-pass.cred → password cifrada con systemd-creds (root:rclone, 0640)
/etc/rclone/secrets/get-config-pass.sh → script que descifra la password (root:rclone, 0750)
/var/lib/rclone/                   → caches, vfs-cache, working dir (rclone:rclone, 0750)
/var/lib/rclone/versions/          → backup-dir con versionado por fecha
/var/log/rclone/                   → logs (rclone:rclone, 0750)
/etc/systemd/system/rclone-backup@.service → template unit hardened
/etc/systemd/system/rclone-backup@.timer   → timer diario
/etc/systemd/system/rclone-rcd.service     → daemon API RC
/etc/logrotate.d/rclone            → rotación de logs (14 días, comprimido)
```

---

## 4. Instalación paso a paso

### 4.1 Usuario de sistema dedicado

```bash
sudo groupadd --system rclone
sudo useradd --system \
  --gid rclone \
  --shell /usr/sbin/nologin \
  --home-dir /var/lib/rclone \
  --no-create-home \
  --comment "Rclone service account" \
  rclone
```

**Por qué**:
- `--shell /usr/sbin/nologin`: imposible hacer SSH o `su rclone`.
- `--home-dir /var/lib/rclone`: FHS correcto para servicios (no `/home`).
- UID < 1000: excluido de listados de login, no aparece en pantallas de login.

### 4.2 Estructura de directorios

```bash
sudo install -d -o root -g rclone -m 0750 /etc/rclone
sudo install -d -o root -g rclone -m 0750 /etc/rclone/secrets
sudo install -d -o rclone -g rclone -m 0750 /var/lib/rclone
sudo install -d -o rclone -g rclone -m 0750 /var/log/rclone
```

### 4.3 Binario oficial

```bash
curl -fsSL https://rclone.org/install.sh -o /tmp/rclone-install.sh
sudo bash /tmp/rclone-install.sh
sudo chown root:root /usr/bin/rclone
sudo chmod 0755 /usr/bin/rclone
sudo chattr +i /usr/bin/rclone  # inmutable: rclone no puede auto-modificarse
```

### 4.4 Configuración cifrada

```bash
# Paso MANUAL (requiere interacción):
sudo -u rclone rclone --config /etc/rclone/rclone.conf config
# → Crear remote(s) necesarios
# → "Set configuration password" → yes → ingresar password fuerte

sudo chown rclone:rclone /etc/rclone/rclone.conf
sudo chmod 0600 /etc/rclone/rclone.conf
```

### 4.5 Password maestra con systemd-creds

```bash
# Cifrar la password (ligada a ESTE host — inútil si se copia el disco)
echo -n 'TU_PASSWORD_MAESTRA' | \
  sudo systemd-creds encrypt --name=rclone-config-pass - \
  /etc/rclone/secrets/config-pass.cred

sudo chown root:rclone /etc/rclone/secrets/config-pass.cred
sudo chmod 0640 /etc/rclone/secrets/config-pass.cred
```

Script de desencriptado:

```bash
# /etc/rclone/secrets/get-config-pass.sh
#!/bin/bash
set -euo pipefail
systemd-creds decrypt /etc/rclone/secrets/config-pass.cred -
```

```bash
sudo chown root:rclone /etc/rclone/secrets/get-config-pass.sh
sudo chmod 0750 /etc/rclone/secrets/get-config-pass.sh
```

### 4.6 Remote con capa crypt

```bash
sudo -u rclone rclone --config /etc/rclone/rclone.conf config create remote-crypt crypt \
  remote=remote-real:bucket/backups \
  filename_encryption=standard \
  directory_name_encryption=true
# password y password2 se generan automáticamente con rclone config password
```

---

## 5. Unidad systemd de backup (hardened)

### 5.1 Template service: `/etc/systemd/system/rclone-backup@.service`

```ini
[Unit]
Description=Rclone backup job: %i
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=rclone
Group=rclone

Environment=RCLONE_CONFIG=/etc/rclone/rclone.conf
Environment=RCLONE_PASSWORD_COMMAND=/etc/rclone/secrets/get-config-pass.sh

ExecStart=/usr/bin/rclone sync /srv/data/%i remote-crypt:%i \
    --backup-dir /var/lib/rclone/versions/%i/%Y-%m-%d \
    --log-level INFO \
    --log-file /var/log/rclone/backup-%i.log \
    --transfers 8 --checkers 16

# ════════════════════════════════════════════════════════════
# SANDBOXING (sin FUSE — máximo aislamiento posible)
# ════════════════════════════════════════════════════════════

NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadOnlyPaths=/srv/data/%i
ReadWritePaths=/var/lib/rclone/versions/%i /var/log/rclone
PrivateTmp=true
PrivateDevices=true
PrivateNetwork=false
ProtectClock=true
ProtectHostname=true
ProtectKernelLogs=true
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
ProtectProc=invisible
ProcSubset=pid

# Capabilities: NINGUNA (no necesita FUSE, no necesita puertos privilegiados)
CapabilityBoundingSet=
AmbientCapabilities=

# Namespaces y restricciones
RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true
MemoryDenyWriteExecute=true
RemoveIPC=true

# Syscalls: solo lo que un proceso de red normal necesita, sin mount/privileged/debug
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @debug @mount
SystemCallErrorNumber=EPERM
SystemCallArchitectures=native

# Red: solo lo necesario para HTTPS a la nube
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

# Límites de recursos (evitar agotamiento)
LimitNOFILE=65536
TasksMax=128
MemoryMax=1G
CPUQuota=100%
IOWeight=50

[Install]
WantedBy=multi-user.target
```

### 5.2 Timer diario: `/etc/systemd/system/rclone-backup@.timer`

```ini
[Unit]
Description=Daily timer for rclone backup job: %i

[Timer]
OnCalendar=*-*-* 03:30:00
RandomizedDelaySec=600
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
```

### 5.3 Activar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rclone-backup@documentos.timer
```

---

## 6. Daemon API RC (rclone rcd)

Para que el agente NAS consulte estado real de transferencias sin parsear journalctl:

### 6.1 Service: `/etc/systemd/system/rclone-rcd.service`

```ini
[Unit]
Description=Rclone RC daemon (localhost-only control API)
After=network.target

[Service]
Type=simple
User=rclone
Group=rclone
EnvironmentFile=/etc/rclone/secrets/rcd.env
Environment=RCLONE_CONFIG=/etc/rclone/rclone.conf
Environment=RCLONE_PASSWORD_COMMAND=/etc/rclone/secrets/get-config-pass.sh

ExecStart=/usr/bin/rclone rcd \
    --rc-addr=127.0.0.1:5572 \
    --rc-user=${RC_USER} \
    --rc-pass=${RC_PASS} \
    --rc-no-auth=false

# Sandboxing (sin FUSE)
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/rclone
PrivateTmp=true
PrivateDevices=true
ProtectClock=true
ProtectHostname=true
ProtectControlGroups=true
ProtectProc=invisible
ProcSubset=pid
CapabilityBoundingSet=
AmbientCapabilities=
RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true
MemoryDenyWriteExecute=true
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 6.2 Credenciales del daemon RC

```bash
# /etc/rclone/secrets/rcd.env (root:rclone, 0640)
RC_USER=agent
RC_PASS=una_password_larga_de_al_menos_12_chars
```

### 6.3 Endpoints útiles para el agente

| Endpoint | Método | Uso |
|----------|--------|-----|
| `POST /core/stats` | — | Velocidad, bytes transferidos, errores, transferencias activas |
| `POST /job/list` | — | IDs de jobs async en curso |
| `POST /job/status` | `{"jobid": N}` | Estado de un job específico |
| `POST /sync/sync` | `{"srcFs": "...", "dstFs": "...", "_async": true}` | Disparar sync vía API (no systemctl) |
| `POST /config/listremotes` | — | Nombres de remotes (sin credenciales) |
| `POST /rc/noop` | — | Health check (¿el daemon responde?) |

---

## 7. Rotación de logs

```bash
# /etc/logrotate.d/rclone
/var/log/rclone/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 rclone rclone
    su rclone rclone
}
```

---

## 8. Integración con el agente NAS

### 8.1 Archivos a crear en `nas-dotfiles`

```
agent/core/rclone_config.py       ← constantes (RCLONE_USER, paths, regex de validación)
agent/core/rclone_manager.py      ← RcloneManager (check, install, setup_user, list_remotes, status, run_job)
agent/core/rclone_install.py      ← RcloneInstaller (encrypt_password, install_backup_unit, install_rc_daemon)
agent/core/rclone_rc.py           ← cliente HTTP de la API RC (core_stats, job_status, start_sync)
agent/tools/rclone_tools.py       ← @tool wrappers operacionales
agent/tools/rclone_install_tools.py ← @tool wrappers de instalación
agent/plugins/rclone_plugin.py    ← registro en el sistema de plugins
```

### 8.2 Ajustes necesarios al código base existente

| Problema | Solución |
|----------|----------|
| `rclone_install_tools.py` mezcla tools de instalación con tools de estado | Mover `rclone_status_rc` y `rclone_job_status` a `rclone_tools.py` |
| `rclone_install.py` importa constantes de `rclone_manager.py` (dep. circular) | Extraer constantes a `rclone_config.py` |
| `encrypt_config_password` no pasa `env=` a `safe_run` | Extender `safe_run` con param `env=` o usar archivo temporal 0600 |
| `rc_available()` se llama dentro de `rc_call()` (doble HTTP) | Mover a check independiente; en `rc_call()` intentar directamente y manejar error |
| Tools destructivas no están en `_DESTRUCTIVE_TOOLS` frozenset | Agregar: `rclone_install_binary`, `rclone_setup_user`, `rclone_encrypt_config_password`, `rclone_install_backup_unit`, `rclone_install_rc_daemon`, `rclone_run_backup_job` |
| `RclonePlugin` sin dependencias declaradas | Agregar `dependencies=["backup"]` si se integra con offsite post-backup |

### 8.3 Flujo de instalación completo (tools del agente)

```python
# Orden que el agente ejecutaría:
rclone_install_binary()                    # 1. Descarga binario, bloquea permisos
rclone_setup_user()                        # 2. Crea usuario/grupo/directorios
# ← PASO MANUAL: sudo -u rclone rclone config (crear remote + activar cifrado)
rclone_encrypt_config_password("...")      # 3. Cifra la password con systemd-creds
rclone_install_backup_unit(                # 4. Genera unit + timer hardened
    job_name="documentos",
    source_path="/srv/data/documentos",
    remote_target="remote-crypt:documentos"
)
rclone_install_rc_daemon(                  # 5. Instala daemon API RC
    rc_user="agent",
    rc_pass="password_larga_12+"
)
# A partir de aquí, consultas vía API RC:
rclone_status_rc()                         # Stats globales
rclone_job_status(job_id=42)               # Estado de un job específico
rclone_run_backup_job("documentos")        # Disparar backup manualmente
```

### 8.4 Integración con BackupManager existente

El `BackupPlugin` del agente ya tiene un schedule `_daily_backup()` que respalda servicios Docker localmente (tar.gz). La integración natural es:

```python
# En rclone_plugin.py:
self.register_event(EventHandler(
    event_type="agent.command.backup.completed",
    handler=self._push_offsite,
    description="Sync backup local a cloud después de completar"
))

async def _push_offsite(self, event):
    """Después de que BackupPlugin crea el tar.gz, lo sincroniza offsite."""
    service = event.data.get("service_name")
    RcloneManager.run_backup_job(f"docker-backups-{service}")
```

---

## 9. Verificación y auditoría

### 9.1 Checklist post-instalación

| Control | Comando |
|---------|---------|
| Rclone no corre como root | `systemctl show rclone-backup@*.service -p User` |
| Config cifrada | `head -c 20 /etc/rclone/rclone.conf` (debe ser basura binaria) |
| Permisos config | `stat -c '%a %U:%G' /etc/rclone/rclone.conf` → `600 rclone:rclone` |
| Binario no escribible | `stat -c '%a %U:%G' /usr/bin/rclone` → `755 root:root` |
| Binario inmutable | `lsattr /usr/bin/rclone` → debe mostrar `i` |
| Sandboxing activo | `systemd-analyze security rclone-backup@documentos.service` |
| Capabilities vacías | `systemctl show rclone-backup@*.service -p CapabilityBoundingSet` |
| Sin secretos en logs | `grep -iE 'token\|password\|secret' /var/log/rclone/*.log` (vacío) |
| Timers activos | `systemctl list-timers 'rclone-*'` |
| RC daemon solo localhost | `ss -tlnp \| grep 5572` → debe mostrar 127.0.0.1 |

### 9.2 Puntuación de seguridad

```bash
systemd-analyze security rclone-backup@documentos.service
# Objetivo: score <= 2.0 (de 10). Con todas las directivas debería dar ~1.5
```

### 9.3 Verificación manual de aislamiento

```bash
sudo -u rclone ls /home        # → Permission denied
sudo -u rclone ls /root        # → Permission denied
sudo -u rclone touch /etc/x    # → Permission denied
sudo -u rclone cat /etc/shadow # → Permission denied
```

---

## 10. Notas de seguridad avanzadas

### 10.1 Nunca usar variables de entorno para secretos

```ini
# ❌ MALO: el secreto aparece en /proc/<pid>/environ y en journalctl
Environment=RCLONE_CONFIG_PASS=mi_password

# ✅ BUENO: el secreto vive en systemd-creds, se descifra al vuelo
Environment=RCLONE_PASSWORD_COMMAND=/etc/rclone/secrets/get-config-pass.sh
```

### 10.2 LoadCredential para secretos adicionales

Si un job necesita un token extra (ej: webhook de notificación):

```ini
[Service]
LoadCredential=notify-token:/etc/rclone/secrets/notify-token.cred
```

El secreto queda en `$CREDENTIALS_DIRECTORY/notify-token` (tmpfs privado, destruido al terminar).

### 10.3 Errores comunes a evitar

- `ProcSubset=ptrace` → **NO es válido**. Solo `all` o `pid`. Usar `ProcSubset=pid`.
- Capabilities "por si acaso" (CAP_DAC_OVERRIDE, CAP_FOWNER) → para sync NO se necesitan si el usuario es dueño de los directorios.
- `ProtectSystem=full` → inferior a `strict`. Usar siempre `strict`.
- `-vv` (debug) en producción → vuelca headers de auth. Solo `--log-level INFO`.

### 10.4 Diferencia con el módulo 3 (rclone-media)

| Aspecto | Este módulo (backup) | Módulo 3 (media) |
|---------|---------------------|------------------|
| Tipo de operación | `sync` (oneshot) | `mount` (persistente 24/7) |
| FUSE | No | Sí |
| CAP_SYS_ADMIN | No (vacío) | Sí (requerido para FUSE) |
| SA rotation | No (1 sola SA) | Sí (100 SA pool) |
| VFS cache | No | Sí (50 GB+) |
| Consumo de recursos | Bajo, puntual | Alto, constante |

---

## 11. Diagrama de flujo completo

```
┌─────────────────────────────────────────────────────────────┐
│                   systemd-creds (TPM/host key)              │
│                   cifra la password maestra                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  /etc/rclone/rclone.conf (AES-256)                          │
│  0600 rclone:rclone                                         │
└───────────────────────────┬─────────────────────────────────┘
                            │ leído solo por
┌───────────────────────────▼─────────────────────────────────┐
│  usuario de sistema "rclone"                                 │
│  nologin, sin home real, UID < 1000                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ ejecutado dentro de
┌───────────────────────────▼─────────────────────────────────┐
│  systemd unit con sandboxing:                                │
│  • ProtectSystem=strict (todo readonly excepto ReadWritePaths)│
│  • NoNewPrivileges=true                                      │
│  • CapabilityBoundingSet= (vacío, sin capabilities)          │
│  • SystemCallFilter=@system-service ~@privileged             │
│  • MemoryMax=1G, CPUQuota=100%, IOWeight=50                  │
│  • RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6          │
└───────────────────────────┬─────────────────────────────────┘
                            │ disparado por
┌───────────────────────────▼─────────────────────────────────┐
│  systemd timer (no cron)                                     │
│  • Persistent=true (ejecuta si el NAS estaba apagado)        │
│  • RandomizedDelaySec=600 (jitter, no golpear cloud a la vez)│
│  • AccuracySec=1min                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ datos van a
┌───────────────────────────▼─────────────────────────────────┐
│  Cloud (Google Drive, S3, B2, etc.)                          │
│  • Datos cifrados con capa crypt (nombres + contenido)       │
│  • El proveedor NO puede leer nada                           │
│  • Versionado en --backup-dir con fecha                      │
└─────────────────────────────────────────────────────────────┘
```
