# Generar un roadmap técnico priorizado y ejecutable

## Propósito

Genera un backlog técnico futuro para `[PROJECT_ROOT]` a partir de un gap analysis verificable. El roadmap debe ayudar a priorizar mejoras sin confundir capacidades existentes con trabajo pendiente, y sin trasladar a otro proyecto los nombres, pines, protocolos, hosts, secretos o snippets del proyecto fuente.

## Entradas

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target/variante]
SNAPSHOT: [commit/tag/fecha]
ARCHITECTURE_PATH: [ruta opcional]
CHANGELOG_PATH: [ruta opcional]
EXECUTION_PLAN_PATH: [ruta opcional]
EXISTING_ROADMAP_PATH: [ruta opcional]
BACKLOG_SOURCES: [issues, ideas, bugs, notas o NONE]
VALIDATION_EVIDENCE: [build/test/log/hardware o NONE]
OUTPUT_PATH: [ruta del roadmap]
```

## Procedimiento

1. Lee el proyecto completo y todos los documentos de contexto disponibles.
2. Identifica capacidades actuales observadas y compáralas con bugs, riesgos, decisiones y necesidades documentadas.
3. Clasifica cada propuesta como `NEW`, `IMPROVEMENT`, `BUGFIX`, `MIGRATION`, `VALIDATION`, `DOCUMENTATION` o `REJECTED`.
4. Prioriza por seguridad, bloqueo de operación, compatibilidad, impacto, dependencia y esfuerzo estimado. Si no se puede estimar, usa `UNKNOWN`.
5. Verifica que las APIs, archivos, módulos y configuraciones mencionados existan. Una ruta candidata no prueba que el cambio sea correcto.
6. Separa tareas futuras de estado actual. Una tarea no se marca completada por aparecer en changelog, arquitectura o documentación.
7. Para cada tarea, define escenarios negativos y criterios de aceptación observables.

## Formato de tarea

```markdown
### [ID] [título parametrizado]

- Tipo: `NEW | IMPROVEMENT | BUGFIX | MIGRATION | VALIDATION | DOCUMENTATION`
- Prioridad: `CRITICAL | HIGH | MEDIUM | LOW`
- Estado: `PROPOSED | BLOCKED | READY | IN_PROGRESS | DONE | REJECTED`
- Problema/objetivo: [evidencia y resultado deseado]
- Dependencias: [IDs, módulos o NONE]
- Archivos candidatos: [rutas abstractas, no asumir que deben modificarse]
- Diseño: [pasos de alto nivel parametrizados]
- Riesgos y casos negativos: [fallos que deben probarse]
- Criterios de aceptación: [checks observables]
- Validación requerida: [build/test/simulación/hardware/revisión]
- Procedencia: [fuente y referencia]
```

## Reglas de contenido

- El roadmap solo propone trabajo; no aplica cambios ni genera commits.
- No inventes bugs, hardware, dependencias, fechas, rendimiento o compatibilidad.
- No copies ejemplos con nombres concretos: reemplázalos por `[DEVICE_ID]`, `[PIN]`, `[MODULE]`, `[ENDPOINT]`, `[TOPIC]`, `[COMMAND]` o placeholders equivalentes.
- No incluyas secretos ni instrucciones para exponerlos.
- Si una tarea depende de una decisión no tomada, márcala `BLOCKED` y formula la pregunta.
- Si una capacidad existe en una biblioteca pero no está conectada al flujo, separa “disponible” de “integrada”.
- Si la propuesta contradice la arquitectura o la fuente de verdad, registra la contradicción y no la conviertas en tarea automática.
- Los comandos y snippets deben ser genéricos, mínimos y no destructivos.

## Estructura de salida

1. Alcance y snapshot.
2. Estado actual resumido.
3. Reglas e invariantes que no deben romperse.
4. Gap analysis con evidencia.
5. Backlog priorizado por fases o versiones abstractas.
6. Dependencias y decisiones bloqueantes.
7. Validación global y riesgos.
8. Matriz de trazabilidad.
9. Preguntas abiertas y definición de terminado.

## Validación antes de entregar

Comprueba que cada tarea tenga procedencia, prioridad, estado, dependencia, aceptación y validación; que no haya propuestas presentadas como implementadas; que las rutas candidatas existan o estén marcadas como hipotéticas; que los conflictos queden visibles; y que ningún valor específico o sensible haya pasado al roadmap genérico.
