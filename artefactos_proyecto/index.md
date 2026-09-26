# Índice de artefactos_proyecto

Una línea por artefacto. Lee esto primero; abre solo la ficha (`entries/<slug>.md`)
que encaje con la situación de tu proyecto actual; copia la plantilla de `templates/`
solo si aplica.

| Slug | Archivo | Qué aporta | Cuándo aplica | Estado |
|------|---------|-----------|---------------|--------|
| [upstream](entries/upstream.md) | `UPSTREAM.md` | Procedencia de un mirror/fork (fuente, autor, licencia, commit, motivo) | mirror/fork de repo ajeno, vendoring | ESTABLE |
| [contributing](entries/contributing.md) | `CONTRIBUTING.md` | Convenciones para contribuir (ramas, commits, tests, PRs) | repo que recibe PRs o lo toca un agente LLM | ESTABLE |
| [env-example](entries/env-example.md) | `.env.example` | Lista las variables de entorno sin valores reales | proyecto que usa secretos/config por entorno | ESTABLE |
| [changelog](entries/changelog.md) | `CHANGELOG.md` | Historial de cambios por versión | proyecto con versiones/releases | ESTABLE |
| [adr-decisiones](entries/adr-decisiones.md) | `docs/ideas-decisions.md` | Registro del POR QUÉ de las decisiones técnicas | decisiones de diseño que querrás recordar | ESTABLE |
| [security](entries/security.md) | `SECURITY.md` | Cómo reportar vulnerabilidades en privado + versiones soportadas | proyecto público / servicio expuesto | ESTABLE |

## Cómo elegir (por situación)

- **¿Haces un mirror/fork de un repo ajeno?** → `upstream` (procedencia + licencia).
- **¿El repo recibirá PRs o lo toca un agente?** → `contributing`.
- **¿Usa API keys / hosts / tokens?** → `env-example` (y `.env` en `.gitignore`).
- **¿Tiene versiones/releases?** → `changelog`.
- **¿Tomas decisiones técnicas no triviales?** → `adr-decisiones` (fuente dueña:
  `nas-dotfiles/docs/ideas-decisions.md`).
- **¿Es público o expone un servicio/MCP?** → `security`.
