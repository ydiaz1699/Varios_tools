# Generar una especificación para recrear un artefacto documental

## Propósito

Usa este prompt cuando exista un proyecto fuente completo y un artefacto documental que se desea reproducir en otros proyectos. El resultado no es una copia del documento fuente ni una adaptación del firmware: es una especificación y un prompt genérico que explican cómo generar el mismo tipo de artefacto a partir de la evidencia de otro proyecto.

El flujo debe responder esta pregunta:

> ¿Qué contrato, entradas, reglas, condiciones y validaciones se pueden inferir de este proyecto y de su artefacto documental para generar un equivalente parametrizable en otro proyecto?

El proyecto fuente es procedencia y caso de estudio. No es un destino de integración. No modifiques sus archivos.

## Entradas

Sustituye los valores entre corchetes por rutas y datos reales:

```text
PROJECT_ROOT: [ruta absoluta del proyecto fuente]
TARGET_ID: [identificador estable y no sensible del artefacto]
SNAPSHOT: [commit, tag o identificador de procedencia; si no existe, UNKNOWN]
DOCUMENT_PATH: [ruta del artefacto documental dentro de PROJECT_ROOT]
EXISTING_PROMPT_PATHS: [cero o más prompts que aparentemente generan el artefacto]
BASELINE_PATHS: [artefactos relacionados, si existen]
OUTPUT_ROOT: [ruta fuera de PROJECT_ROOT donde se escribirán las salidas]
```

`EXISTING_PROMPT_PATHS` es opcional. Si no hay prompt equivalente, el procedimiento debe inferirlo a partir de la relación entre el proyecto completo, el artefacto y sus documentos relacionados.

## Reglas no negociables

1. Lee el proyecto completo de forma progresiva y verificable. Recorre todos los archivos relevantes, no solo los que parecen relacionados por nombre.
2. Lee `DOCUMENT_PATH` completo, incluyendo todas sus secciones, tablas, listas, enlaces y bloques de código.
3. Lee por completo cada prompt existente, baseline y documento relacionado que se use como evidencia.
4. Sigue imports, includes, referencias cruzadas, scripts, configuraciones, comandos de build, archivos de CI y documentación operativa hasta entender qué comportamiento está realmente respaldado por el código.
5. Registra cualquier archivo ausente, ilegible, truncado o no procesado como `LECTURA_INCOMPLETA`. No presentes una inferencia como definitiva si depende de una lectura incompleta.
6. Separa siempre cuatro clases de contenido:
   - `REUSABLE`: reglas y estructura transferibles a otros proyectos.
   - `PARAMETRIZABLE`: nombres, rutas, targets, comandos, secciones y convenciones que deben sustituirse.
   - `PRODUCT_SPECIFIC`: comportamiento, hardware, pines, topología, protocolos configurados, nombres de dispositivos y valores del proyecto fuente.
   - `SENSITIVE`: secretos, credenciales, tokens, claves, SSID, direcciones privadas, UUID, MAC y cualquier valor que permita identificar o acceder al proyecto.
7. Nunca copies firmware, código de producto, secretos o valores concretos al prompt genérico ni a la especificación. Puedes describir su función abstracta y conservar únicamente nombres de campos o categorías necesarias para parametrizar el proceso.
8. No inventes hardware, dependencias, relaciones, objetivos, fechas, comandos ni estados. Cada afirmación debe tener una fuente y un estado de evidencia.
9. Trata documentos como `ROADMAP.md` como documentación histórica, propuesta o de planificación, no como verdad ejecutable. Contrasta sus afirmaciones con el código y marca las contradicciones.
10. No promociones ni publiques automáticamente ningún artefacto. La salida debe conservar `promotion_allowed: false` y `review_required: true`.
11. Escribe todas las salidas bajo `OUTPUT_ROOT`, nunca dentro de `PROJECT_ROOT` ni dentro de `codigo_tools` salvo que el usuario lo solicite explícitamente después de una revisión.

## Procedimiento

### 1. Inventario y estado de lectura

Construye un inventario archivo por archivo con, como mínimo:

- ruta relativa;
- tipo y papel probable: código, configuración, documentación, prompt, plantilla, script, test, CI u otro;
- tamaño en bytes y líneas;
- hash SHA-256 cuando sea posible;
- headings, referencias y marcadores relevantes;
- estado de lectura: `COMPLETE`, `PARTIAL`, `MISSING`, `UNREADABLE`;
- clasificación de contenido según las cuatro clases anteriores;
- si el archivo se usó como evidencia de una afirmación.

No incluyas cuerpos completos de archivos de producto en las salidas. El inventario puede contener metadatos, resúmenes abstractos y referencias de línea, pero debe omitir valores sensibles.

### 2. Comprensión del artefacto

Describe el artefacto fuente sin reproducirlo. Determina:

- `artifact_type`: por ejemplo, roadmap, mapa de archivos, guía operativa, arquitectura, changelog o inventario;
- `document_role`: qué decisión o necesidad satisface;
- audiencia y momento de uso;
- secciones que siempre aparecen y secciones condicionales;
- entradas explícitas e implícitas;
- salidas y efectos esperados;
- reglas de inclusión, exclusión, orden y formato;
- claims que el documento realiza;
- qué partes proceden del código, qué partes son planificación y qué partes son convenciones editoriales;
- qué debe omitirse cuando la evidencia no existe.

Para cada conclusión, registra la fuente y uno de estos estados:

```text
CONFIRMED       respaldada directamente por código o documentación coherente
INFERRED        deducida de varios indicios, pero no expresada literalmente
CONTRADICTED    contradicha por otra fuente o por el código
UNKNOWN         no puede determinarse con la evidencia disponible
LECTURA_INCOMPLETA depende de archivos que no se pudieron leer por completo
```

