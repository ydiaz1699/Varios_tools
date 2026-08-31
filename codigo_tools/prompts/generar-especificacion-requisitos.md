# Generar una especificación de requisitos auditable

## Propósito

Convierte una idea, necesidad o problema de `[PROJECT_ROOT]` en una especificación revisable sin saltar directamente a una solución técnica. El resultado separa objetivos, requisitos, supuestos, preguntas, alternativas, riesgos, decisiones y criterios de aceptación.

Este prompt sirve para explorar y cerrar alcance antes de implementar. No modifica el proyecto, no selecciona una tecnología por autoridad, no genera patches y no presenta una idea como requisito aprobado.

## Entradas obligatorias

```text
PROJECT_ROOT: [raíz absoluta o NONE si es un proyecto nuevo]
TARGET_ID: [target, variante o sistema exacto]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta de la especificación]
```

## Entradas opcionales

```text
PROBLEM_STATEMENT: [necesidad o NONE]
STAKEHOLDERS: [roles abstractos o NONE]
EXISTING_SYSTEM_DOCS: [rutas o NONE]
CONSTRAINTS: [seguridad, compatibilidad, coste, rendimiento, operación o NONE]
ALTERNATIVES_TO_COMPARE: [opciones o NONE]
VALIDATION_EVIDENCE: [tests, métricas, tickets, observaciones o NONE]
DECISION_RECORDS: [ADRs, aprobaciones o NONE]
LANGUAGE: [idioma]
```

Si no existe una necesidad concreta, si hay varias interpretaciones incompatibles o si falta el target, devuelve `INPUT_AMBIGUOUS` y solo entrega inventario, preguntas y alternativas de alcance.

## Estados y vocabularios

### Estado epistemológico

```text
OBSERVED_IN_CODE
OBSERVED_IN_OPERATION
DOCUMENTED
STAKEHOLDER_REPORTED
INFERRED
PROPOSED
CONTRADICTED
UNKNOWN
INCOMPLETE_READ
EXTERNAL_UNVERIFIED
```

### Estado de decisión

```text
OPEN
PENDING_REVIEW
DECIDED
REJECTED
BLOCKED
SUPERSEDED
```

### Estado de validación

```text
NOT_EXECUTED
PARTIALLY_VALIDATED
VALIDATED_IN_TEST
VALIDATED_IN_OPERATION
EXTERNAL_UNVERIFIED
```

Una petición de usuario puede justificar un objetivo o una necesidad, pero no demuestra una solución técnica. Un criterio de aceptación describe lo que debe observarse; no prueba que ya ocurrió.

## Fase 0 — Alcance, actores y baseline

Registra:

```text
Target seleccionado:
Snapshot y método de identificación:
Problema de entrada y fuente:
Actores/roles incluidos:
Variantes incluidas/excluidas:
Sistema actual y límites:
Restricciones conocidas:
Decisiones previas:
Evidencia disponible:
Preguntas iniciales:
```

Para un proyecto existente, inventaría y lee completamente código, configuración, build, dependencias locales, tests, CI y documentación relacionada. Para un proyecto nuevo, declara que no existe baseline de implementación y no inventes componentes.

Usa chunks estables en archivos grandes:

```text
FILE_ID | ruta | tipo | bytes/líneas | hash |
read_state | chunks | rol | usado por REQUIREMENT_ID/DECISION_ID
```

Si una fuente necesaria falta, está truncada o es ilegible, devuelve `LECTURA_INCOMPLETA` y limita las conclusiones.

## Fase 1 — Separación del problema

Antes de proponer arquitectura, separa:

```text
GOAL_ID | objetivo medible | actor beneficiado | fuente | estado | prioridad
NEED_ID | necesidad/problema | síntoma o contexto | fuente | estado | impacto
CONSTRAINT_ID | restricción | origen | fuerza | evidencia | estado
ASSUMPTION_ID | supuesto | qué habilita | cómo se comprobará | estado
QUESTION_ID | pregunta abierta | decisión que bloquea | responsable abstracto | fecha o UNKNOWN
```

No conviertas preferencias, ejemplos o una solución sugerida en requisitos sin identificar su origen y estado.

## Fase 2 — Requisitos verificables

Cada requisito debe ser atómico, observable y trazable:

```text
REQUIREMENT_ID | texto normativo parametrizado | tipo |
fuente | actor | prioridad | estado de decisión |
criterio de aceptación | método de validación | dependencia |
risk/limitación | estado de validación | destino
```

Clasifica como:

```text
FUNCTIONAL
NON_FUNCTIONAL
SECURITY
SAFETY
COMPATIBILITY
OPERABILITY
DATA
OBSERVABILITY
MIGRATION
COMPLIANCE
OUT_OF_SCOPE
```

Un requisito debe evitar términos no medibles como “rápido”, “seguro” o “fácil” sin umbral, contexto o método. Si no puede hacerse medible aún, marca `OPEN` y formula la pregunta necesaria.

Cada criterio de aceptación debe especificar:

```text
ACCEPTANCE_ID | requisito | escenario/precondición |
acción o entrada | resultado observable | caso negativo/límite |
método | evidencia esperada | estado
```

