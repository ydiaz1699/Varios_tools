# Spec-Driven Development (SDD) — flujo destilado

Conocimiento **destilado** del video de Gentleman Programming sobre SDD
(ver ficha `tool_catalog/entries/gentleman-programming/sdd-video.md`), para no
releer la transcripción. Amplía lo que quedó a medias en
`gentleman-dots-case-study.md` (el orquestador SDD) con el **flujo completo**.

> Aquí se documenta la metodología. NO es que tus proyectos ya la usen; adoptarla
> (crear comandos/skills SDD reales) es una decisión aparte.

## Idea central

SDD = **ingeniería de proceso**, no prompt engineering. El problema no es la IA:
es darle contexto **vago** (adivina) o **demasiado** (ruido que ofusca el
objetivo). Regla: darle "lo justo y necesario". Antes de implementar, definir el
cambio → requerimientos → diseño → tareas, y hacer que el agente **respete el
proceso, no pierda contexto y verifique lo que hizo**. Se inspira en
OpenSpec.dev + TDD, pero añade orquestación y verificación.

## Paso 0: SDD Init (calibrar antes de construir)

No es el cambio funcional; es **calibrar el arnés** antes de empezar:

- Detecta el proyecto: lee `package.json`/`go.mod`/`pyproject.toml`, estructura
  de carpetas, frameworks, convenciones, tooling, tests, patrones existentes.
- **Preflight** (pregunta al inicio): ¿interactivo o automático? ¿dónde guardar
  (carpeta `openspec/` del repo, o Engram)? ¿presupuesto de review para PRs
  grandes?
- Aterriza en el proyecto: crea/lee `openspec/config.yaml` con el contexto del
  stack, **reglas por fase** y testing capabilities.
- Verifica el **Skill Registry** (ver abajo) y detecta **testing capabilities**
  (runner + scripts) → activa **Strict TDD mode**.

Analogía del video: es calibrar la máquina antes de cortar las piezas.

## Skill Registry (índice, no biblioteca)

Un **índice** de skills disponibles (proyecto + usuario), NO una biblioteca
gigante ni un megaprompt. Tabla: `skill | trigger | dónde encontrarla`. Cargarlo
en contexto es **baratísimo**.

- El **orquestador** lee el registry, detecta qué skills aplican al contexto, y
  **selecciona los paths exactos** que pasa al subagente.
- El subagente NO recibe 20 documentos: recibe un **contrato claro** ("carga
  estas skills, respeta estas reglas"). Reduce ruido y tokens.
- Separación: el **orquestador coordina**, el **subagente ejecuta**, las
  **skills son la fuente de verdad**.

> Este es exactamente el patrón de `tool_catalog` (índice ligero para decidir qué
> leer) + la tabla auto-invoke de AGENTS.md. Mismo principio de lazy-loading.

## Strict TDD mode (en apply/verify)

Regla fuerte, no "implemento y luego veo":
1. Escribir los **tests primero** (satisfacen los requerimientos).
2. Hacerlos pasar.
3. Buscar y cubrir **casos edge** que puedan romper la lógica.
4. Dejar **evidencia**; no saltarse la verificación.

## Flujo SDD (fases)

```text
(pre) research/briefing   ← humano dirige: approaches, tradeoffs, decisiones → briefing.md
      │
      ▼
   explore    ← subagente: entiende el código, NO implementa
   propose    ← propuesta con idea central, riesgos, rollback, accept criteria
   spec       ← requerimientos
   design     ← diseño técnico
   tasks      ← desglose en tareas
   apply      ← implementación en Strict TDD (test→pasar→edge→evidencia)
   verify     ← verificación con evidencia
```

- Cada step corre en un **subagente** para no ensuciar la conversación del
  orquestador (este solo rastrea estado y decisiones del usuario).
- **Pre-research** (fase previa donde el humano dirige): investigar patrones,
  tradeoffs, alternativas → un `briefing.md` que alimenta explore/propose. Cuanto
  mejor el briefing, menos adivina el agente y menos tokens gasta.

## PRs encadenadas + auto-forecast

Si el cambio crece: estima el tamaño (auto-forecast) y, si supera un límite
(ej. ~400 líneas), pregunta cómo **dividir en PRs encadenadas**. Mantiene los PRs
revisables.

## Qué llevarte (y qué no) para tus proyectos

| Idea SDD | ¿Adoptar? | Nota |
|---|---|---|
| "Lo justo y necesario" de contexto | Sí (principio) | Ya es la base de tool_catalog/skills |
| Skill Registry (índice + paths a subagente) | Sí (concepto) | Es lo que hace tool_catalog + auto-invoke |
| Briefing previo antes de implementar | Sí | Barato y reduce adivinación |
| Strict TDD (test→pasar→edge→evidencia) | Según proyecto | Útil donde haya runner de tests |
| Fases explore→...→verify con subagentes | Si adoptas SDD formal | Requiere comandos/skills SDD reales |
| PRs encadenadas + auto-forecast | Avanzado | Para cambios grandes |

## Herramientas de terceros que menciona el video (NO propias)

- **Engram** (memoria del agente): ver ficha
  `tool_catalog/entries/gentleman-programming/engram.md`.
- **Genspark** (AI workspace / deep research para el briefing): sponsor del
  video; no catalogado como propio.
- **OpenSpec.dev**: inspiración del enfoque spec-first.

## Referencia

- Video: https://www.youtube.com/watch?v=KILEn2VSXX8
- Transcripción (gist): https://gist.github.com/ydiaz1699/4f29624bf0d0b4806e5269c9d7230013
- SDD aplicado en un repo real: `gentleman-dots-case-study.md` (orquestador SDD).
