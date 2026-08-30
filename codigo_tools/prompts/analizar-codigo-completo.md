---
name: analizar-codigo-completo
description: Genera un informe trazable para comprender un proyecto completo, archivo por archivo, flujo por flujo y problema por problema.
---

# Analizar código completo y generar informe de comprensión

## Objetivo

Analiza un proyecto completo y genera un informe técnico que permita a otra persona o LLM comprender qué hace realmente el código sin tener que abrir cada archivo. El informe debe ser más que un resumen de arquitectura: debe explicar el inventario individual, las responsabilidades de cada archivo, el flujo de ejecución, las máquinas de estado, las dependencias, la configuración, los errores, las limitaciones y las contradicciones entre código y documentación.

Este prompt no modifica el código ni corrige automáticamente los problemas. Solo analiza, clasifica y propone acciones basadas en evidencia.

## Entradas obligatorias

Identifica antes de comenzar:

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: target o ensamblaje que se analizará.
- `SNAPSHOT`: commit, rama, tag o fecha del código observado.
- `OUTPUT_PATH`: ruta del informe; si no se indica, proponer `docs/analysis/<TARGET_ID>-analysis.md`.
- `BASELINE_DOCS`: README, repo-map, changelog, prompts, planos o documentación existente que debe compararse, no obedecerse ciegamente.

Si el repositorio contiene varios targets, placas, entornos, servicios o versiones, no los mezcles. Primero enuméralos y separa el análisis por `TARGET_ID` y entorno de build. Si el usuario solicita una vista conjunta, conserva subsecciones independientes y una comparación final.

## Reglas no negociables

1. **Leer todo antes de concluir.** Inventaría y lee todos los archivos versionados del target: código, headers, configuración, documentación, prompts, tests, assets, manifiestos y archivos generados relevantes.
2. Sigue dependencias y referencias: `#include`, imports, `lib_extra_dirs`, `library.json`, `platformio.ini`, `CMakeLists.txt`, `package.json`, Makefiles, flags, variables compartidas y rutas de configuración.
3. Lee ambos lados de una interfaz: un `.h` no demuestra el comportamiento de su `.cpp`, y un README no demuestra que una característica exista.
4. Si un archivo o chunk no se puede leer, detente antes del informe final y entrega `LECTURA_INCOMPLETA` con la lista exacta de faltantes.
5. Conserva un inventario con IDs estables (`F01`, `F02`; para archivos grandes `F01-C01`, `F01-C02`). Toda afirmación importante debe poder apuntar a ruta y línea, símbolo o chunk.
6. No inventes comportamiento, hardware, métricas, versiones, protocolos, comandos, problemas ni soluciones. Marca lo no demostrable como `PENDIENTE_DE_CONFIRMAR`.
7. No presentes un comentario, README, changelog, prompt o repo-map como implementación. Distingue siempre `OBSERVADO_EN_CODIGO`, `OBSERVADO_EN_BUILD`, `DOCUMENTADO`, `INFERIDO`, `ESTIMADO`, `PROPUESTO` y `CONTRADICTORIO`.
8. No imprimas secretos. Sustituye contraseñas, tokens, claves, SSID reales, URLs privadas y valores sensibles por `[REDACTADO]`; conserva el nombre de la variable y la ruta.
9. Cuando el código y la documentación difieran, describe primero el comportamiento ejecutable observado y luego la divergencia documental.
10. No declares que el proyecto compila, funciona o fue probado si no se ejecutó la evidencia correspondiente. Usa `⚠️ PENDIENTE DE VERIFICACIÓN`.
11. Las ausencias son información válida: tests inexistentes, watchdog no configurado, timeout declarado pero no usado, dependencia ausente o archivo esperado que no existe deben registrarse como `NO ENCONTRADO`.
12. No reduzcas el informe para cumplir un límite de líneas. Prioriza trazabilidad y detalle sobre brevedad.

## Estados de evidencia

Usa estos estados sin mezclarlos:

