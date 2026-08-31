# codigo_tools

Colección de prompts y herramientas para analizar proyectos de código y generar documentación derivada de la fuente real.

## Objetivo

`codigo_tools` no contiene la lógica de los proyectos analizados. Contiene procedimientos reutilizables para que una LLM o una herramienta:

- lea el proyecto completo antes de documentarlo;
- siga `#include`, imports, `platformio.ini`, configuraciones y bibliotecas locales;
- distinga hechos observados de inferencias y datos pendientes;
- genere documentación de hardware y diagramas draw.io sin inventar conexiones;
- audite los documentos generados contra el código cuando este cambie.

La fuente de verdad es el código/configuración actual del proyecto analizado. Los README, notas y diagramas existentes son referencias secundarias y deben marcarse como tales.

## Estructura

```text
codigo_tools/
├── README.md
├── prompts/
│   ├── analizar-codigo-completo.md
│   ├── generar-repo-map.md
│   ├── generar-readme.md
│   ├── generar-contexto-agentes.md
│   ├── generar-arquitectura-verificable.md
│   ├── generar-changelog-evidencial.md
│   ├── generar-plan-ejecucion-canonico.md
│   ├── generar-roadmap-tecnico.md
│   ├── generar-ledger-bugs-evidencial.md
│   ├── generar-auditoria-protocolo.md
│   ├── generar-especificacion-requisitos.md
│   ├── generar-checklist-cambio-seguro.md
│   ├── generar-preflight-contexto.md
│   ├── gen-notas-hw.md
│   ├── gen-conexiones-svg.md
│   ├── audit-hardware-docs.md
│   └── audit-project-docs.md
├── references/
│   ├── criterios.md
│   ├── tipos-documentacion.md
│   ├── coding-style-tags.md
│   ├── shared-platformio-environment.md
│   └── context-bundle-contract.md
└── templates/
    ├── repo-map.yml
    ├── README-project.md
    └── project-context-bundle/
        ├── README.md
        ├── project-context-bundle-manifest.json
        ├── shared/
        │   ├── CODING_STYLE.md
        │   └── SOFTWARE.md
        └── project/.ai/
            ├── PROJECT_CONTEXT.md
            ├── HARDWARE.md
            ├── SOFTWARE.md
            ├── SKILL.md
            ├── TASKS.md
            ├── DECISIONS.md
            ├── ROADMAP.md
            ├── CHANGELOG.md
            ├── ARCHITECTURE.md
            ├── PROTOCOL.md
            └── TESTING.md
```

`tools/validate_context_bundle.py` valida el punto de entrada, los enlaces, secretos redactados y referencias de catálogo en modo report-only.

Los prompts son independientes y se pueden copiar o adjuntar a otra LLM. `references/criterios.md` documenta el método común, pero un prompt debe repetir las reglas críticas que necesita para no depender de que ese archivo también sea adjuntado. Las referencias `coding-style-tags.md` y `shared-platformio-environment.md` describen cómo parametrizar las dos piezas compartidas del bundle de contexto sin convertir sus defaults en hechos del proyecto.

## Prompts disponibles

