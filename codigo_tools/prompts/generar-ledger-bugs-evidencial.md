# Generar un ledger de bugs evidencial

## Propósito

Genera o actualiza un ledger de defectos para `[PROJECT_ROOT]` sin convertir hipótesis, notas históricas o soluciones propuestas en hechos. El ledger debe permitir responder qué ocurrió, cómo se sabe, qué se cambió, qué se validó y qué sigue pendiente.

Este prompt documenta defectos y su evolución. No modifica el proyecto, no ejecuta cambios y no autoriza publicación. El resultado es una vista derivada de evidencia primaria y requiere revisión humana.

## Entradas obligatorias

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target, variante o sistema exacto]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta del ledger]
```

## Entradas opcionales

```text
BUG_SOURCES: [issues, notas, changelogs, auditorías o NONE]
CODE_BASELINE: [ruta o NONE]
CHANGELOG_BASELINE: [ruta o NONE]
EXECUTION_PLAN: [ruta o NONE]
VALIDATION_EVIDENCE: [builds, tests, logs, integración, hardware o NONE]
EXTERNAL_EVIDENCE: [tickets, métricas, capturas o NONE]
LANGUAGE: [idioma]
```

Si hay varias variantes, entornos o snapshots, no los mezcles. Enumera las alternativas y detén la redacción consolidada con `INPUT_AMBIGUOUS` hasta que el alcance sea seleccionable.

## Estados separados

### Estado epistemológico del defecto

```text
OBSERVED              síntoma reproducido o localizado en una fuente primaria
DOCUMENTED            declarado por una fuente secundaria, aún no confirmado
INFERRED              explicación deducida, con limitación explícita
CONTRADICTED          una fuente confiable discrepa
UNKNOWN               evidencia insuficiente
INCOMPLETE_READ       depende de una fuente no leída completamente
EXTERNAL_UNVERIFIED   depende de entorno o evidencia externa no adjunta
```

### Estado del ciclo de solución

```text
REPORTED              registrado, sin causa confirmada
TRIAGED               alcance e impacto clasificados
ROOT_CAUSE_PROPOSED   causa propuesta, pendiente de confirmación
FIX_PROPOSED          solución diseñada, no aplicada
APPLIED               cambio presente en el snapshot evaluado
REJECTED              propuesta descartada con motivo
DUPLICATE             absorbido por otro BUG_ID
CLOSED                solo si los criterios de cierre están satisfechos
BLOCKED               no puede avanzar por dependencia o decisión
```

### Estado de validación

```text
NOT_EXECUTED
REPRODUCED
COMPILED
TESTED
REGRESSION_TESTED
INTEGRATION_VERIFIED
HARDWARE_VERIFIED
EXTERNAL_UNVERIFIED
```

`APPLIED` no significa `TESTED`; `TESTED` no significa `INTEGRATION_VERIFIED`; `CLOSED` nunca se infiere de una nota que diga “fixed”.

## Fase 0 — Alcance e inventario

Registra antes de redactar:

```text
Target seleccionado:
Snapshot y método de identificación:
Variantes incluidas y excluidas:
Fuentes de bugs disponibles:
Código/configuración consultados:
Historial consultado:
Evidencia de validación disponible:
Fuentes no disponibles:
```

Inventaría completamente código, configuración, build, tests, scripts, CI, módulos locales y documentos que puedan afectar el defecto. Sigue imports/includes, símbolos llamados, flags y rutas de ejecución. Usa chunks estables para archivos grandes y registra:

```text
FILE_ID | ruta | tipo | bytes/líneas | hash |
read_state | chunks | relación con BUG_ID
```

Si una fuente necesaria falta, está truncada o es ilegible, devuelve `LECTURA_INCOMPLETA`, lista los BUG_ID afectados y no presentes el ledger como completo.

## Fase 1 — Registro normalizado

Cada defecto debe tener una identidad estable y una fila de procedencia:

```text
BUG_ID | target/variante | título abstracto | estado epistemológico |
fuente del reporte | fuente primaria | referencia |
síntoma | frecuencia | severidad | impacto | estado de ciclo |
estado de validación | dependencia | destino
```

El `BUG_ID` debe ser estable aunque cambie la redacción. Si dos entradas describen el mismo defecto, conserva ambas fuentes, registra la relación `DUPLICATE` y elige un registro canónico sin borrar la procedencia.

## Fase 2 — Contrato de cada bug

Para cada `BUG_ID`, completa esta estructura:

```markdown
### BUG-[ID] — [título parametrizado]

