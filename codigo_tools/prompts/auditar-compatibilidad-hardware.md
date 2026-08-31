---
name: auditar-compatibilidad-hardware
description: Audita la compatibilidad entre una placa, periféricos y wiring de proyecto sin sustituir datasheet ni prueba física.
---

# Auditar compatibilidad de hardware

## Entradas

- Catálogo de boards y peripherals.
- `project-wiring.json`.
- Código/configuración del target.
- Datasheets o evidencia física disponibles.

## Comprobaciones

1. Referencias y variantes existen.
2. Board ID, plataforma, framework y configuración coinciden con el proyecto.
3. Cada señal tiene pin de origen y destino válidos.
4. No hay pines duplicados salvo buses compartidos declarados.
5. No se usan pines boot, flash, PSRAM, USB o UART sin decisión explícita.
6. VCC, lógica y dirección de señal son compatibles o tienen level shifter documentado.
7. Direcciones I2C no colisionan sin mux/configuración.
8. Protocolo, librería y timing están declarados.
9. El presupuesto de corriente está documentado o queda pendiente.
10. Se separan cables físicos de comunicaciones lógicas.
11. Código, wiring y catálogo no se contradicen.

## Estados

- `PASS`: estructura y evidencia suficientes para las comprobaciones aplicables.
- `PASS_CON_ADVERTENCIAS`: no hay bloqueo, pero faltan mediciones o datos de variante.
- `FAIL`: conflicto eléctrico, de pin, variante o evidencia crítica.
- `LECTURA_INCOMPLETA`: falta una fuente necesaria.

## Salida

Produce matriz:

```text
ID | elemento | board/peripheral/wiring | evidencia | estado | severidad | acción
```

No marques `PASS` si hay una contradicción de flash, nivel lógico, pin reservado, variante o wiring no respaldado. No inventes una conexión ni una especificación para completar la tabla.
