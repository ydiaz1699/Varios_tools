# Guia de Instalacion - Consul CWM15AB ESP32

## Prerequisitos

- [ ] Multimetro digital
- [ ] Destornilladores (Phillips y plano)
- [ ] Cautin y estano (para conexiones)
- [ ] Camara/celular para fotos
- [ ] Cronometro (para medir ciclos)
- [ ] Cables AWG 18 (potencia) y AWG 22 (senal)
- [ ] Todos los componentes del BOM (ver hardware/schematic_notes.md)

## Fase 1: Documentacion (CON PLACA ORIGINAL)

> **NO retirar la placa original hasta completar esta fase**

### 1.1 Fotografiar todo
- Foto general del area de la placa
- Foto de cada conector con su cable
- Foto del panel de botones (frente y reverso)
- Foto de las etiquetas/colores de cables

### 1.2 Medir los ciclos
- Ejecutar cada programa y cronometrar (ver docs/ciclos_lavado.md)
- Anotar el patron de agitacion (escuchar el cambio de direccion)
- Contar los enjuagues de cada programa

### 1.3 Mapear el panel
Con multimetro en modo continuidad:
1. Desconectar conector del panel de la placa
2. Presionar cada boton y ver que pines se cortocircuitan
3. Identificar anodo/catodo de cada LED (medir con diodo)
4. Documentar todo en una tabla

### 1.4 Identificar cables de actuadores
| Cable | Color | Va a... | Voltaje |
|-------|-------|---------|---------|
| | | Valvula agua | |
| | | Motor (comun) | |
| | | Motor (dir A) | |
| | | Motor (dir B) | |
| | | Centrifugado | |
| | | Bomba drenaje | |
| | | Trava tapa | |
| | | Presostato | |
| | | Switch tapa | |

## Fase 2: Montaje del Hardware

### 2.1 Preparar la fuente de alimentacion
1. Montar HLK-PM01 en la placa perforada
2. Conectar capacitor 100uF en salida 5V
3. Montar AMS1117-3.3V con capacitores de filtro
4. Verificar: 5V estable y 3.3V estable con multimetro
5. **PROBAR SIN CONECTAR AL ESP32 PRIMERO**

### 2.2 Montar ESP32
1. Soldar headers o montar en socket
2. Conectar 3.3V y GND
3. Verificar que enciende (LED integrado)
4. Cargar firmware de prueba (blink)

### 2.3 Conectar modulo de reles
1. Alimentar modulo con 5V
2. Conectar pines IN a los GPIOs del ESP32
3. Probar cada rele individualmente con firmware de test
4. Escuchar el "click" de cada rele

### 2.4 Conectar panel
1. Usar el mapeo de la Fase 1.3
2. Conectar botones a GPIOs con pull-up
3. Conectar LEDs con resistencia serie si es necesario
4. Probar cada boton/LED con firmware de test

### 2.5 Conectar sensores
1. Presostato: verificar que es normalmente abierto o cerrado
2. Switch tapa: verificar polaridad
3. Conectar a GPIOs con pull-up

## Fase 3: Pruebas (SIN AGUA)

### 3.1 Test de reles
```
- [ ] Rele valvula: se escucha click al activar
- [ ] Rele motor A: se escucha click
- [ ] Rele motor B: se escucha click
- [ ] Rele centrifugado: se escucha click
- [ ] Rele bomba: se escucha click
- [ ] Rele trava: se escucha click
```

### 3.2 Test de panel
```
- [ ] Boton Power enciende/apaga
- [ ] Boton Programa cicla entre programas
- [ ] Boton Nivel cicla entre niveles
- [ ] LEDs de programa se encienden correctamente
- [ ] Boton Inicio NO arranca si tapa esta "abierta"
```

### 3.3 Test de logica (simular sensores)
1. Puentear pin del presostato para simular "nivel alcanzado"
2. Verificar que pasa de LLENADO a LAVADO
3. Verificar que la agitacion alterna direccion
4. Verificar la secuencia completa

### 3.4 Test con motor real (sin carga)
1. Conectar motor SIN ropa ni agua
2. Ejecutar programa rapido
3. Verificar que motor gira en ambas direcciones
4. Verificar que centrifugado funciona
5. Verificar que la bomba de drenaje funciona

## Fase 4: Instalacion Final

### 4.1 Montar en la lavadora
1. Retirar placa original (guardarla como referencia)
2. Montar nueva placa en el mismo espacio
3. Conectar todos los cables segun mapeo
4. Asegurar conexiones mecanicamente (borneras, no empalmes sueltos)
5. Verificar que no hay cables cerca de partes moviles

### 4.2 Primer ciclo completo con agua
1. Usar programa RAPIDO primero (el mas corto)
2. Supervisar TODO el ciclo
3. Verificar:
   - [ ] Llena correctamente
   - [ ] Corta agua al nivel correcto
   - [ ] Agita sin ruidos anormales
   - [ ] Drena completamente
   - [ ] Enjuaga correctamente
   - [ ] Centrifuga sin vibracion excesiva
   - [ ] Se detiene al abrir tapa durante centrifugado
   - [ ] Desbloquea tapa al finalizar

### 4.3 Ajustar tiempos
- Comparar con los tiempos medidos en Fase 1.2
- Ajustar valores en el array `ciclos[]` del firmware
- Recargar firmware via USB o OTA

## Fase 5: Sellado y Finalizacion

1. Aplicar barniz conformado (conformal coating) a la PCB
2. Asegurar que la ventilacion es adecuada
3. Etiquetar cables por si se necesita servicio futuro
4. Ejecutar todos los programas al menos una vez

## Solucion de Problemas

| Problema | Posible Causa | Solucion |
|---------|---------------|----------|
| No enciende | Fuente quemada | Verificar HLK-PM01 |
| No llena | Rele valvula no activa | Verificar GPIO y rele |
| No agita | Motor desconectado | Verificar reles motor |
| No drena | Bomba desconectada | Verificar rele bomba |
| Llenado infinito | Presostato mal conectado | Verificar sensor nivel |
| No centrifuga | Interlock tapa | Verificar switch tapa |
| LEDs no encienden | Polaridad invertida | Verificar anodo/catodo |

## Actualizacion de Firmware (OTA - Futuro)

Si se agrega WiFi al proyecto:
1. Conectar ESP32 a la red WiFi
2. Usar ArduinoOTA o ESPHome para actualizar sin cable
3. No es necesario abrir la maquina para ajustar tiempos
