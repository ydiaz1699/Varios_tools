# Lavadora Consul CWH15AB

---

# 🧺 Guia Maestra: Lavadora Consul CWH15AB (15 kg) ✨

*Guia completa de usuario, especificaciones tecnicas y referencia para desarrollo de firmware (ESP32).*

---

## 1. Identificacion y Especificaciones Tecnicas

| Dato | Valor |
| --- | --- |
| **Marca / Modelo** | Consul (Whirlpool S.A.) CWH15AB |
| **Tipo** | Lavadora automatica de carga superior (top load) con agitador central |
| **Capacidad** | 15 kg de ropa seca |
| **Voltaje** | 127 V **o** 220 V (NO es bivolt, elegir version al comprar) |
| **Potencia / Consumo** | 620 W |
| **Consumo energetico** | 0,46 kWh por ciclo (Sello Procel A) |
| **Consumo de agua** | ~186 litros por ciclo (en nivel maximo) |
| **Dimensiones (AxAnxP)** | 100 x 63 x 70 cm |
| **Peso del equipo** | 38 kg |
| **Cesto / Tambor** | Acero inoxidable con base plastica |
| **Velocidad de centrifugado** | ~750 rpm (maxima) |
| **Dispenser** | Dual "Limpa Facil" (Jabon + Suavizante) |

### 🏠 1.1 Instalacion y Requisitos Tecnicos

- 📖 Sigue las instrucciones del **Manual del Producto** que viene dentro de la lavadora.
- ⚖️ Asegurate de que el electrodomestico este perfectamente **nivelado** (girar pies: derecha sube, izquierda baja).
- 🎁 Puedes retirar la pelicula protectora del gabinete; no afecta la funcionalidad.
- 🔌 **Electrico:** Voltaje exclusivo (127V o 220V, *no es bivolt*). Usar toma con tierra y disyuntor exclusivo.
- 🚿 **Agua:** Solo agua fria (5C a 30C). Presion de 20 a 800 kPa. **No usar cinta teflon** en las conexiones.
- 📏 **Desague:** La manguera de salida debe estar a una altura entre **0,85 m y 1,20 m**.
- 📐 **Espacio:** Dejar minimo 10 cm de separacion de paredes o muebles.

---

## 2. Instalacion y Requisitos

- ⚡ **Electrico:** Toma exclusiva con tierra (3 patas) y disyuntor independiente. No usar extensiones, "T" o adaptadores. (Cable 2,5 mm2 hasta 29m en 127V / 70m en 220V; 4,0 mm2 para distancias mayores).
- 🚿 **Agua:** Canilla exclusiva de 3/4". Solo agua fria (5C a 30C). Presion de 20 a 800 kPa. **NO usar cinta teflon** en las roscas de la manguera.
- 🌊 **Desague:** La manguera de salida debe estar a una altura estricta de **0,85 m a 1,20 m**. (Menos de 0,85 m no llena; mas de 1,20 m no drena).
- 📏 **Posicionamiento:** Superficie plana, nivelada (girar pies: derecha sube, izquierda baja). Dejar minimo 10 cm de separacion de paredes. No instalar sobre alfombras ni al sol directo.



---

## 3. 🎛️ Panel de Control y Secuencia de Operacion

### Elementos del Panel

- **Selector giratorio (knob):** 16 posiciones para elegir el programa.
- **Indicadores de etapa:** Luces para Remojo, Lavado, Enjuague, Centrifugado.
- **Botones:** `Nivel de Agua` (1 a 4 barras), `Nivel de Suciedad` (Poco/Sucias/Muy sucias), `Enxague` (Unico/Duplo/Eco).
- **Botones:** `Avancar Etapas` (saltar etapas manualmente) e `Iniciar / Desligar`.
- **Display:** Muestra programa, tiempo restante, etapa actual y "LISTO" al finalizar.
- **Teclas tactiles adicionales:**
    - **Nivel de Agua** - 4 niveles (1 a 4 barras).
    - **Nivel de Suciedad** - Pouco / Sujas / Muito (poco / sucias / muy sucias).
    - **Enxague** - Unico / Duplo / Unico+Eco / Duplo+Eco.

### Indicaciones del display

- Nombre del programa seleccionado (en espera).
- Tiempo restante estimado (durante operacion).
- Etapa actual: Lavado, Enjuague, Centrifugado.
- Indicacion de "LISTO" al finalizar.
- Indicacion de error si hay problema.

> **Nota:** El documento tecnico mencionaba un boton "Mas Secas" (centrifugado extra). El PDF oficial no lo confirma explicitamente como boton independiente, pero la funcion de centrifugado adicional puede implementarse via firmware.

### Secuencia Normal de Operacion

1. Enchufar y abrir la llave de paso de agua.
2. Colocar ropa (max. 15 kg) y cerrar la tapa.
3. Agregar insumos en el dispenser.
4. Encender, seleccionar programa y ajustar niveles si es necesario.
5. Presionar **INICIAR**. La traba de la tapa se activa automaticamente.
6. Al finalizar, suena una alerta, se muestra "LISTO" y se destraba la tapa.
- **Pausa:** Presionar `Iniciar/Desligar`. La traba se libera tras unos segundos. No se puede pausar durante el centrifugado por seguridad.

