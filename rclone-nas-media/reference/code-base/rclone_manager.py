"""
agent/core/rclone_manager.py — Gestión de Rclone (instalación, remotes, jobs).

Sigue el mismo patrón que service_manager.py / backup_manager.py:
retorna siempre ToolResult, usa safe_run() (shell=False) y respeta
readonly_guard() para acciones que tocan el sistema.

Filosofía de seguridad (ver guía "rclone-seguro-debian"):
- rclone corre como usuario de sistema dedicado (RCLONE_USER), nunca root.
- rclone.conf vive en RCLONE_CONFIG_PATH, cifrado con password propio de rclone
  (no lo gestiona este módulo — se configura una sola vez a mano con
  `sudo -u rclone rclone config`).
- Todas las operaciones pasan por systemd (rclone-backup@<job>.service /
  rclone-mount@<remote>.service), nunca se invoca `rclone` directo como root.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from agent.core._result import ToolResult, Timer
from agent.tools._shell import safe_run, readonly_guard, is_dryrun


# ─────────────────────────────────────────────────────────────────────────────
# Configuración fija (coherente con la guía de hardening)
# ─────────────────────────────────────────────────────────────────────────────

RCLONE_USER = "rclone"
RCLONE_GROUP = "rclone"
RCLONE_CONFIG_PATH = Path("/etc/rclone/rclone.conf")
RCLONE_BIN = "/usr/bin/rclone"
RCLONE_LOG_DIR = Path("/var/log/rclone")
RCLONE_MOUNT_BASE = Path("/mnt/rclone")
SYSTEMD_DIR = Path("/etc/systemd/system")

_REMOTE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
_JOB_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


class InvalidRcloneName(ValueError):
    """Nombre de remote/job de rclone no válido."""
    pass


def _validate_remote_name(name: str) -> str:
    name = (name or "").strip()
    if not name or not _REMOTE_NAME_RE.match(name):
        raise InvalidRcloneName(
            f"Nombre de remote '{name}' inválido. "
            f"Solo letras, números, guión, punto y guión bajo."
        )
    return name


def _validate_job_name(name: str) -> str:
    name = (name or "").strip()
    if not name or not _JOB_NAME_RE.match(name):
        raise InvalidRcloneName(
            f"Nombre de job '{name}' inválido. "
            f"Solo minúsculas, números, guión, punto y guión bajo."
        )
    return name


class RcloneManager:
    """Gestor de Rclone: instalación, estado, remotes y jobs systemd."""

    # ── Instalación / verificación ──────────────────────────────────────

    @staticmethod
    def check_installed() -> ToolResult:
        """Verifica si rclone está instalado y con qué configuración de seguridad."""
        version = safe_run([RCLONE_BIN, "version"], timeout=10)
        installed = version and "ERROR" not in version and "rclone v" in version.lower()

        if not installed:
            return ToolResult.warn(
                "❌ Rclone no está instalado.\n\n"
                "Instalación recomendada (bare-metal + hardening):\n"
                "  1. install_rclone_binary()  — descarga e instala el binario\n"
                "  2. setup_rclone_user()      — crea usuario de sistema dedicado\n"
                "  3. Configurar manualmente:  sudo -u rclone rclone config\n"
                "     (crear el remote + activar password de config)\n"
                "  4. install_rclone_systemd_units() — genera unidades hardened",
                data={"installed": False},
                tool_name="rclone_check",
            )

        # Verificar usuario dedicado
        user_check = safe_run(["id", RCLONE_USER], timeout=5)
        user_exists = user_check and "ERROR" not in user_check and "no such user" not in user_check.lower()

        # Verificar que el binario no sea escribible por el usuario rclone
        perms = safe_run(["stat", "-c", "%a %U:%G", RCLONE_BIN], timeout=5)

        # Verificar si el config está cifrado (heurística: primeros bytes no son "[")
        config_encrypted = "desconocido"
        if RCLONE_CONFIG_PATH.exists():
            try:
                head = RCLONE_CONFIG_PATH.read_bytes()[:1]
                config_encrypted = "no (texto plano ⚠️)" if head == b"[" else "sí (parece cifrado)"
            except PermissionError:
                config_encrypted = "no se pudo leer (permisos OK)"

        return ToolResult.ok(
            f"✅ Rclone instalado\n\n"
            f"{version.splitlines()[0]}\n"
            f"Usuario dedicado '{RCLONE_USER}': {'✅ existe' if user_exists else '❌ falta — usar setup_rclone_user()'}\n"
            f"Permisos binario: {perms}\n"
            f"Config cifrada: {config_encrypted}",
            data={
                "installed": True,
                "user_exists": user_exists,
                "binary_perms": perms,
                "config_encrypted": config_encrypted,
            },
            suggestions=[] if user_exists else ["setup_rclone_user()"],
            tool_name="rclone_check",
        )

    @staticmethod
    def install_binary() -> ToolResult:
        """Instala el binario oficial de rclone vía script oficial y lo bloquea a root:root."""
        blocked = readonly_guard("rclone_install_binary")
        if blocked:
            return ToolResult.error(blocked, tool_name="rclone_install_binary")

        with Timer() as t:
            dl = safe_run(
                ["curl", "-fsSL", "https://rclone.org/install.sh", "-o", "/tmp/rclone-install.sh"],
                timeout=30,
            )
            if "ERROR" in dl:
                return ToolResult.error(f"Fallo al descargar el instalador: {dl}",
                                         tool_name="rclone_install_binary")

            install_out = safe_run(["bash", "/tmp/rclone-install.sh"], timeout=180)
            # Bloquear el binario: solo root escribe, todos ejecutan
            safe_run(["chown", "root:root", RCLONE_BIN], timeout=5)
            safe_run(["chmod", "0755", RCLONE_BIN], timeout=5)

        return ToolResult.ok(
            f"✅ Rclone instalado y binario bloqueado (root:root, 0755).\n\n{install_out[-500:]}",
            data={"action": "install_binary"},
            suggestions=["setup_rclone_user()", "rclone_check_installed()"],
            tool_name="rclone_install_binary",
            elapsed_ms=t.elapsed_ms,
        )

    @staticmethod
    def setup_user() -> ToolResult:
        """Crea el usuario/grupo de sistema dedicado y la estructura de directorios."""
        blocked = readonly_guard("rclone_setup_user")
        if blocked:
            return ToolResult.error(blocked, tool_name="rclone_setup_user")

        steps = []

        # Grupo
        grp = safe_run(["getent", "group", RCLONE_GROUP], timeout=5)
        if not grp or "ERROR" in grp:
            safe_run(["groupadd", "--system", RCLONE_GROUP], timeout=5)
            steps.append(f"grupo '{RCLONE_GROUP}' creado")
        else:
            steps.append(f"grupo '{RCLONE_GROUP}' ya existía")

        # Usuario
        usr = safe_run(["id", RCLONE_USER], timeout=5)
        if not usr or "ERROR" in usr or "no such user" in usr.lower():
            safe_run([
                "useradd", "--system",
                "--gid", RCLONE_GROUP,
                "--shell", "/usr/sbin/nologin",
                "--home-dir", "/var/lib/rclone",
                "--no-create-home",
                "--comment", "Rclone service account",
                RCLONE_USER,
            ], timeout=10)
            steps.append(f"usuario '{RCLONE_USER}' creado (nologin, sin home real)")
        else:
            steps.append(f"usuario '{RCLONE_USER}' ya existía")

        # Directorios
        dirs = [
            ("/etc/rclone", "root", RCLONE_GROUP, "0750"),
            ("/etc/rclone/secrets", "root", RCLONE_GROUP, "0750"),
            ("/var/lib/rclone", RCLONE_USER, RCLONE_GROUP, "0750"),
            (str(RCLONE_LOG_DIR), RCLONE_USER, RCLONE_GROUP, "0750"),
            (str(RCLONE_MOUNT_BASE), RCLONE_USER, RCLONE_GROUP, "0750"),
        ]
        for path, owner, group, mode in dirs:
            safe_run(["install", "-d", "-o", owner, "-g", group, "-m", mode, path], timeout=5)
        steps.append(f"directorios creados: {', '.join(d[0] for d in dirs)}")

        return ToolResult.ok(
            "✅ Usuario y estructura de directorios listos:\n\n"
            + "\n".join(f"  • {s}" for s in steps)
            + "\n\n⚠️  Siguiente paso MANUAL obligatorio (no lo hace el agente):\n"
            "  sudo -u rclone rclone --config /etc/rclone/rclone.conf config\n"
            "  → crear el remote + activar 'Set configuration password'",
            data={"action": "setup_user"},
            tool_name="rclone_setup_user",
        )

    # ── Estado / diagnóstico ────────────────────────────────────────────

    @staticmethod
    def list_remotes() -> ToolResult:
        """Lista los remotes configurados (nombres solamente, sin credenciales)."""
        if not RCLONE_CONFIG_PATH.exists():
            return ToolResult.warn(
                f"No existe {RCLONE_CONFIG_PATH}. Aún no hay remotes configurados.",
                tool_name="rclone_list_remotes",
            )

        output = safe_run(
            ["sudo", "-u", RCLONE_USER, RCLONE_BIN, "--config", str(RCLONE_CONFIG_PATH),
             "listremotes"],
            timeout=20,
        )

        if "ERROR" in output or "password" in output.lower():
            return ToolResult.warn(
                "No se pudo listar remotes (probablemente el config está cifrado "
                "y requiere RCLONE_PASSWORD_COMMAND configurado en el entorno).",
                data={"raw": output},
                tool_name="rclone_list_remotes",
            )

        remotes = [r.strip().rstrip(":") for r in output.strip().splitlines() if r.strip()]
        return ToolResult.ok(
            f"Remotes configurados ({len(remotes)}):\n\n"
            + "\n".join(f"  • {r}" for r in remotes) if remotes else "No hay remotes configurados.",
            data={"remotes": remotes},
            tool_name="rclone_list_remotes",
        )

    @staticmethod
    def status() -> ToolResult:
        """Dashboard de unidades systemd relacionadas con rclone."""
        units = safe_run(
            ["systemctl", "list-units", "--all", "--no-legend",
             "rclone-*.service", "rclone-*.timer"],
            timeout=10,
        )

        if not units or not units.strip():
            return ToolResult.warn(
                "No hay unidades systemd de rclone instaladas todavía.",
                tool_name="rclone_status",
            )

        return ToolResult.ok(
            f"=== UNIDADES SYSTEMD DE RCLONE ===\n\n{units}",
            data={"raw": units},
            tool_name="rclone_status",
        )

    # ── Jobs de backup/sync ─────────────────────────────────────────────

    @staticmethod
    def run_backup_job(job_name: str) -> ToolResult:
        """Dispara manualmente un job de backup ya instalado."""
        blocked = readonly_guard("rclone_run_backup_job")
        if blocked:
            return ToolResult.error(blocked, tool_name="rclone_run_backup_job")

        try:
            job_name = _validate_job_name(job_name)
        except InvalidRcloneName as e:
            return ToolResult.error(f"ERROR: {e}", tool_name="rclone_run_backup_job")

        unit = f"rclone-backup@{job_name}.service"
        unit_file = SYSTEMD_DIR / f"rclone-backup@.service"
        if not unit_file.exists():
            return ToolResult.error(
                f"ERROR: no existe la unidad template {unit_file}.",
                tool_name="rclone_run_backup_job",
            )

        with Timer() as t:
            out = safe_run(["systemctl", "start", unit], timeout=30)
            journal = safe_run(
                ["journalctl", "-u", unit, "-n", "30", "--no-pager"], timeout=10
            )

        return ToolResult.ok(
            f"▶️ Job '{job_name}' disparado ({unit})\n\n"
            f"--- Últimas líneas de log ---\n{journal}",
            data={"job": job_name, "unit": unit},
            suggestions=[f"journalctl -u {unit} -f"],
            tool_name="rclone_run_backup_job",
            elapsed_ms=t.elapsed_ms,
        )

    @staticmethod
    def mount_status(remote_name: str) -> ToolResult:
        """Verifica si un mount FUSE está activo y montado."""
        try:
            remote_name = _validate_remote_name(remote_name)
        except InvalidRcloneName as e:
            return ToolResult.error(f"ERROR: {e}", tool_name="rclone_mount_status")

        unit = f"rclone-mount@{remote_name}.service"
        active = safe_run(["systemctl", "is-active", unit], timeout=5)
        mount_point = RCLONE_MOUNT_BASE / remote_name
        mounted = safe_run(["mountpoint", "-q", str(mount_point)], timeout=5, check=False)
        is_mounted = "not a mountpoint" not in (mounted or "")

        return ToolResult.ok(
            f"Servicio systemd: {active.strip()}\n"
            f"Punto de montaje {mount_point}: {'montado ✅' if is_mounted else 'no montado ❌'}",
            data={"remote": remote_name, "service_active": active.strip(), "mounted": is_mounted},
            tool_name="rclone_mount_status",
        )
