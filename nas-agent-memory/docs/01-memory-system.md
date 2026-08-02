# Sistema de Memoria Persistente

> **Propósito**: Diseño completo de los archivos de memoria que el agente mantiene entre sesiones.

---

## 1. Visión general

El sistema de memoria se compone de **4 archivos/directorios** que cumplen roles diferentes:

```
agent/memory/
├── MEMORY.md      ← QUÉ sabe (hechos, lecciones, estado del entorno)
├── USER.md        ← QUIÉN es el usuario (preferencias, estilo, decisiones)
├── SKILLS.md      ← CÓMO hace las cosas (procedimientos reutilizables)
└── sessions/      ← QUÉ hizo antes (historial resumido por sesión)
```

### Principios de diseño

1. **Markdown plano**: cualquier LLM puede leerlo sin parser especial.
2. **Bounded**: cada archivo tiene un tamaño máximo (~50KB). La curación evita crecimiento infinito.
3. **Legible por humanos**: el usuario puede leer/editar la memoria directamente.
4. **Accionable**: cada entrada debe ser útil para tomar decisiones, no solo informativa.
5. **Timestamped**: toda entrada tiene fecha para facilitar curación (eliminar lo viejo).

---

## 2. `MEMORY.md` — Conocimiento del agente

### Estructura

```markdown
# Memoria del Agente NAS
> Auto-curado. Última actualización: {timestamp}
> Entradas: {count} | Tamaño: {size_kb} KB / 50 KB máx

## Entorno
<!-- Estado actual del sistema: hardware, software, red, servicios -->
- NAS: {distro}, kernel {version}
- Docker: {version}, compose {version}
- IP: {ip_interna}
- Discos: {configuración}
- Servicios activos: {lista}

## Lecciones aprendidas
<!-- Cosas que descubrió resolviendo problemas — formato: [fecha] lección -->
- [2026-07-15] Los permisos de /var/lib/rclone deben ser 0750 (no 0700)
- [2026-08-01] emqx requiere al menos 512MB de RAM o falla con OOM silencioso

## Patrones que funcionaron
<!-- Enfoques generales que dieron resultado -->
- Backup: tar.gz local → rclone sync offsite → verificar con rclone check
- Deploy nuevo servicio: catálogo → validate → compose up → healthcheck → backup config

## Cosas que NO funcionaron
<!-- Evitar repetir errores -->
- [2026-07-20] Usar `version:` en compose v2 → Docker lo rechaza silenciosamente
- [2026-07-25] Reiniciar emqx sin detener clientes MQTT → mensajes perdidos

## Estado pendiente
<!-- Cosas que quedaron a medias o requieren seguimiento -->
- Rclone media mount: pendiente de crear pool de SA (ver rclone-nas-media docs)
- Jellyfin: pendiente de configurar bibliotecas después del mount
```

### Reglas de escritura

| Regla | Razón |
|-------|-------|
| Máximo 50 KB | Evitar que el system prompt se infle (se inyecta al inicio) |
| Una línea por lección | Fácil de escanear, fácil de eliminar en curación |
| Siempre con `[fecha]` | Permite curación temporal (eliminar > 90 días sin uso) |
| Solo hechos accionables | "el puerto 1883 es MQTT" NO va. "emqx necesita ≥512MB" SÍ va |
| Sin duplicados | La curación (capa C) consolida entradas similares |

### Cuándo se lee

- **Inicio de sesión**: se inyecta la sección `## Entorno` en el system prompt.
- **`recall()`**: se busca en todo el archivo por keywords/relevancia.
- **Curación (capa C)**: se lee completo para evaluar qué mantener.

### Cuándo se escribe

- **`remember(fact, category="leccion")`**: agrega una línea a la sección correspondiente.
- **Curación (capa C)**: puede eliminar, mover, o consolidar entradas.
- **Capa B (event-driven)**: puede agregar lecciones automáticamente post-tarea.

---

## 3. `USER.md` — Modelo del usuario

### Estructura

