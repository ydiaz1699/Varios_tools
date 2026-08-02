"""
agent/tools/rclone_install_tools.py — Instalación completa (guía hardening)
y consultas de estado vía la API RC de Rclone.
"""

from strands.tools import tool


def _installer():
    from agent.core.rclone_install import RcloneInstaller
    return RcloneInstaller


@tool
def rclone_encrypt_config_password(password: str) -> str:
    """Cifra la password maestra de rclone.conf usando systemd-creds, ligándola
    a este host (inútil si el disco se copia a otra máquina).

    Requiere systemd >= 252 (Debian 12+).

    Args:
        password: La password maestra que protege rclone.conf. Mínimo 8 caracteres.
    """
    return str(_installer().encrypt_config_password(password))


@tool
def rclone_install_backup_unit(job_name: str, source_path: str, remote_target: str) -> str:
    """Instala una unidad systemd completa de backup (rclone-backup@<job>.service +
    .timer diario) con sandboxing recomendado. Activa el timer automáticamente.

    Args:
        job_name: nombre corto para el job, ej. "documentos".
        source_path: ruta local a respaldar, ej. "/srv/data/documentos".
        remote_target: remote:ruta destino, ej. "remote-crypt:documentos".
    """
    return str(_installer().install_backup_unit(job_name, source_path, remote_target))


@tool
def rclone_install_rc_daemon(rc_user: str, rc_pass: str, rc_addr: str = "127.0.0.1:5572") -> str:
    """Instala el daemon de control remoto de Rclone (rclone rcd) como servicio
    systemd hardened, bindeado SOLO a localhost y con autenticación obligatoria.

    Args:
        rc_user: usuario para autenticar contra la API RC.
        rc_pass: password para la API RC. Mínimo 12 caracteres.
        rc_addr: dirección de bind (default 127.0.0.1:5572).
    """
    return str(_installer().install_rc_daemon(rc_user, rc_pass, rc_addr))


@tool
def rclone_status_rc() -> str:
    """Consulta estadísticas GLOBALES de transferencias en curso vía la API RC
    de Rclone (velocidad, bytes transferidos, errores).

    Requiere que rclone-rcd.service esté instalado y activo.
    """
    try:
        from agent.core.rclone_rc import core_stats, rc_available
    except ImportError:
        return "ERROR: falta el módulo agent.core.rclone_rc"

    if not rc_available():
        return (
            "❌ El daemon RC no responde. ¿Está instalado y activo?\n"
            "Instalar con: rclone_install_rc_daemon(rc_user=..., rc_pass=...)\n"
            "Verificar: systemctl status rclone-rcd"
        )

    try:
        stats = core_stats()
    except Exception as e:
        return f"ERROR consultando stats: {e}"

    speed = stats.get("speed", 0)
    bytes_done = stats.get("bytes", 0)
    errors = stats.get("errors", 0)
    transferring = stats.get("transferring", [])

    return (
        f"=== ESTADO RCLONE (vía API RC) ===\n\n"
        f"Velocidad actual: {speed/1024/1024:.2f} MB/s\n"
        f"Bytes transferidos (sesión): {bytes_done/1024/1024:.1f} MB\n"
        f"Errores: {errors}\n"
        f"Transferencias activas: {len(transferring)}\n"
        + ("\n".join(f"  • {t.get('name', '?')}" for t in transferring[:10]) if transferring else "  (ninguna)")
    )


@tool
def rclone_job_status(job_id: int) -> str:
    """Consulta el estado de un job asíncrono específico de Rclone.

    Args:
        job_id: ID numérico del job, devuelto al disparar una operación async.
    """
    try:
        from agent.core.rclone_rc import job_status
    except ImportError:
        return "ERROR: falta el módulo agent.core.rclone_rc"

    try:
        status = job_status(job_id)
    except Exception as e:
        return f"ERROR: {e}"

    finished = status.get("finished", False)
    success = status.get("success", None)
    error = status.get("error", "")
    duration = status.get("duration", 0)

    if not finished:
        return f"Job {job_id}: en curso ({duration:.1f}s transcurridos)"

    result = "✅ éxito" if success else f"❌ error: {error}"
    return f"Job {job_id}: finalizado en {duration:.1f}s — {result}"
