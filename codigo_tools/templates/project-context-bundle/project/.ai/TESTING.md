# TESTING — [PROJECT_ID]

> Artefacto condicional para estrategia y evidencia de pruebas.

## Matriz de verificación

| Nivel | Comando/procedimiento | Alcance | Ejecutado | Resultado | Evidencia |
|---|---|---|---|---|---|
| Lint/sintaxis | `[COMMAND_OR_NONE]` | `[SCOPE]` | `[SÍ | NO | NO_EXISTE]` | `[RESULT_OR_PENDING]` | `[LOG/PATH]` |
| Unitario | `[COMMAND_OR_NONE]` | `[SCOPE]` | `[SÍ | NO | NO_EXISTE]` | `[RESULT_OR_PENDING]` | `[LOG/PATH]` |
| Integración | `[COMMAND_OR_NONE]` | `[SCOPE]` | `[SÍ | NO | NO_EXISTE]` | `[RESULT_OR_PENDING]` | `[LOG/PATH]` |
| Simulación | `[COMMAND_OR_NONE]` | `[SCOPE]` | `[SÍ | NO | NO_EXISTE]` | `[RESULT_OR_PENDING]` | `[LOG/PATH]` |
| Hardware/deployment | `[PROCEDURE_OR_NONE]` | `[SCOPE]` | `[SÍ | NO | NO_EXISTE]` | `[RESULT_OR_PENDING]` | `[LOG/PATH]` |

## Criterios de aceptación

- `[ACCEPTANCE_CRITERION]` — fuente: `[PATH/ISSUE]` — estado: `[PENDING | PASS | FAIL]`.

## Reglas

- No marcar PASS por la existencia de un archivo o por una inferencia.
- Registrar versión de toolchain, target y snapshot cuando afecten al resultado.
- Separar fallo reproducido, riesgo no probado y ausencia de pruebas.
