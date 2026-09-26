# Schema de una ficha de `artefactos_proyecto`

Cada ficha (`entries/<slug>.md`) tiene frontmatter YAML + cuerpo breve. Es análogo al
de `tool_catalog`, adaptado a "tipos de archivo-artefacto de proyecto".

## Frontmatter (campos)

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `slug` | Sí | Identificador único, kebab/snake-case (= nombre de archivo sin `.md`) |
| `title` | Sí | Nombre legible del artefacto |
| `artifact` | Sí | Nombre real del archivo que se crea (ej. `UPSTREAM.md`, `.env.example`) |
| `problem` | Sí | En UNA frase: qué aporta al proyecto |
| `applies_to` | Sí | Situaciones donde SÍ conviene (ej. `["mirror/fork de repo ajeno"]`) |
| `not_for` | No | Situaciones donde NO hace falta |
| `tags` | Sí | Palabras clave para filtrar |
| `template` | No | Ruta a la plantilla lista para pegar (`templates/<archivo>`), si la hay |
| `owner_source` | No | Si el tema ya tiene una fuente dueña en el ecosistema, apuntarla (enlazar-no-duplicar) |
| `status` | Sí | Estado (ver abajo) |

## Estados (`status`)

```text
ESTABLE        # ficha + plantilla listas y usadas
BORRADOR       # ficha creada, plantilla puede faltar o estar incompleta
SOLO_REFERENCIA # se apunta a una fuente dueña externa; no hay plantilla propia
```

## Cuerpo de la ficha

- **Qué es** — 2–3 frases.
- **Cuándo SÍ aplica** — situaciones concretas.
- **Cuándo NO aplica** — para descartar rápido.
- **Cómo usarlo** — copiar `templates/<archivo>`, qué rellenar.
- **Fuente/plantilla** — enlace a la plantilla y, si existe, a la fuente dueña.

## Regla

La ficha decide *si* y *cuándo* añadir el artefacto; la plantilla (`templates/`) es el
contenido. Nunca duplicar una fuente dueña ya existente: apuntarla en `owner_source`.