- `OBSERVADO_EN_CODIGO`: aparece en instrucciones, símbolos, constantes o flujo ejecutable leído.
- `OBSERVADO_EN_BUILD`: aparece en configuración de compilación o despliegue.
- `DOCUMENTADO`: aparece en README, notas, changelog, prompt o mapa, pero no está confirmado por el código.
- `INFERIDO`: conclusión razonable cuya evidencia indirecta debe explicarse.
- `ESTIMADO`: valor aproximado sin medición reproducible.
- `PROPUESTO`: mejora futura, workaround o diseño sugerido.
- `CONTRADICTORIO`: fuentes actuales no coinciden.
- `NO ENCONTRADO`: se buscó y no existe en el snapshot.
- `PENDIENTE_DE_VERIFICACIÓN`: requiere build, test, simulación o hardware real.

## Procedimiento obligatorio

### Fase 1 — Inventario y alcance

Antes de redactar, muestra:

```text
Target:
Snapshot/commit/rama:
Entorno(s) de build:
Placa/OS/runtime:
Cantidad de archivos versionados analizados:
Archivos leídos completamente:
Archivos/chunks no leídos:
Dependencias locales seguidas:
Baseline/documentos comparados:
Targets excluidos y motivo:
Estado de lectura: COMPLETA | LECTURA_INCOMPLETA
```

Clasifica cada archivo, como mínimo, en:

- punto de entrada;
- implementación;
- header/interfaz;
- configuración/build;
- secretos/plantilla;
- documentación humana;
- contexto para agentes/prompts;
- tests/CI;
- assets/datos;
- archivo genérico generado por la herramienta.

### Fase 2 — Ficha de cada archivo

Para cada archivo relevante, genera una ficha individual. No agrupes archivos distintos si eso oculta responsabilidades o contradicciones:

```markdown
### F## — `ruta/archivo`

- Tipo:
- Estado de lectura:
- Responsabilidad real:
- Símbolos públicos o puntos de integración:
- Dependencias/imports/includes:
- Constantes, pines, tiempos, estados o formatos definidos:
- Efectos secundarios:
- Archivos que lo consumen:
- Evidencia:
- Observaciones, ausencias o contradicciones:
```

Los README estándar de PlatformIO pueden marcarse como `GENÉRICO_SIN_LÓGICA`; no los confundas con documentación específica del proyecto.

### Fase 3 — Reconstrucción del sistema

Después de las fichas, explica:

1. Objetivo real inferido del código.
2. Componentes y límites entre módulos.
3. Punto de entrada y orden exacto de `setup`, inicialización, callbacks, eventos y `loop`/main.
4. Flujo de datos: entradas, transformaciones, salidas y efectos persistentes.
5. Dependencias runtime frente a dependencias de desarrollo.
6. Hardware, pines, buses, niveles activos y protocolos si aplica.
7. Configuración, secretos, archivos generados y comandos reales de build/upload/ejecución/test.

Incluye un diagrama textual basado en llamadas observadas, no en la arquitectura que el README afirma:

```text
entrada → función/símbolo → estado/transformación → salida/efecto
```

### Fase 4 — Máquinas de estado y temporalidad

Para cada FSM explícita o implícita, documenta:

```markdown
### FSM: [nombre]

- Estado inicial:
- Estados observados:
- Evento/condición:
- Transición real:
- Acción/efecto:
- Timeout/intervalo:
- Contador/reintentos:
- Estado terminal o recuperación:
- Evidencia:
```

Comprueba específicamente:

- constantes declaradas pero no usadas;
- estados declarados pero inalcanzables;
- transiciones descritas en documentación pero ausentes en código;
- `delay()` y llamadas potencialmente bloqueantes;
- temporizadores basados en `millis()` y su overflow;
- orden de llamadas que produzca estados obsoletos o efectos antes de validar;
- reintentos, backoff, timeouts y condiciones de recuperación;
- valores iniciales que puedan perder el primer evento.

### Fase 5 — Problemas y contradicciones

No conviertas toda diferencia en bug. Clasifica cada hallazgo:

