# Generar un changelog basado en evidencia

## Propósito

Genera o actualiza un historial de evolución para `[PROJECT_ROOT]` sin inventar releases, fechas, commits ni resultados. El changelog debe explicar qué cambió, por qué, qué impacto tiene y qué evidencia respalda cada entrada.

No es un README ni un roadmap. Una propuesta futura debe permanecer fuera de las entradas de cambios realizados o marcarse claramente como no publicada.

## Entradas

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target o producto abstracto]
SNAPSHOT: [commit/tag/fecha]
PREVIOUS_CHANGELOG: [ruta opcional]
HISTORY_SOURCE: [git log/diffs/releases/tickets o NONE]
VALIDATION_EVIDENCE: [tests/builds/logs/releases o NONE]
RELATED_DOCUMENTS: [architecture/plan/roadmap opcionales]
OUTPUT_PATH: [ruta del changelog]
```

## Procedimiento

1. Lee el proyecto actual completo y el changelog existente completo si existe.
2. Inspecciona la historia disponible: commits, tags, merges, diffs, releases o tickets. Si no existe una fuente histórica verificable, no fabriques una cronología: usa `UNKNOWN`.
3. Relaciona cada cambio con archivos, símbolos, configuración o evidencia de prueba. Distingue cambio implementado, cambio preparado, cambio propuesto y cambio rechazado.
4. Compara el historial narrado contra el árbol actual. Registra contradicciones como notas de auditoría, no las ocultes.
5. Para cambios de API, protocolo, esquema o configuración, identifica compatibilidad, migración y consumidores afectados solo si la evidencia lo permite.
6. Redacta nombres y valores sensibles. Usa placeholders para targets, endpoints, credenciales y dispositivos.

## Formato de cada entrada

Cada versión, fecha o agrupación verificable debe usar:

```markdown
## [VERSION_O_FECHA]

- Estado: `IMPLEMENTED | PROPOSED | PARTIAL | REJECTED | UNKNOWN`
- Evidencia: [commit/tag/diff/ruta/rango o UNKNOWN]
- Cambio: [qué se modificó]
- Motivo: [problema o decisión respaldada]
- Impacto: [componentes, interfaces o comportamiento afectado]
- Compatibilidad/migración: [impacto o UNKNOWN]
- Validación: [build/test/log/hardware o NOT_EXECUTED]
- Pendientes/limitaciones: [lo que no se puede confirmar]
```

Agrupa por categorías solo cuando esa agrupación no esconda el orden ni la procedencia. Conserva regresiones y correcciones importantes; no reescribas la historia para que parezca lineal.

## Reglas de evidencia

- Un commit o diff demuestra que hubo un cambio, no que el resultado funcionó.
- Un comentario o roadmap demuestra intención, no implementación.
- Un build demuestra compilación en un entorno, no funcionamiento de hardware.
- Un test demuestra únicamente los casos que realmente ejecutó.
- Una fecha solo se incluye si proviene de la historia o de una fuente explícita.
- Si una entrada existente contradice el código, conserva el texto como histórico y añade la discrepancia actual.
- No conviertas una capacidad disponible en una capacidad integrada: verifica que el camino real la invoque.

## Salidas y validación

Entrega el changelog y una matriz de auditoría con `claim → fuente → estado`. Verifica que cada entrada tenga procedencia; que no haya releases inventadas; que propuestas no aparezcan como realizadas; que los cambios incompatibles tengan nota; que los secretos y datos privados estén ausentes; y que build, tests y hardware no ejecutados aparezcan como `NOT_EXECUTED`.
