# artefactos_proyecto — catálogo de archivos-artefacto estándar de un proyecto

Fichas **ligeras** de los archivos/documentos que un proyecto suele necesitar
(`UPSTREAM.md`, `CONTRIBUTING.md`, `.env.example`, `CHANGELOG.md`, ADR/decisiones,
`SECURITY.md`, …), para **acordarse de que existen en el momento oportuno** y tener
una **plantilla lista** para pegar.

## El problema que resuelve

No es difícil *crear* un `UPSTREAM.md` o un `CONTRIBUTING.md`; el problema es
**acordarse de que existen** cuando toca (al crear un repo, al hacer un mirror, al
abrir el proyecto a colaboradores…). Igual que `tool_catalog` evita re-leer repos
externos y `repo-index` evita re-descubrir tus repos, este catálogo evita **olvidar
qué archivos-artefacto podrían mejorar un proyecto**.

```text
Situación del proyecto (mirror / va a recibir PRs / usa secretos / …)
        ↓
El LLM (o tú) escanea este índice → ¿qué artefactos aplican a ESTA situación?
        ↓
Ficha: qué es + cuándo SÍ/NO aplica + plantilla lista en templates/
        ↓
Se añade el artefacto al proyecto (sin inventar formato ni olvidarlo)
```

## Cuándo usar este catálogo

- **Al crear/ordenar un repo** — escanear qué artefactos convienen.
- **Al hacer un mirror/fork** de un repo ajeno → `UPSTREAM.md` (procedencia + licencia).
- **Al abrir el proyecto a colaboradores** → `CONTRIBUTING.md`, `SECURITY.md`.
- **Cuando un proyecto usa secretos** → `.env.example`.
- **Cuando tomas decisiones técnicas que querrás recordar** → ADR / `ideas-decisions.md`.

## Cómo lo usa un LLM (flujo de decisión)

1. Leer `index.md` (o `catalog.json`) — una línea por artefacto.
2. Filtrar por `applies_to` según la situación del proyecto actual.
3. Leer la(s) ficha(s) candidata(s) en `entries/<slug>.md`.
4. Revisar **"Cuándo SÍ / Cuándo NO aplica"**.
5. Si aplica → copiar la plantilla de `templates/<archivo>` y adaptarla.

## Estructura

```text
artefactos_proyecto/
├── README.md          ← este archivo
├── index.md           ← índice humano (una línea por artefacto)
├── catalog.json       ← índice máquina (para filtrar sin abrir cada ficha)
├── SCHEMA.md          ← campos y estados de una ficha
├── _template.md       ← plantilla de FICHA (para catalogar un artefacto nuevo)
├── entries/           ← una ficha por artefacto
│   └── <slug>.md
└── templates/         ← el ARCHIVO listo para pegar en un proyecto
    └── <archivo>
```

> Distinción clave: `entries/<slug>.md` describe **cuándo usar** el artefacto;
> `templates/<archivo>` es el **contenido listo** para copiar al proyecto destino.

## Regla de oro (igual que en el resto del repo)

Enlazar, **no duplicar**. Si un artefacto ya tiene una fuente dueña en tu ecosistema
(ej.: las decisiones se registran en `nas-dotfiles/docs/ideas-decisions.md`), la ficha
**apunta** ahí en vez de re-explicarlo. Las plantillas son genéricas, sin datos de un
proyecto concreto.

## Añadir un artefacto nuevo

1. Copiar `_template.md` a `entries/<slug>.md` y rellenarlo (<60 líneas).
2. Poner el archivo genérico en `templates/<archivo>`.
3. Añadir una línea en `index.md` y una entrada en `catalog.json` (`file` real).
