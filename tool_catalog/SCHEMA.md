# Schema de una ficha de `tool_catalog`

Cada ficha (`entries/<slug>.md`) tiene frontmatter YAML + cuerpo breve.

## Frontmatter (campos)

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `slug` | Sí | Identificador único, snake/kebab-case (= nombre de archivo sin `.md`) |
| `title` | Sí | Nombre legible del recurso |
| `type` | Sí | Tipo de recurso: `repo` \| `video` \| `dotfiles` \| `tool` \| `article` \| `pattern` |
| `problem` | Sí | En UNA frase: qué problema resuelve (para filtrar rápido) |
| `applies_to` | Sí | Lista de contextos donde SÍ aplica (ej. `["proyectos con .kiro/skills", "agentes LLM"]`) |
| `not_for` | No | Lista de contextos donde NO aplica (ej. `["firmware arduino", "proyectos sin agentes"]`) |
| `tags` | Sí | Palabras clave para búsqueda (`agent-skills`, `dotfiles`, `docker`, ...) |
| `reference` | Sí | `{ url, kind }` — la fuente real a leer si aplica. `kind`: `github` \| `youtube` \| `web` |
| `related` | No | Otras fichas o rutas locales relacionadas |
| `status` | Sí | Estado de evaluación (ver abajo) |
| `evaluated_on` | No | Fecha en que se revisó la fuente por última vez |

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