```markdown
# Perfil del Usuario
> Actualizado por el agente basado en interacciones
> Última actualización: {timestamp}

## Identidad
- Nombre: {si se proporcionó}
- Idioma preferido: español (código/configs en inglés)
- Nivel técnico: avanzado (systemd, Docker, Linux internals)

## Preferencias de interacción
- Estilo: directo, sin rodeos
- Prefiere: ver el comando antes de explicación larga
- Aprobación: preguntar antes de acciones destructivas
- Formato: markdown con código en bloques

## Decisiones técnicas
<!-- Decisiones explícitas del usuario que el agente debe respetar SIEMPRE -->
- No usar cron (solo systemd timers)
- Siempre cifrar datos en la nube (capa crypt obligatoria)
- Docker para servicios, bare-metal para rclone y el agente
- Preguntar antes de subir a GitHub
- Cada proyecto en su subcarpeta en Varios_tools (nunca en raíz)

## Proyectos activos
- NAS homelab con agente autónomo (nas-dotfiles)
- IoT con ESPHome/ESP-NOW
- Rclone media library para Jellyfin (3 módulos)
- SAG_SDK

## Horarios / disponibilidad
- {si se observa un patrón}
```

### Reglas de escritura

| Regla | Razón |
|-------|-------|
| Máximo 10 KB | Es contexto breve, no una biografía |
| Solo preferencias OBSERVADAS | No inventar. Solo anotar lo que el usuario dijo/mostró |
| Sección "Decisiones técnicas" es sagrada | Estas son reglas duras del usuario — nunca contradecirlas |
| Actualizar, no duplicar | Si una preferencia cambia, reemplazar (no agregar otra línea) |

### Cuándo se lee

- **Inicio de TODA sesión**: se inyecta completo en el system prompt (es pequeño, ~2-5 KB).
- Esto permite que el agente adapte su tono, formato y decisiones desde el primer mensaje.

### Cuándo se escribe

- **`update_user_model(key, value)`**: cuando el agente observa una preferencia nueva.
- **Capa B**: si el usuario corrige al agente ("no hagas X, prefiero Y") → update automático.
- **NUNCA automáticamente sin evidencia**: el agente no debe "adivinar" preferencias.

---

## 4. `SKILLS.md` — Procedimientos aprendidos

### Estructura

```markdown
# Skills del Agente NAS
> Procedimientos reutilizables aprendidos de tareas exitosas
> Total: {count} skills | Última actualización: {timestamp}

---

## skill: diagnosticar-servicio-caido
> Aprendido: 2026-07-10 | Usado: 5 veces | Último uso: 2026-08-01
> Éxito: 100% | Trigger: "servicio no responde", "container down"

### Procedimiento
1. `docker compose -f /docker/{servicio}/compose.yml ps`
2. Si está "exited": revisar logs → `docker compose logs --tail 50`
3. Si OOMKilled: aumentar `mem_limit` en compose.yml
4. Si restart loop: verificar volúmenes (permisos, disco lleno)
5. Si healthcheck failing: revisar dependencias (red, DNS, puertos)
6. Después de fix: `docker compose up -d` + verificar healthcheck

### Contexto
- Funciona para todos los servicios Docker del NAS
- No aplica para servicios bare-metal (rclone, el propio agente)

---

## skill: backup-y-sync-offsite
> Aprendido: 2026-07-20 | Usado: 3 veces | Último uso: 2026-07-30
> Éxito: 100% | Trigger: "hacer backup", "respaldar"

### Procedimiento
1. Identificar servicio: `backup_service("{nombre}")`
2. Verificar que el backup local se creó: `ls /docker/backups/{nombre}*`
3. Si rclone está configurado: `rclone_run_backup_job("{nombre}")`
4. Verificar sync: `rclone_status_rc()` → bytes transferidos > 0
5. Verificar integridad: `rclone check /docker/backups/ remote-crypt:backups/`

### Contexto
- Requiere que rclone esté instalado y configurado (módulo 1 de rclone-nas-media)
- El timer systemd ya lo hace automáticamente; este skill es para ejecución manual
```

### Reglas de escritura

| Regla | Razón |
|-------|-------|
| Máximo 100 KB | Los skills pueden ser detallados — más espacio que MEMORY.md |
| Formato estricto (header YAML-like) | Facilita parsing para búsqueda y métricas |
| Contar usos y éxito | Para curación: skills no usados en 90 días → candidatos a eliminar |
| Trigger explícito | Permite matching: "usuario dijo X" → ¿hay un skill con trigger similar? |
| Procedimiento paso a paso | Debe ser ejecutable directamente por el agente (tools reales) |

### Cuándo se lee

- **`recall(query)`**: busca skills con trigger que matchee la query.
- **Capa B**: después de resolver algo, verifica si ya existe un skill similar.

### Cuándo se escribe

- **`learn_skill(name, procedure, trigger)`**: creación explícita (modelo o capa B).
- **Capa B**: auto-genera skill cuando una tarea compleja (>3 tools) se completa exitosamente.
- **Curación (capa C)**: actualiza contadores, elimina skills no usados.

