---
slug: makefile
title: Makefile — atajos de comandos del proyecto
artifact: Makefile
problem: >
  Reúne los comandos habituales (install, test, lint, run, build) tras nombres cortos y
  memorables, para no recordar invocaciones largas ni repetirlas en la doc.
applies_to:
  - proyecto con varios comandos repetidos (test/lint/build/run/deploy)
  - repos donde quieres un punto único de entrada a las tareas
not_for:
  - proyecto con un solo comando trivial
  - ecosistemas con su propio runner (npm scripts, uv, cargo) que ya bastan
tags: [makefile, make, tareas, comandos, automatizacion, dx]
template: templates/Makefile
owner_source: null
status: ESTABLE
---

# Makefile

## Qué es

Archivo con "recetas" que agrupan comandos tras nombres cortos: `make test`, `make lint`,
`make run`. Documenta y estandariza las tareas del proyecto en un solo lugar. Disponible
en cualquier Unix; en Windows requiere `make` (o WSL / Git Bash).

## Cuándo SÍ aplica

- El proyecto tiene varios comandos que repites (test, lint, build, run).
- Quieres un punto único de entrada a las tareas.

## Cuándo NO aplica

- Un solo comando trivial.
- Ya usas un runner que basta (npm scripts, `uv run`, `cargo`). En Windows puro sin make,
  valora un `tasks.ps1` o los scripts del ecosistema.

## Cómo usarlo

Copiar `templates/Makefile`, ajustar las recetas a tus comandos reales. **Ojo:** las
recetas de Make se indentan con TAB real, no espacios (el `.editorconfig` de la plantilla
ya lo contempla).

## Fuente / plantilla

- Plantilla: `templates/Makefile`
