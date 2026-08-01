# Guia de Identificacion de Cables - Consul CWH15AB

> Procedimiento paso a paso para identificar cada cable/conector
> de la placa original y conectarlos al ESP32 con modulo de reles.

---

## Contexto del Problema

La placa original falla:
- Se cuelga a mitad del ciclo (parpadean todos los LEDs)
- Hay que desenchufar y volver a enchufar para que funcione
- El drenaje no se activa automaticamente
- El motor de la bomba esta PERFECTO (probado manualmente)
- Actualmente se opera la bomba de forma manual (conectar/desconectar)

**Solucion:** Reemplazar la placa por ESP32 + reles + Home Assistant/ESPHome

---

## Datos de la Lavadora

| Dato | Valor |
|------|-------|
| Modelo | Consul CWH15AB |
| Voltaje | **220V** |
| ESP32 | Generico 38 pines |
| Bomba drenaje | 2 cables (ya identificados) |
| Home Assistant | Ya instalado con ESPHome |

---

## Herramientas Necesarias

- [ ] Multimetro digital (con modo continuidad y voltaje AC)
- [ ] Destornillador Phillips y plano
- [ ] Celular/camara para fotos
- [ ] Cinta de enmascarar + marcador (para etiquetar cables)
- [ ] Papel y lapiz (para anotar)
- [ ] Pinzas de cocodrilo (opcional, facilita medicion)

---

## PASO 1: Seguridad (ANTES de tocar)

1. **DESENCHUFAR** la lavadora de la toma de corriente
2. **CERRAR** la canilla/llave de agua
3. **ESPERAR 5 minutos** (los capacitores se descargan)
4. Verificar con multimetro en modo voltaje AC que NO hay tension entre los cables de alimentacion

---

## PASO 2: Acceder a la Placa

1. Retirar la tapa trasera superior (generalmente 2-4 tornillos Phillips)
2. La placa esta en la parte superior-trasera de la lavadora
3. **ANTES DE TOCAR NADA: FOTOGRAFIAR TODO**
   - Foto general de la placa con todos los conectores
   - Foto de cerca de cada conector (que se vean colores de cables)
   - Foto de las etiquetas/serigrafias en la placa (CN1, CN2, etc.)

---

## PASO 3: Identificar los Conectores

La placa deberia tener entre 5 y 7 conectores. Anotarlos asi:

```
CONECTOR 1: ___ cables, colores: _______________
CONECTOR 2: ___ cables, colores: _______________
CONECTOR 3: ___ cables, colores: _______________
CONECTOR 4: ___ cables, colores: _______________
CONECTOR 5: ___ cables, colores: _______________
CONECTOR 6: ___ cables, colores: _______________
CONECTOR 7: ___ cables, colores: _______________
```

---

## PASO 4: Identificar los Cables Conocidos

### 4.1 Alimentacion 220V (3 cables)
- **Como identificar:** Es el cable que viene del enchufe/cable de alimentacion
- Generalmente: Marron/Negro = Fase, Azul = Neutro, Verde-Amarillo = Tierra
- **Etiquetar:** "220V - F / N / T"

### 4.2 Bomba de Drenaje (2 cables - YA LOS CONOCES)
- **Como identificar:** Son los 2 cables que ya conectas/desconectas manualmente
- Seguirlos hasta el conector de la placa
- **Etiquetar:** "BOMBA"
- **Anotar colores:** _______________

---

## PASO 5: Identificar los Cables Desconocidos

### Metodo: Seguir cada cable fisicamente

Con la lavadora desenchufada, seguir cada cable desde el conector de
la placa hasta el componente fisico al que llega.

### 5.1 Valvula de Entrada de Agua (Solenoide)
- **Donde esta:** En la parte trasera-superior, donde se conecta la manguera de entrada
- **Como se ve:** Bobina cilindrica con 2 cables
- **Como confirmar:** Poner multimetro en resistencia (ohmios).
  Una valvula solenoide mide entre **1k y 4k ohms**
- **Etiquetar:** "VALVULA"
- **Anotar colores:** _______________

