---
name: generar-project-wiring
description: Genera un manifest de wiring de un proyecto referenciando fichas de board y peripherals sin duplicar sus especificaciones.
---

# Generar wiring por proyecto

## Entradas

- `PROJECT_ROOT`, `TARGET_ID` y `SNAPSHOT`.
- Ficha de board seleccionada.
- Fichas exactas de peripherals y variantes.
- Código, configuración, esquemas y mediciones disponibles.

## Lectura obligatoria

Lee código, headers, build, documentación y fichas referenciadas. Separa:

- GPIO/pines que el código configura;
- periféricos que la documentación o hardware identifica;
- conexiones eléctricas confirmadas;
- comunicaciones lógicas que no deben dibujarse como cables;
- supuestos y datos pendientes.

## Salida

Genera `project-wiring.json` con:

- project/target/snapshot;
- `board_ref`;
- instancias de peripherals y variantes;
- conexiones `from`, `to`, señal, protocolo y level shifter;
- alimentación y presupuesto de corriente si está documentado;
- procedencia por conexión y estado de evidencia;
- conflictos, pines reservados y preguntas pendientes.

No copies las tablas genéricas de la board ni del peripheral. Una asignación lógica de GPIO no prueba por sí sola el componente físico ni su alimentación.

## Validación

Comprueba referencias, pines duplicados, pines boot/reservados, niveles lógicos, direcciones de bus, adaptadores y discrepancias entre código y documentación. Si falta evidencia, conserva la conexión como `PENDIENTE_DE_VERIFICAR` y no la conviertas en diagrama físico confirmado.

Termina con: `Wiring generado con lectura completa`, `Wiring generado con pendientes` o `Wiring no generado: lectura incompleta`.
