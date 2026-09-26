---
name: artefactos-proyecto
description: >-
  Cataloga los archivos-artefacto estándar de un proyecto (UPSTREAM.md, CONTRIBUTING.md,
  .env.example, CHANGELOG.md, ADR/ideas-decisions.md, SECURITY.md) con "cuándo SÍ/NO
  aplica" y plantilla lista. Actívala ANTES de: crear/ordenar un repo, hacer un
  mirror/fork de un repo ajeno, abrir un proyecto a colaboradores, o cuando un proyecto
  usa secretos/tiene releases/toma decisiones técnicas — para no OLVIDAR qué archivo
  conviene añadir. NO cubre recursos externos (repos/videos → tool_catalog) ni el índice
  de tus repos (→ repo-index); esta trata de TIPOS DE ARCHIVO dentro de un proyecto.
license: MIT
metadata:
  author: ydiaz1699
  version: 1.0.0
  scope: project-artifacts
  auto_invoke:
    - "crear o inicializar un repo/proyecto nuevo"
    - "hacer un mirror o fork de un repo ajeno"
    - "abrir el proyecto a colaboradores / va a recibir PRs"
    - "el proyecto usa secretos o variables de entorno"
    - "el proyecto tiene versiones/releases o toma decisiones técnicas"
---

# Skill: artefactos-proyecto

## Qué hace

Ayuda a **no olvidar** qué archivo-artefacto estándar conviene añadir a un proyecto,
según su situación, y provee la **plantilla lista**. Es un índice consultable, igual
que `tool_catalog` (recursos externos) o `repo-index` (tus repos), pero para
**tipos de archivo dentro de un proyecto**.

## Cuándo activarla (triggers)

Antes de actuar, si la situación encaja con alguna de estas, consulta el catálogo:

| Situación | Artefacto a considerar |
|-----------|------------------------|
| Mirror/fork de un repo ajeno, vendoring | `UPSTREAM.md` (procedencia + licencia) |
| El repo recibirá PRs o lo toca un agente | `CONTRIBUTING.md` |
| Usa API keys / hosts / tokens | `.env.example` (+ `.env` en `.gitignore`) |
| Tiene versiones/releases | `CHANGELOG.md` |
| Decisiones técnicas que querrás recordar | `docs/ideas-decisions.md` (ADR) |
| Proyecto público / servicio o MCP expuesto | `SECURITY.md` |

## Cómo usarla

1. Lee `artefactos_proyecto/index.md` (o `catalog.json`) — una línea por artefacto.
2. Filtra por `applies_to` según la situación del proyecto actual.
3. Abre la ficha `entries/<slug>.md` candidata y revisa "Cuándo SÍ / NO aplica".
4. Si aplica, copia la plantilla de `artefactos_proyecto/templates/<archivo>` y adáptala
   (rellena los placeholders en MAYÚSCULAS).

## Frontera (qué NO cubre)

- **Recursos externos** (repos, videos, dotfiles a evaluar) → usa `tool_catalog`.
- **Índice de tus repos** (qué repo existe y de qué trata) → usa `repo-index`.
- **Recrear artefactos documentales desde `_drafts`** → usa `codigo_tools`.

## Regla

Enlazar-no-duplicar: si un artefacto ya tiene fuente dueña en el ecosistema (ej.
`nas-dotfiles/docs/ideas-decisions.md` para las decisiones), la ficha apunta ahí; no se
copia. Las plantillas son genéricas, sin datos de un proyecto concreto.