- `BUG_DEMOSTRABLE`: el flujo o una condición del código evidencia el fallo.
- `RIESGO_TÉCNICO`: puede fallar según plataforma, librería, hardware o carga; requiere confirmación.
- `DIVERGENCIA_DOCUMENTAL`: README/mapa/prompt afirma algo distinto al código.
- `CONFIGURACIÓN_INCOMPLETA`: falta un archivo, variable, dependencia o paso de setup.
- `AUSENCIA_RELEVANTE`: no existe una capacidad esperable y su ausencia afecta el objetivo.
- `PROPUESTA_NO_IMPLEMENTADA`: está descrita como futura, pero no existe en el código.

Para cada hallazgo:

```markdown
### H## — [título]

- Clasificación:
- Severidad: CRÍTICA | ALTA | MEDIA | BAJA
- Comportamiento observado:
- Evidencia de código:
- Fuente documental relacionada:
- Impacto:
- ¿Está probado?: SÍ | NO | PENDIENTE
- Acción sugerida:
```

La acción sugerida debe ser proporcional. Si no hay suficiente evidencia para elegir una solución, presenta opciones y deja la decisión pendiente.

### Fase 6 — Comparación contra baseline

Si existe README, `archivo-mapa.yml`, changelog, prompt o documentación previa, añade una tabla:

```markdown
| Tema | Código observado | Baseline/documentación | Estado | Impacto | Acción |
|---|---|---|---|---|---|
```

El código actual describe el comportamiento ejecutable; la documentación puede describir intención, histórico o propuesta. No borres la divergencia ni elijas silenciosamente una versión.

## Formato de salida obligatorio

Genera un informe Markdown con esta estructura:

```markdown
# Análisis completo — [TARGET_ID]

## Estado del análisis
- Snapshot:
- Lectura: COMPLETA | LECTURA_INCOMPLETA
- Evidencia ejecutada: build/test/simulador/hardware/ninguna
- Estado global: IMPLEMENTADO | PARCIAL | PROPUESTO | CONTRADICTORIO | NO VERIFICADO

## Resumen ejecutivo
[Qué hace realmente y cuáles son los riesgos principales.]

## Inventario analizado
[Fichas individuales de todos los archivos relevantes.]

## Arquitectura y límites
[Componentes, responsabilidades, dependencias y diagrama de llamadas.]

## Flujo de ejecución real
[Setup, loop, callbacks, entradas, salidas y efectos.]

## Máquinas de estado y temporización
[Tablas/FSM con valores reales y transiciones observadas.]

## Hardware y comunicaciones
[Placa, pines, periféricos, alimentación solo si está respaldada, protocolos y formatos.]

## Configuración, build y operación
[platformio.ini/package/build, secretos, comandos y archivos ausentes.]

## Problemas, riesgos y contradicciones
[Hallazgos clasificados con evidencia y severidad.]

## Comparación con baseline
[Documentación contra código actual.]

## Tests y verificación
[Tests existentes, ausentes y evidencia realmente ejecutada.]

## Qué es reutilizable
[Procedimientos, módulos, patrones o prompts reutilizables; separar código específico de proyecto y propuestas.]

## Qué no debe reutilizarse sin adaptación
[Incompatibilidades de placa, plataforma, versiones, rutas, protocolos o supuestos.]

## Próximos pasos
[Acciones ordenadas y criterios de aceptación; no ejecutar cambios automáticamente.]

## Matriz de trazabilidad
| ID | Afirmación | Fuente | Estado de evidencia | Destino |
|---|---|---|---|---|

## Archivos y datos no encontrados
[Todo lo buscado que no existe o no se pudo verificar.]
```

## Validación antes de entregar

No entregues el informe final hasta comprobar:

- todos los archivos del inventario tienen ficha o están marcados fuera de alcance;
- cada flujo importante apunta a funciones, símbolos y archivos;
- cada FSM tiene estados y transiciones observados, no solo declarados;
- las constantes no usadas aparecen en contradicciones o ausencias;
- documentación y código se compararon explícitamente;
- secretos están redactados;
- no se afirmó compilación/test/hardware sin evidencia;
- las propuestas futuras no se presentan como implementadas;
- la matriz de trazabilidad tiene destino para las afirmaciones importantes;
- si falta algún archivo, el estado global es `LECTURA_INCOMPLETA`.

Termina con una frase clara: `Análisis completado con lectura completa y sin verificación de ejecución`, o `Análisis incompleto: faltan [archivos/chunks]`.
