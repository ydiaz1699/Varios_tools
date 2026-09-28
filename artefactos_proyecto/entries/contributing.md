---
slug: contributing
title: CONTRIBUTING.md — cómo contribuir al proyecto
artifact: CONTRIBUTING.md
problem: >
  Define las convenciones para contribuir (ramas, commits, tests, estilo de PR) para
  que colaboradores —humanos o agentes LLM— sigan las mismas reglas.
applies_to:
  - repo que va a recibir PRs (de otros o de un agente LLM)
  - proyecto con convenciones repetidas (ramas, commits, linters)
  - repos donde un agente Kiro/Claude colabora y debe respetar el flujo
not_for:
  - scripts personales de un solo uso sin colaboración
  - repos privados de notas sueltas
tags: [contributing, pr, ramas, commits, convenciones, colaboracion]
template: templates/CONTRIBUTING.md
owner_source: null
status: ESTABLE
---

# CONTRIBUTING.md

## Qué es

Documento en la raíz (o `.github/`) que explica cómo contribuir: naming de ramas,
formato de commits, cómo abrir un PR, qué tests/linters correr, y a qué rama apuntan
los PRs. Los agentes LLM (y este entorno) lo leen para respetar el flujo del repo.

## Cuándo SÍ aplica

- El repo recibirá PRs o lo tocará un agente LLM.
- Hay convenciones que se repiten y conviene fijar.

## Cuándo NO aplica

- Proyecto de un solo autor sin PRs ni agentes.

## Cómo usarlo

Copiar `templates/CONTRIBUTING.md`, ajustar el flujo real del repo (rama base, formato
de commits, comandos de test/lint). Mantenerlo corto y accionable.

## Fuente / plantilla

- Plantilla: `templates/CONTRIBUTING.md`
- Nota: este entorno (Kiro) lee `CONTRIBUTING.md` para seguir las convenciones del repo.
