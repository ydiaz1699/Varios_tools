---
name: audit-project-docs
description: Audita README, repo-map, notas y otros documentos contra el código y la configuración actuales de un target.
---

# Auditar la documentación completa de un proyecto

## Objetivo

Compara la documentación derivada de un target con el código/configuración actuales para detectar afirmaciones omitidas, extras, contradictorias, estimadas o desactualizadas. Audita el conjunto completo: README, `repo-map.yml`, notas de hardware, diagramas, changelog, prompts y documentación operativa.

Este prompt no corrige archivos automáticamente. Produce una matriz de auditoría y propone correcciones con procedencia.

## Entradas

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: target y entorno exactos.
- `SNAPSHOT`: commit/rama/tag/fecha del código.
- `DOCS_PATHS`: documentos a auditar.
- `BASELINE_PATHS`: documentación histórica opcional.

Si hay varios targets, separar la auditoría por target. No comparar un emisor con un receptor, V3 con V4 o dos placas distintas como si fueran el mismo sistema.

## Lectura obligatoria

1. Inventaría y lee completamente el código, headers, configuración de build, dependencias y archivos de setup del target.
2. Lee completamente cada documento indicado y comprueba, en SVG, tanto la vista exterior como el XML interno draw.io.
3. Sigue includes/imports, flags y configuración compartida.
4. Si falta un archivo relevante o un chunk, devuelve `LECTURA_INCOMPLETA` y no emite PASS.
5. No expongas secretos; registra solo su variable/ruta con `[REDACTADO]`.

## Matriz

```text
ID | afirmación | fuente actual | documento | evidencia | estado | severidad | acción
```

Audita como mínimo:

- identidad del target, snapshot, placa, entorno y versión;
- funciones implementadas frente a features documentadas;
- pines, modos, niveles, buses y conexiones físicas;
- protocolos lógicos, puertos, topics, endpoints y formatos;
- constantes, timers, reintentos, FSM y orden de ejecución;
- comandos de build/upload/run/test/monitor;
- rutas y creación de secretos/configuración;
- tests y mediciones realmente ejecutados;
- problemas y propuestas presentados como tales;
- licencia, métricas, consumo y versiones solo si tienen fuente;
- presencia de datos sensibles;
- validez del YAML y XML draw.io cuando aplique.

## Estados

- `COINCIDE`: respaldado por código/configuración.
- `OMITIDO`: existe en código pero falta en documentación.
- `EXTRA`: se afirma sin respaldo actual.
- `CONTRADICTORIO`: código y documento difieren.
- `ESTIMADO_SIN_MARCA`: estimación presentada como hecho.
- `PROPUESTA_PRESENTADA_COMO_IMPLEMENTADA`.
- `COMANDO_NO_VERIFICADO`.
- `LECTURA_INCOMPLETA`.
- `SECRETO_EXPUESTO`.
- `FORMATO_INVALIDO`.

## Salida

```markdown
# Auditoría documental — [TARGET_ID]

- Snapshot:
- Documentos:
- Lectura: COMPLETA | LECTURA_INCOMPLETA
- Estado global: PASS | PASS_CON_ADVERTENCIAS | FAIL

## Resumen
[Conteo y hallazgos principales.]

## Matriz de cobertura y contradicciones
| ID | Afirmación | Fuente actual | Documento | Evidencia | Estado | Severidad | Acción |
|---|---|---|---|---|---|---|---|

## Problemas críticos y altos
[Hallazgos con rutas y referencias exactas.]

## Comandos y setup no verificables
[Comandos o pasos sin fuente ejecutable.]

## Features documentadas no encontradas en código
[Lista separada de propuestas o afirmaciones no implementadas.]

## Datos pendientes
[Mediciones, datasheets, hardware, builds o respuestas necesarias.]

## Decisión
[Aceptar, regenerar documentos o pedir información.]
```

No emitas `PASS` si falta lectura, hay secretos expuestos, el target no coincide o queda una contradicción crítica sin registrar.
