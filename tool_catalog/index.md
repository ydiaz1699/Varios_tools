# Índice de tool_catalog

Una línea por ficha. Lee esto primero; abre solo la ficha (`entries/<slug>.md`)
que encaje con tu proyecto actual; lee la fuente completa solo si la ficha dice
que aplica.

### Recursos externos (fuentes a leer si aplican)

| Slug | Tipo | Problema que resuelve | Aplica a | Estado |
|------|------|-----------------------|----------|--------|
| [prowler-agent-skills](entries/prowler-agent-skills.md) | repo | Contexto para LLM en 3 niveles (AGENTS.md + skills por trigger + auto-invoke) | proyectos con .kiro/skills, agentes LLM | APLICADO |
| [gentleman-agents-skills-video](entries/gentleman-agents-skills-video.md) | video | Arquitectura AGENTS.md + skills + auto-invoke + subagentes (sin releer la transcripción) | diseñar contexto de agentes, dividir AGENTS.md, subagentes | REVISADO_A_FONDO |
| [gentleman-dots](entries/gentleman-dots.md) | dotfiles | Entorno de desarrollo completo (Neovim/shells/terminales) + capa IA; ejemplo de 1 AGENTS.md + orquestador SDD/subagentes | montar entorno terminal/Neovim, capa IA multi-CLI, ver subagentes aplicados | REVISADO_A_FONDO |

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
- **¿Diseñas un agente con memoria/aprendizaje?** → `nas-agent-memory`.
- **¿Quieres estandarizar tu entorno de terminal/Neovim?** → `gentleman-dots`.
- **¿Firmware Arduino/ESP sin agentes?** → ninguna aplica; no leas esos repos.
