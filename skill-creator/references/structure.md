# Anatomía de una skill — estructura y límites

---

## Estructura mínima

```
mi-skill/
└── SKILL.md       ← obligatorio
```

## Estructura completa

```
mi-skill/
├── SKILL.md              ← Instrucciones principales (obligatorio)
├── references/           ← Documentación on-demand (opcional)
│   ├── api-guide.md
│   ├── examples.md
│   └── troubleshooting.md
├── scripts/              ← Código ejecutable (opcional)
│   ├── generate.py
│   └── validate.sh
├── templates/            ← Plantillas de archivos (opcional)
│   ├── component.tsx.template
│   └── test.spec.ts.template
└── assets/               ← Archivos estáticos (opcional)
    ├── config.json
    └── base-template.html
```

---

## Límites de tamaño recomendados

| Tipo de archivo | Máximo recomendado | Notas |
|-----------------|-------------------|-------|
| SKILL.md | 500 líneas | Ideal: 100-200 líneas |
| Cada reference file | 200 líneas | Para archivos grandes: TOC al inicio |
| Scripts | 300 líneas | Si es más largo, dividir en módulos |
| Templates | 100 líneas | Solo la estructura, no contenido real |

Archivos más grandes funcionan pero impactan el context window del LLM.

---

## SKILL.md — formato

### Frontmatter YAML (obligatorio)

```yaml
---
name: mi-skill
description: >
  Qué hace la skill y cuándo usarla. Tercera persona.
  Máximo 1024 caracteres.
---
```

Propiedades permitidas en frontmatter:
- `name` (requerido): kebab-case, 1-64 chars
- `description` (requerido): ≤1024 chars, sin `<` ni `>`
- `license` (opcional): identificador de licencia
- `allowed-tools` (opcional): lista de tools permitidos
- `metadata` (opcional): campos custom
- `compatibility` (opcional): requisitos de entorno, ≤500 chars

### Body Markdown

Estructura típica del body:

```markdown
# Título de la skill

Descripción breve de una línea.

## Reglas / Workflow principal
(lo que aplica en CADA trigger)

## Sección 2
(segundo concern principal)

## Referencias
(punteros a references/ con contexto de cuándo leer)
```

---

## Carga progresiva — cómo funciona

```
Startup (todas las sesiones):
  → Solo name + description de cada skill instalada

Trigger (skill activada):
  → Se carga el body completo de SKILL.md

On-demand (paso específico):
  → Se carga el reference file cuando el LLM lo necesita
```

Esto significa:
- La description paga costo en TODAS las sesiones → hacerla mínima
- El body paga solo cuando la skill se usa → puede ser más detallado
- Los references pagan solo en el paso que los necesita → pueden ser extensos

---

## references/ — patrones de organización

### Por concern (recomendado)

```
references/
├── shell.md           ← aliases, navegación, prompt
├── docker-cli.md      ← comandos de svc
├── agent.md           ← tools, plugins, memoria
└── security.md        ← mecanismos, variables
```

### Por dominio/variante

```
references/
├── aws.md
├── gcp.md
└── azure.md
```

El LLM lee solo el relevante.

### Por tipo de contenido

```
references/
├── templates.md       ← plantillas de código
├── examples.md        ← ejemplos detallados
└── troubleshooting.md ← diagnóstico de problemas
```

---

## Punteros desde SKILL.md a references/

Siempre incluir contexto de CUÁNDO leer el reference:

**Bien:**
```markdown
Para plantillas de compose con YAML anchors obligatorios, ver `references/svc.md`.
```

**Mal:**
```markdown
Ver `references/svc.md`.
```

El LLM necesita saber si debe leerlo ahora o más tarde.

---

## Convenciones de naming

### Carpetas
- Kebab-case: `mi-skill/`, `code-review/`
- Nombres cortos pero descriptivos

### Archivos
- `SKILL.md` — siempre MAYÚSCULAS
- References: kebab-case (`api-guide.md`)
- Scripts: lowercase con extensión (`generate.py`)
- Templates: incluir extensión target (`component.tsx.template`)

---

## Para archivos de referencia grandes (>150 líneas)

Incluir tabla de contenidos al inicio:

```markdown
# Guía de API

## Contenido
- [Autenticación](#autenticación)
- [Endpoints](#endpoints)
- [Rate Limiting](#rate-limiting)
- [Errores](#errores)

---

## Autenticación
...
```
