---
name: skill-creator
description: >
  Crea, estructura y optimiza skills para agentes LLM (Kiro, Claude Code,
  Claude.ai). Guía el proceso completo: captura de intent, escritura del
  SKILL.md con carga progresiva, creación de references/, optimización de
  la description para triggering, y evaluación iterativa. Usar cuando el
  usuario quiera crear una skill nueva, mejorar una existente, o entender
  las best practices de authoring de skills.
license: MIT
metadata:
  author: ydiaz1699
  version: "1.1"
  scope: [root]
  auto_invoke:
    - "Crear una skill nueva o mejorar/optimizar una existente"
---

# skill-creator

Meta-skill para crear y optimizar skills de agentes LLM.

---

## Proceso completo

```
1. Capturar intent     → qué hace, cuándo triggerea, formato de salida
2. Escribir SKILL.md   → frontmatter + body conciso + punteros a references/
3. Crear references/   → detalle on-demand (plantillas, guías, ejemplos)
4. Optimizar description → triggering preciso sin overtriggering
5. Evaluar + iterar    → test cases → feedback → mejora → repetir
```

---

## Paso 1: Capturar intent

Antes de escribir, responder:

1. ¿Qué debe hacer la skill? (capacidad concreta)
2. ¿Cuándo debe triggerear? (frases, contextos, keywords)
3. ¿Cuál es el formato de salida esperado?
4. ¿Hay edge cases o restricciones críticas?
5. ¿Necesita scripts, plantillas o archivos de referencia?

Si la conversación ya contiene un workflow (ej: "convierte esto en skill"),
extraer las respuestas del historial antes de preguntar.

---

## Paso 2: Escribir SKILL.md

### Frontmatter YAML (obligatorio)

```yaml
---
name: mi-skill
description: >
  Descripción en tercera persona, 100-200 palabras, ≤1024 chars.
  Incluir: qué hace + cuándo usarla + keywords de triggering.
---
```

Reglas del frontmatter:
- `name`: kebab-case, 1-64 chars, sin guiones consecutivos
- `description`: ≤1024 chars, sin angle brackets, tercera persona
- Campos opcionales: `license`, `allowed-tools`, `metadata`, `compatibility`

### Body (workflow + reglas)

- **Máximo ~150-200 líneas** en el body
- Solo lo que el LLM necesita en CADA trigger
- Reglas estrictas, workflow principal, punteros a references/
- NO incluir detalle que solo se necesita a veces → mover a references/

### Estilo de escritura

- Imperativo para instrucciones ("Usar X", "Crear Y")
- Explicar el **porqué** detrás de las reglas (no solo MUST/NEVER)
- Libertad baja para reglas frágiles, libertad alta para preferencias
- No repetir lo que el LLM ya sabe (ej: qué es Docker)
- Sin info time-sensitive (versiones, fechas)
- Terminología consistente en todo el documento

Para anatomía completa y límites de tamaño, ver `references/structure.md`.

---

## Paso 3: Crear references/

Archivos que se cargan **solo cuando el LLM los necesita**:

```
mi-skill/
├── SKILL.md              ← siempre cargado al trigger (~700 tokens)
└── references/           ← cargado on-demand
    ├── guia-detallada.md
    ├── plantillas.md
    └── troubleshooting.md
```

Reglas de references/:
- Cada archivo ≤200 líneas (ideal)
- Un nivel de profundidad (no subdirectorios)
- Punteros claros desde SKILL.md: `ver references/X.md`
- Separar por concern: no mezclar plantillas con troubleshooting

Para patrones de organización, ver `references/structure.md`.

---

## Paso 4: Optimizar description

La description es lo MÁS caro — se carga en TODAS las sesiones.

Principios:
- 1-2 oraciones: capacidad + cuándo usar
- No listar todas las frases posibles (el router del LLM generaliza)
- Ser "un poco pushy" — el LLM tiende a under-trigger
- Evitar keywords ambiguas que compitan con otras skills
- Probar con queries reales (should-trigger Y should-NOT-trigger)

Para el flujo completo de optimización, ver `references/description-optimization.md`.

---

## Paso 5: Evaluar e iterar

Ciclo:
```
Escribir/mejorar skill → Correr test cases → Revisar outputs →
Identificar fallas → Corregir skill → Repetir
```

Criterios de éxito:
- El usuario dice que está satisfecho
- Los test cases pasan sin feedback negativo
- No hay mejoras significativas entre iteraciones

Para el flujo detallado de evaluación, ver `references/eval-workflow.md`.

---

## Paso 6 (opcional): auto-invoke y metadata

Si el proyecto tiene varias skills y un `AGENTS.md`, el `description` NO basta:
los modelos no auto-activan skills de forma fiable. Reforzar con:

- Frontmatter `metadata.{scope, auto_invoke}` (campos extra que Kiro ignora sin
  romper nada; habilitan router/índice y un futuro sync).
- Una tabla **"Auto-invoke Skills"** en el `AGENTS.md` que ORDENE cargar la skill
  antes de actuar.

Plantilla lista para copiar: `assets/SKILL-TEMPLATE.md`.
Detalle del patrón (scope, auto_invoke, manual vs skill-sync, assets/ vs
references/, qué NO copiar de Prowler): ver
`references/auto-invoke-and-metadata.md`.

Para cómo encaja la skill en la documentación del proyecto —tamaño del AGENTS.md
(~250, máx ~500 líneas), uno vs varios AGENTS.md por feature con root que enruta,
y cuándo delegar un flujo en subagentes (contexto aislado que devuelve solo un
resumen)—: ver `references/agents-md-and-subagents.md`.

Ejemplos reales aplicados (conocimiento destilado para NO clonar los repos):
- `references/prowler-case-study.md` — repo grande multi-área: 6 AGENTS.md,
  37 skills en 3 familias, frontmatter con scope/auto_invoke, references/ vs assets/.
- `references/gentleman-dots-case-study.md` — repo simple: 1 AGENTS.md, tabla
  auto-invoke con columna "Why", auto-invoke manual (sin scope/auto_invoke), y el
  orquestador SDD delegate-only con subagentes (el patrón del video aplicado).

Fuente externa de ambos patrones: `tool_catalog/entries/prowler-agent-skills.md`
y `tool_catalog/entries/gentleman-agents-skills-video.md` (Agent Skills / video
de Gentleman Programming).

---

## Anti-patrones (evitar siempre)

| Anti-patrón | Problema | Solución |
|-------------|----------|----------|
| SKILL.md monolítico (>500 líneas) | Context rot, ~4800 tokens/trigger | Split a references/ |
| Description como phrasebook | Tokens desperdiciados en cada sesión | 1-2 oraciones genéricas |
| Reglas sin porqué | El LLM no generaliza bien | Explicar la razón |
| Info duplicada del harness | Pagar tokens por algo gratis | Borrar |
| Wildcards en allowed-tools | Ambigüedad + bugs latentes | Lista explícita |
| Plantillas inline en SKILL.md | Se cargan siempre aunque no se usen | Mover a references/ |

---

## Best practices consolidadas

Para las lecciones completas (progressive disclosure, token efficiency,
cuándo usar scripts vs references, etc.), ver `references/best-practices.md`.
