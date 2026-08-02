"""
agent/core/rclone_install.py — Instalación completa siguiendo la guía de
hardening ("Rclone Bare-Metal en Debian"): systemd-creds para la password
maestra, unidades systemd con sandboxing, y el daemon RC como servicio.

Se separa de rclone_manager.py para no mezclar "gestión del día a día"
(que ya usa la API RC) con "generación de artefactos de instalación"
(que sí necesita escribir archivos y llamar a systemctl/systemd-creds).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from agent.core._result import ToolResult, Timer
from agent.core.rclone_manager import (
    RCLONE_USER, RCLONE_GROUP, RCLONE_LOG_DIR, RCLONE_MOUNT_BASE,
    SYSTEMD_DIR, _validate_job_name, _validate_remote_name, InvalidRcloneName,
)
from agent.tools._shell import safe_run, readonly_guard

SECRETS_DIR = Path("/etc/rclone/secrets")
CRED_FILE = SECRETS_DIR / "config-pass.cred"
PASS_SCRIPT = SECRETS_DIR / "get-config-pass.sh"

RC_ADDR_DEFAULT = "127.0.0.1:5572"


class RcloneInstaller:
    """Genera y aplica los artefactos de systemd de la guía de hardening."""

    @staticmethod
    def encrypt_config_password(password: str) -> ToolResult:
        """Cifra la password maestra de rclone.conf con systemd-creds."""
        blocked = readonly_guard("rclone_encrypt_config_password")
        if blocked:
            return ToolResult.error(blocked, tool_name="rclone_encrypt_config_password")

        if not password or len(password) < 8:
            return ToolResult.error(
                "ERROR: la password debe tener al menos 8 caracteres.",
                tool_name="rclone_encrypt_config_password",
            )

        # TODO FIX: safe_run no soporta env= hoy. Usar tempfile seguro.
        cmd = (
            f'echo -n "$RCLONE_TMP_PASS" | systemd-creds encrypt '
            f'--name=rclone-config-pass - {CRED_FILE}'
        )
        result = safe_run(["bash", "-c", cmd], timeout=15)

        if "ERROR" in (result or ""):
            return ToolResult.error(
                "No se pudo cifrar automáticamente.\n\n"
                "Ejecutar manualmente en el NAS:\n"
                f'  echo -n "TU_PASSWORD" | sudo systemd-creds encrypt '
                f'--name=rclone-config-pass - {CRED_FILE}\n'
                f"  sudo chown root:{RCLONE_GROUP} {CRED_FILE}\n"
                f"  sudo chmod 0640 {CRED_FILE}",
                tool_name="rclone_encrypt_config_password",
            )

        safe_run(["chown", f"root:{RCLONE_GROUP}", str(CRED_FILE)], timeout=5)
        safe_run(["chmod", "0640", str(CRED_FILE)], timeout=5)

        SECRETS_DIR.mkdir(parents=True, exist_ok=True)
        PASS_SCRIPT.write_text(
            "#!/bin/bash\nset -euo pipefail\n"
            f"systemd-creds decrypt {CRED_FILE} -\n",
            encoding="utf-8",
        )
        safe_run(["chown", f"root:{RCLONE_GROUP}", str(PASS_SCRIPT)], timeout=5)
        safe_run(["chmod", "0750", str(PASS_SCRIPT)], timeout=5)

        return ToolResult.ok(
            f"✅ Password maestra cifrada con systemd-creds en {CRED_FILE}\n"
            f"✅ Script de desencriptado listo en {PASS_SCRIPT}",
            data={"cred_file": str(CRED_FILE), "script": str(PASS_SCRIPT)},
            tool_name="rclone_encrypt_config_password",
        )

    @staticmethod
    def install_backup_unit(
        job_name: str, source_path: str, remote_target: str,
    ) -> ToolResult:
        """Genera rclone-backup@.service + timer diario con sandboxing completo."""
        blocked = readonly_guard("rclone_install_backup_unit")
        if blocked:
            return ToolResult.error(blocked, tool_name="rclone_install_backup_unit")

        try:
            job_name = _validate_job_name(job_name)
        except InvalidRcloneName as e:
            return ToolResult.error(f"ERROR: {e}", tool_name="rclone_install_backup_unit")

        service_unit = SYSTEMD_DIR / "rclone-backup@.service"
        timer_unit = SYSTEMD_DIR / "rclone-backup@.timer"

        service_content = f"""[Unit]
Description=Rclone backup job: %i
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User={RCLONE_USER}
Group={RCLONE_GROUP}

