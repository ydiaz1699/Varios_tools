# Propósito de `codigo_tools`

## Objetivo principal

`codigo_tools` existe para:

> **Analizar proyectos y documentos de `_drafts`, leer su código y documentación completa, y recrear sus comportamientos documentales como artefactos genéricos reutilizables.**

Esos artefactos pueden ser:

- prompts parametrizables;
- templates con placeholders;
- herramientas de análisis y generación;
- referencias de procedimiento;
- schemas y validadores cuando sean necesarios.

Estos artefactos deben poder aplicarse posteriormente a otros proyectos sin depender de los nombres, firmware, hardware o valores concretos de los proyectos de procedencia.

La pregunta central para cada archivo es:

> **¿Qué herramienta, prompt o artefacto reutilizable se puede recrear a partir de este material?**

No es:

> ¿Cómo adapto este código a `wifi_PIR`?

## Fuentes de procedencia

Los proyectos de `_drafts` se conservan como fuentes de procedencia y casos de estudio. No son destinos de integración. En particular, `wifi_PIR` no es el destino de este proceso: no se debe comparar ni adaptar automáticamente el material hacia `wifi_PIR`.

```text
_drafts/reloj NPT/
_drafts/sensor pir/
_drafts/cierre sentralizado esp32/
```

El snapshot de referencia principal de la tanda analizada es:

```text
1ef29a9ee22af797fb1e4e94c6fccbd0ba50901d
```

Las fuentes deben permanecer intactas. No se deben borrar, sobrescribir ni modificar archivos de `_drafts` durante el análisis o la extracción.

## Fuera de alcance

No copiar a `codigo_tools`:

- firmware de producto;
- lógica funcional específica;
- pines o wiring concretos;
- protocolos configurados para un producto concreto;
- secretos, credenciales, SSID, tokens o claves;
- nombres de dispositivos, direcciones, UUIDs o valores particulares;
- fichas de hardware sin procedencia y validación suficientes.

`wifi_PIR` no es el destino de integración de este proceso. Puede aparecer como contexto histórico, pero no debe usarse como objetivo automático de comparación ni de adaptación.

## Material documental que se debe extraer

Priorizar comportamientos documentales como:

- prompts que leen el código completo;
- inventarios de archivos y dependencias;
- análisis de responsabilidades y flujos;
- generación de `docs/notas.md`;
- generación de `docs/conexiones.drawio.svg`;
- generación de `README.md`;
- generación de mapas de repositorio;
- generación de archivos `.ai/`;
- auditorías contra el código actual;
- reglas para no inventar hardware o comportamiento;
- formatos de procedencia y estados de evidencia;
- pasos de validación;
- condiciones para generar, omitir o marcar un artefacto como pendiente.

## Cuatro contratos documentales extraídos de `wifi_PIR/docs`

La prueba sobre los cuatro documentos confirmó que no forman un único prompt, sino cuatro artefactos con responsabilidades diferentes:

- `ARCHITECTURE.md` → `prompts/generar-arquitectura-verificable.md`: mapa de componentes, dependencias, flujos, contratos, variantes e invariantes con estados de evidencia.
- `CHANGELOG.md` → `prompts/generar-changelog-evidencial.md`: historial cronológico basado en cambios trazables, impacto, compatibilidad y validación.
- `PLAN_EJECUCION_FUTURA.md` → `prompts/generar-plan-ejecucion-canonico.md`: continuidad segura desde una línea base, con fases, gates, rollback, trazabilidad y checklist.
- `ROADMAP.md` → `prompts/generar-roadmap-tecnico.md`: backlog priorizado derivado de gaps, riesgos, dependencias, escenarios negativos y aceptación.

La abstracción reusable está en el procedimiento y el contrato, no en el contenido de `wifi_PIR`. Los nombres de dispositivos, protocolos, pines, hosts, topics, comandos, versiones y snippets quedan fuera o se convierten en placeholders. Las contradicciones entre documentación y código se conservan como evidencia y no se resuelven inventando una versión correcta.

## Qué significa recrear

Recrear no significa copiar literalmente un documento o prompt específico. Significa abstraer su comportamiento:

```text
prompt específico del proyecto
        ↓
prompt genérico parametrizable

script o procedimiento manual específico
        ↓
herramienta reusable

estructura documental concreta
        ↓
template con placeholders

regla basada en una placa o producto concreto
        ↓
regla abstracta con evidencia y condiciones
```

