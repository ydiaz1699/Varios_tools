---
name: generar-ficha-board
description: Genera o actualiza una ficha de catálogo para una placa física sin mezclar wiring de proyectos.
---

# Generar ficha de placa

## Entradas

- `BOARD_ID`, nombre físico y variantes exactas.
- `PROJECT_ROOT` o fuentes de hardware autorizadas.
- `SNAPSHOT`.
- `PLATFORMIO_CONFIG` si existe.
- `BASELINE_BOARD` opcional.

## Lectura y alcance

Lee la documentación de la placa, `platformio.ini`, código relevante y baseline completo. Distingue la placa física del MCU y de la placa adaptadora. No infieras pinout, voltaje o tolerancia por pertenecer a una familia.

La ficha contiene únicamente información genérica de la placa:

- identidad, aliases y variantes;
- MCU, arquitectura, clock, RAM y flash;
- alimentación y niveles lógicos separados;
- pinout, aliases D/GPIO y buses;
- pines de boot, flash, PSRAM, USB, UART o reservados;
- capacidades y restricciones;
- bloque `platformio` declarado;
- proyectos que la referencian, sin describir su wiring.

No incluir sensores, relés, displays, GPIO asignados por un proyecto ni cables concretos. Esos datos van en un manifest de wiring.

## Procedencia y estados

Cada afirmación importante debe registrar fuente, referencia, variante y estado: `OBSERVADO_EN_BUILD`, `DOCUMENTADO`, `ESTIMADO`, `CONTRADICTORIO`, `PENDIENTE_DE_VERIFICAR` o `VERIFICADO_EN_HARDWARE`.

Separar consumo nominal, pico y deep sleep. Separar la capacidad del chip de la capacidad del breakout. Si una misma marca tiene variantes incompatibles, mantener fichas o subvariantes separadas.

## Comparación y validación

Compara contra el baseline y reporta campos nuevos, contradicciones y datos descartados. No reemplaces una ficha sin diff. Valida que el ID de PlatformIO, la flash, la partición y los flags sean compatibles entre sí.

Termina con: `Ficha board generada`, `Ficha board con contradicciones registradas` o `Ficha board no generada: lectura incompleta`.