| Prompt | Función |
|---|---|
| `prompts/analizar-codigo-completo.md` | Genera un informe archivo por archivo sobre arquitectura, flujo, FSM, dependencias, problemas, contradicciones y reutilización. |
| `prompts/generar-repo-map.md` | Genera un `repo-map.yml`/`archivo-mapa.yml` compacto y trazable para dar contexto a otra LLM. |
| `prompts/generar-readme.md` | Genera un README operativo para instalar, configurar, ejecutar y diagnosticar el proyecto. |
| `prompts/generar-contexto-agentes.md` | Genera contexto general y una skill accionable desde el target real, con matriz de consistencia. |
| `prompts/generar-arquitectura-verificable.md` | Genera arquitectura por claims, dependencias, flujos, variantes, límites y evidencia. |
| `prompts/generar-changelog-evidencial.md` | Genera historial basado en diffs/historia disponible, separando cambio de validación. |
| `prompts/generar-plan-ejecucion-canonico.md` | Genera fases con baseline, gates, aceptación, rollback, riesgos y trazabilidad. |
| `prompts/generar-roadmap-tecnico.md` | Prioriza gaps futuros con dependencias, riesgos, aceptación y validación. |
| `prompts/generar-ledger-bugs-evidencial.md` | Registra síntoma, causa, solución, aplicación, validación, regresión y criterios de cierre. |
| `prompts/generar-auditoria-protocolo.md` | Compara contratos y alternativas antes de recomendar reutilizar, adaptar o crear un protocolo. |
| `prompts/generar-especificacion-requisitos.md` | Convierte una necesidad en requisitos verificables, alternativas, decisiones, aceptación y fases. |
| `prompts/generar-checklist-cambio-seguro.md` | Ordena cambios acotados con baseline, precondiciones, validación, rollback y promoción manual. |
| `prompts/generar-preflight-contexto.md` | Construye la matriz de claims, sensibilidad, destino y condiciones antes de generar contexto. |
| `prompts/gen-notas-hw.md` | Genera notas de hardware y pinout a partir del código completo y su configuración. |
| `prompts/gen-conexiones-svg.md` | Genera un diagrama de conexiones draw.io SVG editable, limitado a conexiones físicas verificables. |
| `prompts/audit-hardware-docs.md` | Compara `notas.md` y el SVG contra el código y reporta omisiones, contradicciones y datos no demostrados. |
| `prompts/audit-project-docs.md` | Audita README, repo-map, notas, changelog y otros documentos contra el código actual. |

## Flujo recomendado

1. Elegir un **target concreto** del proyecto. No mezclar automáticamente placas o versiones incompatibles.
2. Adjuntar el prompt y proporcionar la raíz del proyecto completo.
3. Leer todos los archivos relevantes, incluyendo fuentes, headers, configuración de build y bibliotecas locales.
4. Generar primero las notas de hardware.
5. Generar el diagrama desde el inventario de hardware validado, no desde una interpretación independiente.
6. Ejecutar el prompt de auditoría después de cualquier cambio de pines, placa, módulos o conexiones.
7. Registrar manualmente cualquier confirmación hecha con datasheet, multímetro o hardware real.

## Bundle genérico de contexto compartido

El scaffold [`templates/project-context-bundle/`](templates/project-context-bundle/) recrea de forma genérica el patrón histórico `workspace-context-engineering/` sin copiar sus valores de proyecto. Es un bundle coordinado, no ocho herramientas independientes:

- `shared/CODING_STYLE.md` y `shared/SOFTWARE.md`: convenciones y entorno común, parametrizados.
- `project/.ai/PROJECT_CONTEXT.md`: punto de entrada mínimo y obligatorio.
- Templates condicionales: `HARDWARE.md`, `SKILL.md`, `TASKS.md`, `DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, `ARCHITECTURE.md`, `PROTOCOL.md` y `TESTING.md`.
- `project-context-bundle-manifest.json`: condiciones de generación, estados de evidencia y promoción bloqueada.

El preflight decide qué archivos condicionales tienen justificación. El contrato está en [`references/context-bundle-contract.md`](references/context-bundle-contract.md). PlatformIO/Arduino, Todo Tree, `115200` y `F()` no se tratan como requisitos universales: se registran como defaults o reglas condicionadas y deben confirmarse en el proyecto destinatario.

## Aplicación a `wifi_PIR`

`wifi_PIR` tiene más de un ensamblaje y más de una versión de firmware. Debe documentarse por separado, como mínimo:

- `emisor_pir` — D1 Mini, firmware V3.5.1.
- `receptor_bocina` — NodeMCU v2, firmware V3.5.1.
- `emisor_pir_v4` — D1 Mini, firmware V4.3.
- `receptor_central_v4` — NodeMCU v2, firmware V4.3.

La biblioteca `lib/IoTProtocol` y los archivos comunes deben analizarse como dependencias, pero no deben convertirse en conexiones físicas del diagrama. La red UDP, MQTT y OTA pertenecen a una sección lógica separada, no a un cable físico.

Una salida posible es:

```text
docs/hardware/
├── emisor_pir/
│   ├── notas.md
│   └── conexiones.drawio.svg
├── receptor_bocina/
│   ├── notas.md
│   └── conexiones.drawio.svg
├── emisor_pir_v4/
│   ├── notas.md
│   └── conexiones.drawio.svg
└── receptor_central_v4/
    ├── notas.md
    └── conexiones.drawio.svg
