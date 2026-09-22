---
name: NOMBRE-KEBAB-CASE
description: >
  QUÉ HACE en 1–2 frases (tercera persona) + CUÁNDO activarla (triggers/keywords)
  + si aplica, qué NO cubre y a qué skill ir en su lugar. ≤1024 chars, sin < >.
license: MIT
metadata:
  author: TU_USUARIO
  version: "1.0"
  scope: [SCOPE]           # dominio/AGENTS.md al que pertenece (opcional pero recomendado)
  auto_invoke:
    - "ACCIÓN concreta del usuario que debe disparar esta skill"
    # - "otra acción (opcional)"
---

# NOMBRE

Una frase de propósito. Si hay una guía/fuente dueña, enlazarla y NO duplicarla.

## Cuándo usar

- BULLET de cuándo activar.

## Reglas / workflow (lo propio de la skill)

Reglas SIEMPRE/NUNCA primero (con el porqué), luego el flujo. Ejemplos mínimos.
El detalle largo va en `references/`, no aquí. Body ≤150–200 líneas.

## Referencias (opcional)

- `references/DETALLE.md` — se carga on-demand.
- `assets/PLANTILLA.md` — recurso que el LLM copia/ejecuta.

<!--
CHECKLIST (borrar antes de publicar):
[ ] Frontmatter parsea (YAML); name kebab-case; description ≤1024 chars sin < >
[ ] Body ≤200 líneas; detalle movido a references/
[ ] Si el proyecto usa auto-invoke: metadata.scope + auto_invoke y fila en AGENTS.md
[ ] No duplica fuentes dueñas (enlaza)
[ ] Si se versiona en Kiro: revisar .gitignore (.kiro/skills/* suele estar ignorado)
-->
