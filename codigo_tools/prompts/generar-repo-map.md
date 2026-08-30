---
name: generar-repo-map
description: Genera un repo-map YAML compacto y trazable a partir de la lectura completa de un repositorio.
---

# Generar `repo-map.yml` desde el repositorio completo

## Objetivo

Genera un mapa estructurado del proyecto para que otra LLM pueda entender su arquitectura, flujo, configuración, dependencias, restricciones y estado sin explorar inicialmente todos los archivos. El mapa es un índice derivado del código; no sustituye el análisis detallado ni convierte la documentación histórica en fuente de comportamiento.

Este prompt no modifica código ni corrige problemas. Solo genera el YAML y reporta contradicciones o datos no verificables.

## Entradas obligatorias

Identifica antes de generar:

- `PROJECT_ROOT`: raíz del repositorio.
- `TARGET_ID`: target, servicio, firmware o ensamblaje. Si hay varios, separar mapas o secciones por target.
- `SNAPSHOT`: commit, rama, tag o fecha observada.
- `OUTPUT_PATH`: por defecto `repo-map.yml` o `archivo-mapa.yml`, según la convención del proyecto.
- `BASELINE_MAP`: mapa previo, README, roadmap, changelog y otros documentos a contrastar.

## Reglas no negociables

1. Inventaría y lee todos los archivos relevantes antes de generar: código, headers, configuración, documentación, tests, prompts, assets, manifiestos y archivos generados que afecten al comportamiento.
2. Sigue `#include`, imports, `platformio.ini`, `CMakeLists.txt`, `package.json`, `library.json`, `lib_extra_dirs`, build flags, variables compartidas y rutas de configuración.
3. Si falta un archivo, dependencia o chunk necesario, detente y devuelve `LECTURA_INCOMPLETA`; no generes un mapa aparentemente completo.
4. Lee el mapa anterior y la documentación solo como baseline. El comportamiento ejecutable se extrae del código y la configuración actual.
5. No inventes versión, licencia, métricas, consumo, rendimiento, comandos, hardware, endpoints ni problemas. Usa `NO ENCONTRADO`, `PENDIENTE_DE_CONFIRMAR` o `ESTIMADO` cuando corresponda.
6. No presentes una propuesta, comentario, README o changelog como una función implementada.
7. Redacta secretos, tokens, contraseñas, claves, SSID reales y URLs privadas como `[REDACTADO]`.
8. Cada afirmación importante debe tener `fuente`, `línea/símbolo` o `chunk` y `estado_evidencia`.
9. Separa implementación actual, documentación, estimaciones y propuestas futuras.
10. Genera YAML válido: no uses tabs, escapa comillas, conserva listas como listas y valida el resultado con un parser YAML si está disponible.

## Estados de evidencia

Usa solo estos valores:

- `OBSERVADO_EN_CODIGO`
- `OBSERVADO_EN_BUILD`
- `DOCUMENTADO`
- `INFERIDO`
- `ESTIMADO`
- `PROPUESTO`
- `CONTRADICTORIO`
- `NO_ENCONTRADO`
- `PENDIENTE_DE_VERIFICACION`

## Procedimiento

### 1. Inventario

Antes del YAML, informa:

```text
Target:
Snapshot:
Archivos versionados/relevantes:
Archivos leídos:
Archivos/chunks faltantes:
Entornos de build:
Dependencias seguidas:
Baseline comparado:
Estado: COMPLETA | LECTURA_INCOMPLETA
```

### 2. Extracción

Construye una matriz interna:

```text
ID | afirmación | fuente | línea/símbolo | estado_evidencia | sección YAML
```

Extrae como mínimo:

- identidad, objetivo real y punto de entrada;
- targets y entornos de build;
- hardware, pines, periféricos y comunicaciones si aplica;
- componentes y responsabilidades;
- flujo de inicialización y loop/eventos;
- FSM, estados, transiciones, timers, reintentos y fallbacks;
- dependencias runtime y desarrollo con versión declarada;
- configuración, secretos y archivos que deben crearse;
- comandos reales de build, upload, ejecución, monitor y tests;
- tests existentes y ausencias relevantes;
- limitaciones, riesgos y contradicciones con el baseline.

### 3. Generación

Usa `templates/repo-map.yml` como estructura inicial, pero no copies valores del ejemplo. Sustituye cada placeholder por datos observados o por un estado explícito de ausencia/pendiente.

## Reglas del YAML

- `estado_analisis` debe ser `COMPLETO`, `LECTURA_INCOMPLETA` o `COMPLETO_CON_CONTRADICCIONES`.
- Las métricas no medidas deben tener `estado_evidencia: ESTIMADO`.
- Las features futuras deben estar bajo `propuestas_no_implementadas`, nunca bajo `features_implementadas`.
- Cada problema debe incluir evidencia, impacto, severidad y acción; si la solución no está demostrada, marcarla como propuesta.
- Cada target debe mantener su placa, entorno, versión y archivos separados.
- Las conexiones de red lógicas no deben confundirse con conexiones eléctricas.

## Validación antes de entregar

1. Parsear el YAML y comprobar que es válido.
2. Confirmar que todos los archivos del inventario tienen destino o están marcados fuera de alcance.
3. Confirmar que cada FSM y flujo apunta a fuentes.
4. Confirmar que no hay secretos ni valores privados.
5. Comparar con `BASELINE_MAP` y registrar divergencias.
6. Confirmar que las propuestas no aparecen como implementación.
7. Si no se pudo leer todo, no entregar `repo-map.yml`; entregar el inventario con `LECTURA_INCOMPLETA`.

Termina con: `Repo-map generado con lectura completa`, `Repo-map generado con contradicciones registradas`, o `Repo-map no generado: lectura incompleta`.
