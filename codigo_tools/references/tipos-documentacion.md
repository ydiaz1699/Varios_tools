# Tipos de documentación generada por `codigo_tools`

`codigo_tools` mantiene capas complementarias. Cada artefacto tiene un lector y un propósito distinto; no deben duplicar contenido sin necesidad.

| Artefacto | Lector principal | Propósito | Fuente de verdad |
|---|---|---|---|
| `analizar-codigo-completo.md` (salida Markdown) | desarrollador/LLM | Comprensión profunda archivo por archivo, flujo, FSM, riesgos y reutilización | código y configuración actuales |
| `repo-map.yml` / `archivo-mapa.yml` | LLM/agente | Contexto estructurado y compacto del proyecto | código/config actuales, con procedencia |
| `README.md` | usuario/desarrollador | Instalar, configurar, ejecutar y diagnosticar | comandos y comportamiento comprobados |
| `docs/notas.md` | persona que monta hardware | Pinout, componentes, estados de señales y advertencias físicas | código + documentación técnica confirmada |
| `docs/conexiones.drawio.svg` | persona que cablea | Diagrama visual de conexiones físicas | inventario de hardware validado |
| `audit-*` (salida Markdown) | mantenedor | Detectar documentación desactualizada, omitida o contradictoria | comparación código-documentación |
| `SKILL.md`/prompts | agente/LLM | Reglas y procedimientos para trabajar | decisión de proceso, no comportamiento del producto |

## Diferencias que deben conservarse

- El análisis completo puede ser extenso y narrativo; el repo-map debe ser compacto y estructurado.
- El README explica cómo usar el proyecto; no debe reemplazar el mapa interno ni la matriz de análisis.
- Las notas y el SVG representan hardware físico. WiFi, UDP, MQTT, NTP, OTA, topics y direcciones IP pertenecen a comunicaciones lógicas y no deben dibujarse como cables.
- Un prompt es una instrucción reutilizable; su resultado es un artefacto derivado y no una prueba de que el proyecto implementa una feature.
- Un baseline histórico puede conservar intención o decisiones antiguas, pero el código actual tiene precedencia al describir el comportamiento ejecutable.

## Regla de procedencia

Cada salida debe registrar, cuando sea posible:

```text
snapshot/commit | target | archivo fuente | línea/símbolo/chunk | estado de evidencia
```

Si una salida se genera para varios targets, cada afirmación debe indicar a cuál pertenece. No mezclar V3/V4, emisor/receptor o placas diferentes en una tabla única sin separarlos explícitamente.

## Estados recomendados

- `IMPLEMENTADO`: existe en código; no implica que esté probado.
- `DOCUMENTADO`: aparece en documentación, pero no fue confirmado en código.
- `ESTIMADO`: valor aproximado sin medición reproducible.
- `PROPUESTO`: futura mejora o workaround.
- `PENDIENTE_DE_VERIFICAR`: requiere build, prueba, datasheet o hardware.
- `CONTRADICTORIO`: fuentes actuales no coinciden.
- `NO_ENCONTRADO`: se buscó y no existe en el snapshot.
