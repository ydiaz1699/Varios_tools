# Consul CWM15AB - ESP32 Controller

Reemplazo de la placa de control original de la lavadora **Consul CWM15AB** (15kg) por un **ESP32**, manteniendo el panel de botones/LEDs original y replicando la logica de lavado de fabrica.

## Objetivo

- Sustituir la PCB original danada o discontinuada
- Mantener el panel de usuario (botones + LEDs) sin modificaciones
- Replicar exactamente los ciclos de lavado de fabrica
- Opcionalmente agregar conectividad WiFi (IoT/Home Assistant)

## Estructura del Proyecto

```
Consul_CWM15AB/
├── README.md                  # Este archivo
├── src/
│   └── main.cpp               # Firmware principal (Arduino/ESP32)
├── hardware/
│   ├── pinout.md              # Mapeo de pines ESP32 <-> actuadores/panel
│   └── schematic_notes.md     # Notas del esquematico y componentes
├── docs/
│   ├── ciclos_lavado.md       # Documentacion de ciclos de fabrica
│   └── guia_instalacion.md    # Guia paso a paso de instalacion
└── platformio.ini             # Configuracion PlatformIO
```

## Hardware Necesario

| Componente | Cantidad | Notas |
|-----------|----------|-------|
| ESP32 DevKit V1 (o S3) | 1 | Controlador principal |
| Modulo reles 6 canales (5V, optoacoplador) | 1 | Contactos 10A 250VAC |
| Fuente Hi-Link HLK-PM01 (AC->5V) | 1 | Alimentacion aislada |
| Regulador AMS1117 3.3V | 1 | Para ESP32 si no usa DevKit |
| Resistencias 10k ohm | 8 | Pull-ups para botones/sensores |
| Conectores compatibles panel original | - | Segun modelo |

## Ciclos Implementados

| Ciclo | Lavado | Enjuagues | Centrifugado |
|-------|--------|-----------|--------------|
| Pesado | 15 min | 2x 4 min | 7 min |
| Normal | 12 min | 2x 3 min | 5 min |
| Delicado | 7 min | 1x 3 min | 3 min |
| Rapido | 5 min | 1x 2 min | 3 min |
| Solo Centrifugado | - | - | 7 min |
| Solo Enjuague | - | 2x 3 min | 3 min |

## Seguridad

- Interlock de tapa (no centrifuga con tapa abierta)
- Timeout de llenado (15 min max)
- Corte total ante error
- Aislamiento galvanico AC/DC

## Compilacion

```bash
# Con PlatformIO
pio run

# Subir al ESP32
pio run --target upload

# Monitor serial
pio device monitor
```

## Licencia

Proyecto personal / uso libre.
