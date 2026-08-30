---
name: gen-conexiones-svg
description: Genera un diagrama de conexiones físicas en SVG editable por draw.io a partir del inventario completo y trazable de un target.
---

# Generar `conexiones.drawio.svg` desde el código completo

## Objetivo

Genera un diagrama **draw.io SVG editable** para un target concreto del proyecto. El diagrama debe representar únicamente conexiones físicas suficientemente respaldadas por el código y la documentación técnica disponible. No debe inventar cables, tensiones, módulos ni correspondencias de GPIO.

Este prompt no modifica firmware ni configuración. Solo genera o propone el SVG indicado por el usuario.

## Variables que debes identificar

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: ensamblaje exacto que se dibujará.
- `PLATFORM_ENV`: entorno de compilación que confirma la placa de ese target.
- `OUTPUT_PATH`: por defecto `docs/hardware/<TARGET_ID>/conexiones.drawio.svg`.
- `NOTES_PATH`: notas de hardware del mismo target, usadas como referencia secundaria y no como prueba suficiente.
- `BASELINE_DIAGRAM`: diagrama anterior, si existe, para comparar y no reintroducir errores.

Si existen varios targets, placas o versiones, no generes un diagrama combinado sin autorización. Por ejemplo, cada uno de `emisor_pir`, `receptor_bocina`, `emisor_pir_v4` y `receptor_central_v4` requiere un alcance separado.

## Reglas no negociables

1. Lee completamente el target y sus dependencias antes de dibujar: fuentes, headers, configuración de build, bibliotecas locales y documentación baseline.
2. Sigue `#include`, imports, `build_flags`, `lib_extra_dirs`, `library.json` y constantes compartidas. No deduzcas el hardware desde un único `main.cpp`.
3. Construye primero un inventario textual de placa, componentes, pines, modos, niveles activos y evidencia. El SVG debe ser una representación de ese inventario, no una interpretación independiente.
4. Antes de dibujar, demuestra que el inventario de archivos relevantes está completo. Si un archivo, dependencia o chunk no se pudo leer, detente y entrega `LECTURA_INCOMPLETA`; no dibujes un diagrama que pueda parecer completo.
5. Distingue **conexión física** de **comunicación lógica**. WiFi, UDP, MQTT, OTA, topics y direcciones IP no se dibujan como cables eléctricos. Si se necesita, colócalos en una página o sección lógica separada y rotulada.
6. Solo dibuja una línea física cuando exista evidencia suficiente: conexión explícita entre pin del componente y pin de la placa en una fuente, o conexión documentada por una fuente técnica identificada sin contradicción. No dibujes conexiones `INFERIDO` o `PENDIENTE_DE_CONFIRMAR`.
7. Las conexiones `OBSERVADO_EN_CODIGO` o confirmadas físicamente se dibujan con línea sólida. Las conexiones solo `DOCUMENTADO` se dibujan, como máximo, con línea discontinua gris y etiqueta `DOCUMENTADO—CONFIRMAR`; si no hay evidencia suficiente, quedan fuera del SVG y aparecen en las notas.
8. No inventes voltajes. Si el voltaje está documentado pero no confirmado por el código, etiqueta la conexión como `DOCUMENTADO` o `PENDIENTE_DE_CONFIRMAR`, no como hecho observado.
9. Conserva los nombres de placa (`D2`, `D3`, `D5`, etc.) y añade el GPIO equivalente solo si está respaldado por la plataforma o una fuente verificable.
10. No leas ni incluyas secretos. Redacta cualquier credencial o clave.
11. Debe existir un XML draw.io válido embebido en el atributo `content` del elemento `<svg>`. No entregues un SVG plano que solo parezca un diagrama.
12. No uses un límite artificial de componentes o líneas; prioriza claridad y cobertura.

## Procedimiento obligatorio

### Fase 1 — Inventario previo

Antes del SVG, produce una tabla o bloque con:

```text
Target:
Entorno de compilación exacto:
Versión/identidad declarada por código o build:
Placa principal:
Componentes:
Pines usados:
Conexiones físicas demostradas:
Conexiones documentadas pero no confirmadas:
Conexiones desconocidas no dibujadas:
Comunicaciones lógicas separadas:
Fuentes y líneas/símbolos:
Conflictos con notas o diagramas anteriores:
Archivos no leídos o inaccesibles:

Si `Archivos no leídos o inaccesibles` no está vacío, detente y entrega solo este inventario con `LECTURA_INCOMPLETA`; no generes el SVG.
```