- Target/variante: [TARGET_ID]
- Estado epistemológico: OBSERVED | DOCUMENTED | INFERRED | CONTRADICTED | UNKNOWN | INCOMPLETE_READ | EXTERNAL_UNVERIFIED
- Estado del ciclo: REPORTED | TRIAGED | ROOT_CAUSE_PROPOSED | FIX_PROPOSED | APPLIED | REJECTED | DUPLICATE | CLOSED | BLOCKED
- Estado de validación: NOT_EXECUTED | REPRODUCED | COMPILED | TESTED | REGRESSION_TESTED | INTEGRATION_VERIFIED | HARDWARE_VERIFIED | EXTERNAL_UNVERIFIED
- Síntoma observable: [qué ocurre, sin atribuir causa no demostrada]
- Condición de aparición: [precondición, frecuencia o UNKNOWN]
- Impacto: [capacidad, seguridad, datos, disponibilidad o UNKNOWN]
- Severidad/prioridad: [criterio y evidencia]
- Causa: [OBSERVED | PROPOSED | UNKNOWN, con fuente]
- Evidencia primaria: [archivo, línea, símbolo, log o fixture]
- Evidencia secundaria: [documento o ticket, claramente etiquetado]
- Contradicciones: [fuentes que discrepan o NONE]
- Solución propuesta: [contrato de alto nivel, no patch literal]
- Cambio aplicado: [snapshot, ruta/símbolo y estado; NONE si no existe]
- Compatibilidad/migración: [contrato anterior/nuevo o UNKNOWN]
- Casos de reproducción: [positivo, negativo, límite y dependencia caída]
- Prevención/regla reusable: [regla abstracta o NONE]
- Criterios de cierre: [gates concretos]
- Rollback: [alcance, reversibilidad y estado probado/no probado]
- Preguntas bloqueantes: [preguntas o NONE]
- Procedencia: [CLAIM_ID/FILE_ID/VALIDATION_ID]
```

No afirmes una causa porque el nombre de una función o módulo parezca coincidir con el síntoma. No afirmes una corrección porque exista una función nueva. La integración debe demostrarse siguiendo el camino de ejecución.

## Fase 3 — Reconciliación de soluciones

Separa siempre:

1. síntoma observado;
2. causa confirmada o hipótesis;
3. solución propuesta;
4. solución aplicada al snapshot;
5. compilación;
6. prueba de regresión;
7. integración o hardware;
8. cierre y evidencia.

Cuando una fuente histórica afirma que un bug está resuelto pero el snapshot no lo demuestra, conserva la afirmación histórica como `DOCUMENTED` o `CONTRADICTED`; no la conviertas en `CLOSED`.

Cuando un bug depende de seguridad, autenticación, deduplicación, replay, persistencia, red, payloads o recuperación, registra el contrato afectado y el caso negativo. No documentes valores privados, direcciones, credenciales, topics, claves, pines ni snippets de producto.

## Fase 4 — Salida mínima

Genera `OUTPUT_PATH` con esta estructura:

```markdown
# Ledger de bugs — [TARGET_ID]

> Snapshot: [SNAPSHOT]
> Cobertura: COMPLETE | LECTURA_INCOMPLETA | UNKNOWN
> Estado de auditoría: DRAFT | GENERATED | AUDITED | AUDIT_FAILED

## 1. Alcance, método y variantes
## 2. Inventario y cobertura de lectura
## 3. Resumen por estado y prioridad
## 4. Ledger de bugs
## 5. Duplicados, contradicciones y decisiones
## 6. Soluciones aplicadas y validación real
## 7. Regresiones y casos negativos
## 8. Reglas preventivas reutilizables
## 9. Matriz de claims y procedencia
## 10. Pendientes, bloqueos y limitaciones
```

El resumen no puede ocultar entradas `UNKNOWN`, `CONTRADICTED`, `INCOMPLETE_READ`, `BLOCKED` o `NOT_EXECUTED`. Cada afirmación importante debe apuntar a `BUG_ID` y fuente.

## Seguridad y generalización

- No copies firmware, secretos, hosts, IPs, topics, IDs, pines, claves, payloads privados ni comandos específicos.
- Usa placeholders tipados: `[MODULE]`, `[FUNCTION]`, `[EVENT]`, `[ENDPOINT]`, `[CONFIG_KEY]`, `[DEVICE_ID]`.
- No ejecutes comandos, no apliques soluciones y no fabriques resultados de build/test.
- Una credencial mencionada por una fuente se registra como categoría redactada, nunca como valor.
- Las condiciones externas son `EXTERNAL_UNVERIFIED` si no existe evidencia autorizada.

## Fase 5 — Replay y auditoría

Vuelve a comparar el ledger contra todas las fuentes primarias completas. Marca `AUDIT_FAILED` si:

- un BUG_ID no tiene procedencia;
- una hipótesis aparece como causa confirmada;
- una solución propuesta aparece como aplicada sin snapshot;
- `CLOSED` carece de criterios y evidencia de cierre;
- un bug duplicado borra su fuente original;
- una integración se afirma por la existencia de una clase o log aislado;
- una validación aparece como ejecutada sin resultado y entorno;
- se mezclaron variantes o estados históricos;
- aparece un secreto o valor específico en una salida reusable.

Incluye una matriz final:

```text
REPLAY_CHECK_ID | BUG_ID | afirmación comprobada | fuente |
resultado esperado | resultado observado | estado | limitación
```

Toda salida requiere revisión humana. Este prompt no autoriza cambios ni promoción.
