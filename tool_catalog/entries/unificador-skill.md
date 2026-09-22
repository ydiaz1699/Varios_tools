---
slug: unificador-skill
title: unificador-skill — consolida fragmentos dispersos en una guía coherente
type: tool
problem: >
  Unir notas/diagnósticos/conversaciones dispersas en un solo documento de
  ejecución paso a paso, sin resumir código ni inventar, deduplicando y
  respetando el orden real de ejecución.
applies_to:
  - consolidar múltiples fragmentos de un mismo tema en una guía
  - convertir notas sueltas o handoffs en un documento autocontenido
not_for:
  - redactar desde cero sin fragmentos fuente
tags: [unificar, consolidar, documentacion, guia, deduplicar, drafts]
reference:
  url: tools_AI/skills/unificador-skill/SKILL.md
  kind: web
related:
  - "Meta-prompt equivalente en nas-dotfiles: docs/meta-prompt-unificar.md"
status: REVISADO_A_FONDO
evaluated_on: 2026-09-22
---

# unificador-skill (artefacto propio en tools_AI)

## Idea central

Unifica fragmentos dispersos en una guía de ejecución coherente con 5 reglas
no-negociables: NO resumir (código/configs íntegros), NO inventar (huecos →
"⚠️ PENDIENTE"), deduplicar (N versiones → la más completa), orden de ejecución
real (mkdir → archivos → permisos → levantar → verificar), y documento
autocontenido (no referenciar los fragmentos originales).

## Qué problema resuelve

Evita perder comandos/configs al consolidar, y evita guías incoherentes con
pasos en orden imposible (ej. chmod antes del mkdir).

## Cuándo SÍ aplica

- Tienes varias notas/diagnósticos de un tema y quieres UNA guía.

## Cuándo NO aplica

- No hay fragmentos fuente que unificar.

## Qué llevarte si aplica

- `SKILL.md` (reglas + workflow) y `references/{formato, mejoras}.md`.

## Referencia

- Artefacto: `tools_AI/skills/unificador-skill/` (vive íntegro en este repo).
