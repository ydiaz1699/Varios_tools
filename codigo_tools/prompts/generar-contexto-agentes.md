---
name: generar-contexto-agentes
description: Genera y mantiene copilot-instructions.md y SKILL.md a partir del código, la configuración y el propósito confirmado de un proyecto.
---

# Generar contexto de agentes desde el proyecto actual

## Objetivo

Genera dos artefactos complementarios para que un agente de IA trabaje con un repositorio sin tener que redescubrir su contexto en cada sesión:

- `copilot-instructions.md`: reglas generales del repositorio, restricciones, estilo y datos técnicos que deben mantenerse.
- `SKILL.md`: procedimiento accionable para la tarea recurrente principal del proyecto.

Estos archivos describen cómo debe trabajar el agente; no sustituyen al código, al README, al `repo-map.yml` ni a las pruebas. No conviertas una propuesta documental en una feature implementada.

## Entradas obligatorias

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: target, firmware, servicio, placa o ensamblaje exacto.
- `SNAPSHOT`: commit, rama, tag o fecha observada.
- `PROJECT_PURPOSE`: propósito confirmado por el usuario o `PENDIENTE_DE_CONFIRMAR`.
- `BASELINE_PATHS`: versiones previas de `copilot-instructions.md`, `SKILL.md`, README, mapas y documentación relacionada.
- `OUTPUT_PATHS`: rutas donde deben escribirse los dos archivos.

Si hay varios targets o tareas recurrentes, sepáralos. No generes un archivo ambiguo que mezcle placas, versiones, emisores/receptores o servicios incompatibles.

## Lectura obligatoria

1. Inventaría y lee completamente el target: código, headers, configuración de build, dependencias, scripts, tests, plantillas de secretos y documentación relacionada.
2. Sigue `#include`, imports, `platformio.ini`, `CMakeLists.txt`, `package.json`, `library.json`, variables compartidas y rutas de configuración.
3. Compara cada baseline con el estado actual. Registra contradicciones antes de reemplazar cualquier archivo.
4. Si falta un archivo, dependencia o chunk necesario, detente con `LECTURA_INCOMPLETA`; no generes contexto aparentemente completo.
5. No ejecutes cambios sobre el firmware o servicio mientras generas estos documentos.

Antes de redactar, produce este inventario:

```text
Target:
Snapshot:
Propósito confirmado:
Archivos relevantes:
Archivos leídos:
Archivos/chunks faltantes:
Builds y dependencias seguidos:
Baselines comparados:
Estado: COMPLETA | LECTURA_INCOMPLETA
```

## Matriz de extracción

Construye una matriz antes de redactar:

```text
ID | afirmación | fuente | línea/símbolo | artefacto destino | estado | baseline | decisión
```

Extrae como mínimo:

- objetivo y alcance real;
- target, plataforma, framework, board/runtime y comandos de build;
- constantes, pines, puertos, endpoints, topics, identificadores y umbrales;
- librerías y dependencias con versiones declaradas;
- flujo de inicialización, ciclo principal, callbacks, eventos y FSM;
- entradas, salidas, estados, errores, timeouts, reintentos y fallbacks;
- convenciones observadas de nombres, idioma, formato y organización;
- restricciones que futuras modificaciones no deben romper;
- tests, builds, simulaciones y pruebas de hardware realmente ejecutados;
- decisiones documentadas, propuestas y pendientes.

## Reglas de evidencia y seguridad

- La fuente de comportamiento es el código y la configuración actuales. El baseline solo se conserva como referencia y para detectar divergencias.
- Cada afirmación importante debe indicar archivo y línea/símbolo cuando sea posible.
- Usa estados separados: `OBSERVADO_EN_CODIGO`, `OBSERVADO_EN_BUILD`, `DOCUMENTADO`, `INFERIDO`, `PROPUESTO`, `PENDIENTE_DE_VERIFICACION` y `CONTRADICTORIO`.
- No afirmes que compila, funciona o fue probado si no se ejecutó esa verificación.
- No inventes versiones, pines, voltajes, tiempos, métricas, comandos ni problemas.
- Redacta contraseñas, tokens, claves, SSID, certificados y secretos como `[REDACTADO]`. No copies secretos reales a los artefactos.
- Los identificadores técnicos solo deben incluirse si son necesarios para operar el target y están autorizados por el material de entrada; si pueden ser sensibles, usa `[REDACTADO]` y conserva el nombre de la variable.
- Separa claramente `IMPLEMENTADO`, `PROPUESTO`, `PENDIENTE_DE_VERIFICAR` y `RECHAZADO`.

