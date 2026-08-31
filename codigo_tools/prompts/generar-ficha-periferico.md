---
name: generar-ficha-periferico
description: Genera o actualiza una ficha de catálogo para un módulo/periférico separando VCC, lógica, protocolo y variante.
---

# Generar ficha de periférico

## Entradas

- `PERIPHERAL_ID`, nombre, modelo y variante exactos.
- `SOURCES`: datasheet, documentación del breakout, librería y código.
- `SNAPSHOT`.
- `BASELINE_PERIPHERAL` opcional.

## Lectura y alcance

Lee todas las fuentes y distingue chip, breakout y módulo comercial. La ficha contiene:

- categoría, aliases y variantes;
- VCC, corriente y fuente de alimentación;
- nivel lógico de señales y nivel activo;
- protocolos e interfaces;
- pines de cada interfaz;
- dirección, timing, pull-ups y calibración cuando aplique;
- librería y versión declarada;
- requisitos de level shifting, desacoplo y seguridad;
- limitaciones por variante.

No incluir la placa concreta ni declarar que el módulo está conectado a un proyecto. Eso va en `project-wiring.json`.

## Reglas técnicas

No mezcles VCC con lógica en una sola columna. No copies rangos, alcances, precisión, consumo, aislamiento o tolerancia de otro modelo. Si el breakout cambia el regulador o level shifting, documenta la variante explícita. Los valores sin fuente son `PENDIENTE_DE_VERIFICAR`.

## Salida

Genera la ficha, matriz de procedencia y comparación contra baseline. Reporta contradicciones y datos que requieren modelo/datasheet/hardware. No afirmes compatibilidad con una placa sin analizar ambos lados.

Termina con: `Ficha peripheral generada`, `Ficha peripheral con contradicciones registradas` o `Ficha peripheral no generada: faltan fuentes`.
