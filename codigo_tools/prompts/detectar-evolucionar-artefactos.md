---
name: detectar-evolucionar-artefactos
description: Detecta material reutilizable en un proyecto y decide si crea un artefacto nuevo, mejora uno existente, conserva una variante o bloquea una contradicción.
---

# Detectar y evolucionar artefactos reutilizables

## Objetivo

Analiza un proyecto completo para encontrar prompts, plantillas, referencias, esquemas, auditorías, skills, instrucciones de agentes, scripts y procedimientos que puedan reutilizarse en `codigo_tools`. Compara cada candidato con los artefactos canónicos existentes y produce una decisión trazable:

- `NUEVO`: no existe equivalente.
- `MEJORA`: existe equivalente y el candidato aporta material nuevo.
- `DUPLICADO`: no aporta información nueva.
- `CONTRADICTORIO`: misma regla con valores o comportamiento incompatible.
- `VARIANTE`: capacidad similar, pero target/formato/dependencias incompatibles.
- `NO_DECIDIBLE`: falta evidencia o contexto.

Este prompt no debe copiar firmware, README ni archivos de configuración específicos como si fueran herramientas generales. Extrae el patrón, parametriza los datos y conserva la procedencia.

## Entradas

- `PROJECT_ROOT`: raíz del proyecto analizado.
- `TARGET_ID`: target exacto.
- `SNAPSHOT`: commit, rama, tag o fecha.
- `PROJECT_PURPOSE`: propósito confirmado o `PENDIENTE_DE_CONFIRMAR`.
- `CANDIDATE_PATHS`: drafts, prompts, skills, plantillas, scripts, documentación y configuraciones candidatas.
- `CODE_ROOTS`: código/configuración que demuestra el comportamiento.
- `ARTIFACT_CATALOG`: catálogo actual de artefactos aceptados; si no existe, declararlo y construir un inventario provisional.
- `BASELINE_PATHS`: README, mapas, skills, instrucciones, prompts o versiones anteriores.
- `OUTPUT_ROOT`: ruta de reportes y propuestas.

## Lectura completa antes de decidir

1. Inventaría todos los archivos del target y de los candidatos.
2. Lee individualmente cada candidato, incluso si parece duplicado por nombre.
3. Lee el código/configuración que respalda sus reglas; sigue imports/includes y dependencias.
4. Lee el artefacto canónico completo antes de proponer una mejora.
5. Compara contra baseline y registra snapshot, rutas y rangos de línea.
6. Si falta un archivo, dependencia o chunk necesario, emite `LECTURA_INCOMPLETA` y no promuevas el candidato.

Inventario obligatorio:

```text
Target:
Snapshot:
Propósito:
Candidatos:
Archivos leídos:
Archivos/chunks faltantes:
Baselines/canónicos comparados:
Código/configuración de respaldo:
Estado de lectura: COMPLETA | LECTURA_INCOMPLETA
```

## Qué extraer de cada candidato

Para cada candidato genera un manifiesto normalizado con:

- `artifact_id_candidate` y `artifact_type`;
- propósito y tarea repetible;
- lector principal;
- alcance y compatibilidad;
- capacidades accionables;
- entradas y salidas;
- secciones funcionales;
- reglas, decisiones, formatos y criterios de aceptación;
- claims importantes con `key`, `value`, estado y procedencia;
- dependencias y restricciones;
- datos específicos del producto que deben eliminarse o parametrizarse;
- secretos/identificadores redactados;
- comandos y verificaciones realmente ejecutados o no ejecutados.

Una afirmación no respaldada por el código/documentación debe conservarse como `DOCUMENTADO`, `INFERIDO`, `PROPUESTO` o `PENDIENTE_DE_VERIFICAR`; nunca como implementación observada.

## Comparación semántica

No compares solo nombres o texto completo. Compara en este orden:

1. `artifact_type` y propósito.
2. `target_scope` y compatibilidad.
3. capacidades, entradas, salidas y secciones funcionales.
4. claims normalizados, especialmente reglas con la misma clave.
5. evidencia, cobertura, seguridad y verificaciones.
6. texto solo como apoyo para detectar posibles coincidencias.

Para cada comparación registra:

```text
Candidato | Canónico | Capacidades comunes | Capacidades nuevas | Claims iguales | Claims distintos | Compatibilidad | Evidencia | Decisión
```

## Criterios de decisión

### NUEVO

Usa `NUEVO` solo cuando no haya capacidad equivalente y el candidato sea separable de los datos del producto. Propón un nombre estable, tipo, ruta, entradas, salidas y plantilla de destino.

