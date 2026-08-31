---
name: generar-checklist-cambio-seguro
description: Convierte una solicitud de cambio en un checklist trazable y no destructivo, con baseline, precondiciones, validación y promoción manual.
---

# Generar checklist de cambio seguro

## Objetivo

Transforma una solicitud de cambio en un plan ejecutable y revisable sin aplicar modificaciones automáticamente. El resultado debe permitir distinguir lo que se propone, lo que se observó en el repositorio, lo que se ejecutó y lo que todavía requiere autorización o verificación.

Este prompt abstrae el patrón de los drafts de cambios, bugs y patches. No genera firmware, no aplica parches, no hace commit, no hace push y no sustituye la revisión humana.

## Entradas obligatorias

Identifica antes de analizar:

- `PROJECT_ROOT`: raíz del repositorio.
- `TARGET_ID`: target, servicio, módulo o ensamblaje afectado.
- `SNAPSHOT`: commit, rama, tag o fecha observada.
- `CHANGE_REQUEST`: solicitud exacta, sin ampliarla por inferencia.
- `OUTPUT_PATH`: ruta fuera de la fuente para el checklist.
- `BASELINE_DOCS`: documentos, incidencias o decisiones que deben contrastarse.
- `AUTHORIZED_ACTIONS`: acciones que el usuario autorizó ejecutar, si existe alguna.

Si hay varios targets o versiones, separa cada uno. No conviertas un cambio de un target en una modificación global.

## Reglas no negociables

1. Leer primero el código, configuración, tests, documentación y dependencias relacionadas.
2. Ejecutar `git status --short` si está disponible y registrar cambios previos sin sobrescribirlos.
3. No asumir que un patch, bug report, changelog o instrucción histórica describe el estado actual.
4. No copiar secretos. Redacta valores de contraseñas, tokens, claves, SSID, certificados, URLs privadas e identificadores sensibles.
5. No documentar un build, test, simulación, hardware o despliegue como ejecutado si no existe comando, entorno y resultado.
6. Mantener separadas estas categorías: `OBSERVADO`, `PROPUESTO`, `APLICADO`, `COMPILADO`, `TESTEADO`, `VERIFICADO`, `RECHAZADO` y `PENDIENTE`.
7. No usar un patch como fuente de verdad. El código actual y la configuración actual tienen prioridad para describir comportamiento.
8. Si el cambio es destructivo, afecta producción, cambia interfaz o toca secretos, marcarlo como `REQUIERE_AUTORIZACIÓN_EXPLÍCITA`.
9. Si faltan archivos o dependencias, detener la conclusión con `LECTURA_INCOMPLETA`.
10. El output debe estar fuera de `PROJECT_ROOT` o en un archivo explícitamente autorizado; nunca sobrescribir fuentes.

## Procedimiento

### Fase 1 — Baseline y alcance

Registrar:

```text
Target:
Snapshot:
Rama/commit:
Estado inicial del repositorio:
Solicitud literal:
Archivos y dependencias en alcance:
Targets excluidos:
Secretos detectados por nombre, nunca por valor:
Estado de lectura: COMPLETA | LECTURA_INCOMPLETA
```

Construir una matriz:

| Elemento | Fuente | Estado actual | Relación con el cambio | Riesgo |
|---|---|---|---|---|
| Archivo/símbolo | `ruta:línea/símbolo` | observado | directo/indirecto | bajo/medio/alto |

### Fase 2 — Precondiciones

Antes de proponer pasos, comprobar:

- target y snapshot inequívocos;
- cambios previos del usuario preservados;
- archivos y dependencias disponibles;
- configuración/secretos requeridos identificados sin exhibirlos;
- compatibilidad entre versiones, interfaces y consumidores;
- comandos declarados y comandos realmente disponibles;
- rollback posible o condición explícita de no reversibilidad.

Si alguna precondición falla, escribir `BLOCKED` y la acción necesaria. No rellenar con suposiciones.

### Fase 3 — Plan mínimo

Descomponer el cambio en pasos ordenados:

1. preparar copia, branch o output separado según la autorización;
2. modificar solo los archivos necesarios;
3. actualizar documentos derivados afectados;
4. ejecutar validaciones pequeñas;
5. ejecutar build/tests autorizados;
6. revisar diff y secretos;
7. decidir promoción, rollback o pendiente.

Cada paso debe incluir:

```markdown
### Paso C## — [acción]

- Estado inicial requerido:
- Archivos afectados:
- Acción propuesta:
- Evidencia esperada:
- Comando documentado:
- Comando ejecutado: SÍ | NO
- Resultado:
- Rollback:
- Gate de salida:
```

No pedir `chmod`, crear archivos, ejecutar comandos ni desplegar en un orden que contradiga las precondiciones reales.

### Fase 4 — Validación y regresión

Definir criterios verificables para:

- sintaxis/configuración;
- build o lint;
- tests unitarios/integración;
- compatibilidad de interfaces;
- regresión del comportamiento existente;
- seguridad y ausencia de secretos en el diff;
- documentación y referencias;
- hardware o despliegue, si aplica.

Clasificar cada criterio como `EJECUTADO`, `DECLARADO_NO_EJECUTADO`, `NO_EXISTE` o `PENDIENTE`.

### Fase 5 — Promoción manual

Terminar con una decisión explícita:

- `READY_FOR_REVIEW`: el checklist está completo, pero requiere revisión.
- `BLOCKED`: falta información, dependencia o autorización.
- `REJECTED`: el cambio no cumple alcance o seguridad.
- `APPLIED_NOT_VERIFIED`: se aplicó, pero falta evidencia.
- `VERIFIED_PENDING_PROMOTION`: hay evidencia, pero no autorización para integrar.

Nunca usar `DONE` únicamente porque exista un diff o porque un comando terminó sin error.

## Formato de salida

Genera un Markdown con estas secciones:

```markdown
# Checklist de cambio seguro — [TARGET_ID]

## Estado y alcance
## Baseline y cambios previos
## Solicitud literal y supuestos
## Matriz de trazabilidad
## Precondiciones y bloqueos
## Plan ordenado de ejecución
## Validación y regresión
## Seguridad y secretos
## Rollback
## Decisión de promoción
## Pendientes
## Evidencia ejecutada
```

Incluye una tabla final:

| Afirmación | Fuente | Estado | Evidencia | Acción |
|---|---|---|---|---|

## Criterios de calidad

Antes de entregar, confirma:

- la solicitud no fue ampliada silenciosamente;
- cada archivo afectado tiene una razón;
- el orden de pasos es ejecutable;
- los comandos ejecutados se distinguen de los documentados;
- el rollback está definido o marcado como no disponible;
- los secretos están redactados;
- no hay afirmaciones de build, tests o hardware sin evidencia;
- no se aplicaron cambios automáticamente.
