# Contrato de `recreator-spec.json`

## Propósito

`recreator-spec.json` es el manifiesto normalizado de un análisis cuyo objetivo es reconstruir, de forma genérica, el prompt o procedimiento que genera un artefacto documental. Describe la procedencia y la evidencia sin transportar el contenido completo del proyecto fuente. No es el prompt final, no es una aprobación y no autoriza promoción.

La herramienta `recreator_spec.py` valida la forma, los estados de lectura y los guardrails básicos. La inferencia sobre el contrato documental la realiza un LLM siguiendo `prompts/generar-especificacion-recreador.md`; la validación no debe fingir que puede probar una conclusión semántica por sí sola.

## Identidad y procedencia

- `schema_version`: versión entera del contrato.
- `recreator_id`: identificador estable del recreador, no una ruta ni un secreto.
- `artifact_id`: identificador estable del tipo de artefacto analizado.
- `artifact_type`: categoría normalizada del documento fuente.
- `status`: ciclo de vida (`candidate`, `proposed`, `accepted`, `deprecated`). La preparación inicial debe usar `candidate` o `proposed`.
- `purpose`: problema documental general que se resuelve.
- `target_scope`: alcance previsto; debe ser `general` o indicar un alcance abstracto.
- `document_role`: función del documento en el flujo del proyecto, no su contenido específico.
- `snapshot`: commit, tag, rama o fecha. Si no existe debe ser `UNKNOWN`.
- `source_project`: identificador o valor redactado. No debe contener secretos ni credenciales.

`source_files` conserva trazabilidad mínima: ruta relativa, referencia, tipo, papel, estado de lectura, clase de contenido, hash y presencia de material sensible. No debe contener el cuerpo de ningún archivo fuente.

### Estados de lectura

- `COMPLETE`: el archivo se leyó entero y pudo procesarse.
- `PARTIAL`: solo se leyó una parte, hubo truncamiento o el procesamiento fue incompleto.
- `MISSING`: la ruta era esperada pero no existe.
- `UNREADABLE`: existe, pero no pudo leerse o decodificarse.

Si algún archivo necesario está en `PARTIAL`, `MISSING` o `UNREADABLE`, `verification.read_complete` debe ser `false`, la ruta debe aparecer en `verification.incomplete_files` y las conclusiones que dependan de ella deben usar `LECTURA_INCOMPLETA`.

## Entradas, estructura y comportamiento

- `document_inputs`: entradas que el generador necesita, su origen, si son obligatorias y el placeholder que las representa.
- `capabilities`: acciones generales que permite el recreador.
- `inputs` y `outputs`: resumen legible de entradas y salidas.
- `sections`: estructura del documento generado. Cada sección declara si es obligatoria, cuándo se incluye, cuándo se omite y qué evidencia requiere.
- `behavioral_contract`: contrato abstracto del generador:
  - `preconditions`: condiciones previas;
  - `analysis_order`: orden de lectura y análisis;
  - `transformations`: cómo se convierte evidencia en texto;
  - `invariants`: reglas que no pueden romperse;
  - `evidence_policy`: estados admitidos y respuesta ante claims no respaldados.

La estructura debe describir el comportamiento, no copiar headings o párrafos específicos sin demostrar que son una convención reutilizable.

## Trazabilidad y estados de evidencia

`claims`, `generation_conditions`, `omission_conditions` y `reconstruction_steps` deben apuntar a rutas y referencias. Se admiten estos estados:

- `CONFIRMED`: respaldado directamente por código o por documentación coherente.
- `INFERRED`: deducido de varios indicios; debe conservar la limitación.
- `CONTRADICTED`: una fuente contradice la afirmación.
- `UNKNOWN`: no hay evidencia suficiente.
- `LECTURA_INCOMPLETA`: la decisión depende de una fuente no leída completamente.

En la evidencia de claims pueden mantenerse los estados heredados del catálogo (`OBSERVADO_EN_CODIGO`, `DOCUMENTADO`, `INFERIDO`, `CONTRADICTORIO`, `PENDIENTE_DE_VERIFICAR`). El estado normalizado del claim debe seguir siendo explícito.

Una afirmación sin evidencia no debe marcarse como `CONFIRMED`. Si el valor concreto es específico del producto, debe convertirse en placeholder o registrarse bajo `product_specific_content`; no debe aparecer en el prompt genérico.

## Reconstrucción y condiciones

- `reconstruction_steps` es una secuencia ordenada del procedimiento inferido. Cada paso declara entradas, resultado, evidencia y acción ante fallo.
- `generation_conditions` expresa cuándo se puede producir el artefacto o una sección.
- `omission_conditions` expresa cuándo hay que omitir, advertir o bloquear.
- `conflicts_with_code` registra una afirmación del documento que no coincide con la implementación. Nunca se elimina silenciosamente una contradicción.

Para documentos de planificación como `ROADMAP.md`, las propuestas se etiquetan como históricas o planificadas cuando no están implementadas. El código no convierte automáticamente una propuesta en requisito, y el documento no convierte automáticamente una propuesta en estado actual.

## Clasificación de contenido

- `reusable_content`: reglas abstractas que pueden aplicarse a otro proyecto.
- `parameterized_content`: detalles que deben representarse mediante placeholders.
- `product_specific_content`: detalles que pertenecen exclusivamente al proyecto fuente y se excluyen.
- `sensitive_fields`: categorías o rutas redactadas; jamás valores secretos.

Una misma fuente puede ser `MIXED`, pero el contenido reutilizable y el específico deben quedar separados en sus respectivas listas.

## Salidas y verificación

`output_artifacts` enumera las salidas que el LLM debe producir. El flujo base requiere al menos:

- `recreator-spec.json`;
- `recreator-prompt.md`;
- `review.md`.

En todos los casos:

```json
{
  "promotion": {
    "promotion_allowed": false,
    "review_required": true,
    "approved_by": null,
    "approved_at": null
  }
}
```

La herramienta debe rechazar una especificación que habilite promoción, contenga una aprobación simulada, exponga valores sensibles o afirme lectura completa cuando existen archivos incompletos. `verification.output_outside_source_project` se marca `true` solo después de comprobar que la salida no está dentro de `PROJECT_ROOT`.

`traceability_complete` requiere que las reglas relevantes tengan al menos una fuente o estén explícitamente marcadas como `UNKNOWN`/`PENDING_REVIEW`. `sensitive_values_redacted` solo puede ser `true` cuando la validación no detecta valores prohibidos; la ausencia de detección automática no sustituye la revisión humana.

## Guardrails de validación

Una especificación válida debe cumplir, como mínimo:

1. ser JSON válido y contener los campos de identidad, procedencia, comportamiento, condiciones, salidas, verificación y promoción;
2. usar estados pertenecientes a los vocabularios del contrato;
3. no declarar `promotion_allowed: true`;
4. declarar `review_required: true`;
5. no incluir una ruta de salida dentro del proyecto fuente;
6. listar archivos incompletos cuando `read_complete` sea `false`;
7. no incluir cuerpos completos, credenciales ni valores de secreto;
8. conservar trazabilidad para claims y decisiones;
9. no presentar claims `UNKNOWN`, `CONTRADICTED` o `LECTURA_INCOMPLETA` como hechos confirmados;
10. mantener separada la evidencia del proyecto fuente de la abstracción reusable.

La validación es deliberadamente conservadora: un resultado que no puede demostrarse se marca para revisión, no se completa por intuición.