---

## 4. Niveles, Suciedad y Enjuagues

### 👕 Carga de Ropa y Niveles

- 🏷️ Verifica las etiquetas. **No laves tejidos impermeables** 🚫.
- 🔄 Coloca la ropa abierta, distribuyendola uniformemente alrededor del agitador.
- 📏 **Regla de Nivel Facil:** La regla dentro del cesto indica la altura de la ropa. Usala para elegir el nivel de agua y la cantidad de jabon.

### 💧 Niveles de Agua (Regla "Nivel Facil" dentro del cesto)

| Nivel | Barras | Volumen aprox. | Uso recomendado |
| --- | --- | --- | --- |
| **1** | 1 barra | ~80 L | Pocas prendas ligeras, ciclo rapido |
| **2** | 2 barras | ~120 L | Carga media, ropa delicada |
| **3** | 3 barras | ~155 L | Carga normal / completa |
| **4** | 4 barras | ~186 L | Edredon, sabanas, ropa pesada voluminosa |

### 🧼 Niveles de Suciedad (Define el patron de agitacion)

- **Poco:** Ropa usada 1 vez, sin manchas. Agitacion mas lenta, pausas largas.
- **Sucias:** Ropa usada mas de 1 vez. Movimiento normal, balance estandar.
- **Muy sucias:** Ropa con mucho uso o manchas. Agitacion intensa, pausas cortas.

### 🔄 Tipos de Enjuague

- **Unico:** 1 enjuague.
- **Duplo:** 2 enjuagues.
- **Unico + Eco / Duplo + Eco:** Reduce el agua de enjuague un 10%.

> Los programas tienen enjuagues predefinidos, pero el usuario puede aumentar, reducir o cambiar el tipo antes de iniciar.



---

## 5. 🧴 Uso del Dispenser "Limpa Facil"

**🅰️ Compartimento A (Detergente en polvo):**

- Utiliza el **vaso dosificador** incluido.
- Ajusta la cantidad segun el nivel de agua y suciedad.
- *Nunca* coloques el detergente directamente sobre la ropa.
- Capacidad maxima: **240 ml** (aprox. 170 g).

**🅱️ Compartimento B (Suavizante):**

- Su uso es **opcional**. Diluye si es muy viscoso.
- No superes el nivel maximo (**MAX**).
- El nivel MAX esta calibrado para el **Nivel 4** de agua; reduce la cantidad en niveles inferiores.

**🎯 Quitamanchas Liquido / Lejia:**

- Usa lejia (agua sanitaria) **solo para ropa blanca**.
- Para colores, usa quitamanchas **sin cloro**.

---

### Programacion y Tipos de Enjuague

1. Elige el **programa** con el selector giratorio.
2. Ajusta el **nivel de agua** (1 a 4).
3. Selecciona el **nivel de suciedad**.
4. Modifica el **enjuague** si lo deseas:
   - *Unico:* 1 enjuague.
   - *Duplo:* 2 enjuagues.
   - *Unico/Duplo + Eco:* Reduce el agua un 10%.
5. Presiona **Iniciar/Desligar**.



---

## 6. 📋 Los 16 Programas de Lavado (Detalle Tecnico Completo)

*Cada programa incluye los parametros criticos para el usuario y la estructura de datos para el firmware ESP32.*

### 📊 Tabla Rapida de Tiempos

