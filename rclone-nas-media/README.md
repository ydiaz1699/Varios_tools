# Rclone NAS Media — Arquitectura Completa

> **Estado**: Documentación de diseño (pre-implementación).
> **Repositorio de destino final**: [ydiaz1699/nas-dotfiles](https://github.com/ydiaz1699/nas-dotfiles) (módulos 1 y 3 como plugins del agente) + Docker compose para el módulo 2.
> **Fecha**: 2026-08-01

---

## Resumen Ejecutivo

Este proyecto define **3 módulos complementarios** para gestionar almacenamiento en la nube desde un NAS Debian bare-metal, centrados en Rclone y Google Drive:

| # | Módulo | Propósito | Ejecución |
|---|--------|-----------|-----------|
| 1 | **rclone-backup** | Backup offsite seguro, cifrado, con systemd hardening | Plugin del agente NAS (systemd timers) |
| 2 | **9Drive + AutoRclone** | Dashboard web multi-Drive con SA rotation para bypass de cuota de upload (75 TB/día) | Docker container (React + Express + MySQL) |
| 3 | **rclone-media** | Biblioteca de medios cifrada en Google Drive, montada vía FUSE con SA rotation, servida por Jellyfin | systemd service 24/7 (plugin del agente NAS) |

---

## Contexto del Problema

### Limitaciones de Google Drive

- **750 GB/día por cuenta** de upload (API write).
- **10 TB/día por cuenta** de download (API read) — menos documentado, pero existe.
- Los límites son **por Service Account (SA)**, no por proyecto GCP.
- Solución: rotar entre N Service Accounts para multiplicar la cuota efectiva.

### Requisitos del usuario

1. **Backup offsite**: datos críticos del NAS cifrados en la nube, inaccesibles para el proveedor.
2. **Streaming de medios**: biblioteca grande (multi-TB) en Google Drive, accesible por Jellyfin como si fuera local.
3. **Privacidad**: Google NO debe poder ver el contenido de los archivos ni los nombres.
4. **Gestión centralizada**: todo controlable desde el agente NAS (CLI/LLM).

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NAS (Debian bare-metal)                         │
│                                                                         │
│  ┌─────────────────┐  ┌──────────────────────┐  ┌───────────────────┐  │
│  │ 1. rclone-backup│  │ 2. 9Drive+AutoRclone │  │ 3. rclone-media   │  │
│  │                 │  │                      │  │                   │  │
│  │ • 1 SA/OAuth    │  │ • N cuentas Drive    │  │ • 100 SA pool     │  │
│  │ • sync oneshot  │  │ • Web UI (Docker)    │  │ • mount FUSE 24/7 │  │
│  │ • crypt layer   │  │ • Upload routing     │  │ • crypt layer     │  │
│  │ • systemd timer │  │ • SA rotation        │  │ • VFS cache       │  │
│  │ • hardened unit │  │ • 75 TB/día upload   │  │ • Jellyfin ←read  │  │
│  │                 │  │                      │  │                   │  │
│  │ Destino:        │  │ Destino:             │  │ Origen:           │  │
│  │ cualquier cloud │  │ Google Team Drives   │  │ Google Team Drive │  │
│  └────────┬────────┘  └──────────┬───────────┘  └─────────┬─────────┘  │
│           │                      │                         │            │
│           ▼                      ▼                         ▼            │
│  /etc/rclone/rclone.conf   Docker stack            /mnt/rclone/media/   │
│  (cifrado, 0600)           (9drive:latest)         (FUSE, --allow-other)│
│                                                         ↓               │
│                                                    Jellyfin container    │
│                                                    lee archivos en claro │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │       Google Cloud Platform    │
                    │                               │
                    │  Proyecto GCP                  │
                    │  ├── 100 Service Accounts      │
                    │  ├── Google Drive API enabled  │
                    │  └── OAuth consent screen      │
                    │                               │
                    │  Shared Drive(s)              │
                    │  ├── media/ (cifrado)         │
                    │  ├── backups/ (cifrado)       │
                    │  └── uploads/ (9Drive)        │
                    └───────────────────────────────┘
```

---

## Cómo se conectan las 3 piezas

### Flujo de datos

```
                         UPLOAD                              DOWNLOAD/STREAMING
                    ┌──────────────┐                    ┌──────────────────────┐
                    │              │                    │                      │
NAS local data ────►│ Módulo 1     │────► Cloud         Cloud ────► Módulo 3  │────► Jellyfin
(/srv/data/)        │ (backup)     │     (cifrado)     (cifrado)  (mount FUSE)│     (streaming)
                    │              │                    │          descifra    │
                    └──────────────┘                    │          al vuelo    │
                                                       └──────────────────────┘
Large uploads ─────► Módulo 2 (9Drive) ────► Cloud (múltiples Drives)
(via web UI/API)     routing inteligente
```

### Recursos compartidos

| Recurso | Módulo 1 | Módulo 2 | Módulo 3 |
|---------|----------|----------|----------|
| SA pool (100 JSONs) | 1 sola SA | Integrado en 9Drive | Pool completo, rotación |
| systemd-creds | Sí (password maestra) | No (Docker) | Sí (password maestra) |
| Agente NAS (plugin) | Sí | Solo gestión Docker | Sí |
| API RC (rclone rcd) | Sí | No | Sí (separado del módulo 1) |
| Capa crypt | Sí | Opcional | Sí (obligatorio) |
| FUSE mount | No | No | Sí (24/7) |

### Independencia

Cada módulo puede implementarse **por separado** y en **cualquier orden**:

- **Módulo 1** no necesita SA rotation ni FUSE — es el más simple.
- **Módulo 2** es una app Docker autocontenida — solo necesita OAuth config de Google.
- **Módulo 3** necesita el pool de SA creado (ver `docs/04-sa-pool-management.md`).

---

## Integración con el Agente NAS (nas-dotfiles)

Los módulos 1 y 3 se integran como **plugins del agente** siguiendo la arquitectura existente:

```
agent/
├── core/
│   ├── rclone_config.py          ← constantes compartidas (rutas, usuario, grupo)
│   ├── rclone_manager.py         ← gestión base (install binary, setup user, list remotes)
│   ├── rclone_install.py         ← hardening: systemd-creds, units, logrotate
│   ├── rclone_rc.py              ← cliente HTTP de la API RC (rclone rcd)
│   ├── rclone_media.py           ← [Módulo 3] mount lifecycle, VFS cache, Jellyfin integration
│   └── rclone_sa_pool.py         ← [Módulo 3] gestión del pool de 100 SA, rotación
├── tools/
│   ├── rclone_tools.py           ← tools operacionales (status, run_job, list_remotes, RC stats)
│   ├── rclone_install_tools.py   ← tools de instalación (una vez)
│   └── rclone_media_tools.py     ← [Módulo 3] tools de media mount
├── plugins/
│   └── rclone_plugin.py          ← registra todas las tools de rclone
│
docker/
└── 9drive/                        ← [Módulo 2] compose.yml + .env
    ├── compose.yml
    └── .env.example

agent/catalog/services/
└── 9drive/
    └── ficha.md                   ← metadata para el catálogo del agente
```

### Patrones que sigue

- **Manager estático** → `@tool` wrappers → **Plugin** (auto-discovered por `PluginLoader`)
- `safe_run()` para ejecución segura (shell=False)
- `readonly_guard()` para bloquear tools destructivas en modo lectura
- `ToolResult` como tipo de retorno estandarizado
- Bus de eventos para integrar con otros plugins (ej: "después de backup local → sync offsite")

---

## Documentación detallada

| Documento | Contenido |
|-----------|-----------|
| [`docs/01-rclone-backup-hardening.md`](docs/01-rclone-backup-hardening.md) | Módulo 1: Backup offsite con hardening systemd completo |
| [`docs/02-9drive-autorclone.md`](docs/02-9drive-autorclone.md) | Módulo 2: 9Drive + AutoRclone (web app, SA rotation, Docker) |
| [`docs/03-rclone-media-jellyfin.md`](docs/03-rclone-media-jellyfin.md) | Módulo 3: Mount FUSE cifrado + SA rotation + Jellyfin |
| [`docs/04-sa-pool-management.md`](docs/04-sa-pool-management.md) | Guía de creación y gestión de 100 Service Accounts (gcloud) |
| [`reference/code-base/`](reference/code-base/) | Código propuesto actual (Python) como referencia de implementación |

---

## Decisiones de diseño clave

### ¿Por qué no un solo módulo?

Los perfiles de seguridad son **opuestos**:

| Aspecto | Módulo 1 (backup) | Módulo 3 (media) |
|---------|-------------------|------------------|
| Credenciales | 1 sola | 100 SA rotando |
| FUSE | No | Sí (CAP_SYS_ADMIN) |
| Duración | Oneshot (minutos) | 24/7 persistente |
| Capabilities | Ninguna (vacío) | CAP_SYS_ADMIN |
| CPU/RAM | Bajo | Alto (VFS cache, buffer) |

Mezclarlos en una sola unidad systemd violaría el principio de menor privilegio.

### ¿Por qué crypt si Jellyfin necesita leer?

Rclone con `crypt` **descifra al vuelo en memoria** durante el mount FUSE:

```
Google Drive: archivos cifrados (nombres y contenido)
     ↓ rclone mount con crypt remote
Descifrado en RAM (nunca toca disco en claro)
     ↓
/mnt/rclone/media/ → Jellyfin ve .mkv, .mp4 normales
```

Google solo ve basura binaria. Jellyfin nunca sabe que hay cifrado.

### ¿Por qué SA rotation en vez de una cuenta premium?

- Google Workspace Enterprise tiene cuotas más altas pero cuesta ~$20/user/mes.
- 100 SA en un proyecto GCP gratuito dan 75 TB/día de upload y ~1 PB/día de read.
- Para un homelab con TB de medios, es la solución costo-efectiva.
- **Riesgo**: viola TOS de Google (abuso de cuota). Mitigación: Shared Drives con las SA como miembros — técnicamente legítimo si las SA tienen acceso real al Drive.

### ¿Por qué 9Drive además de rclone directo?

- 9Drive aporta **UI web** para gestionar uploads y ver cuota — útil para subir contenido nuevo a la biblioteca sin tocar CLI.
- El routing inteligente (most-available, round-robin) complementa la SA rotation de rclone.
- Puede servir como **API de upload** para otros servicios del NAS (ej: scripts de descarga que suben directamente al Drive con cuota disponible).

---

## Prerrequisitos generales

- **NAS**: Debian 12+ (systemd >= 252 para systemd-creds)
- **Google Cloud**: proyecto con Drive API habilitada, hasta 100 SA creadas
- **Shared Drive**: al menos 1 Team Drive donde las SA tengan acceso
- **Docker**: para el módulo 2 (9Drive)
- **Agente NAS**: [nas-dotfiles](https://github.com/ydiaz1699/nas-dotfiles) instalado
- **Python 3.11+**: para los módulos del agente
- **Rclone**: v1.65+ (soporte completo de RC API y crypt improvements)

---

## Estado de implementación

| Módulo | Estado | Próximo paso |
|--------|--------|--------------|
| 1. rclone-backup | Código base escrito, necesita ajustes (ver doc) | Aplicar fixes → PR a nas-dotfiles |
| 2. 9Drive + AutoRclone | Diseño documentado, app externa lista | Deploy Docker + configurar OAuth |
| 3. rclone-media | Diseño documentado, código por escribir | Crear SA pool → implementar módulo |

---

## Referencias externas

- [Rclone docs](https://rclone.org/docs/)
- [Rclone RC API](https://rclone.org/rc/)
- [Rclone Crypt](https://rclone.org/crypt/)
- [rclone-mcp (MCP server)](https://github.com/rclone-ui/rclone-mcp) — 98 endpoints como tools MCP
- [9Drive (web app)](https://github.com/ripperdrive/9drive) — storage gateway multi-Drive
- [AutoRclone](https://github.com/byjlwl/AutoRclone-1) — SA rotation para rclone
- [gclone](https://github.com/l3v11/gclone) — fork de rclone con SA rotation nativa
- [SA creation guide](https://github.com/88lex/sa-guide) — guía de creación de Service Accounts
- [Google Drive MCP (oficial)](https://developers.google.com/workspace/drive/api/guides/configure-mcp-server) — MCP server oficial de Google
