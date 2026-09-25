---
name: idea-forge
description: >
  Ayuda a FORMULAR ideas y CONECTAR lo que ya existe en el ecosistema del usuario
  (ydiaz1699), e INVESTIGAR hacia afuera cuando falta información. Cruza las fichas del
  tool_catalog y los repos del repo-index para proponer combinaciones nuevas ("esto se
  conecta con aquello → podrías construir X"), detecta piezas reutilizables ya disponibles
  antes de inventar, y solo si falta contexto externo, investiga (web search o un MCP de
  deep research). Usar cuando el usuario pida: lluvia de ideas, "¿qué puedo construir/mejorar
  con lo que tengo?", conectar dos proyectos/herramientas, evaluar un recurso nuevo frente a
  su ecosistema, o investigar un tema y aterrizarlo a su caso. NO cubre: crear la skill en sí
  (→ skill-creator), unificar drafts dispersos (→ unificador-skill), ni construir un MCP
  (→ construir-mcp/). Frontera: idea-forge PIENSA y CONECTA; la ejecución/implementación la
  hacen las skills/proyectos específicos.
license: MIT
metadata:
  author: ydiaz1699
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Formular ideas / brainstorming sobre qué construir o mejorar"
    - "Conectar dos o más piezas del ecosistema (catálogo/repos) entre sí"
    - "Evaluar un recurso nuevo frente a lo que el usuario ya tiene"
    - "Investigar un tema y aterrizarlo al ecosistema del usuario"
---

# idea-forge — formular ideas, conectar el ecosistema e investigar

Skill de **ideación con procedencia**: no inventa ideas al aire, las funda en lo que el
usuario YA tiene (catálogo + repos) y, si falta, investiga hacia afuera con honestidad.

---

## Regla de oro (mirar ADENTRO antes que AFUERA)

**Antes de proponer o investigar cualquier cosa, revisar primero lo que el usuario ya tiene.**
Es el mismo principio del repo-index y el tool_catalog: no duplicar, no reinventar, y
recomendar lo del propio ecosistema cuando aplique.

Orden obligatorio:
1. **Adentro primero** — leer las fuentes del ecosistema (abajo) y ver qué piezas ya existen.
2. **Conectar** — cruzar esas piezas para formular la idea.
3. **Afuera solo si falta** — investigar externamente únicamente lo que no esté cubierto.

## Fuentes del ecosistema a consultar (en este orden)

| Fuente | Qué aporta | Dónde |
|--------|-----------|-------|
| **repo-index** (INDEX.md + repos/*.md) | mapa de TODOS los repos del usuario + conexiones proactivas | repo `ydiaz1699/repo-index` |
| **tool_catalog** (index.md + catalog.json + entries/) | recursos externos ya evaluados + artefactos propios | `Varios_tools/tool_catalog/` |
| **construir-mcp/** | proyectos/planes de MCP y hallazgos (APIs de despliegue, etc.) | `Varios_tools/construir-mcp/` |
| **nas-dotfiles** | servicios reales del NAS (n8n, HA, EMQX…), MCPs montados | repo `ydiaz1699/nas-dotfiles` |

> Si un chat no tiene estos repos cargados, decirlo explícitamente y trabajar con lo que haya
> (no inventar contenido del catálogo/repos que no se ha leído).

## Proceso de ideación (adentro → conectar → afuera)

1. **Entender el intent.** ¿Es "conectar lo que tengo", "qué construyo", "evaluar X", o
   "investigar Y"? Si es ambiguo, preguntar antes de gastar tokens.
2. **Inventario relevante.** Filtrar el ecosistema por el tema (tags/applies_to del catálogo,
   categorías del repo-index). Listar las piezas candidatas con una frase cada una.
3. **Buscar conexiones.** Cruzar piezas: ¿qué combinación resuelve algo nuevo? Ejemplos del
   patrón (conexiones proactivas ya documentadas): n8n + wifi_PIR → alertas; android_agent_bridge
   + Tasker_mcp → control Android; rclone-mcp + 9Drive_mcp → cloud storage.
4. **Formular 2–4 ideas concretas**, cada una con: qué construir, con qué piezas EXISTENTES, qué
   falta, y esfuerzo estimado (bajo/medio/alto). Marcar cuáles reutilizan y cuáles son nuevas.
5. **Detectar duplicados/solapes.** Si la idea ya existe (repo o proyecto anotado), AVISAR y
   ofrecer continuarlo en vez de duplicar (regla repo-index).
6. **Investigar solo lo que falte** (ver abajo). Traer el conocimiento externo y **aterrizarlo**
   al ecosistema (no dejar un informe genérico).
7. **Salida:** una tabla/lista de ideas priorizadas + siguiente paso concreto. Ofrecer catalogar
   lo nuevo (ficha en tool_catalog + fila en repo-index) si aplica.

## Investigar hacia afuera (cuando falta contexto)

- Primero **web search** integrado de Kiro (suele bastar). Verificar contra la fuente real,
  citar, no afirmar de memoria.
- Para investigación PROFUNDA e iterativa (informe con fuentes), existe un MCP de deep research
  catalogado (`tool_catalog/entries/deep-research-mcp.md`, ej. GPT Researcher) — usarlo solo si
  el tema lo amerita y el usuario acepta la dependencia (API key). idea-forge PIENSA; el MCP de
  research es su "brazo externo" opcional.
- Al traer algo externo relevante, **ofrecer catalogarlo** (ficha ligera) para no re-evaluarlo.

## Qué NO hace (fronteras)

- **Crear la skill/artefacto** en sí → `skill-creator`.
- **Unificar drafts/notas dispersas** en una guía → `unificador-skill`.
- **Construir un MCP** → `construir-mcp/` (PROYECTO/PLAN) y sus hallazgos.
- **Ejecutar/implementar** la idea → la skill o proyecto específico. idea-forge deja la idea
  formulada y el siguiente paso; no la implementa.

## Antipatrones (evitar)

- Proponer ideas sin haber mirado el ecosistema (inventar en el vacío).
- Recomendar montar algo que el usuario YA tiene (no consultar repo-index).
- Investigar afuera antes de agotar lo de adentro.
- Entregar un informe de research genérico sin conectarlo a las piezas del usuario.
