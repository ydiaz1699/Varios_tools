# Código de referencia: Módulo Rclone para el Agente NAS

> **Estado**: Borrador funcional (pre-integración). Necesita los ajustes documentados en `docs/01-rclone-backup-hardening.md` sección 8.2.
> **Destino final**: `agent/` en [ydiaz1699/nas-dotfiles](https://github.com/ydiaz1699/nas-dotfiles)

## Archivos

| Archivo | Capa | Descripción |
|---------|------|-------------|
| `rclone_manager.py` | Core | Gestión operacional: install, user setup, list remotes, run jobs, mount status |
| `rclone_install.py` | Core | Instalación de hardening: systemd-creds, backup units, RC daemon |
| `rclone_rc.py` | Core | Cliente HTTP de la API RC de Rclone (stats, jobs, sync) |
| `rclone_tools.py` | Tools | `@tool` wrappers operacionales (delegan a RcloneManager) |
| `rclone_install_tools.py` | Tools | `@tool` wrappers de instalación + estado RC |
| `rclone_plugin.py` | Plugin | Registro de todas las tools en el sistema de plugins del agente |

## Ajustes pendientes antes de integrar

1. Extraer constantes a `rclone_config.py` (evitar dep circular manager↔install)
2. Mover `rclone_status_rc` y `rclone_job_status` de install_tools a tools
3. Fix: `encrypt_config_password` — pasar env var a safe_run o usar tempfile
4. Fix: `rc_available()` dentro de `rc_call()` — separar checks
5. Agregar tools destructivas al frozenset `_DESTRUCTIVE_TOOLS` en `_shell.py`
6. Declarar `dependencies=["backup"]` en RclonePlugin si se integra post-backup

## Patrón que siguen

```
agent/core/rclone_manager.py    → métodos estáticos, retornan ToolResult
agent/tools/rclone_tools.py     → @tool decorados, str(Manager.method())
agent/plugins/rclone_plugin.py  → setup() registra tools
```

Idéntico a: `ServiceManager` → `docker_tools.py` → `DockerPlugin`