| # | Programa | Ciclo | ⏱️ Tiempo | 💧 Agua | 🔄 Remojo | 🧼 Enjuagues | 💪 Agitacion | 🌀 Centrif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 🛏️ **Cama y Bano** | Remojo+Lavado+Enj+Centrif | 1h 36m | 4 (Extra) | Si (10m) | 2 | Fuerte (4s giro / 2s pausa) | 7 min |
| 2 | 🛌 **Edredon** | Remojo+Lavado+Enj+Centrif | 1h 33m | 4 (Extra)* | Si (12m) | 2 | Muy suave (3s giro / 5s pausa) | 5 min |
| 3 | 🔧 **Limpieza Pesada** | Remojo+Lavado+Enj+Centrif | 2h 04m | 4 (Extra) | Si (15m) | 2 | Maxima (5s giro / 1s pausa) | 8 min |
| 4 | 🧽 **Panos de Limpieza** | Lavado+Enj+Centrif | 2h 27m | 3 (Alto) | No | 3 | Fuerte (4s giro / 2s pausa) | 6 min |
| 5 | 🌬️ **Quita Olores** | Lavado+Enj+Centrif | 0h 36m | 3 (Alto) | No | 3 | Moderada (3s giro / 3s pausa) | 4 min |
| 6 | ⚡ **Rapido** | Lavado+Enj+Centrif | 0h 29m | 1 (Bajo) | No | 1 | Moderada (3s giro / 2s pausa) | 3 min |
| 7 | ♻️ **Lavado Eco** | Lavado+Enj+Centrif | 0h 46m | 2 (Medio) | No | 2 | Moderada (3s giro / 2s pausa) | 5 min |
| 8 | ⚪ **Ropa Blanca** | Remojo+Lavado+Enj+Centrif | 1h 42m | 3 (Alto) | Si (12m) | 2 | Fuerte (4s giro / 2s pausa) | 7 min |
| 9 | 🎨 **Ropa de Color** | Lavado+Enj+Centrif | 0h 51m | 3 (Alto) | No | 2 | Normal (4s giro / 2s pausa) | 6 min |
| 10 | 🌑 **Ropa Oscura** | Lavado+Enj+Centrif | 0h 43m | 3 (Alto) | No | 2 | Suave (3s giro / 4s pausa) | 5 min |
| 11 | 👖 **Jeans** | Remojo+Lavado+Enj+Centrif | 1h 21m | 3 (Alto) | Si (8m) | 2 | Fuerte (4s giro / 2s pausa) | 6 min |
| 12 | 👔 **Uniforme** | Remojo+Lavado+Enj+Centrif | 1h 55m | 4 (Extra) | Si (12m) | 2 | Fuerte (4s giro / 2s pausa) | 7 min |
| 13 | 👙 **Ropa interior** | Lavado+Enj+Centrif | 1h 03m | 2 (Medio) | No | 2 | Suave (2s giro / 4s pausa) | 4 min |
| 14 | 🌸 **Ropa Ligera** | Remojo+Lavado+Enj+Centrif | 1h 46m | 2 (Medio) | Si (15m) | 2 | Muy suave (2s giro / 6s pausa) | 3 min |
| 15 | 👶 **Ropa de Bebe** | Remojo+Lavado+Enj+Centrif | 2h 20m | 3 (Alto) | Si (15m) | 3 | Suave (3s giro / 3s pausa) | 5 min |
| 16 | 🧼 **Limpieza Lavadora** | Lavado+Enj+Centrif | 0h 54m | 3 (Alto) | No | 2 | Fuerte (5s giro / 1s pausa) | 5 min |

*Edredon: Obligatorio Nivel 4. Solo para tamano matrimonial ("Casal").*

### Descripcion de cada programa (Comportamiento y Agitacion)

- **Cama y Bano:** Ciclo largo para sabanas, toallas, fundas. Nivel extra de agua recomendado por el volumen.
- **Edredon:** Solo para edredon tamano "Casal" (matrimonial). Agitacion muy suave, mucha pausa. Usar nivel 4 obligatorio y maximo jabon segun indicacion "muy sucias".
- **Limpieza Pesada:** Maximo tiempo de agitacion y centrifugado. Para ropa de trabajo muy sucia.
- **Panos de Limpieza:** Ciclo especifico para panos. **No usar suavizante** (no lo aprovecha y puede alterar niveles de agua). Maximo 2 kg.
- **Quita Olores:** 3 enjuagues para eliminar olores persistentes (humo, transpiracion, humedad).
- **Rapido:** Lavado corto, 1 enjuague, centrifugado corto. Para ropa poco sucia.
- **Lavado Eco:** Permite reutilizar el agua del lavado. Tras el lavado, el agua se puede dirigir a un balde en vez del desague. El agua de enjuague NO se reutiliza.
- **Ropa Blanca:** Lavado intenso con remojo para quitar manchas. Agitacion fuerte.
- **Ropa de Color:** El programa mas usado. Agitacion normal, 2 enjuagues, centrifugado completo.
- **Ropa Oscura:** Agitacion reducida (mas pausa entre giros) para evitar decoloracion por friccion.
- **Jeans:** Similar a ropa pesada pero optimizado para denim. Agitacion fuerte.
- **Uniforme:** Ciclo prolongado para uniformes de trabajo.
- **Ropa Interior:** Ciclo suave y corto para telas finas.
- **Ropa Ligera:** Ciclo suave con remojo para prendas delicadas.
- **Ropa de Bebe:** 3 enjuagues (en vez de 2) para eliminar residuos de jabon que irriten la piel.
- **Limpieza de Lavadora:** Ciclo de autolimpieza. Ejecutar 1 vez por mes SIN ropa, con 1/2 litro de blanqueador (agua sanitaria) en el cesto.

### Notas Criticas por Programa (Resumen)

- **Panos de Limpieza:** Max. 2 kg. **NO usar suavizante** (no lo aprovecha y altera niveles).
- **Lavado Eco:** Permite reutilizar agua del lavado (no la de enjuague). La luz parpadea; tienes 35 min para desviar la manguera a un balde. Si no, drena sola. Cancelar con 2 toques en `Avancar Etapas`.
- **Ropa de Bebe / Quita Olores:** Destacan por tener **3 enjuagues** para eliminar residuos irritantes o moleculas de olor.
- **Limpieza de Lavadora:** Ejecutar 1 vez al mes. **SIN ROPA**. Verter 1/2 litro de lejia directamente en el cesto vacio.



---

## 7. Funciones y Sistemas Especiales

