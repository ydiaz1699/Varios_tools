---
name: gen-notas-hw
description: Genera notas de hardware trazables a partir de la lectura completa de un target de código, su configuración de build y sus dependencias.
---

# Generar `notas.md` desde el código completo

## Objetivo

Genera documentación de hardware para un **target concreto** del proyecto actual. La documentación debe ayudar a entender cómo el código usa la placa y sus periféricos, sin inventar conexiones físicas, voltajes ni componentes.

Este prompt no modifica firmware, headers, configuración ni bibliotecas. Solo genera o propone el archivo de documentación indicado por el usuario.

## Variables que debes identificar antes de empezar

- `PROJECT_ROOT`: raíz del proyecto que se está analizando.
- `TARGET_ID`: target concreto; por ejemplo `emisor_pir`, `receptor_bocina`, `emisor_pir_v4` o `receptor_central_v4` si esos nombres existen realmente.
- `PLATFORM_ENV`: entorno de compilación exacto dentro de `platformio.ini`; no lo deduzcas solo del nombre de la carpeta.
- `OUTPUT_PATH`: ruta solicitada para el documento; si no se indica, proponer `docs/hardware/<TARGET_ID>/notas.md`.
- `BASELINE_DOCS`: documentación existente que se comparará, sin asumir que es correcta.

Si el usuario no define `TARGET_ID` y hay varias placas, entornos o firmwares, **no mezcles todo en una sola tabla**. Primero muestra los targets detectados y solicita uno, o genera un documento separado por target solo si el usuario lo autoriza.

## Reglas no negociables

1. **Lee el proyecto completo antes de redactar.** No te limites al primer `main.cpp`, al README ni a los fragmentos visibles.
2. Inventaría primero todos los archivos del target: `platformio.ini`, `CMakeLists.txt` u otra configuración de build, `src`, `include`, `lib`, bibliotecas locales, headers compartidos y archivos de configuración relacionados.
3. Sigue recursivamente `#include`, imports, `lib_extra_dirs`, `build_flags`, `library.json` y referencias a símbolos del target. Lee el contenido completo de cada archivo relevante.
4. Si un archivo es grande, divídelo en chunks con IDs estables (`F01-C01`, `F01-C02`) y conserva un índice de todo lo leído. Un resumen no sustituye el contenido fuente durante la comprobación final.
5. Antes de redactar, demuestra que el inventario de archivos relevantes está completo. Si no puedes leer un archivo, una dependencia o un chunk, **detente y marca `LECTURA_INCOMPLETA`**; no generes una documentación que pueda parecer completa.
6. Busca usos reales de hardware en `pinMode`, `digitalRead`, `digitalWrite`, `analogRead`, `analogWrite`, interrupciones, buses, constructores de módulos y constantes de configuración. No busques únicamente `#define`.
7. Distingue conexiones físicas de comunicaciones lógicas. WiFi, UDP, MQTT, OTA y topics no son cables del pinout.
8. Separa los estados de evidencia: `OBSERVADO_EN_CODIGO`, `OBSERVADO_EN_BUILD`, `DOCUMENTADO`, `INFERIDO`, `PENDIENTE_DE_CONFIRMAR` y `CONTRADICTORIO`.
9. No inventes modelos, voltajes, GPIO equivalentes, cables, polaridades ni corrientes. Si solo aparece `D2`, registra `D2`; añade el GPIO equivalente únicamente si la plataforma o una fuente verificable lo establece.
10. No leas ni imprimas valores secretos. Redacta credenciales, claves, tokens y contraseñas como `[REDACTADO]`; conserva solo el nombre de la variable y su función.
11. La documentación no puede ocultar conflictos entre código, configuración, notas anteriores y diagramas.
12. No uses un límite artificial de líneas. Prioriza completitud y legibilidad.

## Procedimiento obligatorio

### Fase 1 — Inventario

Entrega primero un bloque de análisis con:

