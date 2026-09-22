# tools_AI — artefactos de IA propios y reutilizables

Herramientas que **YO uso/aplico** al trabajar con agentes LLM: skills que se
ejecutan y recursos de diseño reutilizables. A diferencia de
[`tool_catalog/`](../tool_catalog/) (que son **fichas ligeras que apuntan a
recursos externos** para decidir si leerlos), aquí viven los **artefactos
completos**, listos para usar o adaptar en cualquier proyecto.

## Diferencia con `tool_catalog/`

| | `tool_catalog/` | `tools_AI/` (este) |
|---|---|---|
| Qué contiene | Fichas ligeras de recursos **externos** | Artefactos **propios** completos |
| Ejemplo | Ficha de Prowler (apunta a su repo) | `skill-creator` (skill lista para usar) |
| Uso | Decidir si vale la pena leer la fuente | Usar/aplicar directamente |
| Regla | Enlazar, no duplicar | El artefacto vive aquí íntegro |

## Contenido

```text
tools_AI/
├── skills/
│   ├── skill-creator/       # meta-skill: crear/optimizar skills de agentes LLM
│   └── unificador-skill/    # unifica fragmentos dispersos en una guía coherente
├── resources/
│   └── nas-agent-memory/    # doc de diseño: memoria persistente + auto-mejora (Learning Loop)
└── kiro-global-skills/      # skills para instalar a nivel global (Settings/Skills)
    └── tool-catalog-router/ # enruta el uso de tool_catalog + tools_AI
```

## Cuándo usar cada uno

| Cuando la tarea sea... | Usar |
|---|---|
| Crear una skill nueva, mejorar una existente, o entender best practices de authoring | `skills/skill-creator/SKILL.md` |
| Unificar/consolidar notas, fragmentos o diagnósticos dispersos en una guía paso a paso | `skills/unificador-skill/SKILL.md` |
| Diseñar/entender un sistema de memoria persistente y auto-mejora para un agente | `resources/nas-agent-memory/` (referencia de diseño) |

## Relación con los catálogos

- Estos artefactos están **indexados en** [`tool_catalog/`](../tool_catalog/)
  para que un LLM los descubra desde un único punto de entrada.
- `skill-creator` usa como fuente externa la ficha
  [`tool_catalog/entries/prowler-agent-skills.md`](../tool_catalog/entries/prowler-agent-skills.md)
  (el patrón Agent Skills del video).
