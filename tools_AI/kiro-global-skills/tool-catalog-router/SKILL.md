---
name: tool-catalog-router
description: >
  Enruta el uso de los catálogos personales de herramientas del usuario
  (ydiaz1699/Varios_tools): tool_catalog (fichas de recursos EXTERNOS para
  decidir si vale la pena leerlos) y tools_AI (artefactos propios reutilizables:
  skills como skill-creator/unificador-skill, y recursos de diseño). Activar
  ANTES de leer un repo/recurso externo grande "por si sirve", al empezar un
  proyecto nuevo, al crear/mejorar una skill, al unificar notas, o al leer código
  de un proyecto que podría reutilizarse en el futuro (para proponer catalogarlo).
  Palabras clave: catálogo, tool_catalog, tools_AI, herramienta, recurso externo,
  ¿me sirve este repo?, skill-creator, unificar, reutilizar, agregar al catálogo.
license: MIT
metadata:
  author: ydiaz1699
  version: "1.0"
  scope: [global]
  auto_invoke:
    - "Antes de leer un repo/recurso externo grande para ver si aplica"
    - "Crear/mejorar una skill o unificar notas (usar artefactos de tools_AI)"
    - "Leer código de un proyecto reutilizable a futuro (proponer catalogarlo)"
---

# tool-catalog-router

Skill de entrada para los catálogos personales del usuario, que viven en el repo
**`ydiaz1699/Varios_tools`**:

- **`tool_catalog/`** — fichas LIGERAS de recursos **externos** (repos, videos,
  dotfiles). Sirven para **decidir si vale la pena leer la fuente completa** sin
  gastar tokens leyéndola. Enlazar, no duplicar.
- **`tools_AI/`** — **artefactos propios** completos y reutilizables: skills
  (`skill-creator`, `unificador-skill`) y recursos de diseño
  (`resources/nas-agent-memory`). Se usan/adaptan directamente.

> Ubicación: si el repo `Varios_tools` está clonado localmente, usar esa ruta.
> Si no, consultar en GitHub `ydiaz1699/Varios_tools` (leer
> `tool_catalog/catalog.json` primero; es el índice máquina).

## Regla 1 — Antes de leer un recurso externo, consultar el catálogo

Cuando vayas a leer un repo/video/herramienta externo grande "por si sirve":

1. Leer `tool_catalog/catalog.json` (índice; una entrada por recurso).
2. Filtrar por `applies_to` / `not_for` / `tags` según el PROYECTO ACTUAL.
3. Si hay ficha candidata → leer solo esa `entries/<slug>.md` y su sección
   "Cuándo SÍ / Cuándo NO aplica".
4. **Solo si aplica** → seguir `reference.url` y leer la fuente real (lo mínimo).
   Si `not_for` coincide con el proyecto actual → descartar SIN abrir el repo.

Ejemplo: en un repo de **Arduino**, `prowler-agent-skills` tiene
`not_for: [firmware Arduino]` → descartar sin leer Prowler. En un repo de **ADB +
LLM con skills**, sí aplica → entonces leer la fuente.

## Regla 2 — Usar los artefactos propios de tools_AI

Antes de reinventar, revisar si ya existe un artefacto:

| Tarea | Artefacto (`tools_AI/`) |
|---|---|
| Crear/mejorar una skill de agente LLM | `skills/skill-creator/SKILL.md` |
| Unificar/consolidar notas o fragmentos dispersos | `skills/unificador-skill/SKILL.md` |
| Diseñar memoria/auto-mejora de un agente | `resources/nas-agent-memory/` |

## Regla 3 — Al leer código reutilizable, proponer catalogarlo

Si durante una tarea lees un repo/patrón/herramienta que **podría servir en el
futuro** para otros proyectos del usuario, PROPONER (no hacerlo en silencio)
añadirlo o mejorarlo en el catálogo:

- Recurso **externo** (repo/video ajeno) → ficha en `tool_catalog/entries/`.
- Algo **propio** que el usuario quiera reutilizar → artefacto en `tools_AI/` +
  su ficha en `tool_catalog/entries/`.

Para crear/estandarizar la ficha o la skill, usar `tools_AI/skills/skill-creator`
y la plantilla `tool_catalog/_template.md`. Respetar `SCHEMA.md` (campos +
estados: `REVISADO_A_FONDO`, `REVISADO_PARCIAL`, `SOLO_REFERENCIA`, `APLICADO`,
`DESCARTADO`) y la regla del repo: enlazar, no duplicar; cada proyecto en su
subcarpeta (`Varios_tools/.kiro/steering/estructura-proyectos.md`).

Preguntar antes de escribir: qué recurso, si es externo o propio, y a qué
proyectos aplicaría (`applies_to`).

## Qué NO hacer

- No leer un repo externo completo sin antes mirar su ficha (si existe).
- No duplicar en una ficha el contenido del recurso: la ficha solo enlaza.
- No crear archivos sueltos en la raíz de `Varios_tools` (regla de estructura).
