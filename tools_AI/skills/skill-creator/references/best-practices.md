# Best Practices — crear skills eficientes

Consolidación de lecciones del skill-creator de Anthropic, las best practices
oficiales de Claude Platform, y experiencia práctica creando skills.

---

## El context window es un recurso público

Tu skill comparte el context window con: system prompt, historial de
conversación, metadata de TODAS las otras skills, y la petición actual.
No todo token tiene costo inmediato (la metadata se pre-carga, el body
solo al trigger), pero una vez cargado, cada token compite con el resto.

---

## Carga progresiva (3 niveles)

| Nivel | Cuándo se carga | Presupuesto |
|-------|-----------------|-------------|
| `name` + `description` | SIEMPRE (startup) | ~100 palabras total |
| Body de SKILL.md | Al trigger de la skill | <500 líneas, <6KB ideal |
| references/ | Solo cuando se necesita un paso | ≤200 líneas cada uno |

**Regla de oro**: Si un bloque NO se necesita en >50% de los triggers,
moverlo a references/.

---

## Descriptions: tu real estate más caro

La description se inyecta en CADA sesión de CADA usuario. Es el token
con mayor leverage para optimizar.

### Qué funciona

- Capacidad + cuándo usar en 1-2 oraciones
- Tercera persona ("Administra servicios Docker en...")
- Keywords que el router del LLM pueda matchear al intent del usuario
- Ser levemente "pushy" (el LLM tiende a under-trigger)

### Qué NO funciona

- Listar todas las frases posibles ("use when user says X, Y, Z...")
- Detalles de implementación interna
- Más de ~200 palabras (hard limit: 1024 chars)

### Ejemplo — antes vs después

**Antes** (338 tokens always-on):
```
Run Postman collection tests using Postman CLI - use when user says
"run tests", "run collection", "run my postman tests", "verify changes",
"check if tests pass", or wants to execute API test suites...
```

**Después** (reducción del 20%):
```
Run Postman Collection tests with the Postman CLI and report failures.
Use after code changes or when the user asks to run API tests.
```

---

## Body de SKILL.md: workflow, no enciclopedia

### Incluir en el body

- Reglas estrictas que aplican SIEMPRE
- Workflow principal (pasos numerados)
- Punteros a references/ con contexto de cuándo leer cada uno
- Anti-patrones críticos (lo que NUNCA hacer)

### Mover a references/

- Plantillas de código/compose/config
- Listas exhaustivas de comandos/alias
- Guías de troubleshooting
- Tablas de variables de entorno
- Ejemplos detallados por caso de uso

---

## Estilo de escritura

### Explicar el porqué

Los LLMs modernos tienen buen theory of mind. En lugar de:
```
MUST: Always use safe_run() instead of subprocess.run()
```

Preferir:
```
Usar safe_run() en lugar de subprocess directo — safe_run() valida
el nombre del servicio contra path traversal y fuerza shell=False
para prevenir inyección de comandos via f-strings.
```

### Libertad apropiada

| Tipo de regla | Libertad | Ejemplo |
|---------------|----------|---------|
| Seguridad, paths, APIs | Baja (exacta) | "SIEMPRE $dkco, NUNCA /docker/" |
| Formato de salida | Media | "Preferir tablas para comparaciones" |
| Estilo de comunicación | Alta | "Responder en el idioma del usuario" |

### No duplicar el harness

Si el agente ya tiene una capacidad nativa (routing por description,
lectura de archivos, búsqueda), NO pagar tokens para re-explicarla.
Si te encuentras manteniendo una tabla que espeja tu propio frontmatter,
bórrala.

---

## Scripts y tools bundled

### Cuándo crear un script

- Tarea repetitiva que todos los test cases hacen manualmente
- Validación que un humano haría mal (regex, conteo, formato)
- Generación determinista (templates, scaffolding)

### Cuándo NO crear un script

- Lógica que cambia según contexto (mejor como instrucción)
- Algo que el LLM puede hacer inline en 5 líneas
- Wrappers triviales que solo agregan indirección

### allowed-tools: lista explícita