```

No se deben generar todavía esos documentos ni modificar el firmware al crear esta herramienta; primero se prepara el procedimiento reutilizable y después se ejecuta explícitamente sobre cada target.

## Reglas de seguridad y trazabilidad

- Nunca imprimir ni copiar secretos; documentar únicamente que existe una credencial o clave.
- Cada afirmación importante debe indicar su procedencia: archivo y línea/símbolo cuando sea posible.
- `INPUT`, `OUTPUT`, `INPUT_PULLUP`, nombres D/GPIO y niveles activo alto/bajo deben conservarse tal como aparecen en el código.
- No convertir un modelo de componente, voltaje o cableado en hecho solo porque sea habitual.
- Si el código no permite saber algo, escribir `PENDIENTE` o `NO DETERMINADO`.
- No borrar ni sobrescribir documentación existente sin comparar primero contra ella y registrar las diferencias.


## Capas de documentación

`codigo_tools` separa los artefactos por lector y propósito:

```text
analizar-codigo-completo.md → comprensión profunda y auditoría narrativa
        ↓
generar-repo-map.md         → contexto estructurado para LLM/agentes
        ↓
generar-readme.md          → instalación y operación para humanos
        ↓
gen-notas-hw.md           → pinout y notas de hardware
gen-conexiones-svg.md       → diagrama físico editable
        ↓
