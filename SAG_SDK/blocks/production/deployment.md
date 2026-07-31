# Deployment y Runtime en Producción

> **Cuándo usar este bloque:** Cuando tu agente ya funciona en desarrollo y necesitas correrlo en producción: como servicio systemd, en cron, dentro de Docker, o como daemon persistente.
>
> Última verificación de datos externos: 2026-07-31

---

## Opción 1: CLI invocado por el usuario

La más simple — el usuario ejecuta el agente cuando lo necesita:

```bash
agent "diagnostica nextcloud"
```

Configuración necesaria:
- `.bashrc` con alias/función definida
- `.env.agent` con API key
- Session manager para memoria entre invocaciones

No requiere daemon ni servicio. Es el patrón del NAS Agent.

---

## Opción 2: Systemd service (daemon persistente)

Para un agente que corre continuamente (ej: escuchando MQTT, ejecutando scheduler):

```ini
# /etc/systemd/system/nas-agent.service
[Unit]
Description=NAS Agent (scheduler + MQTT listener)
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/nas-dotfiles
ExecStart=/usr/bin/python3 -m agent.daemon
Restart=on-failure
RestartSec=10
Environment=NAS_AGENT_MODEL=gemini
EnvironmentFile=/nas-dotfiles/.env.agent

# Seguridad
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/docker /nas-dotfiles/.nas-agent

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nas-agent
sudo systemctl status nas-agent
journalctl -u nas-agent -f    # ver logs
```

---

## Opción 3: Cron job (tareas programadas)

Para ejecutar el agente periódicamente (backup, health check):

```bash
# crontab -e
# Backup diario a las 3am
0 3 * * * cd /nas-dotfiles && python3 -m agent.nas_agent "backup de todos los servicios" >> /var/log/nas-agent-cron.log 2>&1

# Health check cada hora
0 * * * * cd /nas-dotfiles && python3 -m agent.nas_agent "service_health" >> /var/log/nas-agent-cron.log 2>&1
```

**Nota:** En modo cron, usar `--new` para que cada ejecución sea independiente (sin sesión previa).

---

## Opción 4: Docker container

Para aislar el agente del host:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/ ./agent/
COPY .env.agent .

CMD ["python", "-m", "agent.nas_agent"]
```

```yaml
# compose.yml
services:
  nas-agent:
    build: .
    restart: unless-stopped
    volumes:
      - /docker:/docker:ro          # Acceso a configs Docker
      - /var/run/docker.sock:/var/run/docker.sock  # Docker API
      - agent-sessions:/app/.nas-agent  # Persistir sesiones
    env_file: .env.agent
    network_mode: host              # Para acceder a servicios locales

volumes:
  agent-sessions:
```

---

## Restart policy

| Modo | Restart | Cuándo usar |
|------|---------|-------------|
| CLI manual | No | El usuario ejecuta cuando quiere |
| Systemd | `on-failure` + `RestartSec=10` | Daemon que debe estar siempre vivo |
| Docker | `unless-stopped` | Container que se levanta con el NAS |
| Cron | N/A (se ejecuta y termina) | Tareas periódicas |

---

## Variables de entorno en producción

```bash
# Siempre definir en producción:
NAS_AGENT_MODEL=gemini
NAS_AGENT_MODEL_ID=gemini-3.1-flash-lite
GOOGLE_API_KEY=tu-key
DOCKER_BASE=/docker

# Opcional pero recomendado:
NAS_AGENT_AUDIT=1                    # Registrar todas las acciones
NAS_AGENT_SESSION_TIMEOUT=30         # Auto-reset sesión
NAS_AGENT_READONLY=0                 # 1 para modo seguro en demos
```

---

## Logs y monitoreo

```bash
# Audit log del agente (registra cada tool ejecutada)
tail -f /docker/backups/agent_audit.log

# Si usa systemd:
journalctl -u nas-agent -f --output=short-iso

# Si usa cron:
tail -f /var/log/nas-agent-cron.log
```

---

## Notas importantes

- El agente necesita acceso al Docker socket para administrar servicios
- En modo daemon, el scheduler interno maneja las tareas periódicas (no necesita cron)
- En modo CLI, cron es la forma de agendar ejecuciones
- Siempre usar `NAS_AGENT_AUDIT=1` en producción para trazabilidad
- El `.env.agent` debe tener permisos 600 (contiene API keys)
