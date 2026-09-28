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
| [license](entries/license.md) | `LICENSE` | Términos legales de uso/copia/modificación (sin él: copyright total) | repo público que otros puedan reusar | ESTABLE |
| [gitignore](entries/gitignore.md) | `.gitignore` | Qué NO rastrea git (secretos, deps, artefactos, caches) | casi cualquier repo con código | ESTABLE |
| [editorconfig](entries/editorconfig.md) | `.editorconfig` | Indentación/charset/EOL consistentes entre editores | varios editores/colaboradores | ESTABLE |
| [agents-md](entries/agents-md.md) | `AGENTS.md` | Contexto y convenciones del repo para agentes LLM | repos donde colabora un agente LLM | ESTABLE |
| [readme](entries/readme.md) | `README.md` | Portada: qué es, instalación, uso | cualquier repo | ESTABLE |
| [makefile](entries/makefile.md) | `Makefile` | Atajos de comandos (install/test/lint/run) | proyecto con comandos repetidos | ESTABLE |
| [code-of-conduct](entries/code-of-conduct.md) | `CODE_OF_CONDUCT.md` | Normas de convivencia + a quién reportar abusos | proyecto público con comunidad | ESTABLE |
| [pre-commit](entries/pre-commit.md) | `.pre-commit-config.yaml` | Hooks automáticos antes de commitear (lint/formato/secretos) | proyecto con linters/formateadores | ESTABLE |
| [codeowners](entries/codeowners.md) | `.github/CODEOWNERS` | Revisores automáticos de PR por ruta | repo con varias áreas/equipos | ESTABLE |
| [pull-request-template](entries/pull-request-template.md) | `.github/pull_request_template.md` | Precarga la descripción de cada PR (contexto + checklist) | repo que recibe PRs | ESTABLE |
| [dockerfile](entries/dockerfile.md) | `Dockerfile` | Empaqueta el proyecto en imagen contenedor | servicio/app/MCP en Docker | ESTABLE |

## Cómo elegir (por situación)

- **¿Haces un mirror/fork de un repo ajeno?** → `upstream` (procedencia + licencia).
- **¿El repo recibirá PRs o lo toca un agente?** → `contributing`.
- **¿Usa API keys / hosts / tokens?** → `env-example` (y `.env` en `.gitignore`).
- **¿Tiene versiones/releases?** → `changelog`.
- **¿Tomas decisiones técnicas no triviales?** → `adr-decisiones` (fuente dueña:
  `nas-dotfiles/docs/ideas-decisions.md`).
- **¿Es público o expone un servicio/MCP?** → `security`.
- **¿Repo público que otros puedan reusar?** → `license` (MIT en tu ecosistema).
- **¿Cualquier repo con código?** → `gitignore` (evita subir secretos/artefactos) y `readme` (siempre).
- **¿Varios editores/colaboradores?** → `editorconfig`.
- **¿Colabora un agente LLM?** → `agents-md` (contexto y convenciones).
- **¿Comandos repetidos (test/lint/build/run)?** → `makefile`.
- **¿Proyecto público con comunidad?** → `code-of-conduct`.
- **¿Quieres calidad automática al commitear?** → `pre-commit` (lint/formato/secretos).
- **¿Varias áreas/equipos y revisión por zona?** → `codeowners`.
- **¿El repo recibe PRs?** → `pull-request-template` (+ `contributing`, `codeowners`).
- **¿Se despliega en contenedor (Docker/NAS)?** → `dockerfile`.

## Descubrir artefactos de otros repos (herramienta)

`tools/artefacto_scan.py` escanea repos de referencia (ver `tools/sources.txt`, arranca
con Prowler), compara con este catálogo y reporta qué **añadir** (`NUEVO`) o **mejorar**
(`YA_TIENES`). Con `--seed` crea fichas `BORRADOR`. Descarga los ejemplos a
`tools/_referencias/` (gitignored) como **referencia** — nunca como copia directa: la
generalización la haces tú/un LLM. Ver `tools/README.md`.