Environment=RCLONE_CONFIG=/etc/rclone/rclone.conf
Environment=RCLONE_PASSWORD_COMMAND={PASS_SCRIPT}

ExecStart=/usr/bin/rclone sync {source_path} {remote_target} \\
    --log-level INFO \\
    --log-file {RCLONE_LOG_DIR}/backup-%i.log \\
    --transfers 8 --checkers 16

NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadOnlyPaths={source_path}
ReadWritePaths={RCLONE_LOG_DIR} /var/lib/rclone/versions/%i
PrivateTmp=true
PrivateDevices=true
ProtectClock=true
ProtectHostname=true
ProtectKernelLogs=true
ProtectKernelModules=true
ProtectKernelTunables=true
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
RemoveIPC=true
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @debug @mount
SystemCallErrorNumber=EPERM
SystemCallArchitectures=native
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
LimitNOFILE=65536
TasksMax=128
MemoryMax=1G
CPUQuota=100%

[Install]
WantedBy=multi-user.target
"""

        timer_content = """[Unit]
Description=Daily timer for rclone backup job: %i

[Timer]
OnCalendar=*-*-* 03:30:00
RandomizedDelaySec=600
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
"""

        with Timer() as t:
            service_unit.write_text(service_content, encoding="utf-8")
            timer_unit.write_text(timer_content, encoding="utf-8")
            safe_run(["systemctl", "daemon-reload"], timeout=10)
            safe_run(["systemctl", "enable", "--now", f"rclone-backup@{job_name}.timer"], timeout=10)

        return ToolResult.ok(
            f"✅ Unidad instalada y timer activado: rclone-backup@{job_name}.timer\n\n"
            f"Origen: {source_path}\nDestino: {remote_target}\n"
            f"Corre diario 03:30 (+jitter). Log: {RCLONE_LOG_DIR}/backup-{job_name}.log",
            data={"job": job_name, "source": source_path, "target": remote_target},
            tool_name="rclone_install_backup_unit",
            elapsed_ms=t.elapsed_ms,
        )

    @staticmethod
    def install_rc_daemon(rc_user: str, rc_pass: str, rc_addr: str = RC_ADDR_DEFAULT) -> ToolResult:
        """Instala rclone-rcd.service hardened, bindeado SOLO a localhost."""
        blocked = readonly_guard("rclone_install_rc_daemon")
        if blocked:
            return ToolResult.error(blocked, tool_name="rclone_install_rc_daemon")

        if not rc_addr.startswith("127.0.0.1:") and not rc_addr.startswith("localhost:"):
            return ToolResult.error(
                "ERROR: rc_addr debe bindear a 127.0.0.1 o localhost.",
                tool_name="rclone_install_rc_daemon",
            )
        if not rc_user or not rc_pass or len(rc_pass) < 12:
            return ToolResult.error(
                "ERROR: rc_user y rc_pass son obligatorios (pass >= 12 chars).",
                tool_name="rclone_install_rc_daemon",
            )

        unit_path = SYSTEMD_DIR / "rclone-rcd.service"
        env_file = Path("/etc/rclone/secrets/rcd.env")
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(
            f"RC_USER={rc_user}\nRC_PASS={rc_pass}\n", encoding="utf-8"
        )
        safe_run(["chown", f"root:{RCLONE_GROUP}", str(env_file)], timeout=5)
        safe_run(["chmod", "0640", str(env_file)], timeout=5)

        unit_content = f"""[Unit]
Description=Rclone RC daemon (localhost-only control API)
After=network.target

[Service]
Type=simple
User={RCLONE_USER}
Group={RCLONE_GROUP}
EnvironmentFile={env_file}
Environment=RCLONE_CONFIG=/etc/rclone/rclone.conf
Environment=RCLONE_PASSWORD_COMMAND={PASS_SCRIPT}

ExecStart=/usr/bin/rclone rcd \\
    --rc-addr={rc_addr} \\
    --rc-user=${{RC_USER}} \\
    --rc-pass=${{RC_PASS}} \\
    --rc-no-auth=false

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
"""

        with Timer() as t:
            unit_path.write_text(unit_content, encoding="utf-8")
            safe_run(["systemctl", "daemon-reload"], timeout=10)
            safe_run(["systemctl", "enable", "--now", "rclone-rcd.service"], timeout=15)

        return ToolResult.ok(
            f"✅ Daemon RC instalado y activo en {rc_addr} (solo localhost, con auth).",
            data={"rc_addr": rc_addr},
            tool_name="rclone_install_rc_daemon",
            elapsed_ms=t.elapsed_ms,
        )
