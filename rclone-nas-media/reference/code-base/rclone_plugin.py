"""
agent/plugins/rclone_plugin.py — Plugin de gestión de Rclone.

Registra las tools de instalación/gestión de Rclone. No define schedules
propios: los jobs de backup de rclone se gestionan vía sus propios
systemd timers (rclone-backup@<job>.timer), no vía el scheduler interno
del agente, para mantener el aislamiento descrito en la guía de hardening.
"""

from agent.plugins.base import BasePlugin, PluginMeta


class RclonePlugin(BasePlugin):
    """Plugin de instalación y gestión de Rclone."""

    meta = PluginMeta(
        name="rclone",
        version="1.0.0",
        description="Instalación segura y gestión de Rclone (backups, mounts FUSE)",
    )

    def setup(self):
        from agent.tools.rclone_tools import (
            rclone_check_installed,
            rclone_install_binary,
            rclone_setup_user,
            rclone_list_remotes,
            rclone_status,
            rclone_run_backup_job,
            rclone_mount_status,
        )
        from agent.tools.rclone_install_tools import (
            rclone_encrypt_config_password,
            rclone_install_backup_unit,
            rclone_install_rc_daemon,
            rclone_status_rc,
            rclone_job_status,
        )

        # Instalación / gestión básica (shell-based)
        self.register_tool(rclone_check_installed)
        self.register_tool(rclone_install_binary)
        self.register_tool(rclone_setup_user)
        self.register_tool(rclone_list_remotes)
        self.register_tool(rclone_status)
        self.register_tool(rclone_run_backup_job)
        self.register_tool(rclone_mount_status)

        # Instalación completa de la guía de hardening
        self.register_tool(rclone_encrypt_config_password)
        self.register_tool(rclone_install_backup_unit)
        self.register_tool(rclone_install_rc_daemon)

        # Estado/estadísticas vía API RC
        self.register_tool(rclone_status_rc)
        self.register_tool(rclone_job_status)
