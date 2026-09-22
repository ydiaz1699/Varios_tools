# Case Study — skill `docker-nas` para nas-dotfiles

Caso real de creación de una skill compleja (6 archivos, 1270 líneas)
que documenta un framework completo de administración de NAS con Docker.

---

## Contexto

- **Proyecto:** `nas-dotfiles` — framework bash + Python para NAS Debian
- **Componentes:** Shell (9 módulos), CLI Docker (`svc`), Agente IA (28 tools)
- **Existía una skill vieja:** 4 archivos con rutas hardcodeadas y sin agente
- **Objetivo:** Reescribir la skill para reflejar el entorno real y completo

---

## Proceso seguido

### 1. Analizar el código real (no documentación)

Antes de escribir una sola línea de la skill, se leyeron todos los archivos
fuente del framework:

```
shell/init.sh + shell/lib/*.sh     → 9 módulos, orden de carga, variables
docker/cli/svc.sh + lib/*.sh       → 30+ comandos, discovery, backup
agent/nas_agent.py                 → providers, prompt modular, sesiones
agent/tools/__init__.py            → 28 tools listadas
agent/tools/_shell.py              → seguridad (safe_run, validate)
agent/tools/_audit.py              → audit log JSON Lines
agent/core/memory.py               → memoria persistente
agent/daemon.py                    → modo daemon systemd
agent/plugins/                     → sistema de plugins
agent/config/defaults.yml          → configuración completa
```

**Lección:** Las skills de entorno deben basarse en el CÓDIGO, no en lo
que el usuario dice que tiene. El código es la fuente de verdad.

### 2. Decidir el split body vs references

Criterio: "¿Se necesita en >50% de los triggers?"

| Contenido | ¿>50% triggers? | Destino |
|-----------|-----------------|---------|
| Reglas de rutas ($dkco, $NAS_DOTFILES) | Sí, siempre | Body |
| Formato de nuevo servicio Docker | Sí, muy común | Body |
| Tabla de comandos esenciales | Sí | Body |
| Cuándo usar svc vs agent | Sí | Body |
| Prompt explicado | No, raro | Body (compacto) |
| Todos los aliases del shell | No, solo a veces | references/entorno.md |
| Plantillas Docker completas | No | references/estructura.md |
| 30+ comandos svc detallados | No | references/svc.md |
| 28 tools del agente + providers | No | references/agent.md |
| Mecanismos de seguridad | No | references/seguridad.md |

### 3. Escribir SKILL.md (body)

Principios aplicados:
- Solo reglas que aplican en CADA interacción sobre el NAS
- Tabla de "nunca/siempre" para reglas estrictas (libertad baja)
- Punteros con contexto: "Para mecanismos completos, ver references/seguridad.md"
- Sección de "cuándo usar svc vs agent" (decisión que surge siempre)
- NO incluir listas exhaustivas de comandos

### 4. Escribir 5 references (detalle on-demand)

Cada reference cubre un concern:
- `entorno.md` — shell framework completo
- `estructura.md` — guía Docker con plantillas
- `svc.md` — CLI svc todos los comandos
- `agent.md` — agente IA completo
- `seguridad.md` — mecanismos de protección

### 5. Evaluar contra métricas

Ver sección "Evaluación real" más abajo.

---

## Decisiones de diseño

### Por qué 5 references y no 3

La skill vieja tenía 3 (entorno, estructura, svc). Pero el proyecto
creció con un agente IA completo y mecanismos de seguridad no triviales.
Mantener todo en 3 archivos habría producido references de 400+ líneas.

### Por qué incluir comandos esenciales en el body

Normalmente "listas exhaustivas" van a references. Pero los comandos
`dk`, `adm`, `svc up/down/restart/logs` se necesitan en >90% de las
interacciones. Se incluyó una tabla compacta (no la lista completa)
en el body, con puntero a references/ para el detalle.

### Por qué la tabla NUNCA/SIEMPRE funciona

Para skills de entorno/CLI, el error más común del LLM es sugerir
comandos genéricos (`docker compose`, `cd /docker`, `apt install`)
en vez de los del framework. La tabla de "NUNCA X → USA Y" es el
mecanismo más efectivo para prevenir esto.

### Por qué no scripts/templates

Este tipo de skill (documentación de entorno) no genera código — guía
al LLM sobre cómo USAR el código existente del usuario. No necesita
scripts bundled porque el framework ya tiene sus propios scripts.

---

## Evaluación real

### Métricas finales

| Métrica | Target | Resultado | Veredicto |
|---------|--------|-----------|-----------|
| SKILL.md líneas | <500 (ideal <200) | 240 | ⚠️ Aceptable |
| Description chars | <500 | ~496 | ✅ |
| references/ max | <200 líneas | 154-253 | ⚠️ 2 de 5 exceden |
| Tokens por trigger | <2000 | ~960 | ✅ |
| Carga progresiva | Sí | ✅ | ✅ |
| Punteros con contexto | Sí | ✅ | ✅ |

### Checklist

- [x] name: kebab-case (`docker-nas`)
- [x] description: <1024 chars, tercera persona
- [x] Body: solo workflow + reglas core
- [x] References: un nivel de profundidad
- [x] Sin info time-sensitive
- [x] Sin duplicación del harness
- [x] Terminología consistente
- [x] Punteros claros con contexto
- [ ] Todas las reglas explican el porqué (parcial)

### Problemas detectados y aceptados

1. `entorno.md` (253 líneas) excede target de 200 — son tablas compactas
   de aliases, no prosa. Splitear en dos sería artificial.
2. SKILL.md (240 líneas) excede ideal de 200 — tiene tablas de comandos
   esenciales que se usan en >50% de triggers. Moverlos a references
   causaría carga innecesaria.
3. Algunas reglas dicen "NUNCA X" sin porqué — aceptable en reglas de
   rutas donde el porqué es obvio (portabilidad/configurabilidad).

---

## Antes vs Después

| Aspecto | Skill vieja (4 archivos) | Skill nueva (6 archivos) |
|---------|--------------------------|--------------------------|
| Rutas | Hardcodeadas (`/home/aadm/shell/`) | Variables (`$NAS_DOTFILES`) |
| Cobertura | Solo shell + svc | Shell + svc + agente + seguridad |
| Aliases | `ls` con flags | `eza` (lo real) |
| Funciones | Sin pipins, sin git | Con pipins, git, completions |
| Agente | No documentado | 28 tools, 3 providers, memoria |
| Seguridad | No documentada | safe_run, audit, readonly, dry-run |
| Prompt | Sin git branch | Con `(main*)` |
| Métricas | No evaluada | Evaluada contra checklist |

---

## Template reutilizable para skills de entorno/CLI

```
mi-entorno/
├── SKILL.md              ← Reglas + comandos esenciales + cuándo usar qué
└── references/
    ├── shell.md          ← Aliases, funciones, variables, prompt
    ├── cli.md            ← Comandos del CLI principal
    ├── tools.md          ← Tools/agente si tiene
    └── security.md       ← Mecanismos de protección si aplica
```

Body de SKILL.md para skills de entorno:
1. Variables y rutas (tabla)
2. Regla NUNCA/SIEMPRE (lo que previene comandos genéricos)
3. Comandos esenciales (los del >50% de triggers)
4. Workflow principal (ej: "crear nuevo servicio")
5. Cuándo usar CLI vs agente (si aplica)
6. Punteros a references/ con contexto
