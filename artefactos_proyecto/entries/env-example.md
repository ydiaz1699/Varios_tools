---
slug: env-example
title: .env.example — plantilla de variables de entorno
artifact: .env.example
problem: >
  Documenta qué variables de entorno necesita el proyecto (sin valores reales) para que
  cualquiera pueda arrancarlo sin filtrar secretos.
applies_to:
  - proyecto que lee configuración/secretos de variables de entorno
  - servicios Docker, MCP servers, apps con API keys/tokens
  - repos donde .env está en .gitignore (siempre debería estarlo)
not_for:
  - proyectos sin ninguna configuración por entorno
tags: [env, secretos, configuracion, dotenv, seguridad]
template: templates/env.example
owner_source: null
status: ESTABLE
---

# .env.example

## Qué es

Un archivo versionado que **lista las variables** que el proyecto espera, con
placeholders en vez de valores reales. El `.env` real va en `.gitignore`; el
`.env.example` es la referencia para saber qué rellenar.

## Cuándo SÍ aplica

- El proyecto usa variables de entorno (API keys, hosts, tokens, puertos).
- Hay un `.env` ignorado por git.

## Cuándo NO aplica

- El proyecto no tiene configuración por entorno.

## Cómo usarlo

Copiar `templates/env.example` a `.env.example`, listar cada variable con un
placeholder EN MAYÚSCULAS y un comentario de qué es. **Nunca** poner valores reales.
Asegurar que `.env` esté en `.gitignore`.

## Fuente / plantilla

- Plantilla: `templates/env.example`
- Nota del ecosistema: en nas-dotfiles el patrón es `.env.example` con `__pega_aqui__`
  como placeholder; aquí se usa MAYÚSCULAS + `CAMBIAR` para que sea obvio.
