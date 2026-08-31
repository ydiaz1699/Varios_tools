# Generar un plan canónico de ejecución

## Propósito

Genera un plan operativo para continuar `[PROJECT_ROOT]` desde una línea base reproducible. El plan debe proteger el estado actual, separar variantes, ordenar dependencias y definir gates de evidencia. No ejecuta cambios ni autoriza commits.

Un plan válido no es una lista de ideas: cada fase es un contrato verificable con precondiciones, estado inicial, límites, evidencia, aceptación, rollback y preguntas bloqueantes.

## Entradas obligatorias

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target/variante exacta]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta del plan]
```

## Entradas opcionales

```text
ARCHITECTURE_PATH: [ruta o NONE]
CHANGELOG_PATH: [ruta o NONE]
ROADMAP_PATH: [ruta o NONE]
EXISTING_PLAN_PATH: [ruta o NONE]
BUG_SOURCES: [issues/notas/auditorías o NONE]
VALIDATION_EVIDENCE: [build/test/integración/hardware o NONE]
CONSTRAINTS: [seguridad, compatibilidad, rendimiento, producto]
ALLOWED_COMMANDS: [comandos de solo lectura o NONE]
LANGUAGE: [idioma]
```

## Estados que no se pueden mezclar

```text
PROPOSED             diseño o intención
DECIDED              decisión aprobada, aún no aplicada
APPLIED              cambio presente en el snapshot
COMPILED             build exitoso, entorno y resultado registrados
TESTED               tests ejecutados, casos y resultado registrados
INTEGRATION_VERIFIED integración ejecutada y evidencia adjunta
HARDWARE_VERIFIED   evidencia sobre hardware real
BLOCKED              no puede avanzar por decisión, dependencia o evidencia
REJECTED             descartado con motivo
UNKNOWN              no determinable
NOT_EXECUTED         validación no realizada
INCOMPLETE_READ      depende de una fuente no leída completa
EXTERNAL_UNVERIFIED  depende de condición externa no demostrada
```

`APPLIED` no implica `COMPILED`; `COMPILED` no implica `TESTED`; `TESTED` no implica hardware. Mantén estado de implementación y estado de validación en campos separados.

## Fase 0 — Alcance y baseline

Entrega primero un registro interno:

```text
Target seleccionado:
Snapshot y método de identificación:
Variantes incluidas:
Variantes excluidas y motivo:
Estado Git observado:
Entornos/build targets:
Componentes y dependencias principales:
Tests existentes:
Restricciones:
Documentos baseline:
Evidencia de validación disponible:
```

No mezcles producción, laboratorio, ramas o targets. Si no puede determinarse el target o snapshot, devuelve `INPUT_AMBIGUOUS` y no generes fases prescriptivas.

## Fase 1 — Inventario y lectura completa

Inventaría y lee código, configuración, build, módulos locales, tests, CI, scripts y documentos de contexto. Sigue imports/includes, flags, manifests, referencias, símbolos llamados y dependencias transitivas.

Registra:

```text
FILE_ID | ruta | tipo | target | bytes/líneas | hash |
chunks | read_state | rol | usado en claims/fases
```

Los archivos grandes deben leerse en chunks estables `FILE_ID-CNN`. Si una fuente requerida, dependencia o chunk falta, está truncado o es ilegible, marca `INCOMPLETE_READ` y limita la salida a baseline, gaps afectados y preguntas. No generes un plan que parezca ejecutable desde una lectura parcial.

## Fase 2 — Línea base y fuente de verdad

Construye una matriz:

```text
BASE_ID | claim actual | fuente primaria | rango/símbolo |
estado epistemológico | estado de ejecución | variante |
restricción | contradicción | conservación requerida
```

Autoridad por tipo:

- comportamiento y estado actual: código/configuración del snapshot;
- que un cambio ocurrió: historia/diff;
- decisiones aprobadas: registro de decisión con estado;
- intención: plan/roadmap, siempre propuesta;
- build/test/integración/hardware: evidencia de ejecución;
- restricciones externas: fuente externa autorizada o `EXTERNAL_UNVERIFIED`.

Explica por qué una fuente prevalece cuando existe discrepancia. No borres una afirmación histórica: degrádala, contradícela o conserva su alcance.

## Fase 3 — Bugs, riesgos y decisiones

Cada problema debe tener:

```text
ISSUE_ID | tipo (bug/riesgo/decisión/deuda) | síntoma |
evidencia | impacto | variante | hipótesis | decisión requerida |
prioridad | estado | fase afectada
```

Separa problema observado de solución propuesta. Una capacidad disponible en un módulo pero no conectada al flujo debe registrarse como `AVAILABLE_NOT_INTEGRATED`, no como completada.

## Fase 4 — Contrato de cada fase

Cada fase debe seguir este formato:

```markdown
### FASE-[ID] — [título]

