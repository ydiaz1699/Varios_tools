# Mapeo de Pines - ESP32 <-> Consul CWH15AB

## Pines de Salida (Actuadores via Reles)

| GPIO ESP32 | Funcion | Tipo Carga | Rele |
|-----------|---------|------------|------|
| GPIO 25 | Valvula entrada de agua | Solenoide AC | R1 - NO |
| GPIO 26 | Motor agitacion Dir. A | Motor AC | R2 - NO |
| GPIO 27 | Motor agitacion Dir. B | Motor AC | R3 - NO |
| GPIO 32 | Motor centrifugado | Motor AC | R4 - NO |
| GPIO 33 | Bomba de drenaje | Motor AC | R5 - NO |
| GPIO 14 | Trava/Lock de tapa | Electroiman | R6 - NO |

## Pines de Entrada (Sensores)

| GPIO ESP32 | Funcion | Tipo | Notas |
|-----------|---------|------|-------|
| GPIO 34 | Presostato nivel bajo | Switch presion | Activo LOW |
| GPIO 35 | Presostato nivel alto | Switch presion | Activo LOW |
| GPIO 36 (VP) | Microswitch tapa cerrada | Mecanico | Activo LOW |

## Encoder Rotativo (Selector de Programa)

| GPIO ESP32 | Funcion | Notas |
|-----------|---------|-------|
| GPIO 18 | Encoder CLK (Clock) | Con interrupt, INPUT_PULLUP |
| GPIO 19 | Encoder DT (Data) | INPUT_PULLUP |
| GPIO 21 | Encoder SW (Push button) | Activo LOW, INPUT_PULLUP |

El encoder rotativo reemplaza el boton giratorio (knob) original
del panel CWH15AB. Al girar, cicla entre los 16 programas.
El boton push del encoder puede usarse como confirmacion.

## Display LCD I2C (16x2)

| Pin ESP32 | Funcion | Pin LCD I2C |
|-----------|---------|-------------|
| GPIO 22 | SCL (I2C Clock) | SCL |
| GPIO 21 | SDA (I2C Data) | SDA |
| 5V | Alimentacion | VCC |
| GND | Tierra | GND |

**Direccion I2C:** 0x27 (tipica para modulo PCF8574)
**Nota:** GPIO 21 es compartido con encoder SW. Si esto causa
conflicto, mover encoder SW a otro pin (ej: GPIO 15).

Alternativa: Si el panel original usa display de 7 segmentos
o LEDs individuales, adaptar el codigo para controlar esos
elementos directamente en vez del LCD I2C.

## Botones del Panel

| GPIO ESP32 | Boton | Funcion |
|-----------|-------|---------|
| GPIO 4 | POWER | Encender/Apagar maquina |
| GPIO 5 | INICIO | Iniciar/Pausar ciclo |
| GPIO 16 | NIVEL | Ciclar nivel de agua (4 niveles) |
| GPIO 17 | MAIS SECAS | Activar centrifugado extra |

## LED de Estado

| GPIO ESP32 | Funcion | Notas |
|-----------|---------|-------|
| GPIO 23 | LED Status | Parpadea durante operacion |

## Diagrama de Conexion Resumido

```
                    ┌──────────────────┐
                    │   ESP32 DevKit   │
                    │                  │
      Encoder ────► │ GPIO18 (CLK)     │
      Rotativo ───► │ GPIO19 (DT)      │
      (Knob)  ────► │ GPIO21 (SW)      │
                    │                  │
      LCD I2C ────► │ GPIO22 (SCL)     │
      16x2    ────► │ GPIO21 (SDA)*    │
                    │                  │
      BTN Power ──► │ GPIO4            │
      BTN Inicio ─► │ GPIO5            │
      BTN Nivel ──► │ GPIO16           │
      BTN +Secas ─► │ GPIO17           │
                    │                  │
      Presost.L ──► │ GPIO34           │
      Presost.H ──► │ GPIO35           │
      Sw. Tapa ───► │ GPIO36           │
                    │                  │
      Rele Valv ◄── │ GPIO25           │
      Rele Mot A◄── │ GPIO26           │
      Rele Mot B◄── │ GPIO27           │
      Rele Centr◄── │ GPIO32           │
      Rele Bomba◄── │ GPIO33           │
      Rele Trava◄── │ GPIO14           │
                    │                  │
      LED Status◄── │ GPIO23           │
                    └──────────────────┘

  * SDA en GPIO 21 compartido con encoder SW.
    Si hay conflicto, usar GPIO 15 para encoder SW.
```

## Alimentacion

| Componente | Voltaje | Corriente | Fuente |
|-----------|---------|-----------|--------|
| ESP32 DevKit | 5V (via USB) o 3.3V | ~250mA | HLK-PM01 |
| Modulo Reles 6ch | 5V (VCC) | ~400mA | HLK-PM01 |
| LCD I2C | 5V | ~30mA | HLK-PM01 |
| Encoder rotativo | 3.3V (pull-ups) | <5mA | ESP32 interno |
| **TOTAL DC** | **5V** | **~700mA** | **HLK-PM01 (600mA) + margen** |

> **Nota:** Si el consumo total supera 600mA del HLK-PM01,
> usar HLK-PM03 (3W, 5V 600mA) o HLK-5M05 (5W, 5V 1A).

## GPIOs Utilizados (Resumen)

| GPIO | Uso | Tipo |
|------|-----|------|
| 4 | BTN Power | INPUT_PULLUP |
| 5 | BTN Inicio | INPUT_PULLUP |
| 14 | Rele Trava Tapa | OUTPUT |
| 16 | BTN Nivel | INPUT_PULLUP |
| 17 | BTN Mais Secas | INPUT_PULLUP |
| 18 | Encoder CLK | INPUT_PULLUP + ISR |
| 19 | Encoder DT | INPUT_PULLUP |
| 21 | Encoder SW / SDA | INPUT_PULLUP / I2C |
| 22 | SCL (I2C) | I2C |
| 23 | LED Status | OUTPUT |
| 25 | Rele Valvula | OUTPUT |
| 26 | Rele Motor A | OUTPUT |
| 27 | Rele Motor B | OUTPUT |
| 32 | Rele Centrifugado | OUTPUT |
| 33 | Rele Bomba | OUTPUT |
| 34 | Presostato Bajo | INPUT (solo input) |
| 35 | Presostato Alto | INPUT (solo input) |
| 36 | Switch Tapa | INPUT (solo input) |

**GPIOs libres:** 2, 12, 13, 15 (disponibles para expansiones)

## GPIOs a EVITAR

- GPIO 0: Boot mode (no usar)
- GPIO 2: LED integrado, puede usarse con cuidado
- GPIO 6-11: Flash SPI interno (NUNCA usar)
- GPIO 12: MTDI, puede afectar boot si esta HIGH al inicio
- GPIO 15: MTDO, emite PWM al boot (cuidado con salidas criticas)
