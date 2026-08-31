# Generar roadmap técnico basado en gaps

## Propósito

Genera un roadmap futuro y priorizado para `[PROJECT_ROOT]` a partir de un registro de gaps verificable. El roadmap no es una lista de ideas ni un plan aplicado: cada tarea debe derivarse de un estado actual observado, un estado deseado, una diferencia, una dependencia y una validación.

No modifica el proyecto, no crea commits y no presenta una capacidad propuesta como implementada.

## Entradas obligatorias

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target/variante exacta]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta del roadmap]
```

## Entradas opcionales

```text
ARCHITECTURE_PATH: [ruta o NONE]
CHANGELOG_PATH: [ruta o NONE]
EXECUTION_PLAN_PATH: [ruta o NONE]
EXISTING_ROADMAP_PATH: [ruta o NONE]
BACKLOG_SOURCES: [issues, bugs, ideas, auditorías, notas o NONE]
VALIDATION_EVIDENCE: [build/test/simulación/integración/hardware o NONE]
CONSTRAINTS: [seguridad, compatibilidad, presupuesto, rendimiento]
LANGUAGE: [idioma]
```

## Estados separados

### Estado del gap/tarea

```text
NEW
IMPROVEMENT
BUGFIX
MIGRATION
VALIDATION
DOCUMENTATION
BLOCKED
REJECTED
```

### Estado de planificación/ejecución

```text
PROPOSED
READY
DECIDED
IN_PROGRESS
APPLIED
COMPILED
TESTED
INTEGRATION_VERIFIED
HARDWARE_VERIFIED
NOT_EXECUTED
UNKNOWN
INCOMPLETE_READ
EXTERNAL_UNVERIFIED
```

`DONE` no debe usarse sin declarar qué gates de build, test, integración y hardware se cumplieron.

## Fase 0 — Alcance y baseline

Registra:

```text
Target seleccionado:
Snapshot:
Variantes incluidas/excluidas:
Entornos de build:
Arquitectura y plan baseline:
Roadmap anterior:
Fuentes de backlog:
Restricciones:
Evidencia disponible:
```

Si hay varios targets o variantes, no los combines. Si el alcance o snapshot es ambiguo, devuelve `INPUT_AMBIGUOUS` y no priorices tareas.

## Fase 1 — Inventario completo

Lee completamente código, configuración, build, módulos locales, tests, CI, scripts y todos los documentos relacionados. Sigue imports/includes, flags, manifests, símbolos y rutas llamadas.

Registra:

```text
FILE_ID | ruta | tipo | target | bytes/líneas | hash |
chunks | read_state | rol | usado para gap/task
```

Usa chunks estables `FILE_ID-CNN` en archivos grandes. Si una fuente requerida no se lee completa, devuelve `LECTURA_INCOMPLETA`, lista archivos/dependencias afectados y no produzcas un backlog que parezca completo.

## Fase 2 — Estado actual y claims

Antes del backlog, crea una matriz:

```text
BASE_ID | capacidad/propiedad actual | fuente primaria |
rango/símbolo | estado epistemológico | estado ejecución |
variante | disponible | integrada | limitación | destino
```

Distingue:

- observado en código;
- documentado pero no localizado;
- disponible en una biblioteca pero no integrado;
- aplicado pero no compilado;
- compilado pero no probado;
- probado pero no verificado en integración/hardware;
- propuesta o necesidad externa.

Jerarquía: código/configuración actual para comportamiento; historia para cambios; plan/decisión aprobada para intención decidida; roadmap/issues para necesidades; evidencia de ejecución para validación.

## Fase 3 — Registro de gaps

Cada gap debe tener:

```text
GAP_ID | estado actual | estado deseado | delta |
fuente del actual | fuente del deseado | evidencia |
impacto | variante | dependencia | incertidumbre |
conflicto | decisión requerida | tarea destino
```

No crees tareas a partir de una idea aislada si no puede relacionarse con un gap, bug, riesgo, decisión o requisito explícito. Si la propuesta contradice el código o una decisión aprobada, marca `BLOCKED` o `REJECTED`; no la conviertas en tarea lista.

## Fase 4 — Priorización reproducible

Calcula una puntuación de 0 a 5 por dimensión y conserva la justificación:

```text
SECURITY       riesgo de seguridad si no se realiza
BLOCKING       bloquea operación, recuperación o decisiones posteriores
COMPATIBILITY  riesgo de ruptura o coste de migración
IMPACT         cantidad/importancia de capacidades afectadas
DEPENDENCY     habilita o desbloquea otras tareas
EFFORT         esfuerzo estimado, donde 5 significa menor esfuerzo
UNCERTAINTY    incertidumbre; alta incertidumbre reduce prioridad de ejecución
```

No uses una puntuación como verdad absoluta. Ordena por reglas declaradas, conserva empates y permite `UNKNOWN` cuando no haya evidencia. Una tarea crítica con incertidumbre alta puede quedar `BLOCKED` aunque su impacto sea alto.

## Fase 5 — Contrato de tarea

Cada tarea debe usar este formato:

```markdown
### TASK-[ID] — [título parametrizado]

