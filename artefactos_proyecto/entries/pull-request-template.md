---
slug: pull-request-template
title: pull_request_template.md — plantilla de descripción de PR
artifact: .github/pull_request_template.md
problem: >
  Precarga la descripción de cada PR con secciones y checklist, para que quien abre un PR
  no olvide contexto, pasos de revisión ni comprobaciones.
applies_to:
  - repo que recibe PRs (de humanos o de agentes)
  - proyecto donde quieres PRs consistentes y revisables
not_for:
  - repo de un solo autor que no usa PRs
tags: [pull-request, pr, template, github, revision, checklist]
template: templates/pull_request_template.md
owner_source: null
status: ESTABLE
---

# pull_request_template.md

## Qué es

Archivo (`.github/pull_request_template.md`) que GitHub usa para **precargar el cuerpo**
de cada PR nuevo: contexto, descripción, pasos de revisión y checklist. Estandariza la
información y reduce idas y vueltas. Prowler tiene una versión extensa; aquí va una
genérica y corta.

## Cuándo SÍ aplica

- El repo recibe PRs y quieres que lleguen con contexto y checklist.

## Cuándo NO aplica

- Repo de un solo autor sin PRs.

## Cómo usarlo

Copiar `templates/pull_request_template.md` a `.github/pull_request_template.md` y ajustar
el checklist a tu flujo (tests, docs, changelog). Quitar lo específico de tu proyecto.

## Fuente / plantilla

- Plantilla: `templates/pull_request_template.md`
- Se empareja bien con `contributing` y `codeowners`.