En lugar de wildcards (`*` = todos los tools), listar solo los que
la skill realmente usa. Beneficios:
- Menos schemas en contexto (menos tokens)
- El LLM no se distrae con tools irrelevantes
- Revela bugs de permisos (tool declarado pero no permitido)

---

## Async y polling

Si tu skill interactúa con APIs async (HTTP 202 + polling):
- Instruir backoff exponencial (2s, 4s, 8s)
- "Reportar solo el resultado final, no narrar cada poll"
- Esto evita que el LLM genere running commentary que infla el contexto

---

## Métricas de éxito

| Métrica | Target | Cómo medir |
|---------|--------|------------|
| Tokens per trigger | <2000 | Contar chars del body / 4 |
| Líneas SKILL.md | <200 | `wc -l SKILL.md` |
| Líneas por reference | <200 | `wc -l references/*.md` |
| Description chars | <500 | Contar chars del frontmatter |
| False triggers | <10% | Eval set con should_trigger=false |
| Missed triggers | <10% | Eval set con should_trigger=true |

---

## Patrón: Skill de entorno/CLI

Skills que documentan un framework, shell personalizado, o CLI propio
del usuario. Diferente a skills de código o API porque NO generan código
nuevo — guían al LLM sobre cómo USAR el entorno existente.

### Características

- El error más común del LLM es sugerir comandos genéricos en vez del framework
- La tabla NUNCA/SIEMPRE es el mecanismo más efectivo para prevenir esto
- No necesitan scripts bundled (el framework ya tiene los suyos)
- References tienden a ser tablas de comandos/aliases (compactas, muchas líneas)

### Estructura recomendada

```
mi-entorno/
├── SKILL.md              ← Reglas + comandos esenciales + cuándo usar qué
└── references/
    ├── shell.md          ← Aliases, funciones, variables, prompt
    ├── cli.md            ← Comandos del CLI principal
    ├── tools.md          ← Tools/agente si aplica
    └── security.md       ← Mecanismos de protección si aplica
```

### Body de SKILL.md (para skills de entorno)

1. Variables y rutas (tabla compacta)
2. Regla NUNCA/SIEMPRE (lo que previene comandos genéricos)
3. Comandos esenciales (solo los del >50% de triggers)
4. Workflow principal (ej: "crear nuevo servicio Docker")
5. Cuándo usar CLI vs agente (si el entorno tiene ambos)
6. Punteros a references/ con contexto

### Qué incluir en el body vs references

| En el body (siempre cargado) | En references (on-demand) |
|------------------------------|---------------------------|
| Tabla NUNCA/SIEMPRE | Lista exhaustiva de aliases |
| 5-10 comandos más usados | 30+ comandos con flags y variantes |
| Variables de entorno principales | Tabla completa de variables |
| Formato de salida esperado (ej: árbol + mkdir + compose) | Plantillas completas |
| Reglas de seguridad críticas | Mecanismos detallados (safe_run, audit) |

### Fuente de verdad: el código

Para skills de entorno, SIEMPRE basar la skill en el código fuente real,
no en documentación desactualizada ni en lo que el usuario dice que tiene.
El código es la fuente de verdad:
- Leer `init.sh` para saber qué se carga y en qué orden
- Leer cada módulo para documentar los aliases/funciones reales
- Leer el CLI para saber los comandos implementados (no los planeados)

Para un caso completo, ver `references/case-study-docker-nas.md`.

---

## Checklist antes de publicar

- [ ] name: kebab-case, ≤64 chars, matchea nombre de carpeta
- [ ] description: ≤1024 chars, tercera persona, sin angle brackets
- [ ] Body: <500 líneas, solo workflow + reglas core
- [ ] References: cada uno <200 líneas, un nivel de profundidad
- [ ] Sin info time-sensitive (versiones, fechas)
- [ ] Sin duplicación del harness nativo
- [ ] Terminología consistente (un solo nombre para cada concepto)
- [ ] Punteros claros a references/ con contexto de cuándo leer
- [ ] Probada con 3-5 queries reales (trigger + no-trigger)
