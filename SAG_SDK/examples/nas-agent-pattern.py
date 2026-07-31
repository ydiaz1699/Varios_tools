"""
nas-agent-pattern.py — Patrón real de agente multi-provider con tools

Este ejemplo muestra el patrón usado en producción para el NAS Agent:
- Multi-provider dinámico (Gemini/Bedrock/Ollama) via env var
- Extended thinking para Bedrock (Claude)
- @tool decorator para crear herramientas
- System prompt con instrucciones de razonamiento

Uso:
    python nas-agent-pattern.py "¿Qué servicios están corriendo?"
    NAS_AGENT_MODEL=bedrock python nas-agent-pattern.py "diagnostica nextcloud"
    NAS_AGENT_MODEL=ollama python nas-agent-pattern.py "uso de disco"

Requisitos:
    pip install 'strands-agents[gemini]' strands-agents-tools
"""

import os
import sys
import subprocess
from pathlib import Path

from strands import Agent, tool


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS — cada @tool es una herramienta que el agente puede invocar
# ─────────────────────────────────────────────────────────────────────────────


@tool
def list_services() -> str:
    """Lista todos los servicios Docker con su estado actual.

    Returns:
        str: Tabla con nombre, estado, y puertos de cada servicio
    """
    result = subprocess.run(
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return f"ERROR: {result.stderr}"
    return result.stdout or "No hay contenedores corriendo."


@tool
def disk_usage() -> str:
    """Muestra el uso de disco del sistema con alertas si supera 80%.

    Returns:
        str: Resumen de uso de disco por partición
    """
    result = subprocess.run(
        ["df", "-h", "--type=ext4", "--type=btrfs", "--type=xfs"],
        capture_output=True, text=True
    )
    return result.stdout


@tool
def service_logs(service: str, lines: int = 50) -> str:
    """Muestra las últimas N líneas de logs de un servicio Docker.

    Args:
        service: Nombre del servicio (ej: "nextcloud", "plex", "grafana")
        lines: Número de líneas a mostrar (default: 50)

    Returns:
        str: Últimas líneas de logs del servicio
    """
    # Buscar compose file
    docker_base = Path(os.environ.get("DOCKER_BASE", "/docker"))
    compose_names = ["compose.yml", "compose.yaml", "docker-compose.yml", "docker-compose.yaml"]

    compose_file = None
    for name in compose_names:
        candidate = docker_base / service / name
        if candidate.exists():
            compose_file = candidate
            break

    if not compose_file:
        return f"ERROR: Servicio '{service}' no encontrado en {docker_base}/"

    result = subprocess.run(
        ["docker", "compose", "-f", str(compose_file), "logs", "--tail", str(lines)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return f"ERROR: {result.stderr}"
    return result.stdout


@tool
def scan_ports() -> str:
    """Escanea puertos TCP en uso y sugiere los próximos disponibles.

    Returns:
        str: Lista de puertos ocupados + próximos 5 disponibles en rango 8100-8999
    """
    result = subprocess.run(
        ["ss", "-tlnp"],
        capture_output=True, text=True
    )
    # Extraer puertos en uso
    ports_in_use = set()
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 4:
            addr = parts[3]
            if ":" in addr:
                try:
                    port = int(addr.rsplit(":", 1)[1])
                    ports_in_use.add(port)
                except ValueError:
                    pass

    # Encontrar próximos disponibles en rango 8100-8999
    available = []
    for p in range(8100, 9000):
        if p not in ports_in_use:
            available.append(p)
        if len(available) >= 5:
            break

    output = result.stdout + "\n"
    output += f"\nPuertos en uso (total): {len(ports_in_use)}"
    output += f"\nPróximos disponibles (8100-8999): {available}"
    return output


# ─────────────────────────────────────────────────────────────────────────────
# MULTI-PROVIDER — selección dinámica por variable de entorno
# ─────────────────────────────────────────────────────────────────────────────


def get_model():
    """Selecciona el modelo según NAS_AGENT_MODEL.

    Providers:
        - gemini (default): Barato (~$0.15/1M tokens), solo GOOGLE_API_KEY
        - bedrock: Mejor razonamiento (~$3/1M), extended thinking habilitado
        - ollama: Gratis, local, sin internet
    """
    proveedor = os.environ.get("NAS_AGENT_MODEL", "gemini").lower()
    model_id_override = os.environ.get("NAS_AGENT_MODEL_ID")

    if proveedor == "gemini":
        from strands.models.gemini import GeminiModel

        api_key = os.environ.get("GOOGLE_API_KEY")
        client_args = {"api_key": api_key} if api_key else None

        return GeminiModel(
            model_id=model_id_override or "gemini-3.1-flash-lite",
            client_args=client_args,
            params={"temperature": 0.3, "max_output_tokens": 4096},
        )

    elif proveedor == "bedrock":
        from strands.models.bedrock import BedrockModel

        thinking_budget = int(os.environ.get("NAS_AGENT_THINKING_BUDGET", "10000"))

        return BedrockModel(
            model_id=model_id_override or "us.anthropic.claude-sonnet-4-20250514-v1:0",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            additional_request_fields={
                "anthropic_beta": ["interleaved-thinking-2025-05-14"],
                "thinking": {"type": "enabled", "budget_tokens": thinking_budget},
            },
        )

    elif proveedor == "ollama":
        from strands.models.ollama import OllamaModel

        return OllamaModel(
            model_id=model_id_override or "llama3.1",
            host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        )

    else:
        raise ValueError(
            f"Provider '{proveedor}' no soportado.\n"
            f"Opciones: gemini, bedrock, ollama\n"
            f"Configura con: export NAS_AGENT_MODEL=<opción>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT con instrucciones de razonamiento
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
# RAZONAMIENTO

Antes de ejecutar cualquier acción, SIEMPRE razona paso a paso:

1. **Entender** — ¿Qué pide el usuario?
2. **Planificar** — ¿Qué herramientas necesito? ¿En qué orden?
3. **Verificar** — Consultar estado actual ANTES de actuar
4. **Ejecutar** — Solo después de tener la información necesaria
5. **Confirmar** — ¿El resultado responde la pregunta?

# MISIÓN

Eres un agente de administración de NAS/Docker. Ayudas a:
- Ver estado de servicios
- Diagnosticar problemas (logs, puertos, disco)
- Sugerir soluciones concretas

# REGLAS
- Responder en ESPAÑOL
- Ser conciso — el usuario administra desde terminal
- Si detectás un problema, sugerir la solución concreta
- Si no sabés algo, DILO — no inventes
"""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────


def main():
    # Obtener query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("🖥️ > ")
        if not query.strip():
            print("Sin query.")
            sys.exit(0)

    # Crear agente
    model = get_model()
    agent = Agent(
        model=model,
        tools=[list_services, disk_usage, service_logs, scan_ports],
        system_prompt=SYSTEM_PROMPT,
    )

    # Ejecutar
    proveedor = os.environ.get("NAS_AGENT_MODEL", "gemini").lower()
    print(f"⚡ Provider: {proveedor}")
    print(f"📝 Query: {query}\n")
    print("-" * 50)
    result = agent(query)
    print("-" * 50)
    print("\n✅ Completado.")


if __name__ == "__main__":
    main()
