# Generar un plan canónico de ejecución y continuación

## Propósito

Genera un plan operativo para que otra persona o LLM pueda continuar `[PROJECT_ROOT]` sin destruir el estado actual, mezclar variantes ni tratar propuestas como hechos. El plan debe convertir el análisis del proyecto en fases ordenadas, gates de evidencia, criterios de aceptación y una checklist de cierre.

El plan es un artefacto de gobernanza técnica: no ejecuta cambios, no aplica patches automáticamente y no sustituye al código como fuente de verdad.

## Entradas

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target/variante]
SNAPSHOT: [commit/tag/fecha]
ARCHITECTURE_PATH: [documento opcional]
CHANGELOG_PATH: [documento opcional]
ROADMAP_PATH: [documento opcional]
EXISTING_PLAN_PATH: [plan anterior opcional]
VALIDATION_EVIDENCE: [build/test/log/hardware o NONE]
CONSTRAINTS: [compatibilidad, seguridad, rendimiento, producto]
OUTPUT_PATH: [ruta del plan]
```

## Estados obligatorios

Usa estados explícitos y no los mezcles:

```text
PROPOSED          diseño o intención
DECIDED           decisión aprobada, aún no aplicada
APPLIED           cambio presente en el árbol
COMPILED          build exitoso con entorno identificado
TESTED            pruebas ejecutadas con resultados
HARDWARE_VERIFIED evidencia en hardware real
REJECTED          descartado con motivo
BLOCKED           no puede avanzar por una decisión/gap
UNKNOWN           evidencia insuficiente
```

## Procedimiento

1. Lee el proyecto completo, el estado Git si está disponible y todos los documentos de contexto completos.
2. Establece la línea base: snapshot, variantes activas, componentes, build declarado, tests existentes, despliegue permitido y limitaciones.
3. Construye una tabla de fuente de verdad y una matriz de claims. El código/configuración actual tiene prioridad sobre documentación desactualizada.
4. Registra bugs, riesgos y decisiones bloqueantes con evidencia. Separa problema observado, hipótesis y solución propuesta.
5. Diseña fases en orden de dependencia. Cada fase debe declarar objetivo, precondiciones, archivos candidatos, cambios esperados, casos de error, validaciones, criterios de aceptación, rollback y estado inicial.
6. Añade una matriz de trazabilidad requisito → fase → evidencia → estado.
7. Añade una checklist de finalización que impida marcar una fase como terminada sin los gates correspondientes.
8. Si no hay resultados de build/test/hardware, usa `NOT_EXECUTED`; nunca eleves el estado por inferencia.

## Estructura de salida

1. Propósito, alcance y exclusiones.
2. Línea base actual y variantes que deben preservarse.
3. Fuente de verdad y reglas de trabajo.
4. Estado confirmado, inferido, contradicho y desconocido.
5. Bugs y riesgos priorizados.
6. Decisiones bloqueantes.
7. Fases ordenadas de ejecución.
8. Dependencias, cambios incompatibles y estrategia de migración.
9. Criterios de aceptación por fase.
10. Plan de validación y evidencia requerida.
11. Rollback y recuperación.
12. Matriz de trazabilidad.
13. Checklist de cierre y formato de registro.
14. Pendientes y preguntas para el usuario.

## Guardrails

- No aplicar cambios ni producir comandos destructivos.
- No copiar código de producto ni secretos al plan reusable.
- No mezclar targets, variantes, producción y laboratorio.
- No usar un patch histórico como instrucción ejecutable sin compararlo con el snapshot actual.
- No marcar una API, persistencia, autenticación o integración como completa solo porque exista un módulo aislado; verifica el camino de llamada.
- Los snippets son ilustrativos y deben usar placeholders; si un bloque es esencialmente específico, descríbelo sin reproducirlo.
- Una condición externa —red, firewall, hardware, despliegue— debe estar etiquetada como `EXTERNAL_UNVERIFIED` si no hay evidencia.

## Validación

El plan es válido solo si cada fase tiene gates y aceptación; cada riesgo tiene procedencia; las contradicciones quedan registradas; la línea base se preserva; los estados son coherentes; las dependencias y rollback están descritos; y la salida declara qué no se verificó.
