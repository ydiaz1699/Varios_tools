Perfecto, queda claro. Son **3 piezas distintas** con propósitos diferentes pero que comparten infraestructura. Déjame organizar cómo encaja cada una:

---

## Vista general: Las 3 piezas

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NAS (Debian bare-metal)                       │
├──────────────────┬──────────────────────┬───────────────────────────┤
│  1. rclone-backup│  2. 9Drive+AutoRclone│  3. rclone-media          │
│  (agente NAS)    │  (app web Docker)    │  (mount FUSE + Jellyfin)  │
├──────────────────┼──────────────────────┼───────────────────────────┤
│ Backup offsite   │ Dashboard web para   │ Biblioteca de medios      │
│ seguro, cifrado  │ gestionar múltiples  │ montada desde Google      │
│ systemd hardened │ cuentas Drive,       │ Drive, con SA rotation    │
│ 1 SA/OAuth       │ uploads distribuidos │ para bypass de cuota      │
│ Corre como       │ routing inteligente  │ + capa crypt (Google no   │
│ plugin del agente│                      │ ve nada)                  │
│                  │ Corre en Docker      │ + Jellyfin lee el mount   │
│ → /etc/rclone/   │ (React+Express+MySQL)│                           │
│ → systemd timers │ → docker/9drive/     │ Corre como systemd unit   │
│                  │                      │ con VFS cache agresivo    │
└──────────────────┴──────────────────────┴───────────────────────────┘
```

---

## 1. Rclone-Backup (Agente NAS) — Tu guía de hardening

**Propósito**: Backup offsite seguro de datos del NAS a la nube.

**Ubicación**: Integrado al agente como plugin (como ya discutimos).

```
agent/
├── core/
│   ├── rclone_config.py       ← constantes compartidas
│   ├── rclone_manager.py      ← install, user, remotes, run_job
│   ├── rclone_install.py      ← systemd-creds, units hardened
│   └── rclone_rc.py           ← cliente API RC
├── tools/
│   ├── rclone_tools.py        ← tools operacionales
│   └── rclone_install_tools.py
├── plugins/
│   └── rclone_plugin.py
docs/
└── rclone-hardening.md
```

**Características**:
- 1 sola credencial (SA o OAuth)
- Config cifrada con systemd-creds
- Jobs `sync` oneshot vía timers
- Capa `crypt` (Google no ve nada)
- `CapabilityBoundingSet=` vacío (no FUSE)
- El agente lo controla todo

**Status**: Código base listo, necesita los ajustes que te listé. ✅

---

## 2. 9Drive + AutoRclone (App Web Docker)

**Propósito**: Dashboard web para gestionar múltiples cuentas Google Drive con routing inteligente de uploads y SA rotation para bypass de cuota.

**Ubicación**: Como servicio Docker gestionado por el agente (ficha en catálogo).

```
docker/
└── 9drive/
    ├── compose.yml            ← 9Drive (frontend + backend + MySQL)
    └── .env                   ← credenciales (Google OAuth, JWT, etc.)

agent/catalog/services/9drive/
└── ficha.md                   ← metadata para el catálogo del agente
```

**Características**:
- **9Drive** como web app (ya está dockerizada)
- Conecta N cuentas de Google Drive
- Routing: most-available / round-robin / priority
- API de uploads externa (para que otros servicios del NAS suban archivos)
- **AutoRclone**: las 100 SA se integran como "cuentas conectadas" en 9Drive
- El agente NAS solo gestiona el contenedor (start/stop/backup), no la lógica interna

**Preguntas de diseño**:
- ¿Quieres que 9Drive sea el **frontend de gestión** de tus Drives y que AutoRclone/rclone-media consuman las SA que 9Drive administra?
- ¿O prefieres que 9Drive y rclone-media sean independientes (cada uno con su propio pool de SA)?

---

## 3. Rclone-Media (Mount FUSE + Jellyfin + Cifrado)

**Propósito**: Montar Google Drive(s) como filesystem local para que Jellyfin lea la biblioteca de medios. Con SA rotation para bypass de cuota de lectura y capa `crypt` para que Google no vea los archivos.

**Ubicación**: Módulo propio del agente (separado de rclone-backup porque tienen perfiles de seguridad opuestos).

```
agent/
├── core/
│   ├── rclone_media.py        ← SA pool manager, rotation logic, mount lifecycle
│   └── rclone_sa_pool.py      ← gestión de 100 SA JSONs (crear, rotar, health check)
├── tools/
│   └── rclone_media_tools.py  ← tools del agente
├── plugins/
│   └── rclone_media_plugin.py ← o integrado en rclone_plugin.py

