# Índice de tool_catalog

Una línea por ficha. Lee esto primero; abre solo la ficha (`entries/<slug>.md`)
que encaje con tu proyecto actual; lee la fuente completa solo si la ficha dice
que aplica.

| Slug | Tipo | Problema que resuelve | Aplica a | Estado |
|------|------|-----------------------|----------|--------|
| [prowler-agent-skills](entries/prowler-agent-skills.md) | repo | Contexto para LLM en 3 niveles (AGENTS.md + skills por trigger + auto-invoke) | proyectos con .kiro/skills, agentes LLM | APLICADO |
| [gentleman-dots](entries/gentleman-dots.md) | dotfiles | Entorno de desarrollo completo (Neovim/shells/terminales) + capa de IA opcional | montar entorno terminal/Neovim, capa IA multi-CLI | REVISADO_PARCIAL |

## Cómo elegir

- **¿Tu repo usa agentes/LLM con skills?** → mira `prowler-agent-skills`.
- **¿Quieres estandarizar tu entorno de terminal/Neovim?** → mira `gentleman-dots`.
- **¿Firmware Arduino/ESP sin agentes?** → ninguna aplica; no leas esos repos.