### Ciclo de vida de un skill

```
CREAR → USAR → MEJORAR → (opcional: OBSOLETO → ELIMINAR)
  ↑                ↑
  │                │ si el procedimiento cambió (ej: nueva versión de Docker)
  │                │ la curación detecta que el skill falló → marca para revisión
  │                │
  └── learn_skill()
```

---

## 5. `sessions/` — Historial de sesiones

### Formato de archivo

Un archivo por sesión significativa (no toda interacción genera uno):

```markdown
# Sesión: 2026-08-01 — Arreglar backup fallido
> Duración: ~15 min | Tools usadas: 7 | Resultado: éxito

## Problema
El timer rclone-backup@documentos no se ejecutó. El usuario reportó que no hay backup de hoy.

## Investigación
- `systemctl status rclone-backup@documentos.timer` → active, pero last trigger = hace 3 días
- `journalctl -u rclone-backup@documentos.service` → error de permisos en /srv/data/documentos
- `ls -la /srv/data/documentos` → owner cambió a root (probable actualización de paquete)

## Solución
- `chown -R rclone:rclone /srv/data/documentos`
- `systemctl start rclone-backup@documentos.service` → éxito
- Verificado: `rclone_status_rc()` → bytes transferidos OK

## Lecciones
- Persistido en MEMORY.md: "Verificar ownership de /srv/data/ después de apt upgrade"
- Skill actualizado: "diagnosticar-backup-fallido" (agregado paso de verificar permisos)
```

### Reglas

| Regla | Razón |
|-------|-------|
| Solo sesiones "significativas" (>3 tools o troubleshooting) | No llenar de ruido ("lista containers" no merece un resumen) |
| Máximo 5 KB por sesión | Es un RESUMEN, no un transcript completo |
| Retención: 90 días | Después, la curación elimina (las lecciones ya están en MEMORY.md) |
| Formato estructurado | Facilita búsqueda: "todas las sesiones donde se arregló backup" |

### Cuándo se escribe

- **Capa B (event-driven)**: al finalizar una sesión compleja, genera el resumen.
- El modelo produce el resumen a partir del contexto de la conversación.

### Cuándo se lee

- **`recall(query)`**: busca en sessions/ por keywords cuando MEMORY.md y SKILLS.md no tienen la respuesta.
- **Curación (capa C)**: revisa sessions/ > 90 días → eliminar (las lecciones ya están consolidadas).

---

## 6. Tamaños y límites

| Archivo | Límite | Justificación |
|---------|--------|---------------|
| MEMORY.md | 50 KB | Se inyecta parcialmente en system prompt — debe ser manejable |
| USER.md | 10 KB | Se inyecta COMPLETO — debe ser breve |
| SKILLS.md | 100 KB | Solo se consulta on-demand (recall), puede ser más grande |
| sessions/ (total) | 500 KB | 90 días × ~5 KB/sesión × ~1 sesión/día = ~450 KB |
| **Total sistema** | **~660 KB** | Cabe cómodamente en cualquier disco; no requiere DB |

### Comparación con context window

El system prompt carga:
- `USER.md` completo (~2-5 KB) → siempre
- `MEMORY.md` sección "Entorno" (~1-2 KB) → siempre
- Skills/lecciones relevantes (vía `recall()`) → solo cuando se necesitan

Total de memoria inyectada por sesión: **~3-7 KB** (< 2000 tokens). Impacto mínimo en context window.

---

## 7. Versionado

### Opción A: gitignored (recomendado para homelab)

```gitignore
# .gitignore en nas-dotfiles
agent/memory/
!agent/memory/.gitkeep
```

La memoria es **local al NAS** — no se sube a GitHub. Cada instancia del agente
tiene su propia memoria (refleja SU entorno, no un entorno genérico).

### Opción B: versionado en git (para auditoría)

Si quieres historial de cómo evoluciona la memoria:

```bash
# Cron/timer que commitea cambios de memoria diariamente
git -C /path/to/nas-dotfiles add agent/memory/
git -C /path/to/nas-dotfiles commit -m "memory: auto-update $(date +%Y-%m-%d)" --allow-empty
```

**No recomendado para `USER.md`** (puede contener preferencias privadas).

### Opción C: Backup con rclone (complemento)

Usar el módulo 1 (rclone-backup) para respaldar `agent/memory/` offsite:
- Si el NAS muere, la memoria se recupera del backup.
- Las lecciones no se pierden.