# Systemd units (generados por el agente):
/etc/systemd/system/rclone-media@.service   ← mount FUSE persistente
/etc/systemd/system/rclone-media-rotate.service  ← rotación de SA bajo demanda
```

**Flujo de datos**:

```
100 SA JSONs (/etc/rclone/sa-pool/*.json)
    ↓ rotación automática cuando una SA alcanza cuota
rclone mount (FUSE) con crypt
    ↓
/mnt/rclone/media/  ← Jellyfin lee de aquí (descifrado transparente)
    ↓
Google Drive (Shared Drive) ← archivos cifrados, Google no ve nada
```

**El tema del cifrado con Jellyfin** — Así funciona:

```
[Google Drive]                    [NAS local]
archivos cifrados (crypt)  ←→  rclone descifra en memoria  →  /mnt/rclone/media/
                                                                    ↓
                                                               Jellyfin ve
                                                               archivos normales
                                                               (.mkv, .mp4, etc.)
```

Rclone con `crypt` **descifra al vuelo** cuando lee. Jellyfin nunca sabe que hay cifrado — ve archivos normales en el mountpoint. Google solo ve basura binaria con nombres cifrados. **Lo mejor de ambos mundos.**

**Características técnicas**:
- Mount FUSE 24/7 con `--allow-other` (Jellyfin = otro usuario)
- `CAP_SYS_ADMIN` necesario (FUSE)
- VFS cache agresivo (`--vfs-cache-mode full`, `--vfs-cache-max-size 50G`)
- `--buffer-size 128M` para streaming fluido
- `--dir-cache-time 72h` (la biblioteca no cambia cada minuto)
- SA rotation: cuando detecta 403/429, cambia a la siguiente SA
- Capa `crypt` encima del remote real
- Automatización de creación de SA vía `gcloud` API (opcional)

---

## Cómo se conectan las 3 piezas

```
                    ┌───────────────────┐
                    │   Google Cloud     │
                    │   Project(s)      │
                    │   100 SA JSONs    │
                    └───────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
    ┌─────────▼──┐  ┌──────▼─────┐  ┌───▼────────────┐
    │ 1. Backup  │  │ 2. 9Drive  │  │ 3. Media Mount │
    │ (1 SA)     │  │ (N cuentas)│  │ (100 SA pool)  │
    │ cifrado    │  │ web UI     │  │ cifrado+FUSE   │
    │ offsite    │  │ uploads    │  │ Jellyfin       │
    └────────────┘  └────────────┘  └────────────────┘
         ↓               ↓                  ↓
    systemd timer   Docker container   systemd service
    (daily sync)    (9drive stack)     (24/7 mount)
```

---

## Plan de acción propuesto

| Orden | Pieza | Complejidad | Dependencias |
|-------|-------|-------------|--------------|
| **1ro** | Rclone-Backup (agente) | Media | Solo los ajustes al código que ya tienes |
| **2do** | Rclone-Media (mount + SA rotation + crypt) | Alta | Necesitas las 100 SA creadas primero |
| **3ro** | 9Drive (Docker) | Baja (deploy) | Solo Docker compose + configurar OAuth |

