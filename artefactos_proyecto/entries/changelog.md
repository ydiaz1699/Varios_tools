---
slug: changelog
title: CHANGELOG.md — historial de cambios
artifact: CHANGELOG.md
problem: >
  Registra los cambios relevantes por versión para que un usuario (o un LLM) sepa qué
  cambió sin leer todo el historial de git.
applies_to:
  - proyecto con versiones/releases
  - librería o herramienta que otros consumen
  - firmware/app donde importa saber qué cambió entre versiones
not_for:
  - repos experimentales sin releases
  - proyectos donde el historial de commits ya basta
tags: [changelog, versiones, releases, keepachangelog, semver]
template: templates/CHANGELOG.md
owner_source: null
status: ESTABLE
---

# CHANGELOG.md

## Qué es

Archivo que resume, por versión, qué se **añadió/cambió/arregló/eliminó**. Sigue el
formato de [Keep a Changelog](https://keepachangelog.com) y suele emparejarse con
versionado semántico (SemVer). Es legible por humanos y por LLMs.

## Cuándo SÍ aplica

- El proyecto tiene versiones o releases.
- Otros consumen la herramienta/librería y necesitan saber qué cambió.

## Cuándo NO aplica

- Repo sin releases; el log de git ya cubre.

## Cómo usarlo

Copiar `templates/CHANGELOG.md`. Mantener una sección `[No publicado]` arriba e ir
moviendo entradas a una versión al hacer release. Agrupar en Added/Changed/Fixed/Removed.

## Fuente / plantilla

- Plantilla: `templates/CHANGELOG.md`
- Referencia: https://keepachangelog.com
