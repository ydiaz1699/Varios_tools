# PROJECT_CONTEXT — [PROJECT_ID]

> Estado: `[BORRADOR | GENERADA | PENDIENTE_DE_VERIFICAR]`
> Target: `[TARGET_ID]`
> Snapshot: `[COMMIT | TAG | BRANCH | FECHA]`
> Propósito confirmado: `[SÍ | NO | PENDIENTE_DE_CONFIRMAR]`

## Propósito y alcance

[Describe brevemente qué hace este target basándote en el código y la configuración actuales.]

- Incluye: `[TARGETS_OR_LAYERS_INCLUDED]`.
- No incluye: `[TARGETS_OR_LAYERS_EXCLUDED]`.
- Fuente del propósito: `[USER | README | CODE | CONFIGURATION | PENDING]`.

## Entradas y archivos clave

| Elemento | Ruta/símbolo | Responsabilidad | Estado |
|---|---|---|---|
| Punto de entrada | `[PATH:SYMBOL]` | `[RESPONSIBILITY]` | `[OBSERVADO_EN_CODIGO | PENDIENTE_DE_VERIFICAR]` |
| Configuración | `[PATH]` | `[RESPONSIBILITY]` | `[OBSERVADO_EN_BUILD | PENDIENTE_DE_VERIFICAR]` |
| Dependencia | `[PATH_OR_PACKAGE]` | `[RESPONSIBILITY]` | `[estado]` |

## Contexto compartido

- Convenciones: [`../../shared/CODING_STYLE.md`](../../shared/CODING_STYLE.md)
- Entorno de desarrollo: [`../../shared/SOFTWARE.md`](../../shared/SOFTWARE.md)
- Contexto específico de este target: `[PROJECT_LOCAL_CONTEXT_OR_N/A]`

No dupliques aquí el contenido completo de esos archivos. Documenta solo overrides o decisiones específicas y enlaza la fuente.

## Restricciones y límites

- `[RULE_BACKED_BY_CODE_OR_CONFIGURATION]` — fuente: `[PATH:LINE_OR_SYMBOL]`.
- `[PENDING_CONSTRAINT]` — estado: `PENDIENTE_DE_VERIFICAR`.
- No rellenar pines, hardware, endpoints, credenciales o comandos por conocimiento general.

## Verificación

| Evidencia | Comando/procedimiento | Estado | Resultado |
|---|---|---|---|
| Build | `[COMMAND_OR_NOT_FOUND]` | `[EJECUTADO | DECLARADO_NO_EJECUTADO | PENDIENTE]` | `[RESULT]` |
| Tests | `[COMMAND_OR_NOT_FOUND]` | `[EJECUTADO | NO_EXISTEN | NO_EJECUTADO]` | `[RESULT]` |
| Integración/hardware | `[PROCEDURE_OR_N/A]` | `[VERIFICADO | PENDIENTE_DE_VERIFICAR]` | `[RESULT]` |

## Pendientes y contradicciones

| Tema | Código/configuración | Documentación | Estado | Acción |
|---|---|---|---|---|
| `[TOPIC]` | `[SOURCE_VALUE]` | `[DOC_VALUE]` | `[CONTRADICTORIO | PENDIENTE_DE_VERIFICAR]` | `[NEXT_ACTION]` |

## Mantenimiento

Actualizar este punto de entrada cuando cambien el target, snapshot, dependencias, entradas, comandos o referencias. No declarar el proyecto verificado solo porque este archivo exista.