- Estado inicial: [estado real]
- Estado de planificación: PROPOSED | DECIDED | BLOCKED | REJECTED
- Objetivo observable: [resultado]
- Requisitos/claims que satisface: [BASE_ID/ISSUE_ID]
- Precondiciones: [lecturas, decisiones, herramientas, backup]
- Dependencias: [fases, módulos, decisiones]
- Alcance permitido: [qué puede cambiar]
- Fuera de alcance: [qué no debe cambiar]
- Archivos/símbolos afectados: [observados o HIPOTÉTICOS, con motivo]
- Diseño de alto nivel: [pasos, no patch específico]
- Casos positivos: [qué debe funcionar]
- Casos negativos y límites: [qué debe fallar o permanecer estable]
- Compatibilidad/migración: [contrato anterior/nuevo o UNKNOWN]
- Observabilidad: [logs/métricas/evidencia]
- Gate de entrada: [evidencia requerida]
- Gate de salida: [evidencia mínima]
- Validación: [método, entorno, resultado esperado]
- Rollback: [manual/automático, probado/no probado, alcance]
- Riesgos residuales: [riesgos]
- Preguntas bloqueantes: [preguntas o NONE]
```

Ordena fases por dependencia. No propongas una fase posterior si su gate de entrada depende de una fase bloqueada sin registrar la relación.

## Fase 5 — Plan de validación y cierre

Construye una matriz:

```text
GATE_ID | fase | claim/requisito | precondición | prueba/método |
resultado esperado | resultado real | entorno/snapshot |
evidencia | estado | revisor
```

Incluye límites, regresión, migración, dependencia caída, datos inválidos, recuperación, integración y hardware cuando aplique. Si no se ejecutó algo, escribe `NOT_EXECUTED`; no lo eleves por documentación.

Define `DEFINITION_OF_READY` y `DEFINITION_OF_DONE`:

```text
READY: baseline leído, decisión tomada, dependencias conocidas, rollback definido.
DONE: cambio aplicado, diff revisado, build/test/gates requeridos registrados,
regresiones comprobadas, documentación actualizada y pendientes explícitos.
```

Un rollback debe clasificarse como: probado/no probado; reversible/no reversible; manual/automático; dependencias; recuperación si falla.

## Estructura del documento

```markdown
# Plan de ejecución — [TARGET_ID]
## 1. Propósito, alcance y exclusiones
## 2. Línea base y variantes preservadas
## 3. Fuente de verdad y reglas no negociables
## 4. Inventario y cobertura de lectura
## 5. Estado actual y matriz de claims
## 6. Bugs, riesgos y decisiones bloqueantes
## 7. Fases contractuales ordenadas
## 8. Dependencias, compatibilidad y migración
## 9. Gates y matriz de validación
## 10. Rollback y recuperación
## 11. Trazabilidad requisito→fase→evidencia
## 12. Definition of Ready/Done y checklist
## 13. Pendientes, preguntas y limitaciones
```

## Guardrails

- No aplicar cambios, patches, commits ni comandos destructivos.
- No copiar firmware, secretos, hosts, pines, protocolos configurados ni snippets específicos.
- Usa placeholders tipados en ejemplos.
- No mezcles variantes ni declares integración por la mera existencia de una clase o biblioteca.
- Condiciones de red, firewall, despliegue y hardware sin evidencia son `EXTERNAL_UNVERIFIED`.
- La documentación existente es contexto, no autoridad automática sobre el snapshot.

## Replay final

Vuelve a contrastar cada fase, claim, dependencia, ruta y gate contra las fuentes completas. Falla con `AUDIT_FAILED` si hay fase sin aceptación, dependencia sin fuente, rollback indefinido, estado imposible, claim huérfano, target mezclado, pendiente oculto o validación afirmada sin resultado. Toda salida requiere revisión humana.