- Tipo: NEW | IMPROVEMENT | BUGFIX | MIGRATION | VALIDATION | DOCUMENTATION
- Estado: PROPOSED | READY | BLOCKED | REJECTED
- Target/variante: [TARGET_ID]
- Gap: [GAP_ID]
- Estado actual: [claim y fuente]
- Estado deseado: [resultado observable]
- Delta: [diferencia exacta]
- Prioridad: CRITICAL | HIGH | MEDIUM | LOW
- Puntuación: SECURITY=0; BLOCKING=0; COMPATIBILITY=0; IMPACT=0; DEPENDENCY=0; EFFORT=0; UNCERTAINTY=0
- Justificación: [razón trazable]
- Precondiciones: [decisiones, backup, herramientas, lectura]
- Dependencias: [TASK/GAP/DECISION o NONE]
- Archivos/símbolos candidatos: [OBSERVED o HYPOTHETICAL, con fuente]
- Diseño permitido: [alto nivel, no patch literal]
- Fuera de alcance: [límites de no cambio]
- Casos positivos: [comportamiento esperado]
- Casos negativos/límites: [fallos, timeouts, corrupción, regresión]
- Compatibilidad/migración: [contrato anterior/nuevo o UNKNOWN]
- Observabilidad: [logs, métricas, evidencias]
- Definition of Ready: [gates]
- Definition of Done: [gates]
- Validación requerida: [build/test/simulación/integración/hardware]
- Rollback: [tipo y estado probado/no probado]
- Riesgos y preguntas bloqueantes: [lista]
- Procedencia: [CLAIM/GAP/fuente/rango]
```

`Files/symbols candidates` no significa que deban modificarse: distingue rutas observadas de rutas hipotéticas. No copies snippets específicos; describe el contrato y usa `[MODULE]`, `[API]`, `[DEVICE_ID]`, `[PIN]`, `[ENDPOINT]`, `[TOPIC]` o placeholders equivalentes.

## Fase 6 — Validación y definición de terminado

Genera una matriz:

```text
CHECK_ID | task | requisito | caso |
precondición | método | resultado esperado | resultado real |
entorno/snapshot | evidencia | estado
```

Incluye casos normales, negativos, límites, dependencia caída, migración, regresión, seguridad, build, test, integración y hardware cuando corresponda. Si no se ejecutó, `NOT_EXECUTED`.

`Definition of Ready` mínima: gap respaldado, alcance cerrado, dependencia conocida, decisión tomada o bloqueo explícito, validación definida y rollback descrito.

`Definition of Done` mínima: cambio aplicado, diff revisado, build/test/gates requeridos registrados, regresiones revisadas, documentación actualizada, secretos ausentes y pendientes explícitos.

## Estructura de salida

```markdown
# Roadmap técnico — [TARGET_ID]
## 1. Alcance, snapshot y exclusiones
## 2. Baseline actual y variantes
## 3. Invariantes y riesgos que no deben romperse
## 4. Matriz de claims actuales
## 5. Gap analysis
## 6. Política de priorización y puntuaciones
## 7. Backlog por prioridad/fase
## 8. Dependencias y decisiones bloqueantes
## 9. Matriz de validación
## 10. Definition of Ready/Done
## 11. Trazabilidad y procedencia
## 12. Preguntas abiertas y limitaciones
```

## Guardrails de seguridad y calidad

- No inventes bugs, hardware, dependencias, fechas, rendimiento, compatibilidad o APIs.
- No copies firmware, secretos, hosts, pines, protocolos configurados, topics, IDs ni comandos específicos.
- El roadmap propone; no aplica y no confirma.
- Una capacidad disponible no equivale a una capacidad integrada.
- Una ruta no localizada debe ser `HYPOTHETICAL` o eliminarse.
- Las condiciones externas son `EXTERNAL_UNVERIFIED` sin evidencia.
- No ocultes una contradicción en el backlog: conviértela en `BLOCKED`, `REJECTED` o pregunta de decisión.

## Replay final

Vuelve a comparar cada claim, gap, puntuación, dependencia y tarea contra las fuentes completas. Falla con `AUDIT_FAILED` si existe una tarea sin gap, procedencia, aceptación, validación o rollback; si se mezclaron variantes; si una propuesta parece aplicada; si una ruta/API fue inventada; si un pendiente fue ocultado; o si aparece un valor sensible. Toda salida requiere revisión humana.