### MEJORA

Usa `MEJORA` cuando exista un canónico y el candidato añada cobertura, trazabilidad, validación, casos límite, compatibilidad o reglas útiles. Enumera cada aporte con fuente y destino exacto. Genera un plan de merge o diff; no sobrescribas automáticamente.

### DUPLICADO

Usa `DUPLICADO` si las diferencias son solo redacción, orden, emojis, nombres o formato. Referencia el canónico y explica por qué no se crea otro.

### CONTRADICTORIO

Usa `CONTRADICTORIO` si la misma clave/regla tiene valores incompatibles. Ejemplos: timeout distinto, condición AND frente a OR, UUID obligatorio frente a opcional, o comando diferente para el mismo paso. Conserva ambas fuentes y formula la decisión pendiente.

### VARIANTE

Usa `VARIANTE` si el patrón es similar, pero cambia target, plataforma, dependencia, formato o contrato de salida de forma incompatible. Parametriza solo lo común y conserva una extensión separada si aporta valor.

### NO_DECIDIBLE

Usa `NO_DECIDIBLE` si falta lectura, propósito, baseline, procedencia, evidencia o no se puede distinguir una mejora real de una reformulación.

## Separar patrón reusable de datos de producto

Para cada candidato divide el contenido en cuatro grupos:

1. `REUSABLE`: reglas, estructura, algoritmo documental, validaciones y flujo.
2. `PARAMETRIZABLE`: nombres de rutas, target, board, dependencias, comandos y formatos.
3. `PRODUCT_SPECIFIC`: firmware, MAC, GPIO, UUID, topics, endpoints, valores de un único proyecto.
4. `SENSITIVE`: secretos o identificadores que deben redactarse.

Solo `REUSABLE` y la estructura parametrizada llegan a `codigo_tools`. `PRODUCT_SPECIFIC` queda documentado en el proyecto fuente; `SENSITIVE` nunca se copia.

## Salidas obligatorias

Escribe en `OUTPUT_ROOT`:

1. `candidates/<id>.json`: manifiesto normalizado del candidato.
2. `reports/<id>.md`: informe humano con inventario, comparación, decisión, confianza, evidencia, aportes y pendientes.
3. `reports/<id>.json`: resultado máquina con `decision`, `canonical_artifact_id`, `matching_capabilities`, `new_claims`, `conflicts`, `evidence_gaps` y `proposal_path`.
4. `proposals/<id>-new.md` si es `NUEVO`.
5. `proposals/<id>-improvement.md` si es `MEJORA`.
6. `proposals/<id>-conflict.md` si es `CONTRADICTORIO`.
7. `proposals/<id>-variant.md` si es `VARIANTE`.

El informe debe indicar:

```text
Estado de lectura:
Candidato:
Canónico comparado:
Decisión:
Confianza: ALTA | MEDIA | BAJA
Qué aporta:
Qué se descartó y por qué:
Qué se parametrizó:
Qué no se pudo verificar:
Aprobación requerida:
```

## Regla de creación y mejora

- En `NUEVO`, usa la plantilla adecuada y crea una propuesta completa, no una copia parcial del draft.
- En `MEJORA`, conserva el artefacto canónico completo y genera un diff por secciones; no reemplaces el archivo con solo el contenido nuevo.
- En `DUPLICADO`, no generes archivo nuevo.
- En `CONTRADICTORIO`, no fusiones hasta que el usuario decida.
- En `VARIANTE`, crea un artefacto separado solo si la diferencia de compatibilidad está documentada.
- En todos los casos, actualiza el catálogo únicamente después de aprobación.

## Validación antes de entregar

- [ ] El target y snapshot están identificados.
- [ ] Cada candidato fue leído individualmente.
- [ ] El código/configuración de respaldo fue leído.
- [ ] Los canónicos comparados fueron leídos completos.
- [ ] Cada claim importante tiene procedencia.
- [ ] Se separaron patrones, parámetros, datos específicos y secretos.
- [ ] Se aplicó una decisión explícita; no se usó “parecido” sin razones.
- [ ] No se sobrescribió ningún artefacto.
- [ ] Las propuestas conservan bloques y detalles completos.
- [ ] Builds, tests y hardware no ejecutados están marcados.
- [ ] Se pidió aprobación para crear o mejorar.

Termina con: `Detección completada: [NUEVO|MEJORA|DUPLICADO|CONTRADICTORIO|VARIANTE|NO_DECIDIBLE]`.