Ejemplos:

```text
reloj NPT/.ai/SOFTWARE.md
        ↓
template genérico de documentación de build

sensor pir/docs/conexiones.drawio.svg
        ↓
prompt para generar diagramas físicos desde wiring validado

cierre centralizado esp32/.ai/PROJECT_CONTEXT.md
        ↓
template genérico de contexto de proyecto

prompt que lee todos los archivos
        ↓
herramienta o prompt de análisis completo parametrizable
```

## Flujo obligatorio

1. Leer los proyectos y documentos fuente de `_drafts`.
2. Identificar prompts, templates, scripts y procedimientos documentales.
3. Leer cada archivo relevante completo y seguir sus referencias.
4. Extraer el contrato del comportamiento:
   - entradas;
   - lectura requerida;
   - procesamiento;
   - salidas;
   - reglas;
   - validaciones;
   - errores;
   - condiciones de generación u omisión.
5. Comparar contra los artefactos actuales de `codigo_tools`.
6. Clasificar cada aporte como:
   - `NUEVO`;
   - `MEJORA`;
   - `DUPLICADO`;
   - `VARIANTE`;
   - `CONTRADICTORIO`;
   - `FUERA_DE_ALCANCE`.
7. Recrear el prompt, template o herramienta genérica, sustituyendo valores de producto por placeholders.
8. Probarlo con un fixture o proyecto de ejemplo sin modificar la fuente.
9. Registrar procedencia exacta, transformación, riesgos y estado de verificación.
10. Publicar únicamente los artefactos genéricos aprobados.

## Flujo específico para recrear un artefacto sin prompt fuente

Cuando existe un documento de referencia —por ejemplo `ROADMAP.md`— pero no existe un prompt que explique cómo se generó, el documento se usa como evidencia de un comportamiento que debe reconstruirse, no como plantilla para copiar literalmente.

```text
PROJECT_ROOT + artefacto documental
        ↓
recreator_spec.py prepare (metadata, hashes, estados; sin cuerpos)
        ↓
prompt de recreación + lectura completa del LLM
        ↓
recreator-spec.json + recreator-prompt.md + review.md
        ↓
validate-spec + revisión semántica
        ↓
aprobación explícita y publicación
```

La preparación determinista debe ejecutarse con una salida externa al proyecto fuente:

```bash
python3 codigo_tools/tools/recreator_spec.py prepare /ruta/proyecto \\
  --artifact ROADMAP.md \\
  --output-dir /ruta/reportes/recreator-roadmap \\
  --target-id proyecto-roadmap \\
  --snapshot COMMIT_O_TAG
python3 codigo_tools/tools/recreator_spec.py validate-spec \\
  /ruta/reportes/recreator-roadmap/recreator-spec.json
```

Si hay un prompt equivalente, se proporciona con `--prompt` y se compara con el documento generado. Si no lo hay, el LLM infiere el contrato contrastando el artefacto completo con código, configuración, scripts y documentación relacionada. Debe parametrizar nombres, rutas, targets, comandos y valores; registrar la trazabilidad; conservar contradicciones; tratar `ROADMAP.md` como planificación/historia; y omitir o marcar como pendiente lo que no esté respaldado.

`recreator_spec.py` no realiza la inferencia semántica ni modifica la fuente: inventaría archivos, calcula hashes, registra headings y referencias, detecta nombres de campos sensibles sin emitir sus valores, prepara un brief y valida la especificación resultante. Los archivos no leídos completamente quedan en `LECTURA_INCOMPLETA`. Las salidas requieren revisión humana y mantienen `promotion_allowed: false`.

## Separación de fases

```text
fuente en _drafts
        ↓
lectura y análisis completo
        ↓
matriz de trazabilidad
        ↓
revisión semántica
        ↓
recreación genérica
        ↓
validación con fixture/proyecto de ejemplo
        ↓
aprobación y publicación
```

El análisis no modifica la fuente. La recreación no debe copiar firmware. La similitud heurística no equivale a aprobación.

## Destino de los artefactos

```text
codigo_tools/
├── prompts/       # instrucciones genéricas parametrizables
├── templates/     # esqueletos con placeholders
├── references/    # contratos, reglas y procedimientos
└── tools/         # herramientas deterministas de análisis/validación
```

La arquitectura de catálogo y contexto es soporte para este propósito, no el objetivo principal. Solo debe ampliarse cuando exista comportamiento documental reutilizable identificado en `_drafts`.