### 5.2 Motor (3-5 cables)
- **Donde esta:** En la parte inferior de la lavadora
- **Como se ve:** Motor grande con varios cables (es el componente mas grande)
- **Cables tipicos:**
  - **Comun (C):** 1 cable
  - **Bobinado Agitacion Dir A:** 1 cable
  - **Bobinado Agitacion Dir B:** 1 cable
  - **Bobinado Centrifugado:** 1 cable
  - **Capacitor:** Puede haber 1-2 cables adicionales al capacitor del motor
- **Como confirmar:** Medir resistencia entre pares de cables:
  - Comun a Dir A: ~5-15 ohms
  - Comun a Dir B: ~5-15 ohms
  - Comun a Centrif: ~3-10 ohms (menor resistencia = mas velocidad)
  - Dir A a Dir B: ~10-30 ohms (suma de los dos bobinados)
- **Etiquetar:** "MOTOR-C", "MOTOR-A", "MOTOR-B", "MOTOR-CENTRIF"
- **Anotar colores:** _______________

### 5.3 Presostato (Sensor de Nivel de Agua)
- **Donde esta:** En la parte superior, tiene una manguerita de aire que baja al tanque
- **Como se ve:** Pieza redonda/cilindrica con la manguerita + 2-3 cables electricos
- **Como confirmar:** Medir continuidad. Si soplas SUAVEMENTE por la manguerita,
  debe cambiar de abierto a cerrado (o viceversa). Se escucha un "click".
- **Etiquetar:** "PRESOSTATO" (anotar cual pin es COM, cual es NO/NC)
- **Anotar colores:** _______________
- **IMPORTANTE:** Si tiene 3 cables, es COM + NO + NC (Normalmente Abierto y Cerrado)

### 5.4 Microswitch de Tapa
- **Donde esta:** Debajo de la tapa, cerca de la bisagra
- **Como se ve:** Switch pequeño que se presiona cuando la tapa se cierra
- **Como confirmar:** Medir continuidad. Al presionar el switch, debe hacer continuidad.
- **Etiquetar:** "TAPA"
- **Anotar colores:** _______________

### 5.5 Traba de Tapa (Electroiman)
- **Donde esta:** Cerca del microswitch de tapa, mecanismo que bloquea fisicamente
- **Como se ve:** Bobina/electroiman con 2 cables
- **Como confirmar:** Medir resistencia: ~50-200 ohms tipicamente.
  Si le das 12-24V DC momentaneamente, debe escucharse un "click" y trabar
- **Etiquetar:** "TRABA"
- **Anotar colores:** _______________
- **NOTA:** Puede ser 12V DC o directamente 220V AC segun modelo. Verificar.

### 5.6 Panel de Control (Flat Cable)
- **Donde esta:** Cable plano que va hacia el frente (panel de botones/display)
- **Como se ve:** Cable plano/ribbon con muchos cables finos
- **Etiquetar:** "PANEL" (este se descarta si usas Home Assistant como interfaz)

---

## PASO 6: Tabla de Cables (Completar)

Completar esta tabla con los datos medidos:

| Componente | Cant. cables | Colores | Resistencia medida | Conector en placa |
|-----------|-------------|---------|-------------------|------------------|
| Alimentacion 220V | 3 | | - | |
| Bomba drenaje | 2 | | ohms | |
| Valvula agua | 2 | | ohms | |
| Motor Comun | 1 | | - | |
| Motor Dir A | 1 | | ohms vs Comun | |
| Motor Dir B | 1 | | ohms vs Comun | |
| Motor Centrif | 1 | | ohms vs Comun | |
| Capacitor motor | 1-2 | | uF | |
| Presostato | 2-3 | | (continuidad) | |
| Switch tapa | 2 | | (continuidad) | |
| Traba tapa | 2 | | ohms | |
| Panel | flat | | - | |

---

## PASO 7: Verificar Voltajes de Operacion

**CON LA LAVADORA ENCHUFADA (CUIDADO - 220V):**

> ⚠️ PELIGRO: Trabajar con 220V puede ser MORTAL.
> Si no tenes experiencia con mediciones en vivo, NO hagas este paso.
> Pedi ayuda a un electricista.

