---
name: analizar-target-unico
description: Analiza un único target del proyecto y genera un informe técnico narrativo, sin mezclar variantes ni comparar targets.
---

# Analizar un único target y generar informe

## Propósito

Analiza **un solo target** de un proyecto y genera un informe técnico comprensible para una persona o LLM. El informe debe explicar qué contiene el target, cómo funciona realmente, qué parámetros se encontraron, qué problemas o contradicciones existen y qué partes podrían reutilizarse.

Este prompt está pensado para una ejecución enfocada. No compara targets, no consolida variantes, no modifica código, no aplica parches y no genera commits. Si el repositorio contiene otros targets, se excluyen y se registran brevemente como fuera de alcance.

Usa `analizar-codigo-completo.md` cuando necesites comparar varios targets o producir una vista transversal. Usa este prompt cuando quieras responder únicamente: **«analiza este target y dame su informe»**.

## Entradas

Proporciona estos valores antes de comenzar:

```text
PROJECT_ROOT: [raíz del repositorio o NONE si TARGET_PATH es autosuficiente]
TARGET_ID: [identificador único del target]
TARGET_PATH: [ruta relativa al directorio o archivo principal del target]
SNAPSHOT: [commit, rama, tag o fecha]
OUTPUT_PATH: [ruta del informe, fuera de PROJECT_ROOT]
LANGUAGE: [español por defecto]
```

Opcionales:

```text
SHARED_PATHS: [bibliotecas, headers o configuración compartida requerida]
BASELINE_DOCS: [README, notas, mapa, changelog o NONE]
VALIDATION_EVIDENCE: [build, tests, simulación, hardware o NONE]
ALLOWED_EXTERNAL_SOURCES: [datasheet, issue, ticket o NONE]
```

### Regla de alcance

`TARGET_PATH` define el único target analizado. Puedes leer una dependencia compartida únicamente cuando el target la consume realmente; en ese caso, incluye solo la parte necesaria y marca la ruta como `DEPENDENCIA_COMPARTIDA`.

No mezcles:

- otras carpetas de firmware;
- otras placas o variantes;
- otros servicios o entornos;
- ramas o snapshots diferentes;
- documentación de otro target como si fuera evidencia del seleccionado.

Si `TARGET_PATH` no es inequívoco, detén el informe final y devuelve `INPUT_AMBIGUOUS` con las alternativas encontradas.

## Estados de evidencia

Usa estados explícitos y no los mezcles:

- `OBSERVADO_EN_CODIGO`: aparece en código ejecutable leído.
- `OBSERVADO_EN_BUILD`: aparece en configuración de compilación o despliegue.
- `DOCUMENTADO`: aparece en documentación, pero no está confirmado por el código.
- `INFERIDO`: deducción razonable; explica la evidencia indirecta.
- `PROPUESTO`: mejora o comportamiento futuro.
- `CONTRADICTORIO`: dos fuentes no coinciden.
- `NO_ENCONTRADO`: se buscó y no existe en el alcance.
- `PENDIENTE_DE_VERIFICAR`: requiere build, test, simulación, datasheet o hardware.
- `PRESENTE_NO_EXHIBIDO`: existe un secreto o dato sensible cuyo valor no se muestra.

El estado de ejecución es independiente:

- `NO_EJECUTADO`
- `EJECUTADO`
- `COMPILADO`
- `TESTEADO`
- `VERIFICADO_EN_HARDWARE`
- `NO_EXISTE`

`OBSERVADO_EN_CODIGO` no significa que funcione. `DOCUMENTADO` no significa que esté implementado. `COMPILADO` no significa que esté verificado en hardware.

## Reglas obligatorias

