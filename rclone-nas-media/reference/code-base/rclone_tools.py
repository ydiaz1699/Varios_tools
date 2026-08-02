"""
agent/tools/rclone_tools.py — Herramientas de Rclone para el agente.

Thin wrappers que delegan a agent.core.rclone_manager.RcloneManager,
igual que docker_tools.py delega a ServiceManager.
"""

from strands.tools import tool


def _mgr():
    from agent.core.rclone_manager import RcloneManager
    return RcloneManager


@tool
def rclone_check_installed() -> str:
    """Verifica si Rclone está instalado y si sigue el hardening recomendado
    (usuario dedicado, binario bloqueado, config cifrada).

    No requiere argumentos. Es el primer paso antes de instalar o gestionar remotes.
    """
    return str(_mgr().check_installed())


@tool
def rclone_install_binary() -> str:
    """Instala el binario oficial de Rclone (script oficial rclone.org/install.sh)
    y lo deja bloqueado como root:root 0755 (no escribible por el usuario de servicio).

    ACCIÓN QUE MODIFICA EL SISTEMA. Segura de ejecutar (no destructiva, no borra datos),
    pero requiere que NAS_AGENT_READONLY esté desactivado.
    """
    return str(_mgr().install_binary())


@tool
def rclone_setup_user() -> str:
    """Crea el usuario de sistema dedicado 'rclone' (sin login, sin home real)
    y la estructura de directorios con permisos mínimos:
    /etc/rclone, /etc/rclone/secrets, /var/lib/rclone, /var/log/rclone, /mnt/rclone.

    Después de esto, el usuario DEBE ejecutar manualmente:
        sudo -u rclone rclone --config /etc/rclone/rclone.conf config
    para crear el remote y activar el cifrado del archivo de configuración.
    """
    return str(_mgr().setup_user())


@tool
def rclone_list_remotes() -> str:
    """Lista los nombres de los remotes configurados en rclone.conf (sin credenciales).

    Si el config está cifrado con password (recomendado), puede fallar si no hay
    RCLONE_PASSWORD_COMMAND configurado — en ese caso es esperado.
    """
    return str(_mgr().list_remotes())


@tool
def rclone_status() -> str:
    """Muestra el estado de todas las unidades systemd relacionadas con Rclone
    (servicios de mount FUSE, servicios de backup, timers).

    No requiere argumentos.
    """
    return str(_mgr().status())


@tool
def rclone_run_backup_job(job_name: str) -> str:
    """Dispara manualmente un job de backup de Rclone ya instalado como
    unidad systemd (rclone-backup@<job_name>.service).

    Args:
        job_name: Nombre del job/carpeta a respaldar, ej. "documentos".
    """
    return str(_mgr().run_backup_job(job_name))


@tool
def rclone_mount_status(remote_name: str) -> str:
    """Verifica si un montaje FUSE de Rclone está activo (unidad systemd)
    y si el punto de montaje está realmente montado.

    Args:
        remote_name: Nombre del remote/montaje, ej. "miremoto".
    """
    return str(_mgr().mount_status(remote_name))