- 🚿 **Spray de Agua:** Chorrea agua durante el llenado para mojar mejor la ropa. Es normal que gotee unos segundos al terminar el llenado (vaciado del sistema).
- ⚖️ **Sistema Anti-Desbalanceo:** Si detecta vibracion extrema en el centrifugado, detiene el ciclo, llena agua y agita para reacomodar. Si persiste, se interrumpe y pide redistribucion manual.
- ♻️ **Reuso de Agua (Lavagem Eco):** Tras el lavado, la luz parpadea. Tienes 35 min para desviar la manguera a un balde. Si no, drena sola.
- 🛑 **Seguridad de Tapa:** La traba electroiman se activa al iniciar. Si se abre la tapa, el motor se detiene **inmediatamente**.

---

## 8. 🧽 Mantenimiento y Diagnostico

**📅 Limpieza Interna (Mensual):**

1. Asegurate de que **no haya ropa**.
2. Vierte **1/2 litro de lejia** directamente en el cesto.
3. Selecciona **"Limpieza de la Lavadora"** y deja terminar.

**🧹 Otras tareas:**

- Limpia el **filtro de pelusas** (arriba del agitador) tras cada lavado.
- Lava la moldura y el sifon del **dispenser** con agua corriente.
- Deja la tapa abierta tras usar para evitar moho.

**⚠️ Solucion rapida de problemas:**

- *No centrifuga:* Tapa abierta o carga desbalanceada.
- *No drena:* Manguera de salida muy baja (<0,85m) o muy alta (>1,20m) / obstruida.
- *Mucha espuma:* Exceso de jabon. Usa el vaso dosificador.

### 🔍 Tabla Rapida de Diagnostico

| Problema | Causa Probable | Solucion |
| --- | --- | --- |
| **No centrifuga** | Tapa abierta o carga desbalanceada | Cerrar tapa, redistribuir ropa uniformemente |
| **No drena** | Manguera de salida <0,85m o >1,20m, u obstruida | Ajustar altura de la manguera o desobstruir |
| **Mucha espuma** | Exceso de jabon | Reducir cantidad usando el vaso dosificador |
| **Vibra mucho** | Mal nivelada o piso irregular | Ajustar los 4 pies niveladores |
| **Se detiene a mitad** | Tapa se abrio, falta presion de agua | Verificar cierre de tapa y llave de paso |



---

## 9. Datos Tecnicos para Proyecto ESP32 (Firmware)

### 🔌 Actuadores y Sensores

| Componente | Tipo de Carga | Voltaje | Corriente Est. | Notas |
| --- | --- | --- | --- | --- |
| **Valvula Solenoide** | AC | 127/220 V | ~300 mA | Entrada de agua |
| **Motor (Agitacion)** | AC | 127/220 V | 2-3 A | Bobinados direccionales |
| **Motor (Centrifugado)** | AC | 127/220 V | 3-4 A | Mismo motor fisico, bobinado distinto |
| **Bomba de Drenaje** | AC | 127/220 V | ~500 mA | Drenaje tipico de ~90 segundos |
| **Traba de Tapa** | DC/AC | 12-24 V | ~200 mA | Electroiman de seguridad |
| **Presostato** | Digital NO/NC | 5V (pull-up) | - | Se cierra al alcanzar el nivel de agua |
| **Microswitch Tapa** | Digital NO | 5V (pull-up) | - | Se cierra cuando la tapa esta cerrada |

*Nota:* El motor usa un sistema de transmision. Agitacion = giro lento con vaiven. Centrifugado = giro rapido directo al cesto. Se requieren reles para: Comun, Direccion A, Direccion B y Centrifugado.

### 🧠 Logica de Maquina de Estados (Firmware)

1. **INICIO:** Verificar tapa cerrada -> Activar traba -> Abrir valvula hasta que el presostato corte -> Cerrar valvula.
2. **REMOJO (si aplica):** Esperar tiempo definido sin agitar.
3. **AGITACION:** Giro Dir A (tiempoGiro_ms) -> **PAUSA** (pausaGiro_ms, OBLIGATORIA) -> Giro Dir B (tiempoGiro_ms) -> **PAUSA**. Repetir hasta completar tiempoLavado_ms.
4. **DRENAJE:** Encender bomba (~90 segundos fijos).
5. **ENJUAGUES:** Si numEnjuagues > 0, volver al paso 1 (con agitacion suave) y restar 1 al contador.
6. **CENTRIFUGADO:** Encender bomba + Motor centrifugado. **Monitorear microswitch tapa** (si se abre, PARAR TODO).
7. **FIN:** Apagar todo -> Desactivar traba -> Mostrar "LISTO".

### 🛡️ Protecciones de Seguridad (Obligatorias en codigo)

- **Timeout de llenado:** 15 min -> ERROR, apagar todo, destrabar tapa.
- **Pausa entre giros:** NUNCA invertir direccion sin pausa (pausaGiro_ms).
- **Tapa abierta:** Interrupcion inmediata del motor y bomba.
- **Corte de energia:** Al volver, ir a estado APAGADO (no retomar ciclo).

### 💻 Estructura de Datos Unificada (C/C++ para ESP32)

