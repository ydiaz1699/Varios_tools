# Changelog — SAG_SDK

Cambios relevantes en la skill. Formato: fecha + qué se tocó.

---

## 2026-07-31

### Agregado
- **Arquitectura Thinking + Bloques Dinámicos**: THINKING.md como entry point, 17 bloques modulares en blocks/
- **blocks/production/testing.md**: testear agentes sin LLM (core layer, mocks, clasificación)
- **blocks/production/deployment.md**: correr agente en producción (systemd, cron, Docker)
- **CHANGELOG.md**: este archivo

### Corregido
- **Tabla de modelos Gemini** actualizada con datos verificados del panel real (jul 2026)
- **Advertencia de caducidad** en THINKING.md regla 7 y en cada tabla de modelos
- **Bug de merge** en blocks/python/gemini.md (filas huérfanas eliminadas)
- **README.md duplicado** — eliminadas secciones "Cobertura" y "Cómo usarlo" repetidas
- **Skill monolítica** sincronizada con bloques (tabla Gemini)

### Deprecado
- `.kiro/skills/strands-gemini-integration.md` — marcado como deprecado, fuente de verdad son los blocks/

---

## 2026-07-28

### Agregado
- **PARTE 4: Patrones de producción** en la skill monolítica
- Credenciales (3 capas), sesión persistente, modo ejecutivo, core layer, ToolResult, 8 errores comunes
- Ejemplos: `nas-agent-pattern.py`, `iot-bridge-agent.ts`, `telegram-bot-agent.ts`
- `prompts/analyze-chat.md` para extraer patrones de conversaciones

### Inicial
- PARTE 1 (Python), PARTE 2 (TypeScript), PARTE 3 (Integración)
- 7 ejemplos funcionales
- Skill monolítica completa (1182 líneas)
