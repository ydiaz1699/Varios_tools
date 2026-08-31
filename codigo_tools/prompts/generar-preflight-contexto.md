---
name: generar-preflight-contexto
description: Construye una matriz previa de evidencia para generar contexto de proyecto, bundles .ai, README y referencias sin inventar claims ni copiar secretos.
---

# Generar preflight de contexto

## Objetivo

Analiza un proyecto antes de generar o actualizar documentación de contexto. El resultado es un inventario de claims, fuentes, sensibilidad, destino y condiciones de generación. No escribe archivos del proyecto ni decide automáticamente qué promocionar.

Este prompt abstrae los procedimientos de lectura completa, separación catálogo/shared/proyecto y preflight observados en los drafts de arquitectura y workspace context.

## Entradas

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: target o ensamblaje exacto.
- `SNAPSHOT`: commit, rama, tag o fecha.
- `OUTPUT_PATH`: reporte fuera de la fuente.
- `REQUESTED_ARTIFACTS`: documentos solicitados o candidatos.
- `CATALOG_ROOT`: catálogo opcional de boards/peripherals o recursos equivalentes.
- `SHARED_ROOT`: contexto compartido opcional.

Si no se proporciona uno de estos valores, marcarlo `PENDIENTE_DE_CONFIRMAR`; no inventarlo.

## Reglas no negociables

1. Leer el proyecto completo y cerrar referencias transitivas: imports, includes, build, scripts, dependencias locales, documentación y tests relevantes.
2. Separar por target, versión, entorno y plataforma.
3. Distinguir hechos observados, documentación, inferencias, propuestas, contradicciones y valores no encontrados.
4. No copiar secretos, valores de credenciales, tokens, claves, SSID, certificados, IPs privadas ni datos sensibles. Conservar solo nombre de variable/ruta y usar `[REDACTADO]`.
5. Un GPIO demuestra una asignación lógica, no por sí solo un componente físico, cableado, alimentación o compatibilidad eléctrica.
6. Un archivo histórico no demuestra que una característica esté implementada.
7. No generar ni sobrescribir artefactos. Solo producir el reporte de preflight.
8. Si falta un archivo necesario, detener el claim afectado con `LECTURA_INCOMPLETA`.

## Estados

Usa exactamente estos estados cuando sean aplicables:

- `OBSERVADO_EN_CODIGO`
- `OBSERVADO_EN_BUILD`
- `DOCUMENTADO`
- `INFERIDO`
- `PROPUESTO`
- `CONTRADICTORIO`
- `NO_ENCONTRADO`
- `PENDIENTE_DE_VERIFICAR`
- `PRESENTE_NO_EXHIBIDO`

Añade por separado el estado de ejecución: `NO_EJECUTADO`, `EJECUTADO`, `NO_EXISTE` o `PENDIENTE`.

## Procedimiento

### Fase 1 — Alcance e inventario

Producir:

```text
PROJECT_ROOT:
TARGET_ID:
SNAPSHOT:
Archivos versionados:
Archivos leídos completamente:
Dependencias transitivas seguidas:
Targets excluidos:
Estado de lectura: COMPLETA | LECTURA_INCOMPLETA
```

Clasificar archivos como código, interfaz, build, secreto/plantilla, documentación humana, contexto de agente, tests/CI, catálogo, wiring, asset o generado.

### Fase 2 — Matriz de claims

Para cada dato potencialmente documentable, registrar:

| Campo | Valor redactado | Fuente | Referencia | Estado | Sensibilidad | Destino | Condición |
|---|---|---|---|---|---|---|---|
| propósito | [resumen] | `ruta` | línea/símbolo | estado | pública | PROJECT_CONTEXT | siempre |
| board/target | [valor] | `ruta` | línea/campo | estado | pública | HARDWARE/context | si existe evidencia |
| dependencia | [nombre/versión] | `ruta` | campo | estado | pública | SOFTWARE | si se mantiene |
| secreto | `[REDACTADO]` | `ruta` | nombre variable | PRESENTE_NO_EXHIBIDO | sensible | no copiar valor | siempre |

El campo `Destino` debe ser uno de:

- `.ai/PROJECT_CONTEXT.md`
- `.ai/HARDWARE.md`
- `.ai/SOFTWARE.md`
- `.ai/SKILL.md`
- `.ai/TASKS.md`
- `.ai/DECISIONS.md`
- `.ai/ROADMAP.md`
- `.ai/CHANGELOG.md`
- `.ai/ARCHITECTURE.md`
- `.ai/PROTOCOL.md`
- `.ai/TESTING.md`
- `README.md`
- `repo-map.yml`
- `catalog-gap-report`
- `PENDIENTE`

### Fase 3 — Condiciones del bundle

Determinar por evidencia qué archivos son necesarios, condicionales o innecesarios:

| Artefacto | Condición de generación | Evidencia | Decisión |
|---|---|---|---|
| `PROJECT_CONTEXT.md` | siempre como punto de entrada | [fuente] | required/blocked |
| `HARDWARE.md` | hardware o wiring identificable | [fuente] | conditional |
| `SOFTWARE.md` | build/dependencias/configuración | [fuente] | conditional |
| `SKILL.md` | tarea recurrente accionable | [fuente] | conditional |
| `TASKS.md` | pendientes mantenidos | [fuente] | conditional |
| `DECISIONS.md` | decisiones/ADR | [fuente] | conditional |
| `ROADMAP.md` | backlog futuro | [fuente] | conditional |
| `CHANGELOG.md` | historial mantenido | [fuente] | conditional |
| `ARCHITECTURE.md` | límites/FSM/flujos complejos | [fuente] | conditional |
| `PROTOCOL.md` | contrato de comunicación propio | [fuente] | conditional |
| `TESTING.md` | estrategia o pruebas relevantes | [fuente] | conditional |

No convertir todos los archivos en obligatorios por defecto.

### Fase 4 — Referencias y gaps

Comprobar:

- enlaces relativos desde el archivo que los contiene;
- referencias a catálogo existentes;
- board/peripheral/wiring separados;
- consumidores de archivos legacy;
- duplicación entre README, repo-map y `.ai/`;
- condiciones que no tienen evidencia;
- campos técnicos con valores contradictorios.

Si falta una ficha, producir un `CATALOG_GAP` con aliases, modelo/variante pendiente, campos faltantes, fuente requerida y riesgo. No crear una ficha automáticamente.

### Fase 5 — Decisión

Clasificar cada candidato como:

- `INTEGRAR`: el contrato es reusable y la evidencia es suficiente.
- `VARIANTE`: reusable solo para una plataforma o formato declarado.
- `PENDIENTE`: falta validación, decisión o contrato.
- `RECHAZAR`: es específico de producto, inseguro o duplicado.
- `BLOQUEADO`: no se pudo leer o resolver una referencia necesaria.

## Salida obligatoria

Generar un reporte Markdown con:

```markdown
# Preflight de contexto — [TARGET_ID]

## Estado de lectura
## Inventario y dependencias
## Matriz de claims
## Condiciones del bundle
## Referencias y enlaces
## Gaps de catálogo/contexto
## Duplicaciones y legacy
## Contradicciones
## Decisiones de integración
## Artefactos no generados
## Matriz de trazabilidad final
```

## Validación antes de entregar

- Cada claim tiene fuente y referencia o está marcado pendiente.
- Los valores sensibles están redactados.
- Los targets están separados.
- No se confundió documentación con implementación.
- No se generó ningún archivo del proyecto.
- Los comandos/build/tests/hardware no ejecutados están claramente marcados.
- Los gaps de catálogo no se publican como fichas.
