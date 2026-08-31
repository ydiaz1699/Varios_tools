# Contrato del bundle de contexto

## Propósito

El bundle de contexto coordina documentos para agentes y humanos sin convertirlos en una segunda fuente de comportamiento. El código y la configuración actuales siguen siendo la fuente de verdad.

## Capas

```text
shared/       → convenciones y defaults comunes
project/.ai/  → contexto del target/proyecto
catalog/      → fichas reutilizables de boards/peripherals
project-wiring.json → instancia de conexiones del target
```

`PROJECT_CONTEXT.md` es el punto de entrada mínimo. Los demás documentos son condicionales y cada uno debe tener una responsabilidad única.

## Archivos y condiciones

| Archivo | Condición |
|---|---|
| `.ai/PROJECT_CONTEXT.md` | siempre, como entrada mínima |
| `.ai/HARDWARE.md` | hardware físico o wiring identificable |
| `.ai/SOFTWARE.md` | build, runtime, dependencias o configuración mantenida |
| `.ai/SKILL.md` | tarea recurrente accionable |
| `.ai/TASKS.md` | backlog o pendientes mantenidos |
| `.ai/DECISIONS.md` | decisiones técnicas/ADR |
| `.ai/ROADMAP.md` | planificación futura activa |
| `.ai/CHANGELOG.md` | historial de cambios mantenido |
| `.ai/ARCHITECTURE.md` | límites, flujos o FSM complejos |
| `.ai/PROTOCOL.md` | contrato de comunicación que requiere mantenimiento |
| `.ai/TESTING.md` | estrategia o evidencia de pruebas |

No crear todos los archivos automáticamente. El preflight debe justificar cada uno.

## Reglas de evidencia

Cada afirmación importante debe registrar:

```text
snapshot | target | archivo | línea/símbolo/chunk | estado de evidencia
```

Los estados de evidencia no se mezclan con los estados de ejecución. `APLICADO`, `COMPILADO`, `TESTEADO`, `VERIFICADO` y `VERIFICADO_EN_HARDWARE` requieren evidencia separada.

## Reglas de seguridad

- Redactar valores de secretos; conservar como máximo el nombre de variable y la ruta.
- No publicar automáticamente fichas de catálogo faltantes.
- Mantener board, peripheral y wiring separados.
- No afirmar que una recomendación de extensión está instalada sin comprobarlo.
- No promover ni sobrescribir fuentes automáticamente.
- Validar enlaces desde el archivo que los contiene.

## Pipeline

```text
scan → preflight → revisión semántica → scaffold en output separado
     → validate_context_bundle → revisión humana → promoción manual
```

El validador determinista solo reporta errores y gaps. No corrige, no instala, no ejecuta builds y no publica artefactos.
