# Schema de una ficha de `tool_catalog`

Cada ficha (`entries/<slug>.md`) tiene frontmatter YAML + cuerpo breve.

## Frontmatter (campos)

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `slug` | Sí | Identificador único, snake/kebab-case (= nombre de archivo sin `.md`) |
| `title` | Sí | Nombre legible del recurso |
| `type` | Sí | Tipo de recurso: `repo` \| `video` \| `dotfiles` \| `tool` \| `article` \| `pattern` |
| `origin` | Sí (en catalog.json) | `external` (fuente a leer si aplica) \| `local` (artefacto propio en `../tools_AI/`) |
| `problem` | Sí | En UNA frase: qué problema resuelve (para filtrar rápido) |
| `applies_to` | Sí | Lista de contextos donde SÍ aplica (ej. `["proyectos con .kiro/skills", "agentes LLM"]`) |
| `not_for` | No | Lista de contextos donde NO aplica (ej. `["firmware arduino", "proyectos sin agentes"]`) |
| `tags` | Sí | Palabras clave para búsqueda (`agent-skills`, `dotfiles`, `docker`, ...) |
| `reference` | Sí | `{ url, kind }` — la fuente real a leer si aplica. `kind`: `github` \| `youtube` \| `web` |
| `related` | No | Lista de enlaces relacionados, formato normalizado (ver abajo) |
| `status` | Sí | Estado de evaluación (ver abajo) |
| `evaluated_on` | No | Fecha en que se revisó la fuente por última vez |

## Formato de `related` (normalizado)

Cada item es un string `"Etiqueta — destino"`, con un guion largo (`—`) separando
la etiqueta del destino. El destino es **una sola** URL o ruta, para que sea
parseable y navegable:

- **Ruta interna** del repo → relativa a la raíz de `Varios_tools`
  (ej. `tools_AI/skills/skill-creator/references/prowler-case-study.md`).
- **URL externa** → completa con `https://`.

Ejemplos:

```yaml
related:
  - "Conocimiento destilado — tools_AI/skills/skill-creator/references/prowler-case-study.md"
  - "Video (fuente) — https://www.youtube.com/watch?v=Nvn6s3r9ZAw"
  - "Ficha del video — entries/gentleman-programming/agents-skills-video.md"
```

Reglas:
- Una etiqueta corta + `—` + un único destino. No mezclar dos destinos en un item.
- Las rutas internas se escriben desde la raíz del repo (sin `../`), para que se
  entiendan igual desde cualquier ficha.
- Notas SIN destino (ej. "Mismo autor que X") van igual con etiqueta, pero
  apuntando a la ficha/recurso concreto en vez de texto suelto.

## Estados (`status`)

Reflejan cuánto se ha verificado el recurso, en el espíritu de `codigo_tools`:

```text
REVISADO_A_FONDO     # se leyó la fuente completa y la ficha refleja su idea real
REVISADO_PARCIAL     # se leyó parte (README, sección clave); idea central capturada
SOLO_REFERENCIA      # aún no se ha leído; ficha creada desde descripción externa
APLICADO             # ya se usó/adaptó en algún proyecto propio (ver `related`)
DESCARTADO           # evaluado y decidido que no es útil (se conserva para no re-evaluar)
```

## Regla

La ficha es *contexto para decidir si leer la fuente*, no una copia de la fuente.
Nunca pegar el repo, la transcripción o la documentación completa: capturar la
idea central y **enlazar**. Si la fuente cambia, actualizar `evaluated_on` y, si
hace falta, la idea central.