1. Lee completamente todos los archivos del target y las dependencias compartidas transitivas necesarias: entry points, headers, fuentes, configuración, manifests, scripts, tests y documentación relacionada.
2. Mantén un inventario de archivos individual; no agrupes archivos distintos si eso oculta responsabilidades o contradicciones.
3. Sigue `#include`, imports, bibliotecas locales, configuración de build, callbacks y consumidores reales.
4. Si falta un archivo necesario, un chunk no puede leerse o una dependencia no se resuelve, detén la conclusión afectada con `LECTURA_INCOMPLETA`.
5. El código/configuración actual es la fuente principal del comportamiento. README, notas, mapas y changelogs son referencias secundarias.
6. No inventes pines, componentes, voltajes, niveles lógicos, tiempos, métricas, protocolos, comandos, problemas ni soluciones.
7. No imprimas secretos. Conserva el nombre de la variable y la ruta, pero sustituye el valor por `[REDACTADO]`.
8. No afirmes build, test, simulación, integración o hardware si no existe evidencia de ejecución.
9. Distingue evento puntual, estado mantenido, acción y efecto externo cuando el target los tenga.
10. Registra constantes declaradas pero no usadas, estados inalcanzables, funciones no conectadas al flujo y documentación que contradice al código.
11. No modifiques el proyecto ni escribas dentro de `PROJECT_ROOT`. El informe debe salir en `OUTPUT_PATH` externo.
12. No incluyas firmware, secretos, wiring o valores de producto como recomendaciones globales. En la sección de reutilización abstrae el patrón y conserva el dato concreto solo como evidencia redactada o específica del target.

## Procedimiento

### Fase 1 — Confirmar el alcance

Antes de analizar, registra:

```text
Target seleccionado:
Ruta del target:
Snapshot:
Targets/variantes excluidos:
Motivo de exclusión:
Dependencias compartidas incluidas:
Dependencias no resueltas:
Estado de lectura: COMPLETA | LECTURA_INCOMPLETA | INPUT_AMBIGUOUS
```

Si encuentras varios candidatos para `TARGET_PATH`, no elijas por intuición. Devuelve la lista y solicita selección.

### Fase 2 — Inventario de archivos

Para cada archivo leído, genera una ficha:

```markdown
### [N] — `ruta/archivo`

- Tipo: código | header | configuración | build | documentación | test | script | secreto/plantilla | dependencia compartida
- Estado de lectura: COMPLETA | INCOMPLETA
- Responsabilidad real:
- Símbolos, entry points o puntos de integración:
- Includes/imports/dependencias:
- Constantes, pines, puertos, timers, estados o formatos:
- Efectos secundarios:
- Consumidores:
- Estado de evidencia:
- Observaciones, ausencias o contradicciones:
```

Incluye también archivos estándar sin lógica propia cuando estén dentro del target, por ejemplo READMEs generados por PlatformIO. Clasifícalos como `GENÉRICO_SIN_LÓGICA` en vez de omitirlos silenciosamente.

### Fase 3 — Reconstruir el comportamiento

Explica con evidencia:

1. propósito real del target;
2. plataforma, placa, framework y entorno de build;
3. punto de entrada y orden de inicialización;
4. flujo principal, callbacks, interrupciones y eventos;
5. entradas, transformaciones, salidas y persistencia;
6. hardware, pines, modos, niveles activos y buses, solo si están respaldados;
7. comunicaciones lógicas y sus límites;
8. timers, debounce, `delay()`, reintentos, timeouts y backoff;
9. errores, estados de recuperación y condiciones de fallo;
10. build, dependencias, tests y comandos declarados.

Representa los flujos importantes así:

```text
entrada → función/símbolo → estado o transformación → salida/efecto
```

### Fase 4 — Parámetros encontrados

Resume los valores que realmente aparecen en el target:

| Parámetro | Valor redactado | Fuente | Estado | Observación |
|---|---|---|---|---|
| `[NOMBRE]` | `[VALOR_O_REDACTADO]` | `ruta:línea/símbolo` | `[estado]` | `[limitación]` |

Incluye constantes de tiempo, debounce, duraciones, límites, pines, puertos, tamaños, estados, intentos, velocidades y flags cuando sean relevantes. No conviertas un valor específico en regla para otros targets.

### Fase 5 — Problemas, riesgos y contradicciones

No llames bug a toda diferencia. Clasifica cada hallazgo como:

- `BUG_DEMOSTRABLE`: el flujo ejecutable evidencia el fallo.
- `RIESGO_TÉCNICO`: puede fallar según plataforma, carga, librería o hardware.
- `DIVERGENCIA_DOCUMENTAL`: documentación y código no coinciden.
- `CONFIGURACIÓN_INCOMPLETA`: falta archivo, variable, dependencia o paso.
- `AUSENCIA_RELEVANTE`: una capacidad esperable no existe en este target.
- `PROPUESTA_NO_IMPLEMENTADA`: está descrita, pero no existe en código.

Usa este formato:

