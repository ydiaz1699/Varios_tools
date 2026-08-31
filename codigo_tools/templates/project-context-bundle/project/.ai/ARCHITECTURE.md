# ARCHITECTURE — [PROJECT_ID]

> Artefacto condicional para límites, flujos, dependencias o FSM que requieran explicación propia.

## Alcance

- Target/snapshot: `[TARGET_ID]` / `[SNAPSHOT]`
- Estado: `[OBSERVADO | PARCIAL | CONTRADICTORIO | PENDIENTE_DE_VERIFICAR]`

## Componentes y límites

| Componente | Responsabilidad | Consume | Produce | Fuente | Estado |
|---|---|---|---|---|---|
| `[COMPONENT]` | `[RESPONSIBILITY]` | `[INPUTS]` | `[OUTPUTS]` | `[PATH:SYMBOL]` | `[estado]` |

## Flujo real

```text
[entrada] → [símbolo/componente] → [estado/transformación] → [salida]
```

## FSM/temporalidad

| Estado | Evento/condición | Transición | Efecto | Timeout/reintento | Evidencia |
|---|---|---|---|---|---|
| `[STATE]` | `[EVENT]` | `[NEXT]` | `[EFFECT]` | `[VALUE_OR_NONE]` | `[PATH:SYMBOL]` |

## Invariantes y contradicciones

- `[INVARIANT]` — fuente: `[PATH]` — estado: `[OBSERVADO | INFERIDO | CONTRADICTORIO]`.
- `[CONTRADICTION]` — código: `[VALUE]`; documentación: `[VALUE]`.

No presentar una arquitectura propuesta como comportamiento implementado.
