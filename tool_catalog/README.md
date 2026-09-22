# tool_catalog — catálogo de recursos y herramientas externas

Fichas **ligeras** de repos, herramientas, videos y patrones externos, para
**decidir si vale la pena leer la fuente completa** antes de gastar tokens/tiempo
en ello.

## El problema que resuelve

Cuando descubres un recurso útil (un repo como Prowler, un video, unos dotfiles),
la única forma de saber si sirve para tu proyecto actual es leerlo entero. Eso:

- gasta muchos tokens y tiempo cada vez que lo reconsideras;
- te obliga a re-explicar el recurso en cada chat nuevo;
- puede ser **innecesario** (ej.: estás en un repo de Arduino y Prowler no aplica).

**La idea (como en el video):** en vez de pasar la transcripción completa o el
repo entero, guardas una **ficha** con la *idea central*, *qué problema resuelve*
y la *referencia*. El LLM lee la ficha (barata), decide si aplica a tu repo
actual, y **solo si aplica** va a leer la fuente completa.

```text
Recurso externo (repo/video/tool)
        ↓  (una vez)
FICHA ligera: idea central + problema + cuándo aplica + referencia
        ↓  (en cada proyecto futuro)
El LLM lee la ficha → ¿aplica a ESTE repo? → NO: descartar sin leer el repo
                                            → SÍ: recién ahí leer la fuente
```

## Cuándo usar este catálogo

- **Antes** de leer un repo/recurso externo grande "por si sirve".
- Al arrancar un proyecto nuevo: escanear el catálogo para ver qué patrones ya
  conocidos aplican.
- Cuando quieras compartir un recurso con un LLM sin pegar el repo completo:
  le pasas la ficha.

## Cómo lo usa un LLM (flujo de decisión)

1. Leer `index.md` (o `catalog.json`) — lista de una línea por ficha.
2. Filtrar por `applies_to` / `tags` según el proyecto actual.
3. Leer solo la(s) ficha(s) candidata(s) en `entries/<slug>.md`.
4. Revisar la sección **"Cuándo SÍ / Cuándo NO aplica"** de la ficha.
5. Si aplica → seguir `reference.url` para leer la fuente real (y solo lo
   necesario). Si no aplica → descartar sin abrir el repo.

> Ejemplo real: en un repo de **Arduino**, el LLM lee el índice, ve que
> `prowler-agent-skills` tiene `applies_to: [proyectos con .kiro/skills, agentes
> LLM]` → **no aplica**, lo descarta sin leer Prowler. En un repo de **ADB +
> LLM con skills**, la misma ficha **sí aplica** → entonces (y solo entonces)
> lee el repo de Prowler.

## Estructura

```text
tool_catalog/
├── README.md              ← este archivo
├── index.md               ← índice humano (una línea por ficha)
├── catalog.json           ← índice máquina (para búsqueda/filtrado)
├── _template.md           ← plantilla de ficha
├── SCHEMA.md              ← campos y estados permitidos
└── entries/
    ├── gentleman-programming/        ← agrupadas por fuente/ecosistema
    │   ├── prowler-agent-skills.md
    │   ├── agents-skills-video.md
    │   └── gentleman-dots.md
    ├── skill-creator.md              ← artefactos propios (sin agrupar)
    ├── unificador-skill.md
    └── nas-agent-memory.md
```

> Las fichas pueden ir sueltas en `entries/` o agrupadas en una subcarpeta por
> **fuente/ecosistema** (ej. `entries/gentleman-programming/`) cuando varios
> recursos vienen del mismo autor o del mismo descubrimiento. El `file` de cada
> entrada en `catalog.json` refleja la ruta real; `index.md` puede agruparlas.

## Regla de oro (igual que en el resto del repo)

Enlazar, **no duplicar**. La ficha NO copia el repo ni la documentación: captura
la idea central y **apunta** a la fuente. Si necesitas el detalle, la ficha te
lleva ahí. La ficha es *contexto para decidir*, no una copia de la fuente.

## Añadir una ficha nueva

1. Copiar `_template.md` a `entries/<slug>.md` (o
   `entries/<fuente>/<slug>.md` si agrupas por fuente/ecosistema) y rellenarlo.
2. Añadir una línea en `index.md` y una entrada en `catalog.json` (el campo
   `file` debe apuntar a la ruta real, incluida la subcarpeta si la hay).
3. Mantener la ficha corta (idealmente < 60 líneas): idea + problema + cuándo
   aplica + referencia. El detalle vive en la fuente enlazada.
