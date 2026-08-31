# Generar arquitectura verificable

## Propósito

Genera una arquitectura técnica de `[PROJECT_ROOT]` para que otro mantenedor o LLM pueda entender el sistema sin confundir código actual, historia, intención, despliegue o hipótesis. Este prompt produce una vista derivada de evidencia; no modifica el proyecto, no ejecuta cambios y no convierte un diagrama en fuente de verdad.

La calidad mínima exige el mismo protocolo de investigación que una documentación técnica de hardware rigurosa: alcance cerrado, inventario demostrable, lectura transitiva, claims trazables, parada segura y auditoría final contra las fuentes primarias.

## Entradas obligatorias

```text
PROJECT_ROOT: [ruta absoluta de la raíz]
TARGET_ID: [target, variante o sistema exacto]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta del documento]
```

## Entradas opcionales

```text
ARCHITECTURE_BASELINE: [ruta o NONE]
CHANGELOG_BASELINE: [ruta o NONE]
EXECUTION_PLAN_BASELINE: [ruta o NONE]
ROADMAP_BASELINE: [ruta o NONE]
VALIDATION_EVIDENCE: [builds, tests, logs, integración, despliegue o NONE]
ALLOWED_EXTERNAL_SOURCES: [datasheets, tickets, runbooks o NONE]
LANGUAGE: [idioma]
```

No asumas que una carpeta contiene un único target. Si hay varias variantes, enuméralas con sus archivos de build, plataforma, entry points y estado; pide selección o genera documentos separados. Nunca mezcles variantes porque compartan nombres de módulos.

## Estados y vocabularios

Separa dos dimensiones que nunca deben colapsarse:

### Estado epistemológico

```text
OBSERVED_IN_CODE       operación, relación o valor localizado en código/configuración
OBSERVED_IN_BUILD      declarado o resuelto por el sistema de build
DOCUMENTED             afirmado por un documento
INFERRED               deducido; requiere explicación y confianza
CONTRADICTED           una fuente confiable discrepa
UNKNOWN                no hay evidencia suficiente
INCOMPLETE_READ        depende de una fuente no leída por completo
EXTERNAL_UNVERIFIED    depende de despliegue, hardware o fuente externa no adjunta
```

### Estado de ejecución

```text
NOT_EXECUTED
COMPILED
TESTED
INTEGRATION_VERIFIED
HARDWARE_VERIFIED
```

`OBSERVED_IN_CODE` nunca significa `WORKS`. `COMPILED` nunca significa `HARDWARE_VERIFIED`.

## Fase 0 — Alcance y línea base

Antes de redactar, entrega un registro interno con:

```text
Target seleccionado:
Snapshot y método para obtenerlo:
Variantes incluidas:
Variantes excluidas y motivo:
Entorno(s) de build:
Entry points:
Documentos baseline:
Evidencia de validación:
Fuentes externas autorizadas:
```

Cada claim debe pertenecer a un `TARGET_ID` y snapshot. Si el snapshot es `UNKNOWN`, no inventes una versión. Si el alcance es ambiguo, detén la arquitectura final con `INPUT_AMBIGUOUS` y devuelve solo el inventario y las preguntas necesarias.

## Fase 1 — Inventario completo y auditable

Recorre todo el proyecto y clasifica cada archivo relevante como código, configuración, build, dependencia local, test, CI, script, documentación, schema o artefacto generado. Registra:

```text
FILE_ID | ruta relativa | tipo | bytes/líneas | hash si está disponible |
read_state | chunks | rol | target(s) | usado como evidencia
```

Debes leer completamente, cuando existan:

- entry points y módulos llamados;
- headers/includes e imports transitivos;
- `platformio.ini`, `CMakeLists.txt`, `package.json`, `pyproject.toml`, Makefiles y build flags;
- bibliotecas locales, manifests y fuentes compartidas;
- configuración, schemas, scripts de generación y CI;
- tests, fixtures y herramientas de simulación;
- README, arquitectura, changelog, plan, roadmap y documentación baseline.

Para archivos grandes usa chunks con IDs estables:

```text
FILE_ID-C01 | líneas inicial-final | estado | hash opcional
```

El índice de chunks debe permitir volver a la fuente. Un resumen no sustituye la lectura del chunk.

Si falta, está truncado, es ilegible o no puede resolverse una dependencia requerida, marca `INCOMPLETE_READ`. No generes un documento que parezca completo: entrega `LECTURA_INCOMPLETA`, inventario, dependencias pendientes y preguntas.

## Fase 2 — Cierre de dependencias y extracción de arquitectura

Sigue las relaciones reales hasta punto fijo. Busca y registra usos, no solo declaraciones:

- funciones de entrada y salida, handlers y callbacks;
- llamadas entre módulos, constructores, interfaces y adapters;
- colas, máquinas de estado, timers, retries, locks y prioridades;
- persistencia, serialización, protocolos, buses y formatos;
- configuración que altera el camino de ejecución;
- errores, timeouts, recuperación y efectos secundarios;
- servicios externos y condiciones de despliegue.

