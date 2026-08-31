# SKILL — [TASK_ID]

> Artefacto condicional. Crear solo si existe una tarea recurrente y accionable.

## Activación

Usar cuando: `[TRIGGER_CONDITION]`.

No usar para: `[OUT_OF_SCOPE]`.

## Entradas

| Entrada | Fuente | Estado |
|---|---|---|
| Target | `[PATH_OR_USER]` | `[OBSERVADO | PENDIENTE]` |
| Configuración | `[PATH]` | `[estado]` |
| Dependencias | `[PATH_OR_PACKAGE]` | `[estado]` |

## Procedimiento

1. Leer `[FILES_OR_SCOPE]` completos antes de cambiar nada.
2. Confirmar target, snapshot y cambios previos.
3. Ejecutar `[STEP_OR_COMMAND]` solo si está autorizado.
4. Revisar diff, secretos, referencias y documentación derivada.
5. Ejecutar validaciones declaradas y registrar el resultado real.
6. Detenerse con `BLOCKED` si falta evidencia o autorización.

## Decisiones y estados

| Decisión | Opciones | Fuente | Estado |
|---|---|---|---|
| `[DECISION]` | `[OPTIONS]` | `[PATH:SYMBOL]` | `[OBSERVADO | PROPUESTO | PENDIENTE]` |

## Criterios de salida

- [ ] Archivos y cambios completos, no fragmentos ambiguos.
- [ ] Comandos ejecutados separados de comandos documentados.
- [ ] Build/tests/hardware marcados como no ejecutados cuando corresponda.
- [ ] Secretos redactados.
- [ ] Rollback o limitación de reversión documentados.
- [ ] La skill no afirma promoción o verificación sin evidencia.

## Mantenimiento

Actualizar cuando cambien el target, entradas, dependencias, estados o comandos. Comparar con `PROJECT_CONTEXT.md`, `SOFTWARE.md` y la fuente real.
