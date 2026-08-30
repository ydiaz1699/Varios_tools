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
│   ├── gen-notas-hw.md
│   ├── gen-conexiones-svg.md
│   └── audit-hardware-docs.md
└── references/
    └── criterios.md
```

Los prompts son independientes y se pueden copiar o adjuntar a otra LLM. `references/criterios.md` documenta el método común, pero un prompt debe repetir las reglas críticas que necesita para no depender de que ese archivo también sea adjuntado.

## Prompts disponibles

| Prompt | Función |
|---|---|
| `prompts/gen-notas-hw.md` | Genera notas de hardware y pinout a partir del código completo y su configuración. |
| `prompts/analizar-codigo-completo.md` | Genera un informe archivo por archivo sobre arquitectura, flujo, FSM, dependencias, problemas, contradicciones y reutilización. |
| `prompts/gen-conexiones-svg.md` | Genera un diagrama de conexiones draw.io SVG editable, limitado a conexiones físicas verificables. |
| `prompts/audit-hardware-docs.md` | Compara `notas.md` y el SVG contra el código y reporta omisiones, contradicciones y datos no demostrados. |

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
