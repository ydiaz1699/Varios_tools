---
slug: agents-md
title: AGENTS.md — contexto e instrucciones para agentes LLM
artifact: AGENTS.md
problem: >
  Da a cualquier agente LLM (Kiro, Claude, etc.) el contexto y las convenciones del repo
  en un solo archivo, para que no improvise ni desconozca las reglas del proyecto.
applies_to:
  - repos donde un agente LLM colabora (Kiro Web/CLI, Claude, Cursor)
  - proyectos con convenciones o arquitectura que el agente debe respetar
  - frameworks con muchas reglas (dónde va cada cosa, cómo build/test)
not_for:
  - repos sin agentes LLM (aunque un README ya cubre a humanos)
tags: [agents-md, llm, contexto, kiro, convenciones, agentes]
template: templates/AGENTS.md
owner_source: "nas-dotfiles/AGENTS.md y repo-index/AGENTS.md (ejemplos reales en el ecosistema)"
status: ESTABLE
---

# AGENTS.md

## Qué es

Archivo (raíz) pensado para **agentes LLM**: resume qué es el proyecto, sus convenciones,
dónde vive cada cosa y cómo enrutar tareas. Formato abierto que leen Kiro, Claude y otros.
En tu ecosistema ya lo usan `nas-dotfiles` y `repo-index` (con tabla de enrutado).

## Cuándo SÍ aplica

- Un agente LLM trabaja en el repo y debe respetar convenciones.
- El proyecto tiene reglas/arquitectura no obvias.

## Cuándo NO aplica

- Repo sin agentes (el README cubre a humanos).

## Cómo usarlo

Copiar `templates/AGENTS.md`, rellenar: qué es, reglas clave, dónde está cada cosa, cómo
build/test, y (opcional) una tabla "si el usuario pide X → consulta Y". Mantenerlo breve;
enlazar a docs en vez de duplicarlas.

## Fuente / plantilla

- Plantilla: `templates/AGENTS.md`
- **Ejemplos reales:** `nas-dotfiles/AGENTS.md`, `repo-index/AGENTS.md` (tabla-veredicto).
- Estándar: https://agents.md