## Salida 1: `copilot-instructions.md`

Genera instrucciones generales y relativamente estables con estas secciones:

1. **Objetivo y alcance** — propósito real, target y snapshot.
2. **Plataforma y herramientas** — lenguaje, framework, board/runtime, dependencias y comandos de build declarados.
3. **Datos técnicos actuales** — tabla de nombre, valor documentable, fuente y estado. Redacta secretos.
4. **Reglas de implementación** — patrones observados que deben preservarse, no preferencias inventadas.
5. **Convenciones de estilo** — idioma, nombres, formato y nivel de detalle observados.
6. **Verificación obligatoria** — qué build/tests/hardware deben ejecutarse y qué no está confirmado.
7. **Límites y pendientes** — contradicciones, riesgos y propuestas sin presentar soluciones no implementadas como hechos.
8. **Mantenimiento** — cuándo actualizar este archivo y cómo compararlo contra el código.

Cada regla no trivial debe incluir procedencia. Si el código no demuestra un dato, escribir `PENDIENTE_DE_VERIFICAR`.

## Salida 2: `SKILL.md`

Genera un procedimiento específico para la tarea recurrente principal del target:

1. **Propósito y activación** — cuándo usar la skill y cuándo no.
2. **Entradas requeridas** — datos que el usuario debe proporcionar y valores que se extraen del proyecto.
3. **Flujo de trabajo** — pasos concretos en orden, desde la lectura/validación hasta la implementación o diagnóstico.
4. **Decisiones clave** — decisiones observadas en código, con su evidencia y alternativas pendientes.
5. **Entradas, salidas y estados** — comportamiento real, errores, timeouts, reintentos y fallbacks.
6. **Criterios de salida** — archivos completos, explicación, diff, comandos ejecutados y estado de verificación.
7. **Ejemplos de solicitudes** — dos o tres ejemplos adaptados al tipo de tarea, sin secretos reales.
8. **Limitaciones y mantenimiento** — indicar que es específica del target y debe sincronizarse con `copilot-instructions.md`.

La skill debe ser accionable, pero no debe ordenar comportamientos que el código no implementa sin marcarlos como `PROPUESTO`.

## Consistencia entre ambos archivos

Antes de entregar, compara los valores compartidos en una matriz:

```text
Dato | copilot-instructions.md | SKILL.md | código/configuración | estado | acción
```

Comprueba como mínimo target, board/runtime, librerías, pines, identificadores, umbrales, timeouts, comandos y nombres de archivos. Si hay una contradicción, no elijas silenciosamente: registra la diferencia y marca el dato como `CONTRADICTORIO` o `PENDIENTE_DE_VERIFICAR`.

## Comparación con baseline

Incluye una sección breve en la respuesta, no necesariamente dentro de ambos artefactos:

```text
Baseline:
Cambios detectados:
Valores desactualizados:
Contenido conservado:
Contenido rechazado y motivo:
Pendientes:
```

No sobrescribas silenciosamente un `SKILL.md` o `copilot-instructions.md` existente.

## Verificación antes de entregar

- [ ] Lectura completa o `LECTURA_INCOMPLETA` explícita.
- [ ] Target y snapshot identificados.
- [ ] Propósito confirmado o marcado pendiente.
- [ ] Cada valor técnico tiene procedencia.
- [ ] No hay secretos expuestos.
- [ ] Las propuestas no aparecen como implementación.
- [ ] Los comandos de build/test están marcados como declarados o ejecutados.
- [ ] La matriz de consistencia no tiene contradicciones ocultas.
- [ ] Los dos archivos se pueden entender sin consultar los drafts originales.
- [ ] El diff contra el baseline fue revisado.

Termina con uno de estos estados:

- `Contexto generado con lectura completa; build y pruebas: [estado real].`
- `Contexto generado con contradicciones registradas; pendientes: [lista].`
- `Contexto no generado: LECTURA_INCOMPLETA; faltan [archivos/chunks].`