audit-*                    → reconciliación contra código/configuración
```

La referencia `references/tipos-documentacion.md` explica qué debe contener cada capa y evita duplicar prosa entre ellas. Las plantillas de `templates/` son esqueletos: sus placeholders no son datos reales de ningún proyecto.

## Aplicación a `reloj NPT`

Los artefactos se diseñaron a partir del análisis de `reloj NPT`:

- `generar-repo-map.md` consolida las variantes `prompt-repo-map.md` y `generar-archivo-mapa.md`.
- `generar-readme.md` conserva la estructura de `generar-readme.md`, pero elimina la obligación de inventar cinco problemas.
- `references/tipos-documentacion.md` incorpora la clasificación de `ress.md`.
- `templates/repo-map.yml` conserva el esquema del `archivo-mapa.yml` sin copiar sus valores específicos.
- `templates/README-project.md` conserva la estructura operativa sin incluir datos del reloj.

## Flujo recomendado por proyecto

1. Ejecutar `analizar-codigo-completo.md` sobre un `TARGET_ID` y snapshot concretos.
2. Usar el inventario y la matriz para generar `repo-map.yml`.
3. Generar o actualizar `README.md` sin ocultar divergencias.
4. Para hardware, generar `docs/notas.md` y después `docs/conexiones.drawio.svg`.
5. Ejecutar las auditorías correspondientes: `audit-hardware-docs.md` para hardware y `audit-project-docs.md` para el conjunto documental.
6. Registrar build, tests, simulación o hardware solo si realmente se ejecutaron.

No se deben mezclar targets, versiones, emisores/receptores o placas en una única documentación ambigua. Si falta un archivo o una dependencia, el artefacto debe detenerse con `LECTURA_INCOMPLETA`.


## Extracción reusable de `wifi_PIR/_drafts`

La extracción se hizo sobre dos capas históricas y no copia el firmware:

- Los **11 drafts pre-consolidación** (`BUGS_FIXED.md`, `META_PROMPT.md`, `ideas.md`, `plantilla de prompt.md`, `prodoco.md`, `prompt.md`, `prompt2.md`, `instrucciones.md`, `1mejoras.md`, `bugs.md` y el patch) aportaron contratos de ledger de bugs, requisitos, auditoría de protocolos, roadmap, checklist de cambios y documentación audit-first.
- La tanda ampliada del snapshot histórico aportó prompts de análisis, README, repo-map, hardware, contexto de agentes, catálogo, wiring y bundle `.ai`.

| Comportamiento extraído | Artefacto reusable | Estado de promoción |
|---|---|---|
| Lectura completa y trazable | `prompts/analizar-codigo-completo.md` | Integrado |
| Repo-map y README derivados | `prompts/generar-repo-map.md`, `prompts/generar-readme.md`, templates asociados | Integrado |
| Notas y diagrama físico | `prompts/gen-notas-hw.md`, `prompts/gen-conexiones-svg.md` | Integrado; el wiring concreto queda en el target |
| Auditoría documental/hardware | `prompts/audit-project-docs.md`, `prompts/audit-hardware-docs.md` | Integrado |
| Requisitos antes de implementar | `prompts/generar-especificacion-requisitos.md` cuando esté disponible en la rama enriquecida | Contrato extraído; no duplicar versiones |
| Ledger de defectos | `prompts/generar-ledger-bugs-evidencial.md` cuando esté disponible en la rama enriquecida | Contrato extraído; bugs concretos excluidos |
| Auditoría comparativa de protocolos | `prompts/generar-auditoria-protocolo.md` cuando esté disponible en la rama enriquecida | Variante reusable; protocolo de producto excluido |
| Arquitectura, changelog, plan y roadmap evidenciales | prompts documentales correspondientes de la línea enriquecida | Contratos extraídos; estados deben revisarse antes de promoción |
| Cambio seguro y promoción manual | `prompts/generar-checklist-cambio-seguro.md` | Integrado en esta extracción |
| Preflight de claims y bundle | `prompts/generar-preflight-contexto.md` | Integrado en esta extracción |
| Bundle coordinado de contexto | `templates/project-context-bundle/` | Scaffold genérico, promoción manual |
| Validación de bundle y gaps de catálogo | `tools/validate_context_bundle.py` | Integrado como herramienta report-only |

El patch `v4.3.1-security.patch`, el firmware, los pines, wiring, protocolos, credenciales, IPs, topics, modelos y valores de producto permanecen fuera de alcance. Una fuente histórica puede demostrar que existió una propuesta; no demuestra que esté implementada ni validada.

## Flujo completo de extracción y uso

```text
fuente histórica → lectura completa → matriz de trazabilidad → revisión semántica
                → prompt/template genérico → preflight → scaffold en salida separada
                → validate_context_bundle → revisión humana → promoción manual
```

Comandos principales:

```bash
# Preparar el contexto antes de generar documentos
# El prompt es report-only y requiere proporcionar PROJECT_ROOT/TARGET_ID/SNAPSHOT.

# Validar un bundle sin modificarlo
python3 codigo_tools/tools/validate_context_bundle.py validate /ruta/proyecto \
  --output /ruta/reportes/context-bundle.json

# Detectar referencias de catálogo ausentes desde project-wiring.json
python3 codigo_tools/tools/validate_context_bundle.py catalog-gap /ruta/proyecto \
  --catalog-root codigo_tools/catalog \
  --output /ruta/reportes/catalog-gap.json
```

La herramienta no corrige enlaces, no ejecuta builds, no crea fichas, no imprime secretos y no promociona archivos. Para cambiar el repositorio fuente debe existir una autorización independiente y un checklist de cambio seguro.

## Artefactos deliberadamente no promovidos

No se convierten en herramientas globales los datos concretos de las fichas de boards/peripherals, los proyectos de ejemplo, los SVG de wiring, los `platformio.ini`, el firmware, el patch de seguridad ni las configuraciones de producto. Las fichas técnicas solo pueden entrar al catálogo tras validación por modelo/variante y procedencia por campo; los gaps generan reportes, no publicaciones automáticas.