Si te animas (con MUCHO cuidado):
1. Enchufar la lavadora
2. Con multimetro en modo AC, medir entre los cables de cada actuador
   mientras la placa los activa (si la placa aun funciona parcialmente)
3. Anotar que voltaje recibe cada componente:
   - Bomba: deberia ser 220V AC
   - Valvula: deberia ser 220V AC
   - Motor: deberia ser 220V AC
   - Traba: puede ser 12V DC, 24V DC, o 220V AC (verificar!)

---

## PASO 8: Esquema de Conexion al ESP32

Una vez identificados todos los cables:

```
                    ┌──────────────────┐
   220V AC ──────── │  FUENTE HLK-PM01 │ ──── 5V DC
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │      ESP32       │
                    │   (38 pines)     │
                    └─┬──┬──┬──┬──┬──┬┘
                      │  │  │  │  │  │
              ┌───────┴──┴──┴──┴──┴──┴───────┐
              │     MODULO DE RELES           │
              │  (contactos 220V AC)          │
              ├──────────────────────────────┤
              │ R1 ── Valvula Agua (220V)    │
              │ R2 ── Motor Dir A (220V)     │
              │ R3 ── Motor Dir B (220V)     │
              │ R4 ── Motor Centrif (220V)   │
              │ R5 ── Bomba Drenaje (220V)   │
              │ R6 ── Traba Tapa (verificar V)│
              └──────────────────────────────┘

   Sensores (directos al ESP32):
   - Presostato ──── GPIO (con pull-up)
   - Switch Tapa ─── GPIO (con pull-up)
```

---

## PASO 9: Antes de Desconectar la Placa Original

Checklist final:

- [ ] Todas las fotos tomadas
- [ ] Todos los cables etiquetados con cinta
- [ ] Tabla de cables completada
- [ ] Voltajes verificados (si fue posible)
- [ ] Resistencias medidas de cada componente
- [ ] Presostato: saber cual es COM, NO, NC

### Guardar la placa original
No la tires. Guardarla como referencia por si necesitas:
- Verificar algo despues
- Volver atras temporalmente
- Identificar algun cable que se te paso

---

## PASO 10: Datos Pendientes (completar cuando desarmes)

```
Fecha de desarmado: ___/___/______

VALVULA DE AGUA:
  Cables (colores): _______________
  Resistencia: _______ ohms
  Voltaje de operacion: _______ V AC

MOTOR:
  Cable Comun (color): _______________
  Cable Dir A (color): _______________
  Cable Dir B (color): _______________
  Cable Centrif (color): _______________
  Cable Capacitor (color): _______________
  Resistencia C-A: _______ ohms
  Resistencia C-B: _______ ohms
  Resistencia C-Centrif: _______ ohms

PRESOSTATO:
  Cables (colores): _______________
  Tipo: 2 cables / 3 cables (COM+NO+NC)
  Cual es COM: _______________
  Cual es NO: _______________

SWITCH TAPA:
  Cables (colores): _______________
  Estado con tapa cerrada: continuidad / abierto

TRABA TAPA:
  Cables (colores): _______________
  Resistencia: _______ ohms
  Voltaje: _______ V (DC / AC)

BOMBA DRENAJE (ya identificada):
  Cables (colores): _______________
  Funciona: SI (probada manual)

NOTAS ADICIONALES:
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## Proximos Pasos (despues de identificar cables)

1. Armar circuito ESP32 + reles en un protoboard
2. Probar cada rele individualmente (escuchar click)
3. Conectar UN componente a la vez y probar
4. Orden recomendado de prueba:
   - Primero: Bomba de drenaje (ya la conoces)
   - Segundo: Valvula de agua (verificar que llena)
   - Tercero: Presostato (verificar que detecta nivel)
   - Cuarto: Motor agitacion (verificar direcciones)
   - Quinto: Motor centrifugado
   - Ultimo: Traba de tapa
5. Una vez todo probado individualmente, ejecutar ciclo completo

---

*Documento creado para el proyecto Consul CWM15AB ESP32 + Home Assistant*
