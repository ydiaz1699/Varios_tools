# TASKS — [PROJECT_ID]

> Artefacto condicional. Solo registrar trabajo mantenido; no convertir ideas históricas en tareas aprobadas.

## Estados permitidos

`OPEN`, `BLOCKED`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `DONE`, `REJECTED`, `PENDING_VERIFICATION`.

`DONE` requiere evidencia de aceptación. Una mención en un changelog o patch no basta.

## Tareas

| ID | Título | Alcance/target | Fuente | Estado | Criterio de aceptación | Evidencia |
|---|---|---|---|---|---|---|
| `[TASK-001]` | `[TITLE]` | `[TARGET_ID]` | `[PATH/ISSUE]` | `[STATUS]` | `[MEASURABLE_CRITERION]` | `[RESULT_OR_PENDING]` |

## Bloqueos y dependencias

- `[BLOCKER]` — responsable/acción: `[ACTION]` — estado: `[BLOCKED | PENDING]`.

## Reglas

- No cerrar una tarea sin registrar la evidencia y el snapshot correspondiente.
- Separar bug confirmado, riesgo, propuesta y pregunta abierta.
- No copiar secretos ni datos de producto innecesarios.
