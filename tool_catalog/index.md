# Índice de tool_catalog

Una línea por ficha. Lee esto primero; abre solo la ficha (`entries/<slug>.md`)
que encaje con tu proyecto actual; lee la fuente completa solo si la ficha dice
que aplica.

### Recursos externos — ecosistema Gentleman Programming (`entries/gentleman-programming/`)

Recursos descubiertos a través del video de Gentleman Programming. (Nota: Prowler
es de `prowler-cloud`, se incluye por ser el ejemplo del video.)

| Slug | Tipo | Problema que resuelve | Aplica a | Estado |
|------|------|-----------------------|----------|--------|
| [prowler-agent-skills](entries/gentleman-programming/prowler-agent-skills.md) | repo | Contexto para LLM en 3 niveles (AGENTS.md + skills por trigger + auto-invoke) | proyectos con .kiro/skills, agentes LLM | APLICADO |
| [gentleman-agents-skills-video](entries/gentleman-programming/agents-skills-video.md) | video | Arquitectura AGENTS.md + skills + auto-invoke + subagentes (sin releer la transcripción) | diseñar contexto de agentes, dividir AGENTS.md, subagentes | REVISADO_A_FONDO |
| [gentleman-dots](entries/gentleman-programming/gentleman-dots.md) | dotfiles | Entorno de desarrollo completo (Neovim/shells/terminales) + capa IA; ejemplo de 1 AGENTS.md + orquestador SDD/subagentes | montar entorno terminal/Neovim, capa IA multi-CLI, ver subagentes aplicados | REVISADO_A_FONDO |
| [sdd-video](entries/gentleman-programming/sdd-video.md) | video | Spec-Driven Development: proceso para que la IA no improvise (init, skill registry, strict TDD, fases, subagentes) | definir proceso anti-improvisación, skill registry, orquestador/subagentes | REVISADO_A_FONDO |
| [engram](entries/gentleman-programming/engram.md) | repo | Memoria persistente para agentes (Go + SQLite/FTS5, MCP, agent-agnostic) | dar memoria a un agente, alternativa lista-para-usar a diseñar memoria propia | REVISADO_PARCIAL |

### Recursos externos — otros

| Slug | Tipo | Problema que resuelve | Aplica a | Estado |
|------|------|-----------------------|----------|--------|
| [rclone-mcp-servers](entries/rclone-mcp-servers.md) | repo | MCP para rclone (control total vía RC API): daemon rcd + rclone-mcp-server con TOOLSETS=all | exponer rclone a un LLM por MCP, elegir base control-total vs read-only | APLICADO |
| [n8n-mcp](entries/n8n-mcp.md) | repo | MCP para que un LLM cree/gestione workflows de n8n (nodos + API REST); gotcha SSRF WEBHOOK_SECURITY_MODE=permissive | que Kiro CLI diseñe/cree workflows de n8n | APLICADO |
| [tasker-mcp-dceluis](entries/tasker-mcp-dceluis.md) | repo | MCP (Go) que EJECUTA tareas de Tasker en vivo en el teléfono (POST /run_task); tarea+TaskVariables → tool MCP | controlar el teléfono en vivo por LLM; parser XML→tools; complementa tu Tasker_mcp (que genera XML) | REVISADO_A_FONDO |

### Artefactos propios (viven en `../tools_AI/`, listos para usar)

| Slug | Tipo | Problema que resuelve | Aplica a | Estado |
|------|------|-----------------------|----------|--------|
| [skill-creator](entries/skill-creator.md) | tool | Crear/optimizar skills de agentes LLM sin reinventar el proceso | crear/mejorar una skill | APLICADO |
| [unificador-skill](entries/unificador-skill.md) | tool | Consolidar fragmentos dispersos en una guía coherente | unificar notas/diagnósticos | REVISADO_A_FONDO |
| [nas-agent-memory](entries/nas-agent-memory.md) | pattern | Memoria persistente + auto-mejora (Learning Loop) para un agente | diseñar memoria de un agente | SOLO_REFERENCIA |

## Cómo elegir

- **¿Quieres entender la arquitectura de agentes (AGENTS.md + skills + subagentes)?** → `gentleman-agents-skills-video` (concepto) y `prowler-agent-skills` (implementación).
- **¿Tu repo usa agentes/LLM con skills?** → `prowler-agent-skills` (patrón) y `skill-creator` (para crearlas).
- **¿Necesitas unificar notas dispersas en una guía?** → `unificador-skill`.
- **¿Quieres un proceso para que la IA no improvise (spec → diseño → apply/verify)?** → `sdd-video`.
- **¿Diseñas un agente con memoria/aprendizaje?** → `nas-agent-memory` (diseño propio) o `engram` (herramienta lista, MCP).
- **¿Quieres estandarizar tu entorno de terminal/Neovim?** → `gentleman-dots`.
- **¿Quieres que un LLM cree/gestione workflows de n8n?** → `n8n-mcp` (usa Kiro CLI en el NAS, no Kiro Web).
- **¿Quieres que un LLM controle el teléfono en vivo vía Tasker?** → `tasker-mcp-dceluis` (Go, ejecuta tareas). Para GENERAR XML de Tasker offline → tu propio `Tasker_mcp` (Python).
- **¿Firmware Arduino/ESP sin agentes?** → ninguna aplica; no leas esos repos.