```cpp
enum NivelAgua { NIVEL_BAJO = 1, NIVEL_MEDIO = 2, NIVEL_ALTO = 3, NIVEL_EXTRA = 4 };

struct ProgramaLavado {
  const char* nombre;
  uint32_t    tiempoRemojo_ms;
  uint32_t    tiempoLavado_ms;
  uint16_t    tiempoGiro_ms;
  uint16_t    pausaGiro_ms;
  uint8_t     numEnjuagues;
  uint32_t    tiempoEnjuague_ms;
  uint32_t    tiempoCentrifugado_ms;
  bool        agitacionFuerte;
  NivelAgua   nivelAguaDefault;
  uint8_t     maxCargaKg;
  bool        requiereRopa;
  uint32_t    pausaReuso_ms;
};

const ProgramaLavado prog_coloridas = {
  .nombre              = "Coloridas",
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 900000,
  .tiempoGiro_ms       = 4000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 180000,
  .tiempoCentrifugado_ms = 360000,
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_ALTO,
  .maxCargaKg          = 15,
  .requiereRopa        = true,
  .pausaReuso_ms       = 0
};
```

> **Nota final:** Este documento prioriza las especificaciones del PDF oficial de Consul.

---

### Parametros medibles por programa (para firmware ESP32)

| # | Parametro | Como medir | Variable sugerida |
| --- | --- | --- | --- |
| 1 | Tiempo de remojo | Desde que llena hasta que agita | tiempoRemojo_ms |
| 2 | Tiempo de lavado | Desde que agita hasta que detiene | tiempoLavado_ms |
| 3 | Giro por direccion | Segundos girando hacia un lado | tiempoGiro_ms |
| 4 | Pausa entre giros | Segundos quieto entre cambios | pausaGiro_ms |
| 5 | Cantidad de enjuagues | Veces que vuelve a llenar | numEnjuagues |
| 6 | Tiempo de enjuague | Agitacion durante cada enjuague | tiempoEnjuague_ms |
| 7 | Tiempo de centrifugado | Giro rapido hasta detenerse | tiempoCentrifugado_ms |
| 8 | Tipo de agitacion | Fuerte o suave | agitacionFuerte_bool |

> **Programas prioritarios:** Coloridas (51 min), Rapido (29 min), Cama y Bano (96 min), Limpieza Pesada (124 min).

---

## 10. Opciones de Panel con ESP32

### Opcion A: Reutilizar botones originales
- Mantener botones tactiles y encoder originales conectados a GPIOs del ESP32.
- Reemplazar display original por LCD I2C 16x2 o OLED.

### Opcion B: Reutilizar flat cable original
- Identificar cada pin del cable plano. Mapear funciones (requiere ingenieria inversa).

### Opcion C: Panel nuevo
- Construir panel con encoder KY-040 + LCD + botones independientes.
- Mayor flexibilidad pero requiere fabricacion de soporte/frente.

---

## 11. Garantia y Servicio Tecnico

- Garantia total: 12 meses (3 legales + 9 del fabricante).
- SAC Brasil: 3003-0777 (capitales) / 0800-970-0777 (interior).
- Web: www.consul.com.br/atendimento
- Fabricante: Whirlpool S.A. - Unidad Electrodomesticos.
- Codigo documento: W10635052 - Rev. C (16/02/2016).
- Solo servicio tecnico autorizado puede abrir/reparar sin perder garantia.

---

*Documento generado el 31 de julio de 2026. Fusiona datos del PDF oficial (Guia Rapida Consul CWH15AB) con especificaciones tecnicas para implementacion con ESP32.*



---

## 4. NIVELES DE AGUA

| Nivel | Barras en display | Volumen aprox. | Uso recomendado |
| --- | --- | --- | --- |
| 1 | 1 barra | ~80 litros | Pocas prendas ligeras, ciclo rapido |
| 2 | 2 barras | ~120 litros | Carga media, ropa delicada |
| 3 | 3 barras | ~155 litros | Carga normal / completa |
| 4 | 4 barras | ~186 litros | Edredon, sabanas, ropa pesada voluminosa |

### Regla de Nivel Facil

Dentro del cesto hay una **regla marcada** visible al abrir la tapa. Indica visualmente la altura que alcanzan las ropas y permite verificar si el nivel de agua seleccionado es adecuado.

---

## 5. NIVELES DE SUCIEDAD

| Nivel | Descripcion | Comportamiento del agitador |
| --- | --- | --- |
| **Pouco** (Poco) | Ropa usada 1 vez, sin manchas (ej. con sudor) | Agitacion mas lenta. Pausas largas. Cuidado especial. |
| **Sujas** (Sucias) | Ropa usada mas de 1 vez, sin manchas | Movimiento normal. Balance estandar. |
| **Muito** (Muy sucias) | Ropa usada mucho tiempo o con manchas (ej. ropa de cama) | Mayor movimiento. Agitacion intensa. |

---

## 6. TIPOS DE ENJUAGUE

| Modo | Descripcion |
| --- | --- |
| **Unico** | 1 enjuague |
| **Duplo** | 2 enjuagues |
| **Unico + Eco** | 1 enjuague con 10% menos de agua |
| **Duplo + Eco** | 2 enjuagues con 10% menos de agua |

> Los programas tienen enjuagues predefinidos, pero el usuario puede aumentar, reducir o cambiar el tipo antes de iniciar.

---