Para cada conexión conserva internamente:

```text
ID | componente/pin | placa/pin | tipo | evidencia | fuente | estado | dibujar sí/no
```

### Fase 2 — Diseño

Usa un layout legible y estable:

- placa principal a la derecha;
- periféricos a la izquierda;
- alimentación en rojo (`#ff0000`) solo si está respaldada;
- GND en negro (`#000000`);
- señal digital en verde (`#00aa00`);
- buses en azul (`#0000ff`);
- línea sólida para `OBSERVADO_EN_CODIGO` o conexión confirmada;
- línea discontinua gris únicamente para `DOCUMENTADO—CONFIRMAR`;
- conexiones no verificadas no se dibujan como si fueran reales;
- nombre del componente en negrita y pines usados visibles;
- leyenda con colores y estado de evidencia;
- etiqueta de señal en cada conexión;
- nombres de archivos y target fuera del área de cables o en una leyenda.

Si un componente solo aparece como abstracción de software y no se conoce su conexión física, no lo dibujes como periférico. Si una conexión lógica es útil, usa una segunda página claramente llamada `Lógica de comunicaciones`, nunca la mezcles silenciosamente con el cableado.

### Fase 3 — Generación

Genera `OUTPUT_PATH` como SVG con estas propiedades:

- raíz `<svg xmlns="http://www.w3.org/2000/svg" ...>`;
- atributo `content` con el XML de `<mxfile>` y `<diagram>` correctamente escapado;
- modelo `mxGraphModel` válido;
- elementos y estilos editables por diagrams.net;
- texto visible de placa, componentes, pines y señales;
- dimensiones que permitan leer etiquetas sin superposición.

El archivo debe poder abrirse en diagrams.net mediante importar/abrir. No reemplaces el XML draw.io por una imagen rasterizada ni por un SVG sin modelo editable.

### Fase 4 — Validación del SVG

Antes de entregar:

1. Comprueba que el archivo es XML bien formado.
2. Comprueba que existe el elemento `<svg>` y que `content` no está vacío.
3. Extrae y desescapa el atributo `content` con un parser XML; confirma que el documento interno tiene raíz `<mxfile>`, al menos un `<diagram>` y un `mxGraphModel` válido.
4. Comprueba que el XML interno no contiene solo una imagen o texto decorativo: debe tener `mxCell`/geometrías editables para los componentes y conexiones.
5. Si está disponible `python3`, ejecuta una validación equivalente a:

```bash
python3 - <<'PY'
import html
import xml.etree.ElementTree as ET
from pathlib import Path

path = Path("OUTPUT_PATH")
outer = ET.parse(path).getroot()
content = outer.attrib.get("content", "")
assert content, "content vacío"
inner = ET.fromstring(html.unescape(content))
assert inner.tag == "mxfile", inner.tag
assert inner.find("diagram") is not None, "falta diagram"
models = inner.findall(".//mxGraphModel")
assert models, "falta mxGraphModel"
assert inner.findall(".//mxCell"), "no hay celdas editables"
print("drawio XML válido")
PY
```

6. Comprueba que cada pin dibujado existe en el inventario del código o en una fuente técnica marcada.
7. Comprueba que cada línea física tiene una fila en la matriz de conexiones y conserva su estado de evidencia.
8. Comprueba que no aparecen cables de WiFi, UDP o MQTT como conexiones físicas.
9. Comprueba que el target, el entorno de compilación y la placa del diagrama coinciden con el inventario.
10. Compara contra `NOTES_PATH` y enumera cualquier diferencia.
11. La validación XML no sustituye abrir el archivo en diagrams.net; si no se realizó esa prueba visual, declara `PENDIENTE_DE_VERIFICACIÓN`.

Entrega junto con el SVG un resumen de validación. Si la herramienta no puede demostrar que el XML es editable, marca `⚠️ PENDIENTE DE VERIFICACIÓN` en lugar de declarar éxito.
