---
name: audit-hardware-docs
description: Audita notas de hardware y diagramas draw.io contra la lectura completa del código y su configuración.
---

# Auditar documentación de hardware contra el código

## Objetivo

Comprueba si `notas.md` y `conexiones.drawio.svg` siguen representando el target real después de cambios en código, pines, placa, módulos o configuración. Este prompt es de auditoría: no debe corregir silenciosamente el firmware ni declarar que un documento es correcto solo porque existe.

## Entradas

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: target exacto que se audita.
- `NOTES_PATH`: archivo de notas del target.
- `SVG_PATH`: diagrama draw.io del target.
- `BASELINE_DOCS`: documentación previa opcional.

Si los paths no se proporcionan, localiza candidatos, pero detente si hay varios targets incompatibles. No compares un emisor con un receptor ni V3 con V4 como si fueran el mismo montaje.

## Lectura obligatoria

1. Inventaría el repositorio y lee completamente los archivos de código, headers, `platformio.ini` o equivalente, bibliotecas locales, configuración compartida y documentos relacionados.
2. Sigue `#include`, imports, `build_flags`, `lib_extra_dirs`, `library.json` y símbolos compartidos.
3. Lee completamente `NOTES_PATH` y `SVG_PATH`.
4. Para el SVG, comprueba tanto la representación visible como el XML draw.io embebido en `content`.
5. Compara identidad y versión: `TARGET_ID`, ruta, entorno PlatformIO, placa, framework, versión declarada por el código/protocolo y commit. Si no coinciden, no lo ocultes dentro de un PASS.
6. No leas ni imprimas secretos; solo registra el nombre de la variable redactada.

## Matriz de auditoría

Construye una matriz con al menos estas columnas:

```text
ID | afirmación/documento | fuente del código | notas | SVG | estado | severidad | acción
```

Audita como mínimo:

- completitud de lectura: no emitir PASS si hay archivos relevantes no leídos;
- identidad del target: ruta, `TARGET_ID`, entorno de compilación, placa, framework, versión y commit;
- todos los pines usados por `pinMode`, lecturas, escrituras, interrupciones y buses;
- alias de placa frente a GPIO;
- modo del pin y nivel activo;
- componentes y modelos;
- conexiones físicas, alimentación, GND y señales;
- voltajes y advertencias eléctricas;
- debounce, timers, calibración e inicialización que afecten al hardware;
- separación entre red lógica y cableado físico;
- diferencias entre código, notas y diagrama;
- secretos ausentes o expuestos;
- existencia y validez del XML draw.io.

## Estados

Usa estos estados, sin confundirlos:

- `LECTURA_INCOMPLETA`: falta código, configuración, dependencia o chunk necesario; no se puede concluir la auditoría.
- `IDENTIDAD_INCONSISTENTE`: target, entorno, placa, versión o commit no corresponden.
- `COINCIDE`: el documento está respaldado por la fuente correspondiente.
- `OMITIDO`: el código usa algo que no aparece en la documentación.
- `EXTRA`: el documento afirma algo sin fuente suficiente.
- `CONTRADICTORIO`: código y documentación discrepan.
- `NO_DETERMINABLE`: falta información para decidir.
- `FORMATO_INVALIDO`: el SVG no contiene un modelo draw.io editable válido.
- `SECRETO_EXPUESTO`: se detectó un valor sensible que debe eliminarse.

Severidades:

- `CRÍTICA`: puede producir conexión incorrecta, daño eléctrico, target equivocado o documentación engañosa.
- `ALTA`: omite o contradice un pin, componente, modo, nivel o función importante.
- `MEDIA`: dato incompleto, procedencia débil o diferencia operativa.
- `BAJA`: mejora de claridad o trazabilidad sin riesgo funcional inmediato.

## Salida obligatoria

Genera un informe con:

```markdown
# Auditoría de hardware — [TARGET_ID]

- Código/configuración analizados: [commit o versión]
- Notas auditadas: [ruta]
- SVG auditado: [ruta]
- Estado global: PASS | PASS_CON_ADVERTENCIAS | FAIL

## Resumen

[Hallazgos críticos y conteo por estado/severidad.]

## Matriz de cobertura

| ID | Afirmación | Fuente de código | Notas | SVG | Estado | Severidad | Acción |
|---|---|---|---|---|---|---|---|

## Problemas críticos y altos

[Uno por uno, con evidencia y corrección propuesta.]

## Pendientes de confirmación física

[Datasheet, medición, inspección o prueba de hardware necesaria.]

## Validación del SVG

- XML exterior bien formado: PASS/FAIL/PENDIENTE
- `content` con `<mxfile>` y `<diagram>`: PASS/FAIL/PENDIENTE
- `mxGraphModel` interno parseado: PASS/FAIL/PENDIENTE
- celdas/geometrías editables presentes: PASS/FAIL/PENDIENTE
- apertura visual en diagrams.net: PASS/FAIL/PENDIENTE
- Pines dibujados respaldados: PASS/FAIL/PENDIENTE
- Target/entorno/placa correctos: PASS/FAIL/PENDIENTE

## Decisión

[Se puede aceptar, debe regenerarse, o requiere confirmación del usuario.]
```

No escribas `PASS` si no se leyó el código completo, si la identidad del target no coincide o si no se pudo inspeccionar el XML embebido. No arregles automáticamente una contradicción: registra el archivo, la evidencia y la decisión que debe tomarse.
