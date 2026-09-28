---
slug: pre-commit
title: .pre-commit-config.yaml — hooks automáticos antes de commitear
artifact: .pre-commit-config.yaml
problem: >
  Corre validadores/formateadores/linters automáticamente antes de cada commit, para no
  subir código mal formateado, secretos o archivos rotos.
applies_to:
  - proyecto con linters/formateadores (Python, JS, YAML, etc.)
  - repos donde quieres calidad consistente sin depender de recordarlo
  - equipos/agentes que commitean a menudo
not_for:
  - repo trivial de un solo archivo
  - quien no quiera instalar el framework pre-commit
tags: [pre-commit, hooks, lint, formato, calidad, git]
template: templates/pre-commit-config.yaml
owner_source: null
status: ESTABLE
---

# .pre-commit-config.yaml

## Qué es

Config del framework [pre-commit](https://pre-commit.com): define "hooks" que se ejecutan
automáticamente al hacer `git commit` (arreglar espacios, validar YAML/JSON, formatear,
lint, detectar secretos). Se instala con `pre-commit install`. Prowler lo usa con tiers
de prioridad; aquí va una versión mínima y genérica.

## Cuándo SÍ aplica

- El proyecto tiene formateadores/linters y quieres aplicarlos sin olvidarte.
- Commits frecuentes (equipo o agente).

## Cuándo NO aplica

- Repo trivial; o no quieres depender del framework pre-commit.

## Cómo usarlo

Copiar `templates/pre-commit-config.yaml` a `.pre-commit-config.yaml`, ajustar los hooks a
tus lenguajes, y `pre-commit install`. Descomenta los bloques de Python/JS según uses.

## Fuente / plantilla

- Plantilla: `templates/pre-commit-config.yaml`
- Framework: https://pre-commit.com — hooks básicos: https://github.com/pre-commit/pre-commit-hooks
