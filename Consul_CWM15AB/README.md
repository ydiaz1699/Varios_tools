# Consul CWH15AB - ESP32 Controller

Reemplazo de la placa de control original de la lavadora **Consul CWH15AB** (15kg, 16 programas) por un **ESP32**, manteniendo el panel original (display digital + boton giratorio) y replicando la logica de lavado de fabrica.

## Modelo Base

| Dato | Valor |
|------|-------|
| Modelo | Consul CWH15AB |
| Capacidad | 15 kg |
| Programas | 16 |
| Niveles de agua | 4 |
| Panel | Display Digital (Tact) + Boton giratorio |
| Potencia | 620W |
| Centrifugacion | ~750 rpm |
| Eficiencia | Classe A (Procel) |
| Dispenser | Dual (Sabao + Amaciante) |
| Funciones | Mais Secas, Lavagem Eco, Autolimpeza |

## Objetivo

- Sustituir la PCB original danada o discontinuada
- Mantener el panel de usuario (display + encoder/knob) sin modificaciones
- Replicar los 16 ciclos de lavado de fabrica
- Display LCD I2C para mostrar programa, estado y tiempo restante
- Opcionalmente agregar WiFi (IoT/Home Assistant)

## Los 16 Programas Implementados

| # | Programa | Lavado | Enjuagues | Centrif. |
|---|---------|--------|-----------|----------|
| 1 | Roupas Brancas | 14 min fuerte | 2x 4 min | 7 min |
| 2 | Roupas Coloridas | 12 min fuerte | 2x 3 min | 6 min |
| 3 | Roupas Escuras | 10 min suave | 2x 3 min | 5 min |
| 4 | Jeans | 13 min fuerte | 2x 4 min | 7 min |
| 5 | Cama e Banho | 15 min fuerte | 2x 4 min | 8 min |
| 6 | Delicadas | 7 min suave | 1x 3 min | 3 min |
| 7 | Roupas de Bebe | 12 min suave | 3x 4 min | 6 min |
| 8 | Casacos e Moletons | 14 min fuerte | 2x 4 min | 7 min |
| 9 | Tenis | 10 min suave | 1x 3 min | 4 min |
| 10 | Roupas Pesadas | 15 min fuerte | 2x 4 min | 8 min |
| 11 | Edredom | 17 min suave | 2x 5 min | 6 min |
| 12 | Tira Odores | 13 min fuerte | 3x 4 min | 6 min |
| 13 | Ciclo Rapido | 5 min fuerte | 1x 2 min | 3 min |
| 14 | Enxague | - | 2x 3 min | 5 min |
| 15 | Centrifugacao | - | - | 8 min |
| 16 | Molho (Remojo) | 30 min reposo | - | - |

## Estructura del Proyecto

```
Consul_CWM15AB/
├── README.md                  # Este archivo
├── platformio.ini             # Configuracion PlatformIO
├── src/
│   └── main.cpp               # Firmware (ESP32 + encoder + LCD)
├── hardware/
│   ├── pinout.md              # Mapeo GPIOs completo
│   └── schematic_notes.md     # Esquematico y BOM
└── docs/
    ├── ciclos_lavado.md       # 16 ciclos detallados + calibracion
    └── guia_instalacion.md    # Guia paso a paso (5 fases)
```

## Hardware Necesario

| Componente | Cantidad | Notas |
|-----------|----------|-------|
| ESP32 DevKit V1 | 1 | Controlador principal |
| Modulo reles 6 canales (5V, opto) | 1 | 10A 250VAC |
| Encoder rotativo KY-040 | 1 | Reemplaza knob original |
| LCD 16x2 con modulo I2C | 1 | Reemplaza display digital |
| Fuente Hi-Link HLK-PM01 | 1 | AC->5V aislada |
| Resistencias 10k | 4 | Pull-ups sensores |
| Conectores panel original | - | Segun medicion |

## Panel de Control

```
┌─────────────────────────────────────────┐
│  [POWER]  ┌────────┐  [NIVEL] [+SECAS] │
│           │ LCD    │                    │
│           │ 16x2   │        [INICIO]    │
│           └────────┘                    │
│      ┌──┐                               │
│      │@@│ <- Encoder rotativo (knob)    │
│      └──┘    Gira = cambia programa     │
│              Push = confirma            │
└─────────────────────────────────────────┘
```

## Seguridad

- Interlock de tapa (no centrifuga con tapa abierta)
- Timeout de llenado (15 min max)
- Corte total ante error con mensaje en display
- Aislamiento galvanico AC/DC (HLK-PM01 + optoacopladores)
- Pausa obligatoria entre cambios de direccion del motor

## Compilacion

```bash
# Con PlatformIO
pio run

# Subir al ESP32
pio run --target upload

# Monitor serial (debug)
pio device monitor
```

## Dependencias

```ini
lib_deps =
    marcoschwartz/LiquidCrystal_I2C@^1.1.4
```

## Calibracion

**IMPORTANTE:** Antes de retirar la placa original, medir con
cronometro los tiempos de cada ciclo y actualizar la tabla
`ciclos[]` en `src/main.cpp`. Ver `docs/ciclos_lavado.md` para
la plantilla de medicion.

## Licencia

Proyecto personal / uso libre.