```text
Target seleccionado:
Entorno de compilación exacto:
Versión/identidad declarada por código o build:
Placa/MCU detectado:
Framework y entorno de build:
Archivos leídos completamente:
Archivos no leídos o inaccesibles:
Dependencias locales seguidas:
Documentos baseline comparados:
Otros targets excluidos y motivo:

Si `Archivos no leídos o inaccesibles` no está vacío, detente y entrega solo el inventario y `LECTURA_INCOMPLETA`; no redactes `notas.md`.
```

### Fase 2 — Extracción

Construye una matriz interna con una fila por afirmación relevante:

```text
ID | afirmación | archivo | línea/símbolo | evidencia | estado | conflicto | destino
```

Extrae como mínimo:

- identidad del target: carpeta, `TARGET_ID`, entorno PlatformIO, placa, versión declarada y commit si existe; si no coinciden, registra la contradicción;
- módulos y componentes mencionados por código o documentación;
- todos los pines usados y su alias de placa/GPIO cuando esté demostrado;
- modo de pin y nivel activo;
- dirección de señal y comportamiento relevante;
- interrupciones, debounce, timers, calibración y estados que afecten al hardware;
- buses y periféricos (`I2C`, `SPI`, `UART`, etc.) si aparecen;
- alimentación y voltajes solo cuando tengan una fuente explícita;
- conexiones lógicas en una sección separada;
- contradicciones y datos que necesitan confirmación física.

### Fase 3 — Redacción

Genera `OUTPUT_PATH` con esta estructura:

```markdown
# Hardware — [TARGET_ID]

> Estado: BORRADOR | GENERADO | AUDITADO
> Código/configuración analizados: [commit o versión si está disponible]
> Fecha de generación: [fecha]
> Alcance: [target exacto]

## 1. Placa y entorno

| Elemento | Valor | Evidencia | Estado |
|---|---|---|---|

## 2. Componentes

| Componente | Modelo/nombre conocido | Función | Fuente | Estado |
|---|---|---|---|---|

## 3. Pinout observado

| Placa | GPIO/canal | Función | Modo | Nivel activo | Dirección | Fuente | Estado |
|---|---|---|---|---|---|---|---|

## 4. Conexiones físicas

| Componente/pin | Placa/pin | Señal | Voltaje | Fuente | Estado |
|---|---|---|---|---|---|

## 5. Comportamiento que afecta al hardware

[Debounce, interrupciones, timers, inicialización, calibración, estados y advertencias extraídos del código.]

## 6. Comunicaciones lógicas

[WiFi, UDP, MQTT, OTA, UART u otros; no presentarlas como cables físicos.]

## 7. Datos no demostrados y decisiones pendientes

- [PENDIENTE_DE_CONFIRMAR]

## 8. Comparación con documentación existente

[Qué coincide, qué está desactualizado y qué contradice al código.]

## 9. Procedencia y cobertura

| ID | Fuente | Destino en este documento | Cobertura | Estado |
|---|---|---|---|---|
```

Si el código no demuestra una conexión física, usa `NO DETERMINADO` o `PENDIENTE_DE_CONFIRMAR`; no rellenes la tabla con una conexión típica del componente.

## Fase 4 — Verificación antes de entregar

Vuelve a comparar el documento contra **todos los archivos fuente leídos**, no solo contra el resumen:

- el inventario de archivos está completo; si no, el resultado es `LECTURA_INCOMPLETA` y no documentación final;
- `TARGET_ID`, entorno de compilación, placa y versión pertenecen al mismo ensamblaje;
- cada placa/target tiene su propia sección o documento;
- no se mezclan V3 y V4 ni emisor y receptor;
- no aparecen pines o componentes sin procedencia;
- los modos y niveles activos coinciden con el código;
- las afirmaciones eléctricas están separadas por estado de evidencia;
- los secretos no aparecen;
- las contradicciones están explícitas;
- la matriz de procedencia tiene destino para cada afirmación relevante.

Si no puedes comprobar un punto, escribe `⚠️ PENDIENTE DE VERIFICACIÓN` y explica qué falta. No afirmes que la documentación está completa solo porque el archivo fue generado.
