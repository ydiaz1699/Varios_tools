# Notas del Esquematico - Consul CWM15AB ESP32

## Diagrama de Bloques

```
┌─────────────────────────────────────────────────────────────┐
│                    RED AC (127V o 220V)                       │
└────┬──────────┬──────────┬──────────┬──────────┬────────────┘
     │          │          │          │          │
     │    ┌─────┴─────┐   │          │          │
     │    │ HLK-PM01  │   │          │          │
     │    │ AC -> 5V  │   │          │          │
     │    └─────┬─────┘   │          │          │
     │          │          │          │          │
     │    ┌─────┴─────┐   │          │          │
     │    │ AMS1117   │   │          │          │
     │    │ 5V -> 3.3V│   │          │          │
     │    └─────┬─────┘   │          │          │
     │          │          │          │          │
     │    ┌─────┴─────┐   │          │          │
     │    │   ESP32   │   │          │          │
     │    │  DevKit   │   │          │          │
     │    └─┬───┬───┬─┘   │          │          │
     │      │   │   │     │          │          │
     │   GPIOs  │  GPIOs  │          │          │
     │   (OUT)  │  (IN)   │          │          │
     │      │   │   │     │          │          │
┌────┴──────┴───┘   │     │          │          │
│  MODULO RELES     │     │          │          │
│  6 CANALES        │     │          │          │
│  (Optoacoplado)   │     │          │          │
├───────────────────┤     │          │          │
│ R1: Valvula H2O  ├─────┘          │          │
│ R2: Motor Dir A  ├────────────────┘          │
│ R3: Motor Dir B  ├──────────────────────────┘
│ R4: Centrifugado ├──── (a motor centrifuga)
│ R5: Bomba Drain  ├──── (a bomba drenaje)
│ R6: Trava Tapa   ├──── (a electroiman)
└───────────────────┘

         ┌─────────────────┐
         │  PANEL USUARIO   │
         │ (Conector Flat)  │
         ├─────────────────┤
         │ BTN Power  ── GPIO 4   │
         │ BTN Programa─ GPIO 16  │
         │ BTN Nivel ─── GPIO 17  │
         │ BTN Inicio ── GPIO 5   │
         │ LED Pesado ── GPIO 18  │
         │ LED Normal ── GPIO 19  │
         │ LED Delicado─ GPIO 21  │
         │ LED Rapido ── GPIO 22  │
         │ LED Lavando ─ GPIO 23  │
         │ LED Enjuague─ GPIO 13  │
         │ LED Centrif.─ GPIO 12  │
         └─────────────────┘

         ┌─────────────────┐
         │    SENSORES      │
         ├─────────────────┤
         │ Presostato L ── GPIO 34 │
         │ Presostato H ── GPIO 35 │
         │ Switch Tapa ─── GPIO 36 │
         └─────────────────┘
```

## Lista de Componentes (BOM)

| # | Componente | Valor/Modelo | Cantidad | Proveedor Sugerido |
|---|-----------|-------------|----------|-------------------|
| 1 | ESP32 DevKit V1 | ESP-WROOM-32 | 1 | AliExpress/Amazon |
| 2 | Modulo Reles 6ch | 5V, optoacoplador, 10A | 1 | AliExpress |
| 3 | Fuente AC-DC | HLK-PM01 (5V 600mA) | 1 | AliExpress |
| 4 | Regulador LDO | AMS1117-3.3V | 1 | Local |
| 5 | Capacitor electrolitico | 100uF 10V | 2 | Local |
| 6 | Capacitor ceramico | 100nF | 3 | Local |
| 7 | Resistencia | 10k ohm 1/4W | 8 | Local |
| 8 | Resistencia | 330 ohm 1/4W | 7 | Para LEDs (si necesario) |
| 9 | Borneras | 2 pines, paso 5mm | 6 | Local |
| 10 | Conector Flat | Compatible panel original | 1 | Medir del original |
| 11 | PCB perforada | 7x9 cm min | 1 | Local |
| 12 | Cable AWG 18 | Para AC (actuadores) | 2m | Local |
| 13 | Cable AWG 22 | Para senales DC | 2m | Local |
| 14 | Fusible | 5A 250V | 1 | Proteccion general |
| 15 | Portafusible | Para PCB o panel | 1 | Local |

## Consideraciones de Diseno

### Aislamiento Electrico
- La fuente HLK-PM01 provee aislamiento galvanico AC/DC
- Los reles con optoacoplador aislan las senales del ESP32 del AC
- NUNCA conectar directamente GPIO del ESP32 a linea AC
- Mantener distancia minima de 8mm entre pistas AC y DC en PCB

### Proteccion
- Fusible de 5A en la entrada AC general
- Diodos flyback en bobinas de reles (normalmente incluidos en modulo)
- Varistor MOV en entrada AC (opcional, proteccion contra picos)
- Capacitores de desacople cerca del ESP32

### Disipacion Termica
- El HLK-PM01 puede calentar: dejar espacio de ventilacion
- El AMS1117 necesita capacitores de filtro (100uF + 100nF)
- No encerrar la electronica en espacio sin ventilacion

### Dimensiones
- La placa debe caber en el espacio de la placa original
- Medir cuidadosamente antes de disenar
- Considerar montaje vertical si el espacio es limitado
- Proteger de humedad con barniz conformado (conformal coating)
