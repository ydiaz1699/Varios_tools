# PROJECT_CONTEXT — [nombre-proyecto]

> Estado: `[BORRADOR | GENERADA | PENDIENTE_DE_VERIFICAR]`
> Target: `[target exacto]`
> Snapshot: `[commit/rama/tag/fecha]`
> Propósito confirmado: `[confirmado | PENDIENTE_DE_CONFIRMAR]`

## Propósito y alcance

[Describe en 2–3 líneas qué hace realmente el target.]

- Incluye: [target, entorno y capas cubiertos].
- No incluye: [targets, versiones, placas o capas excluidos].
- Fuente del propósito: `[usuario | README | código | PENDIENTE_DE_CONFIRMAR]`.

## Entradas y puntos de entrada

| Elemento | Ruta/símbolo | Responsabilidad | Estado |
|---|---|---|---|
| Punto de entrada | `[ruta:símbolo]` | [qué inicia] | `[OBSERVADO_EN_CODIGO]` |
| Configuración | `[ruta]` | [qué configura] | `[OBSERVADO_EN_BUILD | PENDIENTE_DE_VERIFICAR]` |

## Referencias de hardware y documentos

- Catálogo board: `[boards/<board-id>.json | PENDIENTE_DE_VERIFICAR]`.
- Catálogo peripherals: `[peripherals/<peripheral-id>.json | N/A]`.
- Wiring del proyecto: `[project-wiring.json | N/A]`.
- Documentos relacionados: `[ruta relativa]`.

No copies aquí las especificaciones completas del catálogo ni el wiring detallado. Resuelve y valida las referencias desde el archivo que las contiene.

## Archivos clave

| Archivo | Responsabilidad | Estado |
|---|---|---|
| `[ruta]` | [una frase] | `[OBSERVADO_EN_CODIGO | OBSERVADO_EN_BUILD | DOCUMENTADO]` |

## Restricciones y límites

- [Regla respaldada por código/configuración o `PENDIENTE_DE_VERIFICAR`].
- [Separar reglas implementadas de propuestas futuras].

## Verificación

| Evidencia | Comando/procedimiento | Estado | Resultado |
|---|---|---|---|
| Build | `[comando o NO_ENCONTRADO]` | `[EJECUTADO | DECLARADO_NO_EJECUTADO | PENDIENTE]` | `[resultado]` |
| Tests | `[comando o NO_EXISTEN]` | `[EJECUTADO | NO_EJECUTADO | NO_EXISTEN]` | `[resultado]` |
| Hardware | `[procedimiento o N/A]` | `[VERIFICADO_EN_HARDWARE | PENDIENTE_DE_VERIFICAR]` | `[resultado]` |

## Pendientes y contradicciones

| Tema | Código/configuración | Documentación | Estado | Acción |
|---|---|---|---|---|
| [tema] | [valor/fuente] | [valor/fuente] | `[CONTRADICTORIO | PENDIENTE_DE_VERIFICAR]` | [siguiente paso] |

## Mantenimiento

Actualizar este archivo cuando cambien el target, snapshot, puntos de entrada, dependencias, wiring, estados o comandos. No sustituye el README, `repo-map.yml`, `SKILL.md` ni el análisis completo.
