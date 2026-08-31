# CODING_STYLE.md — Convenciones compartidas

> Plantilla reusable. Completa el alcance y las excepciones del workspace antes de adoptarla.

## Alcance

- Workspace/proyecto: `[WORKSPACE_OR_PROJECT]`
- Lenguajes y frameworks: `[LANGUAGES_AND_FRAMEWORKS]`
- Archivo o proceso que aplica estas reglas: `[SOURCE_OF_POLICY]`
- Estado: `[BORRADOR | APROBADO | PENDIENTE_DE_VERIFICAR]`

## Tags de trabajo

Usa únicamente los tags que el equipo pueda revisar y cerrar. Esta lista es un default, no una obligación:

| Tag | Uso | Condición de cierre |
|---|---|---|
| `TODO` | Trabajo pendiente identificado | Debe tener contexto suficiente para retomarlo |
| `FIXME` | Comportamiento incorrecto que requiere corrección | Debe quedar corregido o convertido en tarea trazable |
| `HACK` | Solución temporal o compromiso técnico | Debe indicar por qué existe y cuándo revisarlo |
| `BUG` | Defecto conocido | Requiere ticket en `[ISSUE_TRACKER_OR_TASK_FILE]` antes de cerrar el cambio |
| `NOTE` | Información relevante para mantener el código | Debe describir una decisión o comportamiento verificable |
| `WARN` | Riesgo que puede causar daño o una operación incorrecta | Debe indicar el alcance; no usarlo como sinónimo genérico de `FIXME` |

Si el repositorio usa otra herramienta o nomenclatura, sustituye la tabla y registra la fuente. No declares que un tag es reconocido por el editor sin comprobar la configuración vigente.

## Reglas de estilo del proyecto

- Formato y lint: `[FORMATTER_OR_NONE]` — fuente: `[PATH_OR_COMMAND]`.
- Convención de nombres: `[NAMING_CONVENTION]` — fuente: `[PATH_OR_GUIDE]`.
- Idioma de comentarios/documentación: `[LANGUAGE]`.
- Organización de módulos: `[MODULE_OR_DIRECTORY_RULE]`.
- Regla de revisión para comentarios `BUG`/`FIXME`: `[REVIEW_RULE]`.

No conviertas una preferencia en una regla aplicada hasta que exista evidencia en configuración, documentación mantenida o decisión explícita del equipo.

## Targets con recursos limitados

Si el target tiene restricciones de RAM, flash, tiempo real o consumo, documenta la estrategia específica aquí:

- Targets afectados: `[RESOURCE_CONSTRAINED_TARGETS | NINGUNO_CONFIRMADO]`.
- Medición o límite: `[RESOURCE_LIMIT_AND_SOURCE]`.
- Estrategia para literales y memoria: `[STRATEGY_AND_SOURCE]`.

En un target AVR con framework que soporte la macro `F()`, puede ser apropiado usarla para literales largos; esa regla es condicional al target/framework y no debe generalizarse a otros entornos. Para cualquier otra plataforma, usa el mecanismo documentado por su toolchain y registra la evidencia.

## Revisión y mantenimiento

Antes de integrar cambios:

- [ ] Los tags nuevos están incluidos en la configuración de la herramienta de revisión.
- [ ] Cada `BUG` cerrado tiene ticket o evidencia equivalente.
- [ ] Las excepciones temporales tienen propietario o fecha de revisión.
- [ ] Las reglas se compararon con la configuración y el código actuales.
- [ ] No se copiaron secretos, valores de hardware ni identificadores de producto.

Actualiza este archivo cuando cambien las convenciones compartidas. Las reglas específicas de un proyecto deben vivir en el contexto de ese proyecto y enlazar a su fuente.