```markdown
### H## — [título]

- Clasificación:
- Severidad: CRÍTICA | ALTA | MEDIA | BAJA
- Estado de evidencia:
- Comportamiento observado:
- Evidencia: `ruta:línea/símbolo`
- Impacto en este target:
- ¿Fue reproducido o verificado?: SÍ | NO | PENDIENTE
- Acción sugerida:
- Fuera de alcance: [qué no debe extrapolarse]
```

Separa siempre:

```text
síntoma observado
→ causa confirmada o hipótesis
→ solución propuesta
→ cambio aplicado, si existe
→ build/test/integración/hardware
```

### Fase 6 — Reutilización controlada

Cierra el informe con dos listas distintas:

#### Patrones potencialmente reutilizables

Describe únicamente procedimientos o reglas abstractas, por ejemplo:

- leer el código como fuente de verdad;
- derivar notas de hardware del inventario real;
- separar wiring físico de comunicación lógica;
- comprobar compatibilidad eléctrica;
- registrar timers y estados;
- detenerse ante lectura incompleta;
- mantener una matriz claim → fuente → estado.

#### Datos específicos de este target

Enumera lo que no debe copiarse sin adaptación:

- nombres de pines y componentes;
- modelo de placa;
- voltajes y niveles;
- protocolos, payloads y topics;
- direcciones, rutas, IDs y credenciales;
- tiempos, buffers y límites;
- comandos y dependencias particulares.

## Formato de salida obligatorio

Genera un informe en el idioma indicado, en español por defecto, con esta estructura exacta:

```markdown
# Análisis de un único target — [TARGET_ID]

## Estado del análisis
- Snapshot:
- Target:
- Ruta:
- Lectura: COMPLETA | LECTURA_INCOMPLETA | INPUT_AMBIGUOUS
- Archivos: [leídos]/[inventariados]
- Dependencias compartidas seguidas:
- Build/test/simulación/hardware: [estado real]
- Estado global: IMPLEMENTADO | PARCIAL | CONTRADICTORIO | NO VERIFICADO

## Resumen ejecutivo
[Qué hace realmente este target en lenguaje claro.]

## Inventario analizado
[Fichas individuales de todos los archivos del alcance.]

## Configuración y plataforma
[Placa, framework, build, dependencias y comandos declarados.]

## Flujo principal
[Inicialización, loop/main, callbacks, interrupciones, entradas y salidas.]

## Estados, eventos y temporalidad
[FSM, banderas, debounce, timers, delays, reintentos y recuperación.]

## Parámetros encontrados
[Tabla de constantes y valores con procedencia.]

## Hardware y comunicaciones
[Hardware físico y comunicación lógica separados.]

## Problemas, riesgos y contradicciones
[Hallazgos H## con severidad, impacto y evidencia.]

## Tests y verificación
[Qué existe, qué se ejecutó, qué no existe y qué queda pendiente.]

## Patrones potencialmente reutilizables
[Reglas y procedimientos abstraídos.]

## Datos específicos que no deben copiarse
[Valores y supuestos particulares de este target.]

## Próximos pasos
[Acciones ordenadas, sin aplicarlas automáticamente.]

## Matriz de trazabilidad
| ID | Afirmación | Fuente | Estado de evidencia | Estado de ejecución | Destino |
|---|---|---|---|---|---|

## Archivos, dependencias o datos no encontrados
[Lista explícita o `Ninguno`.]
```

## Criterios de calidad antes de entregar

No cierres el informe hasta confirmar:

- solo se analizó el `TARGET_ID` solicitado;
- los demás targets están excluidos y no mezclados;
- todos los archivos inventariados tienen ficha o motivo de exclusión;
- se siguieron las dependencias compartidas necesarias;
- cada parámetro importante tiene fuente;
- los problemas distinguen hecho, riesgo, contradicción y propuesta;
- secretos y datos sensibles están redactados;
- build/tests/hardware no ejecutados aparecen como pendientes;
- la sección de reutilización no copia valores de producto;
- el informe no modifica el código.

Termina con una de estas frases:

- `Análisis del target completado con lectura completa; verificación de ejecución: [estado real].`
- `Análisis del target incompleto: LECTURA_INCOMPLETA; faltan [archivos/chunks/dependencias].`
- `Análisis detenido: INPUT_AMBIGUOUS; se requiere seleccionar un único target.`