Construye un modelo interno de nodos y aristas:

```text
EDGE_ID | origen | destino | relación | condición |
fuente/rango/símbolo | estado | confianza | destino documental
```

Una arista basada solo en nombres, proximidad de archivos o documentación no confirmada no puede aparecer como relación observada.

## Fase 3 — Registro de claims

Antes de escribir prosa, crea una fila por afirmación relevante:

```text
CLAIM_ID | target | afirmación normalizada | tipo de claim |
fuente primaria | rango/símbolo/chunk | fuente secundaria |
estado epistemológico | confianza | conflicto | sección destino |
limitación | estado de ejecución
```

Clasifica los claims por: identidad, componente, responsabilidad, flujo, interfaz, dependencia, variante, configuración, seguridad, rendimiento, despliegue o riesgo.

Jerarquía por tipo de claim:

- estado actual y comportamiento: código/configuración del snapshot;
- cambio histórico: commit/diff/tag, si existe;
- decisión: decisión aprobada o plan con estado explícito;
- intención futura: plan/roadmap, siempre `PROPOSED`;
- compilación/test/integración/hardware: solo evidencia de ejecución;
- despliegue externo: evidencia externa autorizada, si existe.

Cuando dos fuentes discrepan, registra ambas, explica cuál tiene autoridad para ese tipo de claim y conserva el conflicto.

## Fase 4 — Redacción del documento

Genera `OUTPUT_PATH` con esta estructura mínima:

```markdown
# Arquitectura — [TARGET_ID]

> Snapshot: [SNAPSHOT]
> Estado documental: DRAFT | GENERATED | AUDITED
> Cobertura: COMPLETE | INCOMPLETE_READ

## 1. Alcance y variantes
## 2. Resumen del sistema
## 3. Componentes y responsabilidades
## 4. Flujos de entrada, procesamiento, salida y recuperación
## 5. Interfaces y contratos observados
## 6. Dependencias y configuración que altera el comportamiento
## 7. Versiones, targets y estados CURRENT/HISTORICAL/PROPOSED
## 8. Invariantes, límites, riesgos y fallos conocidos
## 9. Comunicaciones lógicas y servicios externos
## 10. Diagrama abstracto de relaciones verificadas
## 11. Contradicciones y decisiones pendientes
## 12. Matriz de claims y procedencia
## 13. Validación ejecutada y no ejecutada
## 14. Parámetros que otro proyecto debe completar
## 15. Cobertura, exclusiones y limitaciones
```

Cada componente debe indicar responsabilidad, interfaces, fuentes y estado. Cada flujo debe indicar entrada, precondición, pasos, salida, error y recuperación. El diagrama se genera exclusivamente de la matriz de aristas y debe distinguir relación lógica, dependencia de software, transporte y conexión física; nunca dibujes WiFi, UDP, MQTT, OTA, topics o APIs como cables eléctricos.

## Generalización y seguridad

- No copies firmware, nombres de productos, hosts, IPs, pines, topics, IDs, rutas privadas, credenciales, claves, tokens ni valores de despliegue.
- En el documento reusable usa placeholders tipados: `[MODULE]`, `[INTERFACE]`, `[TARGET_ID]`, `[ENDPOINT]`, `[DEVICE_ID]`, `[CONFIG_KEY]`.
- La evidencia interna debe conservar solo ruta, símbolo, rango, hash y categoría; redacta valores sensibles.
- No deduzcas hardware, voltaje, rendimiento, disponibilidad, no-bloqueo o despliegue desde una convención.
- Una dependencia declarada en build prueba configuración, no compilación exitosa.
- Una función disponible en una biblioteca no prueba que el camino real la invoque.

## Fase 5 — Replay y auditoría final

Después de redactar, vuelve a revisar las fuentes primarias completas, no el resumen. Comprueba:

1. Cada componente, arista, flujo e interfaz tiene claim y fuente.
2. No se mezclaron targets, variantes, producción, laboratorio o historia.
3. Cada estado actual/histórico/propuesto está etiquetado.
4. Las contradicciones no fueron ocultadas.
5. Cada claim importante tiene sección destino o exclusión justificada.
6. No aparecen secretos ni valores product-specific en la salida reusable.
7. El diagrama coincide exactamente con las aristas permitidas.
8. Build, tests, integración y hardware no ejecutados aparecen como `NOT_EXECUTED`.
9. La cobertura del inventario coincide con la matriz.

Si una comprobación falla, el estado debe ser `AUDIT_FAILED`; no declares la arquitectura terminada.

## Salida de error y revisión

Si la lectura es incompleta, devuelve un informe limitado con inventario, archivos faltantes, dependencias no resueltas, claims afectados y `LECTURA_INCOMPLETA`. Si hay contradicciones irresueltas, usa `CONFLICT_UNRESOLVED`. Toda salida requiere revisión humana; este prompt no autoriza promoción ni commit.
