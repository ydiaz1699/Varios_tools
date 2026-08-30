# Política de detección y evolución de artefactos

## Propósito

Esta política define cómo decidir si un material encontrado al analizar un proyecto debe convertirse en un artefacto nuevo de `codigo_tools`, mejorar uno existente, conservarse como variante o rechazarse. La unidad de comparación no es el nombre del archivo ni su redacción: es la capacidad/procedimiento normalizado, sus afirmaciones, su alcance y su evidencia.

## Qué se considera artefacto

Un artefacto reutilizable puede ser un prompt, plantilla, referencia, esquema, auditoría, herramienta CLI o procedimiento que:

- resuelve una tarea repetible en más de un proyecto;
- puede separarse de los datos específicos del proyecto de origen;
- tiene entradas, salidas y reglas identificables;
- conserva procedencia y límites;
- no depende de secretos, rutas privadas o valores de un único producto.

Un `README`, `SKILL.md`, `copilot-instructions.md`, mapa o firmware específico no es reutilizable automáticamente. Primero debe extraerse su patrón y eliminar sus valores de producto.

## Flujo obligatorio

```text
1. leer el proyecto y cada candidato individualmente
2. identificar target, snapshot y baseline
3. extraer claims, capacidades, entradas, salidas, restricciones y evidencia
4. redactar secretos y separar datos específicos del patrón reusable
5. comparar contra el catálogo de artefactos existentes
6. decidir NUEVO, MEJORA, DUPLICADO, CONTRADICTORIO, VARIANTE o NO_DECIDIBLE
7. generar reporte y propuesta, nunca sobrescribir en silencio
8. revisión/aprobación humana
9. crear el artefacto nuevo o aplicar el diff de mejora
10. validar y actualizar catálogo, relaciones y procedencia
```

La lectura incompleta bloquea la promoción. La herramienta puede inventariar candidatos, pero no debe declarar `NUEVO` o `MEJORA` con confianza alta si faltan fuentes o líneas de evidencia.

## Unidad normalizada de comparación

Cada candidato debe describirse mediante un manifiesto con:

- `artifact_type`: prompt, template, reference, schema, audit, tool, skill, agent_instructions u otro tipo explícito;
- `purpose`: tarea que resuelve;
- `target_scope`: general, embedded, PlatformIO, Docker, web, etc.;
- `capabilities`: acciones observables que aporta;
- `inputs` y `outputs`;
- `claims`: afirmaciones o reglas con `key`, `value` y procedencia;
- `sections`: estructura funcional, no solo títulos;
- `compatibility`: runtimes, frameworks, formatos o targets;
- `evidence`: snapshot, archivo y línea/símbolo/chunk;
- `sensitive_fields`: valores que fueron redactados.

El `artifact_id` es identificador estable del artefacto canónico. No debe cambiar solo porque cambie la redacción; la versión y el historial registran la evolución.

## Decisiones

### `NUEVO`

No hay artefacto existente con propósito, tipo y capacidad equivalentes. El candidato tiene evidencia suficiente y un patrón separable de los datos específicos. Acción: generar un scaffold/propuesta de nuevo artefacto; no publicarlo sin revisión.

### `MEJORA`

Existe un artefacto canónico con la misma tarea, pero el candidato aporta una o más capacidades, reglas, formatos, casos límite, verificaciones o fuentes que faltan. Acción: generar un diff de secciones y una propuesta de versión; conservar la procedencia del aporte.

### `DUPLICADO`

Propósito, alcance, capacidades y claims relevantes son equivalentes. Las diferencias son redacción, orden, nombres o formato sin información nueva. Acción: no crear otra copia; referenciar el canónico.

### `CONTRADICTORIO`

Mismo propósito/alcance, pero una misma clave tiene valores o reglas incompatibles, por ejemplo un timeout, un estado o una condición de filtrado diferente. Acción: bloquear la fusión, mostrar ambas evidencias y pedir decisión.

### `VARIANTE`

La capacidad es similar, pero el target, framework, formato o dependencia no es compatible. Acción: conservar un artefacto separado o convertirlo en una extensión explícita; no fusionar datos específicos.

### `NO_DECIDIBLE`

Falta propósito confirmado, baseline, archivo, chunk, evidencia, manifiesto válido o la similitud es ambigua. Acción: emitir preguntas y mantener el candidato pendiente.

## Reglas de mejora

- No reemplazar un artefacto canónico completo por un draft parcial.
- No mezclar dos implementaciones incompatibles para obtener una única versión.
- Una mejora debe indicar qué sección/claim agrega, corrige o elimina y por qué.
- Si una fuente contradice el código actual, la contradicción se conserva como hallazgo; no se promueve como regla.
- Las mejoras de proceso son reutilizables; las constantes de producto se quedan en el proyecto fuente.
- Un artefacto puede mejorar a otro sin que el producto de origen esté compilado o probado; marcar cada nivel de evidencia por separado.
- `APLICADO`, `COMPILADO`, `VERIFICADO` y `VERIFICADO_EN_HARDWARE` no son sinónimos.

## Seguridad y revisión

- No copiar secretos, tokens, credenciales, SSID, claves privadas ni identificadores sensibles sin autorización.
- Usar `[REDACTADO]` y conservar el nombre del campo/ruta cuando sea necesario para entender el patrón.
- El modo predeterminado es `propose`: genera manifiesto, comparación y propuesta.
- `apply` requiere aprobación explícita, diff revisable, validación y actualización del catálogo.
- El catálogo solo contiene artefactos aceptados; los candidatos pendientes viven en reportes/propuestas.

## Registro mínimo de una decisión

```text
candidate_id
candidate_source
candidate_snapshot
canonical_artifact_id
decision
confidence
matching_capabilities
new_claims
conflicts
evidence_gaps
proposal_path
review_status
reviewer/approval
```
