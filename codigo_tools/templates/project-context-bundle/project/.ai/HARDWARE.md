# HARDWARE — [PROJECT_ID]

> Artefacto condicional. Crear solo si el target tiene hardware físico o wiring identificable.

## Alcance y evidencia

- Target: `[TARGET_ID]`
- Snapshot: `[SNAPSHOT]`
- Estado: `[BORRADOR | GENERADO | PENDIENTE_DE_VERIFICAR]`
- Fuente principal: `[CODE_OR_BUILD_PATH]`

Separa lo observado en código/configuración, lo documentado por una fuente externa y lo verificado físicamente. Un GPIO no demuestra por sí solo un componente, cableado, alimentación, nivel lógico o polaridad.

## Board y variantes

| Elemento | Valor | Fuente | Estado |
|---|---|---|---|
| Board/modelo | `[BOARD_OR_PENDING]` | `[PATH:FIELD]` | `[OBSERVADO_EN_BUILD | DOCUMENTADO | PENDIENTE_DE_VERIFICAR]` |
| Variante | `[MODEL_VARIANT_OR_N/A]` | `[PATH]` | `[estado]` |
| Alimentación | `[VALUE_OR_PENDING]` | `[DATASHEET_OR_MEASUREMENT]` | `[estado]` |

## Periféricos y señales

| Instancia | Referencia catálogo | Señal/pin lógico | Modo/nivel | Dirección | Fuente | Estado |
|---|---|---|---|---|---|---|
| `[INSTANCE]` | `[peripherals/ID.json | PENDIENTE]` | `[PIN_OR_SIGNAL]` | `[MODE/ACTIVE_LEVEL]` | `[IN/OUT/BIDIR]` | `[PATH:SYMBOL]` | `[estado]` |

## Wiring del proyecto

Describe únicamente conexiones respaldadas por el código, configuración, esquema autorizado o medición. Mantén el wiring concreto separado de las fichas reutilizables de board/peripheral.

```text
[fuente] → [señal/pin] → [destino]
```

## Riesgos y gaps

- `[RISK_OR_UNKNOWN]` — fuente: `[PATH]` — estado: `PENDIENTE_DE_VERIFICAR`.
- Si falta una ficha de catálogo, crear un reporte de gap; no publicar una ficha automáticamente.

## Verificación física

| Comprobación | Procedimiento | Estado | Resultado |
|---|---|---|---|
| Alimentación/niveles | `[PROCEDURE]` | `[NO_EJECUTADO | VERIFICADO_EN_HARDWARE]` | `[RESULT]` |
| Wiring | `[PROCEDURE]` | `[NO_EJECUTADO | VERIFICADO_EN_HARDWARE]` | `[RESULT]` |
