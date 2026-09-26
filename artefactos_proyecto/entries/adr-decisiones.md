---
slug: adr-decisiones
title: ADR / registro de decisiones (ideas-decisions.md)
artifact: docs/ideas-decisions.md
problem: >
  Registra POR QUÉ se tomó cada decisión técnica (problema, idea, proceso, alternativas
  descartadas, aprendizaje) para que un LLM futuro no repita caminos ya evaluados.
applies_to:
  - proyecto donde se toman decisiones técnicas que querrás recordar
  - repos con agentes LLM que deben conocer el "por qué" de las cosas
  - frameworks que evolucionan y acumulan lecciones
not_for:
  - scripts triviales sin decisiones de diseño
tags: [adr, decisiones, ideas-decisions, aprendizajes, contexto, arquitectura]
template: templates/ideas-decisions.md
owner_source: "nas-dotfiles/docs/ideas-decisions.md (fuente dueña del patrón en el ecosistema)"
status: ESTABLE
---

# ADR / registro de decisiones

## Qué es

Un documento vivo que registra decisiones técnicas con su contexto: **Problema → Idea
→ Proceso → Decisión → Alternativas descartadas → Aprendizaje**. Es la versión ligera de
un ADR (Architecture Decision Record). Evita que un LLM (o tú) repita un camino ya
evaluado y descartado.

## Cuándo SÍ aplica

- Tomas decisiones de diseño que querrás justificar más adelante.
- Un agente LLM trabaja en el repo y necesita el "por qué", no solo el "qué".

## Cuándo NO aplica

- Scripts triviales sin decisiones de arquitectura.

## Cómo usarlo

Copiar `templates/ideas-decisions.md` a `docs/`. Añadir una entrada numerada cada vez que
se resuelve un problema no trivial. En nas-dotfiles ya es una regla del framework.

## Fuente / plantilla

- Plantilla: `templates/ideas-decisions.md`
- **Fuente dueña en tu ecosistema:** `nas-dotfiles/docs/ideas-decisions.md` (no duplicar:
  ahí está la versión real y su plantilla; esta ficha solo la generaliza para otros repos).