### 3. Reconstrucción del contrato de generación

Si existe un prompt equivalente, analízalo completo y compara sus instrucciones con el artefacto generado. Identifica qué reglas están explícitas, cuáles faltan y cuáles son específicas del proyecto.

Si no existe un prompt equivalente, infiere el contrato comparando:

1. el contenido y la estructura del artefacto;
2. la implementación y configuración del proyecto;
3. prompts, plantillas, scripts y documentos relacionados;
4. el historial o las convenciones locales, solo si están disponibles y son relevantes.

Explica cada inferencia con una cadena de trazabilidad:

```text
regla abstracta → evidencia → estado → limitación
```

No conviertas una coincidencia visual en una regla universal. Distingue una convención reutilizable de una decisión accidental del proyecto fuente.

### 4. Parametrización

Transforma los detalles específicos en parámetros con nombres claros. Como mínimo considera:

- identidad del proyecto y snapshot;
- raíz del proyecto y rutas de salida;
- tipo y nombre del artefacto;
- lenguaje o plataformas solo cuando cambien el análisis;
- fuentes de evidencia;
- comandos de build, test o análisis como plantillas, no como valores fijos;
- nombres de módulos, targets, dispositivos o servicios;
- secciones y formatos de salida;
- criterios para incluir, actualizar, omitir o marcar una sección;
- política de conflictos y evidencia insuficiente.

Usa placeholders descriptivos como `[PROJECT_ROOT]`, `[TARGET_ID]` o `[OUTPUT_PATH]`. No dejes valores del proyecto fuente en los defaults del prompt genérico.

### 5. Condiciones y conflictos

Define explícitamente:

- condiciones que permiten generar el artefacto;
- condiciones que obligan a generar una versión parcial con advertencias;
- condiciones que obligan a omitir una sección;
- condiciones que deben bloquear la generación;
- cómo resolver contradicciones entre código, documentación, prompt existente y baselines;
- cuándo conservar una afirmación como histórica en vez de presentarla como estado actual;
- qué debe pedir el LLM al usuario cuando falta una decisión esencial.

La ausencia de hardware o de una relación en el código no autoriza a inventarla. Cuando la evidencia es insuficiente, usa `UNKNOWN`, `PENDING_REVIEW` o una omisión justificada.

### 6. Revisión de seguridad y procedencia

Redacta los nombres de secretos y todos sus valores. No imprimas secretos en informes ni en errores. Señala qué archivos contenían material sensible mediante metadatos abstractos, por ejemplo `secret_field_present: true`, sin revelar el valor.

Conserva procedencia para cada salida:

- proyecto fuente y snapshot;
- artefacto analizado;
- archivos fuente usados;
- fecha de análisis si está disponible;
- estado de lectura;
- limitaciones conocidas;
- necesidad de revisión humana.

## Salidas obligatorias

Escribe exactamente estos tres archivos en `OUTPUT_ROOT`:

### `recreator-spec.json`

Especificación normalizada y validable. Debe seguir el contrato de `recreator-spec-contract.md` y contener, como mínimo:

- identidad y procedencia;
- descripción del artefacto y `document_role`;
- fuentes e inventario de lectura;
- capacidades, entradas y salidas;
- `behavioral_contract`;
- `reconstruction_steps`;
- `generation_conditions` y `omission_conditions`;
- conflictos con el código o la documentación;
- clasificación reusable/parametrizable/específica/sensible;
- `output_artifacts`;
- verificación, limitaciones y relaciones;
- `promotion: {"promotion_allowed": false, "review_required": true}`.

### `recreator-prompt.md`

Prompt autónomo y genérico para que otro LLM genere el mismo tipo de artefacto en un proyecto distinto. Debe:

- recibir parámetros explícitos;
- exigir lectura completa y estados de evidencia;
- explicar qué archivos debe consultar;
- definir el formato y las secciones de salida;
- tratar conflictos, ausencias y documentación histórica;
- usar placeholders, no datos del proyecto fuente;
- ordenar los pasos de forma ejecutable;
- declarar qué nunca debe inventar ni copiar;
- exigir revisión humana antes de promoción.

El prompt no debe depender de que el LLM conozca `PROJECT_ROOT` como el proyecto fuente ni debe mencionar firmware, pines o nombres concretos salvo como categorías abstractas.

### `review.md`

Informe de revisión para un humano con:

- resumen del artefacto reconstruido;
- matriz de trazabilidad regla → fuente → estado;
- inventario de archivos leídos y no leídos;
- comparación con prompt existente, si lo había;
- contradicciones y decisiones;
- contenido integrado, rechazado con motivo, fuera de alcance y pendiente;
- parámetros que deben completar otros proyectos;
- riesgos de sobre-generalización;
- comprobaciones realizadas;
- lista de preguntas abiertas;
- confirmación explícita de que no se promovió la salida.

## Criterios de aceptación

Antes de finalizar, verifica todos estos puntos:

- El proyecto y el documento se leyeron completos o las limitaciones quedaron marcadas.
- El documento fuente no se copió como template literal.
- El prompt existente se analizó si fue proporcionado.
- El prompt genérico funciona sin conocer los valores del proyecto fuente.
- Las reglas tienen trazabilidad y estado de evidencia.
- Las contradicciones con el código no fueron ocultadas.
- Los secretos y valores identificables no aparecen en las salidas.
- Las rutas y comandos están parametrizados.
- Las condiciones de generación y omisión son explícitas.
- `promotion_allowed` es `false` y `review_required` es `true`.
- Todas las salidas están fuera de `PROJECT_ROOT`.
- La revisión declara qué no pudo determinarse.

Si alguno de estos criterios falla, no declares el recreador como terminado: deja el estado pendiente y explica el bloqueo en `review.md`.
