# Generar changelog evidencial

## Propósito

Genera o actualiza un changelog que explique la evolución real de `[PROJECT_ROOT]` sin inventar versiones, fechas, commits, resultados ni releases. El documento narrativo debe ser una vista derivada de un inventario histórico y una tabla delta verificable.

Este prompt documenta cambios; no ejecuta cambios, no convierte un roadmap en release y no sustituye la historia de control de versiones.

## Entradas obligatorias

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target o variante exacta]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta del changelog]
```

## Entradas opcionales

```text
PREVIOUS_CHANGELOG: [ruta o NONE]
HISTORY_SOURCE: [git log, commits, tags, diffs, releases, tickets o NONE]
RELATED_ARCHITECTURE: [ruta o NONE]
RELATED_EXECUTION_PLAN: [ruta o NONE]
RELATED_ROADMAP: [ruta o NONE]
VALIDATION_EVIDENCE: [builds, tests, logs, integración, hardware o NONE]
LANGUAGE: [idioma]
```

Si `HISTORY_SOURCE` no existe, no fabriques cronología. Puedes generar un changelog de estado documentado, pero cada fecha, versión y causalidad histórica debe ser `UNKNOWN` o `DOCUMENTED`, nunca confirmada por intuición.

## Estados separados

### Estado del cambio

```text
OBSERVED_IN_DIFF       cambio localizado en diff/commit/tag
PRESENT_IN_SNAPSHOT    resultado presente en el árbol seleccionado
DOCUMENTED_ONLY        narrado pero no localizado en historia/código
PROPOSED               intención futura
PARTIAL                parte del cambio localizada o aplicada
REVERTED               cambio deshecho por una reversión
REJECTED               descartado con evidencia
UNKNOWN                no determinable
INCOMPLETE_READ        fuente histórica requerida no leída completamente
```

### Estado de validación

```text
NOT_EXECUTED
COMPILED
TESTED
INTEGRATION_VERIFIED
HARDWARE_VERIFIED
EXTERNAL_UNVERIFIED
```

Un commit prueba que ocurrió un cambio; no prueba que funcionó. Un build prueba compilación; no prueba integración ni hardware.

## Fase 0 — Alcance y baseline

Registra:

```text
Target seleccionado:
Snapshot actual:
Rango histórico consultado:
Tags/releases incluidos:
Variantes incluidas/excluidas:
Changelog anterior:
Fuentes históricas disponibles:
Fuentes históricas ausentes:
Evidencia de validación:
```

Si existen varias ramas, productos o entornos, no los mezcles. Si el target o rango histórico son ambiguos, devuelve `INPUT_AMBIGUOUS` con las alternativas.

## Fase 1 — Inventario de fuentes

Inventaría por separado:

1. árbol actual: código, configuración, build, tests, CI, scripts y documentación;
2. historia: commits, merges, tags, releases, diffs, reverts y tickets disponibles;
3. validación: resultados de build, tests, integración, despliegue y hardware;
4. baselines narrativos.

Usa este registro:

```text
SOURCE_ID | tipo | ruta/ref | target | rango | hash/commit |
read_state | usado para | limitación
```

Para archivos grandes o diffs extensos usa chunks estables `SOURCE_ID-CNN` con rango y estado. Si un commit, diff o documento requerido está truncado, inaccesible o no fue leído completo, marca `INCOMPLETE_READ`; no generes entradas que dependan de él. `NO_HISTORY` solo aplica cuando la historia no fue proporcionada, no cuando se omitió leer una fuente requerida.

## Fase 2 — Tabla delta verificable

No redactes primero. Construye una fila por cambio:

```text
DELTA_ID | orden temporal | versión/fecha |
antes: archivo/símbolo/contrato | después: archivo/símbolo/contrato |
tipo de cambio | motivo respaldado | consumidores |
compatibilidad | migración | fuente histórica |
presencia en snapshot | validación | contradicción | destino
```

Clasifica cambios de código, configuración, build, API, protocolo, schema, documentación, test, seguridad y despliegue. Trata merges, reverts, commits parciales, cambios sin release y cambios documentales explícitamente.

Para cada cambio verifica si la capacidad realmente está conectada al camino de ejecución. La existencia de una clase, función o biblioteca aislada no confirma integración.

## Fase 3 — Claims y reconciliación

Registra:

```text
CLAIM_ID | afirmación | tipo (histórico/actual/intención/validación) |
fuente | rango/símbolo | estado de cambio | estado de validación |
conflicto | autoridad | entrada destino | limitación
```

Jerarquía:

- que ocurrió un cambio: commit/diff/tag;
- estado actual: código/configuración del snapshot;
- intención: plan/roadmap/documentación marcada como propuesta;
- compilación/test/hardware: resultado de ejecución;
- fecha o release: historia explícita, nunca inferida del contenido.

Si el changelog existente afirma algo que contradice el snapshot, conserva su valor histórico y añade una nota de discrepancia actual.

## Fase 4 — Formato de salida

Genera:

```markdown
# Changelog — [TARGET_ID]

> Snapshot actual: [SNAPSHOT]
> Rango histórico: [RANGO]
> Cobertura: COMPLETE | INCOMPLETE_READ | NO_HISTORY

## 1. Alcance y método
## 2. Evolución cronológica

## [VERSION_O_FECHA_O_UNKNOWN]

- Estado del cambio: `OBSERVED_IN_DIFF | PRESENT_IN_SNAPSHOT | DOCUMENTED_ONLY | PROPOSED | PARTIAL | REVERTED | REJECTED | UNKNOWN`
- Estado de validación: `NOT_EXECUTED | COMPILED | TESTED | INTEGRATION_VERIFIED | HARDWARE_VERIFIED | EXTERNAL_UNVERIFIED`
- Evidencia histórica: [commit/tag/diff/ref o UNKNOWN]
- Cambio: [qué ocurrió]
- Motivo: [fuente o UNKNOWN]
- Impacto: [módulos/contratos/consumidores]
- Compatibilidad: [compatible/ruptura/UNKNOWN]
- Migración: [pasos o NONE/UNKNOWN]
- Regresiones y correcciones: [evidencia o NONE]
- Limitaciones: [lo que no se puede afirmar]

## 3. Cambios incompatibles y migraciones
## 4. Contradicciones entre historia y snapshot
## 5. Validación ejecutada y no ejecutada
## 6. Matriz de claims y procedencia
## 7. Cobertura, fuentes ausentes y preguntas
```

Cada entrada narrativa debe corresponder a una o más filas `DELTA_ID`. No agrupes cambios si ocultas orden, reversión, impacto o procedencia.

## Seguridad y generalización

- No copies credenciales, claves, tokens, endpoints privados, IPs, identificadores, nombres de dispositivos ni snippets específicos.
- Usa placeholders tipados para el changelog reusable.
- No inventes fechas, semver, commits, autores, resultados o compatibilidad.
- Un procedimiento de auditoría puede ser reusable; los hechos concretos de la historia son source-only.

## Fase 5 — Replay final

Compara cada entrada contra el diff/historia, snapshot actual y evidencia de validación. Falla si:

- una entrada no tiene fuente;
- una propuesta aparece como implementada;
- una fecha o versión fue inferida;
- un cambio incompatible carece de nota;
- una integración se afirma por la existencia de un módulo aislado;
- se oculta una reversión o contradicción;
- se afirma build/test/hardware sin resultado;
- la salida contiene un secreto o valor privado.

Entrega también el estado de auditoría: `AUDIT_PASSED`, `AUDIT_FAILED`, `NO_HISTORY` o `INCOMPLETE_READ`. Requiere revisión humana; no autoriza commit ni release.
