---
slug: gitignore
title: .gitignore — archivos que git NO debe rastrear
artifact: .gitignore
problem: >
  Evita commitear artefactos generados, dependencias, secretos y caches; sin él acabas
  subiendo .env, node_modules, venvs o binarios por accidente.
applies_to:
  - prácticamente cualquier repo con código
  - proyectos con .env, venv/node_modules, artefactos de build
  - repos con .kiro/ donde skills/steering se ignoran por defecto
not_for:
  - repos de solo-documentación muy simples (aun así suele convenir)
tags: [gitignore, git, secretos, artefactos, kiro, venv]
template: templates/gitignore
owner_source: null
status: ESTABLE
---

# .gitignore

## Qué es

Lista de patrones de archivos/carpetas que git ignora. Protege de subir secretos
(`.env`), dependencias (`node_modules/`, `.venv/`), caches y artefactos generados.

## Cuándo SÍ aplica

- Casi cualquier repo con código.
- El proyecto tiene `.env`, entornos virtuales, o build artifacts.

## Cuándo NO aplica

- Repos triviales de solo texto (aun así, no estorba).

## Cómo usarlo

Copiar `templates/gitignore` a `.gitignore` y ajustar por lenguaje. **Aviso de tu
ecosistema:** en repos con `.kiro/`, tanto `.kiro/skills/*` como `.kiro/steering/*`
suelen ignorarse por defecto → cada archivo que quieras versionar necesita una
**excepción explícita** (`!.kiro/skills/<n>/` + `!.kiro/skills/<n>/SKILL.md`). La
plantilla incluye ese patrón comentado.

## Fuente / plantilla

- Plantilla: `templates/gitignore`
- Referencia por lenguaje: https://github.com/github/gitignore
