# Arquitectura canónica de contexto, catálogo y scaffolding

## Estado

Esta referencia define el contrato de diseño de `codigo_tools`. No convierte propuestas en hechos de un proyecto ni autoriza promoción automática.

## Tres capas lógicas

```text
catalog  → datos hardware reutilizables y tipados
shared   → prompts, referencias, templates y herramientas de proceso
project  → código, configuración, wiring y contexto de un target
```

`_template-proyecto` es un artefacto de scaffolding dentro de `templates/`; no es una cuarta capa runtime.

### Catálogo

La fuente canónica actual es JSON validado por schemas:

```text
catalog/
├── boards/{index.json,<board-id>.json}
├── peripherals/{index.json,<peripheral-id>.json}
├── compatibility/{rules.json}
└── schemas/{board,peripheral,project-wiring}.schema.json
```

Una ficha de board o peripheral no contiene conexiones de un proyecto. Los índices seleccionan; las fichas documentan; `project-wiring.json` resuelve la instancia concreta.

### Shared

`prompts/`, `references/`, `templates/` y `tools/` contienen procedimientos y contratos reutilizables. Todo contenido acotado a PlatformIO/embedded debe declarar ese alcance.

### Proyecto

El proyecto conserva el código y su contexto. `PROJECT_CONTEXT.md` es el punto de entrada mínimo cuando se genera un bundle `.ai`; el resto de archivos se crea solo si la evidencia o el usuario lo requiere.

## Bundle mínimo y archivos condicionales

Obligatorio al generar contexto de agente:

- `.ai/PROJECT_CONTEXT.md`: propósito, target, snapshot, entradas, referencias, mapa breve, estado de lectura y límites.

Condicionales:

- `SKILL.md`: existe una tarea recurrente accionable.
- `HARDWARE.md`: existe hardware físico o wiring identificable.
- `SOFTWARE.md`: hay build, dependencias o configuración que mantener.
- `ARCHITECTURE.md`: hay FSM, flujo temporal o límites complejos.
- `PROTOCOL.md`: el protocolo necesita un contrato propio.
- `DECISIONS.md`, `TASKS.md`, `TESTING.md`, `CHANGELOG.md`, `ROADMAP.md`: solo si existen decisiones, backlog, tests/estrategia o convenciones mantenidas.

`README.md`, `repo-map.yml`, `copilot-instructions.md` y el análisis completo son artefactos complementarios con lectores y responsabilidades distintas; no se reemplazan silenciosamente.

## Wiring y referencias

`project-wiring.json` debe referenciar IDs estables del catálogo:

```json
{
  "board_ref": "boards/<board-id>.json",
  "peripherals": [{"instance": "<id>", "ref": "peripherals/<id>.json", "variant": "<variant>"}]
}
```

Un GPIO observado en código demuestra una asignación lógica, no por sí solo el componente físico, el cableado, la alimentación ni la polaridad. La evidencia debe conservar `source`, `reference` y `state`.

Si falta una ficha, se produce un `catalog gap report` con alias, modelo pendiente, campos faltantes, fuentes requeridas y riesgos. No se publica una ficha automáticamente.

## Pipeline

```text
scan → análisis semántico → plan/revisión → [aprobación]
     → scaffolding/adaptación en output separado
     → validación → [aprobación] → promoción manual
```

El extractor no escribe en la fuente. El scaffolder es una etapa separada, con `dry-run`, no sobrescritura y procedencia. Los comandos documentados se distinguen de los ejecutados; los secretos se redactan.

## Estados de evidencia

Usar, sin mezclarlos:

`OBSERVADO_EN_CODIGO`, `OBSERVADO_EN_BUILD`, `DOCUMENTADO`, `INFERIDO`, `ESTIMADO`, `PROPUESTO`, `CONTRADICTORIO`, `NO_ENCONTRADO`, `PENDIENTE_DE_VERIFICAR`, `VERIFICADO_EN_HARDWARE`.

La existencia de un archivo no prueba que su contenido sea correcto; `APLICADO`, `COMPILADO`, `VERIFICADO` y `VERIFICADO_EN_HARDWARE` deben registrar evidencia de ejecución separadamente.