## 7. USO DEL DISPENSER "LIMPA FACIL"

Dispensador dual fijo con 2 compartimentos que distribuyen productos automaticamente durante el ciclo.

### Compartimento A - Jabon en Polvo

- Usar el **vaso dosificador** incluido.
- La cantidad depende del **nivel de agua** y del **nivel de suciedad** seleccionados.
- Solo jabon en polvo y/o blanqueador en polvo.
- **Cantidad maxima:** 240 ml (aprox. 170 g).
- **Nunca** verter jabon directamente sobre la ropa.
- Para jabon liquido, seguir recomendacion del fabricante del jabon.

### Compartimento B - Suavizante

- Uso **opcional**.
- Si es muy espeso, diluir con un poco de agua antes de usar.
- **No exceder el nivel maximo (MAX)**. El sifon podria dispensar antes de tiempo y manchar la ropa.
- El nivel maximo esta calibrado para **nivel 4 de agua**; reducir para otros niveles.
- **No usar suavizante** en el ciclo "Panos de Limpieza".

### Tira Manchas

- **Liquido:** Verter en el recipiente indicado en el contorno del cesto (usar recipiente con pico).
- **En polvo:** Usar el compartimento de jabon (A).
- **Agua sanitaria (blanqueador con cloro):** Solo para ropa blanca. Para colores, usar tira manchas sin cloro.

---

## 8. SECUENCIA DE OPERACION (uso normal)

1. Enchufar (verificar voltaje correcto: 127 V o 220 V).
2. Abrir la llave de paso de agua fria.
3. Colocar la ropa en el cesto (respetar limite de 15 kg).
4. Agregar jabon en el compartimento A (y suavizante en B si se desea).
5. Cerrar la tapa.
6. Presionar el boton de encendido.
7. Girar el selector para elegir el programa.
8. Ajustar nivel de agua, suciedad y enjuague si es necesario.
9. Presionar **INICIAR**.
10. Esperar a que termine (display muestra tiempo restante -> "LISTO").
11. Abrir la tapa y retirar la ropa.

### Pausar durante el ciclo

- Presionar **Iniciar/Desligar**.
- La traba de la tapa se libera despues de unos segundos.
- Se puede agregar o sacar prendas.
- Cerrar la tapa y presionar Iniciar para continuar.
- **No se puede pausar durante el centrifugado** por seguridad.

### Reutilizacion de agua (Lavagem Eco)

- Durante el lavado, la luz de la etapa de lavado parpadeara indicando que el agua esta lista para reutilizar.
- El usuario saca la manguera de salida del desague y la dirige a un balde.
- Si no se reutiliza, el agua se drenara automaticamente despues de **35 minutos** y el ciclo continuara normalmente.
- Para cancelar el reuso: presionar **2 veces** el boton "Avancar Etapas".

---

## 9. INSTALACION

### Requisitos electricos

| Voltaje | Disyuntor | Seccion cable | Distancia maxima |
| --- | --- | --- | --- |
| 127 V | Exclusivo | 2,5 mm2 | Hasta 29 m |
| 127 V | Exclusivo | 4,0 mm2 | 30 a 48 m |
| 220 V | Exclusivo | 2,5 mm2 | Hasta 70 m |
| 220 V | Exclusivo | 4,0 mm2 | 71 a 116 m |

**Obligatorio:**

- Toma con tierra (3 patas).
- Circuito electrico exclusivo (no compartir con otros aparatos).
- NO usar adaptadores, zapatillas, extensiones ni "T".
- Si el cable esta danado, solo el servicio autorizado puede cambiarlo.

### Requisitos de agua

- Canilla exclusiva con rosca de 3/4 pulgada.
- Presion: 20 a 800 kPa (2 a 80 m de columna).
- Solo agua fria (5C a 30C).
- NO usar agua caliente ni de calefaccion central.
- NO usar cinta teflon / veda-rosca en las conexiones de manguera.

### Manguera de entrada

- Roscar en la canilla; apretar lo suficiente para que no gotee.
- Si gotea, reapretar (no usar teflon).
- Usar SIEMPRE las mangueras nuevas del equipo.

### Manguera de salida (desague)

- La punta debe estar entre **0,85 m y 1,20 m** de altura.
- Por debajo de 0,85 m: no completa el nivel de agua.
- Por encima de 1,20 m: no logra evacuar el agua.
- Diametro minimo del cano de desague: 5 cm.
- NO soltar la manguera de la abrazadera fijada al gabinete.
- Si no alcanza: pedir manguera de 2,30 m al servicio autorizado.

### Posicionamiento

- Superficie plana y nivelada.
- Minimo 10 cm separada de paredes u otros muebles (por todos los lados).
- Los 4 pies deben estar apoyados en el piso.
- Para nivelar: girar pies a la derecha = sube, izquierda = baja.
- NO instalar sobre alfombra, telgopor / isopor.
- NO exponer a sol directo ni lluvia.
- NO instalar cerca de fuentes de calor.

---

## 10. FUNCIONES Y SISTEMAS ESPECIALES

### Spray de agua

