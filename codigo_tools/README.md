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
│   ├── detectar-evolucionar-artefactos.md
│   ├── generar-repo-map.md
│   ├── generar-readme.md
│   ├── generar-contexto-agentes.md
│   ├── gen-notas-hw.md
│   ├── gen-conexiones-svg.md
│   ├── audit-hardware-docs.md
│   ├── audit-project-docs.md
│   ├── generar-ficha-board.md
│   ├── generar-ficha-periferico.md
│   ├── generar-project-wiring.md
│   └── auditar-compatibilidad-hardware.md
├── references/
│   ├── criterios.md
│   ├── hardware-catalog-policy.md
│   ├── hardware-evidence.md
│   ├── politica-evolucion-artefactos.md
│   └── tipos-documentacion.md
├── catalog/
│   ├── README.md
│   ├── schemas/
│   │   ├── board.schema.json
│   │   ├── peripheral.schema.json
│   │   └── project-wiring.schema.json
│   ├── boards/
│   │   ├── index.json
│   │   └── _template-board.json
│   ├── peripherals/
│   │   ├── index.json
│   │   └── _template-peripheral.json
│   └── compatibility/
│       └── rules.json
├── templates/
│   ├── repo-map.yml
│   ├── README-project.md
│   ├── SKILL-project.md
│   ├── copilot-instructions.md
│   ├── artifact-manifest.json
│   ├── artifact-evolution-report.json
│   └── project-wiring.json
└── tools/
    ├── artifact_evolution.py
    └── hardware_catalog.py
```

Los prompts son independientes y se pueden copiar o adjuntar a otra LLM. `references/criterios.md` documenta el método común, pero un prompt debe repetir las reglas críticas que necesita para no depender de que ese archivo también sea adjuntado.

## Prompts disponibles

| Prompt | Función |
|---|---|
| `prompts/gen-notas-hw.md` | Genera notas de hardware y pinout a partir del código completo y su configuración. |
| `prompts/analizar-codigo-completo.md` | Genera un informe archivo por archivo sobre arquitectura, flujo, FSM, dependencias, problemas, contradicciones y reutilización. |
| `prompts/detectar-evolucionar-artefactos.md` | Detecta material reusable y decide si es nuevo, mejora, duplicado, contradictorio, variante o no decidible. |
| `prompts/generar-repo-map.md` | Genera un `repo-map.yml`/`archivo-mapa.yml` compacto y trazable para dar contexto a otra LLM. |
| `prompts/generar-readme.md` | Genera un README operativo para instalar, configurar, ejecutar y diagnosticar el proyecto. |
| `prompts/generar-contexto-agentes.md` | Genera y compara `copilot-instructions.md` y `SKILL.md` desde el código y la configuración actuales. |
| `prompts/gen-conexiones-svg.md` | Genera un diagrama de conexiones draw.io SVG editable, limitado a conexiones físicas verificables. |
| `prompts/audit-hardware-docs.md` | Compara `notas.md` y el SVG contra el código y reporta omisiones, contradicciones y datos no demostrados. |
| `prompts/audit-project-docs.md` | Audita README, repo-map, notas, changelog y otros documentos contra el código actual. |
| `prompts/generar-ficha-board.md` | Genera una ficha de catálogo para una placa física, separada del wiring de proyectos. |
| `prompts/generar-ficha-periferico.md` | Genera una ficha de módulo separando VCC, lógica, protocolo, variante y requisitos. |
| `prompts/generar-project-wiring.md` | Genera el manifest de conexiones de un proyecto referenciando boards y peripherals. |
| `prompts/auditar-compatibilidad-hardware.md` | Audita pines, niveles, buses, variantes y compatibilidad entre catálogo y wiring. |

## Flujo recomendado

1. Elegir un **target concreto** del proyecto. No mezclar automáticamente placas o versiones incompatibles.
2. Adjuntar el prompt y proporcionar la raíz del proyecto completo.
3. Leer todos los archivos relevantes, incluyendo fuentes, headers, configuración de build y bibliotecas locales.
4. Generar primero las notas de hardware.
5. Generar el diagrama desde el inventario de hardware validado, no desde una interpretación independiente.
6. Ejecutar el prompt de auditoría después de cualquier cambio de pines, placa, módulos o conexiones.
7. Registrar manualmente cualquier confirmación hecha con datasheet, multímetro o hardware real.

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

## Contexto para agentes

El prompt `prompts/generar-contexto-agentes.md` genera dos archivos complementarios a partir del target real:

- `templates/copilot-instructions.md` — instrucciones generales del repositorio, plataforma, reglas, estilo, verificación y procedencia.
- `templates/SKILL-project.md` — procedimiento accionable para una tarea recurrente concreta.

No deben confundirse con la documentación del producto. `copilot-instructions.md` y `SKILL.md` son contexto de trabajo para agentes; el código sigue siendo la fuente de comportamiento. Antes de entregar ambos archivos se debe comparar la matriz de consistencia para detectar valores divergentes, por ejemplo target, dependencias, pines, umbrales, timeouts y comandos. Los secretos se redactan y los builds/tests no ejecutados se marcan como pendientes.

## Detección y evolución de artefactos

El prompt `prompts/detectar-evolucionar-artefactos.md` añade una capa meta al flujo: durante el análisis de cada proyecto busca prompts, plantillas, referencias, auditorías, skills, instrucciones de agentes y herramientas que puedan reutilizarse. No compara únicamente nombres o archivos completos; exige extraer un manifiesto normalizado con propósito, capacidades, entradas, salidas, claims, compatibilidad y procedencia.

La política `references/politica-evolucion-artefactos.md` define seis decisiones:

- `NUEVO`: no existe un equivalente reutilizable.
- `MEJORA`: el artefacto existe, pero el candidato aporta cobertura, evidencia, validación o reglas nuevas.
- `DUPLICADO`: solo cambia redacción, orden o formato.
- `CONTRADICTORIO`: la misma regla tiene valores incompatibles.
- `VARIANTE`: la capacidad es similar, pero cambia target, framework, formato o dependencia.
- `NO_DECIDIBLE`: falta lectura, procedencia, propósito o evidencia.

Las plantillas `templates/artifact-manifest.json` y `templates/artifact-evolution-report.json` permiten intercambiar datos de forma estructurada. `tools/artifact_evolution.py` ofrece una base determinista para inventariar candidatos, validar manifiestos y comparar un candidato contra un catálogo:

```bash
python3 codigo_tools/tools/artifact_evolution.py discover /ruta/proyecto \\
  --output reports/artifact-candidates.json
