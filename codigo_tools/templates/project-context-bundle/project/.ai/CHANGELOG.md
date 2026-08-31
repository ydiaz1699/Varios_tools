# CHANGELOG — [PROJECT_ID]

> Artefacto condicional de historial. Solo registrar cambios respaldados por commits, diffs, releases o evidencia autorizada.

## Formato de entrada

### [VERSION_OR_DATE] — [TITLE]

- Estado: `[DOCUMENTADO | APLICADO | VERIFICADO | PENDIENTE_DE_VERIFICAR]`
- Snapshot/base: `[COMMIT_TAG_BRANCH_DATE]`
- Cambio: `[WHAT_CHANGED]`
- Motivo: `[WHY]`
- Targets afectados: `[TARGETS]`
- Compatibilidad/riesgos: `[IMPACT]`
- Validación ejecutada: `[COMMAND_AND_RESULT | NO_EJECUTADO]`
- Referencias: `[PATH:LINE/SYMBOL | ISSUE]`

## Reglas

- No inventar fechas, releases, resultados ni compatibilidad.
- Una propuesta o patch no equivale a un cambio aplicado.
- Redactar secretos y valores sensibles.
- Conservar contradicciones entre historial y código actual.