Durante el llenado, un chorro de agua se activa para mojar mejor la ropa, mejorando el cuidado de los tejidos. Al finalizar el llenado, el spray puede seguir goteando unos segundos para vaciar el sistema; esto es normal.

### Sistema Anti-Desbalanceo

- Identifica desbalanceo excesivo durante la centrifugacion.
- Si ocurre: realiza un nuevo llenado y agitacion para reacomodar la ropa.
- Si persiste: **interrumpe la centrifugacion**.
- Solucion: presionar Iniciar/Desligar, abrir la tapa, redistribuir la ropa uniformemente, cerrar y avanzar a la etapa de centrifugacion.

### Centrifugado extra ("Mas Secas")

- Agrega aproximadamente 5 minutos mas de centrifugado al final del ciclo.
- La ropa sale con menos humedad.
- Se activa antes de iniciar el ciclo.

### Autolimpieza

- Ciclo especial (programa 16) para limpiar el interior de la maquina.
- Elimina residuos acumulados, moho y malos olores.
- Ejecutar 1 vez por mes **SIN ropa**, con 1/2 litro de blanqueador en el cesto.
- Alternativa: ciclo vacio con un poco de lavandina diluida.

### Dosificacion Economica

- Sistema que promete ahorro de hasta 70% de jabon.
- Incluye vaso medidor exclusivo (copo dosador).
- Medir cantidad exacta segun la carga.
- El exceso de jabon NO lava mejor; causa espuma excesiva y residuos.

---

## 11. MANTENIMIENTO Y LIMPIEZA

### Filtro de pelusas

- Ubicacion: parte superior del agitador central.
- Limpiar despues de cada lavado (recomendado).
- Lavar con agua corriente.
- Volver a colocar antes del siguiente uso.

### Limpieza del cesto / tambor

- Ejecutar ciclo de Autolimpieza 1 vez por mes.
- Secar con un pano al terminar.
- Dejar la tapa abierta un rato para ventilar y evitar moho.

### Limpieza del dispenser

- Retirar la moldura de los compartimentos y lavar con agua corriente.
- Limpiar el interior con esponja.
- Retirar el sifon del compartimento de suavizante, lavarlo y recolocarlo.
- Es normal que quede algo de agua acumulada en el dispenser al final del ciclo (no afecta la vida util).

### Limpieza del gabinete (exterior)

- Limpiar con pano humedo y detergente neutro.
- NO usar productos abrasivos, virulana / esponja de acero ni solventes.
- NO echar agua directamente sobre el panel de control.

---

## 12. DIAGNOSTICO DE PROBLEMAS

| Problema | Causa probable | Solucion |
| --- | --- | --- |
| No enciende | Sin energia, enchufe flojo, disyuntor cortado | Verificar toma, disyuntor, enchufe |
| No llena de agua | Canilla cerrada, manguera doblada u obstruida | Abrir canilla, revisar manguera |
| No centrifuga | Tapa abierta, carga desbalanceada | Cerrar tapa, redistribuir ropa |
| Pierde agua | Mangueras mal conectadas, abrazadera suelta | Reapretar conexiones |
| Vibra mucho | Mal nivelada, carga desbalanceada, piso irregular | Nivelar pies, redistribuir ropa |
| Ropa queda sucia | Programa inadecuado, exceso de ropa, poco jabon | Usar programa correcto, menos carga |
| Mucha espuma | Exceso de jabon | Reducir cantidad (usar dosificador) |
| No drena / desagota | Manguera de salida obstruida o muy alta (>1,20 m) | Desobstruir, verificar altura |
| Manchas en la ropa | Contacto directo con jabon/suavizante sin diluir | Usar dispenser correctamente |
| Se detiene a mitad | Tapa se abrio, falta presion de agua, corte electrico | Verificar tapa, canilla, disyuntor |
| Ruido fuerte | Objeto metalico en cesto, carga desequilibrada | Revisar bolsillos, redistribuir |

---

## 13. DATOS TECNICOS PARA PROYECTO ESP32

### Actuadores controlados por la placa electronica

| Componente | Tipo de carga | Voltaje | Corriente estimada |
| --- | --- | --- | --- |
| Valvula solenoide (entrada de agua) | AC | 127/220 V | ~300 mA |
| Motor de agitacion (bidireccional) | AC | 127/220 V | 2-3 A |
| Motor de centrifugado | AC | 127/220 V | 3-4 A |
| Bomba de drenaje | AC | 127/220 V | ~500 mA |
| Traba de tapa (electroiman) | DC o AC | 12-24 V | ~200 mA |

**Nota sobre el motor:** En muchos modelos Consul, el motor de agitacion y centrifugado es el **mismo motor fisico**, pero con diferentes conexiones electricas (bobinados). La transmision mecanica cambia el modo:

- **Agitacion:** motor gira lento, transmision convierte en vaiven.
- **Centrifugado:** motor gira rapido, transmision conecta directo al cesto.

Esto implica que podrian necesitarse solo 3 reles para el motor:

- Comun
- Bobinado agitacion direccion A (1 rele)
- Bobinado agitacion direccion B (1 rele)
- Bobinado centrifugado (1 rele)

### Sensores que lee la placa