python3 codigo_tools/tools/artifact_evolution.py catalog codigo_tools \\
  --output catalog/artifacts-discovered.json
python3 codigo_tools/tools/artifact_evolution.py validate candidates/mi-artefacto.json
python3 codigo_tools/tools/artifact_evolution.py compare \\
  --candidate candidates/mi-artefacto.json \\
  --catalog catalog/artifacts.json \\
  --output reports/mi-artefacto.json \\
  --markdown reports/mi-artefacto.md
```

`catalog` construye un índice heurístico de los archivos candidatos existentes. Antes de aceptarlo como catálogo canónico, hay que normalizar sus propósitos y capacidades con el prompt y revisar sus fuentes. La herramienta determinista sirve para inventario, validación y preselección; la decisión semántica final requiere el manifiesto normalizado y revisión de evidencia.

Flujo completo recomendado:

```text
analizar-codigo-completo
        ↓
manifest normalizado del candidato
        ↓
detectar-evolucionar-artefactos + artifact_evolution.py
        ↓
NUEVO / MEJORA / DUPLICADO / CONTRADICTORIO / VARIANTE / NO_DECIDIBLE
        ↓
propuesta revisable y aprobación
        ↓
crear o mejorar codigo_tools
        ↓
auditar y actualizar catálogo
```


1. Ejecutar `analizar-codigo-completo.md` sobre un `TARGET_ID` y snapshot concretos.
2. Usar el inventario y la matriz para generar `repo-map.yml`.
3. Generar o actualizar `README.md` sin ocultar divergencias.
4. Para hardware, generar `docs/notas.md` y después `docs/conexiones.drawio.svg`.
5. Ejecutar las auditorías correspondientes: `audit-hardware-docs.md` para hardware y `audit-project-docs.md` para el conjunto documental.
6. Registrar build, tests, simulación o hardware solo si realmente se ejecutaron.

## Catálogo híbrido de hardware

El catálogo usa un motor común con tres espacios separados:

```text
catalog/boards/       → modelos físicos de placas y variantes
catalog/peripherals/  → módulos, sensores, displays, radios y actuadores
project-wiring.json   → conexiones concretas de un target
```

La separación evita mezclar las especificaciones genéricas de una placa con el wiring de un proyecto. Los índices seleccionan; las fichas documentan; el manifest resuelve la instancia; las reglas de `catalog/compatibility/` detectan incompatibilidades obvias.

La procedencia es obligatoria para los datos técnicos. Deben distinguirse VCC, nivel lógico, señal, corriente, protocolo, variante y estado de verificación. El catálogo es contexto reusable: si el código/configuración actual contradice una ficha, se registra `CONTRADICTORIO` o `PENDIENTE_DE_VERIFICAR` y no se corrige silenciosamente.

Herramienta común:

```bash
python3 codigo_tools/tools/hardware_catalog.py validate --type board catalog/boards/_template-board.json
python3 codigo_tools/tools/hardware_catalog.py validate --type peripheral catalog/peripherals/_template-peripheral.json
python3 codigo_tools/tools/hardware_catalog.py validate --type wiring templates/project-wiring.json
python3 codigo_tools/tools/hardware_catalog.py search --type board --catalog-root catalog esp32
python3 codigo_tools/tools/hardware_catalog.py check-project --catalog-root catalog path/to/project-wiring.json
```

`hardware_catalog.py` valida estructura, referencias, pines repetidos, pines boot/reservados y mismatches lógicos declarados. No sustituye datasheets, mediciones ni pruebas físicas. Los prompts de generación y auditoría deben ejecutarse sobre el proyecto real antes de afirmar una conexión.

No se deben mezclar targets, versiones, emisores/receptores o placas en una única documentación ambigua. Si falta un archivo o una dependencia, el artefacto debe detenerse con `LECTURA_INCOMPLETA`.
