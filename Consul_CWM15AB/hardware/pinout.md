# Mapeo de Pines - ESP32 <-> Consul CWM15AB

## Pines de Salida (Actuadores via Reles)

| GPIO ESP32 | Funcion | Tipo Carga | Notas |
|-----------|---------|------------|-------|
| GPIO 25 | Valvula entrada de agua | Solenoide AC | Rele NO |
| GPIO 26 | Motor agitacion Dir. A | Motor AC | Rele NO |
| GPIO 27 | Motor agitacion Dir. B | Motor AC | Rele NO |
| GPIO 32 | Motor centrifugado | Motor AC | Rele NO |
| GPIO 33 | Bomba de drenaje | Motor AC | Rele NO |
| GPIO 14 | Trava/Lock de tapa | Electroiman | Rele NO |

## Pines de Entrada (Sensores)

| GPIO ESP32 | Funcion | Tipo | Notas |
|-----------|---------|------|-------|
| GPIO 34 | Presostato nivel bajo | Switch presion | Activo LOW, INPUT_PULLUP |
| GPIO 35 | Presostato nivel alto | Switch presion | Activo LOW, INPUT_PULLUP |
| GPIO 36 | Microswitch tapa cerrada | Mecanico | Activo LOW, INPUT_PULLUP |

## Pines del Panel de Usuario

### Botones (Entrada - Activo LOW)

| GPIO ESP32 | Boton | Funcion |
|-----------|-------|---------|
| GPIO 4 | POWER | Encender/Apagar maquina |
| GPIO 16 | PROGRAMA | Ciclar entre programas |
| GPIO 17 | NIVEL | Ciclar nivel de agua |
| GPIO 5 | INICIO | Iniciar/Pausar ciclo |

### LEDs Indicadores (Salida - Activo HIGH)

| GPIO ESP32 | LED | Indica |
|-----------|-----|--------|
| GPIO 18 | Pesado | Programa pesado seleccionado |
| GPIO 19 | Normal | Programa normal seleccionado |
| GPIO 21 | Delicado | Programa delicado seleccionado |
| GPIO 22 | Rapido | Programa rapido seleccionado |
| GPIO 23 | Lavando | Etapa de lavado activa |
| GPIO 13 | Enjuague | Etapa de enjuague activa |
| GPIO 12 | Centrifugado | Etapa de centrifugado activa |

## Notas de Conexion

### Modulo de Reles
- Usar modulo de 6 reles con optoacoplador
- Alimentar con 5V (VCC) y 3.3V (senal IN)
- Verificar si el modulo es activo HIGH o LOW y ajustar codigo
- Contactos: minimo 10A 250VAC

### Panel Original
- Identificar conector flat/ribbon del panel
- Medir con multimetro que pin va a cada boton/LED
- Los botones normalmente conectan a GND al presionar
- Los LEDs pueden necesitar resistencia serie (verificar voltaje)

### Alimentacion
- Fuente AC->DC: Hi-Link HLK-PM01 (5V 600mA)
- Regulador 3.3V: AMS1117-3.3 para ESP32
- IMPORTANTE: Aislar completamente circuito DC del AC

### GPIOs a EVITAR en ESP32
- GPIO 0: Boot mode (no usar)
- GPIO 2: LED integrado / boot (evitar)
- GPIO 6-11: Flash SPI (NO USAR)
- GPIO 15: Debug output al boot (evitar para salidas criticas)
- GPIO 34-39: Solo entrada (no tienen pull-up interno fisico,
  pero INPUT_PULLUP funciona via software en algunos boards)