| Sensor | Tipo fisico | Senal electrica | Comportamiento |
| --- | --- | --- | --- |
| Presostato (nivel de agua) | Switch de presion | Digital NO/NC | Se cierra al alcanzar el nivel |
| Microswitch de tapa | Mecanico | Digital NO | Se cierra cuando la tapa esta cerrada |

**Sobre el presostato:** Es un sensor de presion de aire conectado al fondo del tanque mediante una manguerita. A medida que sube el agua, aumenta la presion de aire y el switch cambia de estado. Puede tener 1 o 2 niveles de conmutacion segun el modelo.

### Conectores de la placa original (genericos)

| Conector | Cables | Funcion |
| --- | --- | --- |
| CN1 | 3 cables | Alimentacion AC (Fase, Neutro, Tierra) |
| CN2 | 4-5 cables | Motor (Comun, Dir A, Dir B, Centrifuga) |
| CN3 | 4 cables | Valvula de agua + Bomba de drenaje |
| CN4 | Flat cable | Panel completo (botones + display) |
| CN5 | 2-3 cables | Sensores (presostato + switch de tapa) |
| CN6 | 2 cables | Traba de tapa (electroiman) |

> **IMPORTANTE:** Antes de desconectar la placa original, **FOTOGRAFIAR** cada conector con su color de cable y posicion. Anotar que funcion cumple cada uno midiendo con multimetro.

### Secuencia interna de operacion (logica de firmware)

```
1. Usuario selecciona programa y presiona INICIAR
2. Traba la tapa (activa electroiman)
3. Abre valvula solenoide -> llena hasta que el presostato corta
4. Cierra valvula
5. Inicia agitacion:
   - Motor gira DIRECCION A por X segundos
   - PAUSA de Y segundos (OBLIGATORIA - protege transmision)
   - Motor gira DIRECCION B por X segundos
   - PAUSA de Y segundos
   - Repite hasta completar tiempo total de lavado
6. Detiene el motor
7. Enciende bomba de drenaje -> drena durante ~90 segundos
8. Apaga bomba
9. SI hay enjuagues pendientes: vuelve al paso 3
   (repite llenado + agitacion suave + drenaje por cada enjuague)
10. Enciende bomba de drenaje + motor en modo centrifugado
    - Si se abre la tapa: PARA TODO INMEDIATAMENTE
11. Tras el tiempo de centrifugado: apaga todo
12. Destraba la tapa (desactiva electroiman)
13. Muestra "LISTO" en display / emite senal sonora
```

### Protecciones de seguridad (REPLICAR en ESP32)

1. **Tapa abierta durante centrifugado** -> PARAR motor de inmediato.
2. **Timeout de llenado** (15 minutos) -> ERROR, apagar todo, destrabar tapa.
3. **NUNCA cambiar direccion del motor sin pausa** -> Protege motor y transmision.
4. **Verificar tapa cerrada antes de iniciar** -> NO arrancar si esta abierta.
5. **Corte de energia** -> Al volver, ir a estado APAGADO (no retomar ciclo).
6. **Sobrecarga del motor** -> Si se bloquea, debe cortarse (fusible / proteccion termica).

### Tiempos tipicos de cada etapa (aproximados - MEDIR con placa original)

| Etapa | Tiempo tipico | Notas |
| --- | --- | --- |
| Llenado (nivel alto) | 5-10 min | Depende de la presion de agua |
| Agitacion fuerte | 4 s giro + 2 s pausa | Patron repetitivo |
| Agitacion suave | 3 s giro + 4 s pausa | Mas pausa = mas suave |
| Drenaje | ~90 segundos | Tiempo fijo |
| Enjuague | 3-5 min agitacion suave | Depende del programa |
| Centrifugado | 3-8 min | Depende del programa |
| Centrifugado extra | +5 min | Sumado al centrifugado normal |

---

## 14. OPCIONES DE PANEL CON ESP32

### Opcion A: Reutilizar botones originales

- Mantener los botones tactiles y el encoder originales.
- Conectarlos a GPIOs del ESP32.
- Reemplazar el display original por un LCD I2C 16x2 o OLED.

### Opcion B: Reutilizar flat cable original

- Identificar cada pin del cable plano que va al panel.
- Mapear funciones y conectar al ESP32 (requiere ingenieria inversa).

### Opcion C: Panel nuevo

- Construir panel con encoder KY-040 + LCD + botones independientes.
- Mayor flexibilidad pero requiere fabricacion de soporte/frente.

---

## 15. GARANTIA Y SERVICIO TECNICO

- Garantia total: 12 meses (3 legales + 9 del fabricante).
- SAC Brasil: 3003-0777 (capitales) / 0800-970-0777 (interior).
- Web: www.consul.com.br/atendimento
- Fabricante: Whirlpool S.A. - Unidad Electrodomesticos.
- Codigo documento: W10635052 - Rev. C (16/02/2016).
- Solo servicio tecnico autorizado puede abrir/reparar sin perder garantia.

---

*Documento generado el 31 de julio de 2026. Fusiona datos del PDF oficial (Guia Rapida Consul CWH15AB) con especificaciones tecnicas recopiladas para implementacion con ESP32.*
