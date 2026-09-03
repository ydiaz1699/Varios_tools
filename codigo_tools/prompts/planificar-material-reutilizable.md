---
name: planificar-material-reutilizable
description: Revisa el scan determinista de un proyecto y convierte sus candidatos heurísticos en un plan trazable para mejorar o crear artefactos de codigo_tools.
---

# Planificar material reutilizable desde un scan

## Propósito

Este prompt se ejecuta después de `tools/reusable_material_extractor.py`. El scan lee el proyecto, registra todos los archivos y propone patrones, pero sus decisiones son heurísticas. Este prompt realiza la revisión semántica necesaria antes de crear o mejorar cualquier artefacto en `codigo_tools`.

No copia firmware, lógica de producto, wiring concreto, secretos ni valores específicos como reglas globales.

## Entradas

- `SCAN_JSON`: salida `scan.json` del extractor.
- `PLAN_MD`: salida `plan.md` para revisión humana.
- `PROJECT_ROOT`: fuente exacta analizada.
- `SNAPSHOT`, `TARGET_ID` y propósito confirmado.
- `CODE_TOOLS_ROOT`: versión canónica actual de `codigo_tools`.
- Baselines o artefactos canónicos relacionados.

## Procedimiento obligatorio

1. Verifica que `source.root`, `target_id`, `snapshot` y propósito estén identificados.
2. Revisa `coverage.read_status`, archivos con errores, binarios y directorios excluidos.
3. Si falta un archivo o chunk necesario, marca `LECTURA_INCOMPLETA` y no promuevas el candidato.
4. Lee individualmente cada fuente de los candidatos `REUSABLE` y `PARAMETRIZABLE`.
5. Lee completo el canónico indicado por `canonical_path` antes de decidir `MEJORA`, `DUPLICADO` o `CONTRADICTORIO`.
6. Compara propósito, entradas, salidas, capacidades, claims, compatibilidad, evidencia y validación; no compares solo nombres.
7. Separa cada contenido en:
   - `REUSABLE`: regla, estructura o procedimiento general.
   - `PARAMETRIZABLE`: target, placa, periférico, ruta, dependencia o formato que debe ser placeholder.
   - `PRODUCT_SPECIFIC`: firmware, lógica, GPIO, wiring, valores y decisiones de un proyecto.
   - `SENSITIVE`: secretos o identificadores que no se copian.
8. Conserva una referencia a archivo y línea, heading, símbolo o chunk para cada afirmación.
9. Corrige las decisiones heurísticas cuando la lectura completa aporte evidencia distinta.
10. Clasifica cada fila como `NUEVO`, `MEJORA`, `DUPLICADO`, `CONTRADICTORIO`, `VARIANTE`, `NO_DECIDIBLE` o `FUERA_DE_ALCANCE`.
11. Para hardware, conserva la arquitectura híbrida: `board`, `peripheral` y `project-wiring` son espacios separados.
12. Redacta una propuesta completa; no sobrescribas canónicos ni generes un PR automáticamente.

## Matriz final requerida

```text
ID | fuente | patrón extraído | estado de evidencia | alcance | canónico | decisión | destino | transformación | riesgo | procedencia
```

Cada fila debe responder:

- ¿Qué patrón se extrae?
- ¿Por qué es reutilizable?
- ¿Qué parte se parametriza?
- ¿Qué parte queda únicamente en la fuente?
- ¿Qué artefacto actual mejora o por qué es realmente nuevo?
- ¿Qué evidencia respalda la decisión?
- ¿Qué validación falta?

## Reglas anti-desviación

- `source_code`, configuración de build y wiring concreto son evidencia del producto; no se copian como herramientas.
- Una ficha concreta de Arduino, ESP8266, RF, sensor o periférico no se convierte en regla universal.
- Los pines, rutas, nombres, versiones, topics y valores se convierten en placeholders o se dejan fuera.
- Una decisión automática `NUEVO` o `MEJORA` nunca equivale a aprobación.
- Si dos reglas son incompatibles, conserva ambas fuentes y marca `CONTRADICTORIO`.
- No afirmes build, tests, simulación o hardware si no existe evidencia ejecutada.

## Salida

Entrega:

1. matriz corregida y trazable;
2. lista de artefactos `NUEVO` y `MEJORA` con destino propuesto;
3. candidatos `DUPLICADO`, `CONTRADICTORIO`, `VARIANTE` y `FUERA_DE_ALCANCE` con motivo;
4. preguntas pendientes;
5. propuesta de implementación y validación;
6. confirmación explícita de que las fuentes no fueron modificadas.

Termina con: `Plan de reutilización revisado; ninguna promoción aplicada automáticamente.`