Incluye escenarios normales, error, límites, dependencia caída, recuperación, migración, seguridad y operación cuando correspondan.

## Fase 3 — Alternativas y no-decisión

Compara alternativas sin favorecer automáticamente la primera solución propuesta:

```text
ALTERNATIVE_ID | opción abstracta | requisitos cubiertos |
no cubiertos | compatibilidad | seguridad | coste |
complejidad | operación | migración | reversibilidad |
evidencia | incertidumbre | decisión
```

La decisión debe ser una de:

```text
OPEN
PENDING_REVIEW
DECIDED
REJECTED
BLOCKED
SUPERSEDED
```

Una opción no elegida debe conservar el motivo. Si no existe evidencia para comparar, marca `PENDING_REVIEW`; no rellenes la tabla por convención.

## Fase 4 — Arquitectura y ADR de alto nivel

Solo después de cerrar requisitos y alternativas describe una solución conceptual. Separa:

- requisito de diseño;
- restricción de implementación;
- decisión aprobada;
- propuesta pendiente;
- componente observado en el sistema actual;
- componente hipotético para el estado deseado.

Cada decisión debe tener:

```text
DECISION_ID | decisión | contexto | alternativas |
requisitos afectados | consecuencias positivas |
consecuencias negativas | riesgos | rollback |
aprobador abstracto | estado | evidencia
```

No incluy rutas, APIs, protocolos, hardware o tecnologías concretas salvo que estén observados, explícitamente requeridos o marcados como propuesta parametrizada. No generes una arquitectura de detalle cuando faltan requisitos críticos.

## Fase 5 — MVP, fases y Definition of Done

Construye una secuencia sin presentarla como ejecución realizada:

```text
PHASE_ID | objetivo | requisitos | precondiciones |
fuera de alcance | dependencias | gate de entrada |
gate de salida | validación | rollback | estado
```

Define:

```text
DEFINITION_OF_READY: alcance cerrado, requisitos trazables, riesgos conocidos,
dependencias y decisiones identificadas, validación diseñada.

DEFINITION_OF_DONE: criterios de aceptación satisfechos, validación registrada,
regresión revisada, documentación actualizada, seguridad comprobada y pendientes explícitos.
```

`DONE` no es un estado válido si no se documentan los gates que lo justifican. Todo build, test, simulación, operación o hardware no ejecutado queda como `NOT_EXECUTED`.

## Fase 6 — Salida mínima

Genera `OUTPUT_PATH` con esta estructura:

```markdown
# Especificación de requisitos — [TARGET_ID]

> Snapshot: [SNAPSHOT]
> Estado de decisión: OPEN | PENDING_REVIEW | DECIDED | REJECTED | BLOCKED | SUPERSEDED
> Cobertura: COMPLETE | INCOMPLETE_READ | INPUT_AMBIGUOUS
> Estado de auditoría: DRAFT | GENERATED | AUDITED | AUDIT_FAILED

## 1. Problema, objetivos y alcance
## 2. Actores, variantes y restricciones
## 3. Necesidades, supuestos y preguntas
## 4. Requisitos verificables
## 5. Criterios de aceptación y escenarios negativos
## 6. Alternativas comparadas
## 7. Decisiones y ADR de alto nivel
## 8. Arquitectura conceptual parametrizada
## 9. MVP, fases y Definition of Ready/Done
## 10. Riesgos, dependencias y rollback
## 11. Matriz de trazabilidad y procedencia
## 12. Pendientes y limitaciones
```

## Seguridad y generalización

- No copies secretos, hosts, IPs, topics, IDs, pines, payloads, nombres de dispositivos ni valores privados.
- Usa placeholders: `[ACTOR]`, `[CAPABILITY]`, `[MODULE]`, `[DATA_CLASS]`, `[THRESHOLD]`, `[INTERFACE]`.
- No inventes requisitos desde una tecnología o componente existente.
- No confundas una solicitud con una aprobación ni una propuesta con una implementación.
- Los requisitos regulatorios, operativos o de despliegue sin fuente autorizada son `EXTERNAL_UNVERIFIED`.
- No ocultes requisitos incompatibles: crea una pregunta o decisión bloqueante.

## Fase 7 — Replay y auditoría

Vuelve a comprobar la especificación contra el problema, fuentes primarias y decisiones autorizadas. Marca `AUDIT_FAILED` si:

- un requisito no tiene fuente, actor, aceptación o método de validación;
- una solución aparece antes de justificar el problema;
- una suposición se presenta como hecho;
- una decisión contradice una decisión aprobada sin registrarlo;
- una fase no tiene dependencias, gates o rollback;
- un estado `DECIDED`, `VALIDATED` o `DONE` carece de evidencia;
- se mezclaron variantes o se inventaron componentes;
- aparece un secreto o valor específico del producto.

Incluye:

```text
REPLAY_CHECK_ID | REQUIREMENT_ID/DECISION_ID | afirmación |
fuente | resultado esperado | resultado observado | estado | limitación
```

Toda salida requiere revisión humana y no autoriza implementación ni promoción.
