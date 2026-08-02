"""
agent/core/rclone_rc.py — Cliente de la API RC (Remote Control) de Rclone.

Rclone expone una API HTTP/JSON cuando corre como daemon (`rclone rcd`).
En vez de spawnear el binario por cada operación y parsear stdout/journalctl,
el agente habla con esta API: es la forma soportada de consultar progreso de
transferencias, listar jobs async, y disparar operaciones sin re-autenticar
ni releer rclone.conf en cada llamada.

Referencia: https://rclone.org/rc/

Arquitectura:
    systemd (rclone-rcd.service, hardened como los demás units)
        → rclone rcd --rc-addr=127.0.0.1:5572 --rc-user=... --rc-pass=...
            → expone POST /core/stats, /job/status, /sync/copy (async), etc.
    agent/core/rclone_rc.py → requests.post(...) contra ese endpoint

Seguridad:
- El daemon RC se bindea SOLO a 127.0.0.1 (nunca 0.0.0.0).
- Usuario/password de la API RC se leen de variables de entorno
  (RCLONE_RC_USER / RCLONE_RC_PASS), nunca hardcodeados.
- Este cliente nunca envía comandos de tipo "config/*" que tocarían
  credenciales de remotes vía la API.
"""

from __future__ import annotations

import os
from typing import Any, Optional

try:
    import requests
except ImportError:
    requests = None  # graceful degradation — RC queda deshabilitado


RC_ADDR = os.environ.get("RCLONE_RC_ADDR", "127.0.0.1:5572")
RC_USER = os.environ.get("RCLONE_RC_USER", "")
RC_PASS = os.environ.get("RCLONE_RC_PASS", "")
RC_TIMEOUT = 10


class RcloneRCError(RuntimeError):
    pass


def _base_url() -> str:
    return f"http://{RC_ADDR}"


def rc_available() -> bool:
    """True si el daemon RC está corriendo y responde."""
    if requests is None:
        return False
    try:
        r = requests.post(
            f"{_base_url()}/rc/noop",
            auth=(RC_USER, RC_PASS) if RC_USER else None,
            timeout=3,
        )
        return r.status_code == 200
    except Exception:
        return False


def rc_call(endpoint: str, payload: Optional[dict] = None) -> dict[str, Any]:
    """Llama a un endpoint de la API RC. Lanza RcloneRCError si falla.

    Args:
        endpoint: ej. "core/stats", "job/status", "sync/copy"
        payload: cuerpo JSON de la request (params del comando rclone)
    """
    if requests is None:
        raise RcloneRCError(
            "El paquete 'requests' no está instalado. "
            "Instalar con: pip install requests"
        )

    try:
        r = requests.post(
            f"{_base_url()}/{endpoint}",
            json=payload or {},
            auth=(RC_USER, RC_PASS) if RC_USER else None,
            timeout=RC_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise RcloneRCError(f"Error llamando a {endpoint}: {e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# Wrappers de alto nivel sobre endpoints RC comunes
# ─────────────────────────────────────────────────────────────────────────────


def core_stats() -> dict:
    """Estadísticas globales: transferencias en curso, velocidad, bytes movidos."""
    return rc_call("core/stats")


def list_jobs() -> dict:
    """Lista IDs de jobs asíncronos en curso o recientes."""
    return rc_call("job/list")


def job_status(job_id: int) -> dict:
    """Estado de un job async específico (progreso, error si falló)."""
    return rc_call("job/status", {"jobid": job_id})


def start_sync(src_fs: str, dst_fs: str, async_job: bool = True) -> dict:
    """Dispara un sync vía RC (no bloqueante si async_job=True).

    Args:
        src_fs: remote origen, ej. "documentos_local:/srv/data"
        dst_fs: remote destino, ej. "remote-crypt:backup"
        async_job: si True, retorna inmediatamente con un jobid para pollear
    """
    payload = {"srcFs": src_fs, "dstFs": dst_fs}
    if async_job:
        payload["_async"] = True
    return rc_call("sync/sync", payload)


def list_remotes_rc() -> dict:
    """Lista remotes configurados vía RC — no expone credenciales, solo nombres."""
    return rc_call("config/listremotes")
