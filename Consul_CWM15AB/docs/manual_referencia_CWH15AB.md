# Manual de Referencia - Consul CWH15AB (15kg)

> Este documento contiene TODA la informacion relevante extraida del
> PDF oficial (Guia Rapido) y fichas tecnicas del modelo CWH15AB.
> Sirve como referencia completa para el proyecto ESP32 sin necesidad
> de consultar el PDF original nuevamente.

## Fuente Original

- PDF Guia Rapido: https://whirlpool.vteximg.com.br/arquivos/Consul_Lavadora_CWH15AB_Guia_Rapido_Versão_Digital_1.pdf
- PDF Taqi: https://www.taqi.com.br/file/general/maquina-de-lavar-consul-com-modo-eco-15kg-branca-220-volts.pdf
- Ficha Buscape: https://www.buscape.com.br/lavadora-roupas/lavadora-consul-15kg-cwh15ab/
- Ficha Zoom: https://www.zoom.com.br/lavadora-roupas/lavadora-consul-15kg-cwh15ab/

---

## 1. IDENTIFICACION DEL PRODUCTO

| Dato | Valor |
|------|-------|
| Marca | Consul (Whirlpool S.A.) |
| Modelo | CWH15AB |
| Tipo | Lavadora automatica de ropa |
| Capacidad | 15 kg de ropa seca |
| Color | Blanco |
| Voltaje | 127V o 220V (NO es bivolt, hay que elegir) |
| Potencia | 620W |
| Consumo energetico | 0.46 kWh por ciclo |
| Sello Procel | A (Mas Economico) |
| Consumo agua por ciclo | ~186 litros |
| Peso del equipo | 38 kg |
| Dimensiones (Alto x Ancho x Prof) | 100 x 63 x 70 cm |
| Apertura | Tapa superior (top load) |
| Cesto/tambor | Acero inoxidable con base plastica |
| Tipo de lavado | Agitador central |
| Velocidad centrifugado | ~750 rpm |
| Dispenser | Dual (jabon + suavizante) |


---

## 2. PANEL DE CONTROL (datos del PDF real)

### Controles del Panel
1. **Selector de Programa (giratorio)** - Selecciona entre los programas
2. **Nivel de Agua** - 4 niveles (1 a 4, segun regla interna del cesto)
3. **Nivel de Suciedad** - 3 opciones:
   - Poco: ropa usada 1 vez sin manchas -> agitacion LENTA
   - Sucias: ropa usada varias veces sin manchas -> agitacion NORMAL
   - Muy sucias: ropa con manchas o uso prolongado -> agitacion RAPIDA
4. **Tipo de Enjuague** - 4 opciones:
   - Unico: 1 enjuague normal
   - Doble: 2 enjuagues normales
   - Unico + Eco: 1 enjuague con 10% menos agua
   - Doble + Eco: 2 enjuagues con 10% menos agua
5. **Iniciar/Apagar** - Inicia ciclo o apaga la maquina
6. **Avanzar Etapas** - Salta a la siguiente etapa del ciclo

### Indicadores LED de Etapa
- Molho (remojo) - se enciende cuando esta en remojo
- Lavagem (lavado) - se enciende durante agitacion
- Enxague (enjuague) - se enciende durante enjuague
- Centrifugacao (centrifugado) - se enciende durante centrifugado
- Parpadeo de Lavagem = reutilizacion de agua disponible

---

## 3. LOS PROGRAMAS DE LAVADO (segun PDF)

### Lista completa con tiempos oficiales

| # | Programa | Etapas | Tiempo Total |
|---|---------|--------|-------------|
| 1 | Cama y Bano | Molho+Lavagem+Enxague+Centrif | 1h 36min |
| 2 | Edredon | Molho+Lavagem+Enxague+Centrif | 1h 33min |
| 3 | Limpieza Pesada | Molho+Lavagem+Enxague+Centrif | 2h 04min |
| 4 | Panos de Limpieza | Lavagem+Enxague+Centrif | 2h 27min |
| 5 | Tira Olores | Lavagem+Enxague+Centrif | 0h 36min |
| 6 | Rapido/Economico | Lavagem+Enxague+Centrif | 0h 29min |
| 7 | Lavagem Eco | Lavagem+Enxague+Centrif | 0h 46min |
| 8 | Delicados | Lavagem+Enxague+Centrif | (medir) |
| 9 | Ropa de Bebe | Molho+Lavagem+Enxague+Centrif | 2h 20min |
| 10 | Ropa Intima | Lavagem+Enxague+Centrif | 1h 03min |
| 11 | Blancas | Molho+Lavagem+Enxague+Centrif | 1h 42min |
| 12 | Coloridas | Lavagem+Enxague+Centrif | 0h 51min |
| 13 | Escuras (oscuras) | Lavagem+Enxague+Centrif | 0h 43min |
| 14 | Dia a Dia | Lavagem+Enxague+Centrif | (medir) |
| 15 | Jeans | Molho+Lavagem+Enxague+Centrif | 1h 21min |
| 16 | Uniforme | Molho+Lavagem+Enxague+Centrif | 1h 55min |
| * | Limpieza Lavadora | Lavagem+Enxague+Centrif | 0h 54min |

### Notas:
- **Edredon**: SOLO tamano matrimonial. Nivel 4, jabon "muy sucias"
- **Panos de Limpieza**: Max 2kg. NO suavizante
- **Limpieza Lavadora**: SIN ropa. 1/2L lavandina al cesto. Mensual.
- **Lavagem Eco**: Pausa para reusar agua. Drena sola en 35 min.

---

### QUE MEDIR CON CRONOMETRO (8 datos por programa)

| # | Dato | Como medirlo | Variable codigo |
|---|------|-------------|----------------|
| 1 | Remojo | Llena -> agita (solo Molho) | tiempoMolho |
| 2 | Lavado | Agita -> para drenar | tiempoLavado |
| 3 | Giro/dir | Seg girando un lado | tiempoAgitacion |
| 4 | Pausa | Seg quieto entre giros | pausaAgitacion |
| 5 | Enjuagues | Veces que llena post-lavado | numEnjuagues |
| 6 | T. enjuague | Agitacion enjuague | tiempoEnjuague |
| 7 | Centrifugado | Giro rapido -> para | tiempoCentrifugado |
| 8 | Tipo agit. | Fuerte/suave | agitacionFuerte |

### IMPORTANTE: El nivel de suciedad cambia la agitacion
- **Poco** = agitacion lenta (MAS pausa entre giros)
- **Sucias** = agitacion normal
- **Muy sucias** = agitacion rapida (MENOS pausa entre giros)

Medir los 3 patrones con el mismo programa cambiando solo suciedad.

### Programas prioritarios: Coloridas (51min), Rapido (29min), Cama e Banho (96min)

---

## 3B. FUNCIONES ESPECIALES (del PDF)

### Reutilizacion de Agua (Lavagem Eco)
- La maquina PAUSA despues del lavado
- LED "Lavagem" parpadea = puedes reusar agua
- Si no haces nada: drena sola en 35 minutos
- Cancelar: presionar 2x "Avanzar Etapas"

### Spray de Agua
- Chorro durante llenado para mojar ropa por arriba
- Puede gotear unos segundos al terminar (normal)

### Anti-Desbalanceo
- Si desbalancea en centrifugado: llena y agita para redistribuir
- Si persiste: se detiene. Redistribuir manual + "Avanzar Etapas"

### Si abres la tapa durante ciclo
- Al cerrar: presionar Iniciar/Apagar para continuar

---

## 3C. DISPENSADOR "LIMPA FACIL"

### Compartimento A - Jabon en polvo
- Usar vaso dosificador incluido
- Cantidad depende de: nivel agua + nivel suciedad
- Max: 240 ml (~170 g). NUNCA directo sobre ropa.

### Compartimento B - Suavizante (opcional)
- Si espeso: diluir. NO exceder MAX. NO en "Panos de Limpieza"

### Tira Manchas
- Liquido: recipiente en borde del cesto
- En polvo: compartimento jabon
- Lavandina: SOLO ropa blanca

## 4. NIVELES DE AGUA

| Nivel | Indicacion en display | Volumen aprox. | Cuando usar |
|-------|----------------------|----------------|-------------|
| Bajo | 1 barra | ~80 litros | Pocas prendas livianas, ciclo rapido |
| Medio | 2 barras | ~120 litros | Carga media, ropa delicada, zapatillas |
| Alto | 3 barras | ~155 litros | Carga normal/completa |
| Extra | 4 barras | ~186 litros | Edredon, sabanas, ropa pesada voluminosa |

### Regla de Nivel Facil
La lavadora tiene una regla marcada DENTRO del cesto (visible al abrir
la tapa) que indica visualmente cuanta agua corresponde a la cantidad
de ropa colocada. Es una guia visual para saber si el nivel seleccionado
es adecuado.

---

## 5. FUNCIONES ESPECIALES

### 5.1 Mas Secas (centrifugado extra)
- Agrega 5 minutos mas de centrifugado al final del ciclo
- La ropa sale con menos humedad
- Menos tiempo colgada en el tendedero
- Se activa/desactiva con el boton ANTES de iniciar el ciclo
- Se puede usar con cualquier programa

### 5.2 Lavado Eco (Reusar Agua)
- Permite reutilizar el agua del lavado para otros usos
- Al activar, despues del lavado el agua se puede dirigir a un
  balde o tanque en vez de ir al desague
- Ahorra agua significativamente
- Nota: el agua de enjuague NO se reutiliza (solo la de lavado)

### 5.3 Dual Dispenser (dispensador doble)
- Dos compartimentos separados:
  - Compartimento grande: jabon en polvo o liquido
  - Compartimento pequeno: suavizante/acondicionador
- El dispenser mezcla los productos con agua ANTES de tocar la ropa
- Evita manchas causadas por contacto directo jabon-tela
- Evita residuos de jabon sin disolver

### 5.4 Dosificacion Economica
- Sistema que promete ahorro de hasta 70% de jabon
- Incluye vaso medidor exclusivo (copo dosador)
- Medir la cantidad exacta segun la carga para no desperdiciar
- El exceso de jabon NO lava mejor, causa espuma excesiva y residuos

### 5.5 Autolimpieza
- Ciclo especial para limpiar el interior de la maquina
- Elimina residuos acumulados, moho y malos olores del cesto
- Ejecutar 1 vez por mes (recomendacion del fabricante)
- Se ejecuta SIN ropa, solo con agua y un poco de lavandina

---

## 6. COMO SE USA - SECUENCIA DE OPERACION

### Paso a paso para lavar:
1. Enchufar (verificar que el voltaje sea el correcto: 127V o 220V)
2. Abrir la canilla/grifo de entrada de agua
3. Poner la ropa en el cesto (respetar limite 15kg)
4. Agregar jabon en el dispenser (compartimento grande)
5. Agregar suavizante en el dispenser (compartimento chico, opcional)
6. Cerrar la tapa
7. Presionar boton Encendido
8. Girar el boton para elegir el programa deseado
9. Seleccionar nivel de agua (o dejar el default del programa)
10. Activar "Mas Secas" si se desea (opcional)
11. Presionar INICIAR
12. Esperar a que termine (el display muestra "LISTO")
13. Abrir la tapa y retirar la ropa

### Como pausar durante el ciclo:
- Presionar Iniciar/Pausar
- La traba de la tapa se libera despues de unos segundos
- Se puede agregar o sacar prendas
- Cerrar la tapa y presionar Iniciar para continuar
- NOTA: No se puede pausar durante el centrifugado por seguridad

---

## 7. INSTALACION

### Requisitos Electricos

| Voltaje | Disyuntor | Seccion cable | Distancia maxima |
|---------|-----------|---------------|------------------|
| 127V | Exclusivo | 2.5 mm² | hasta 29 metros |
| 127V | Exclusivo | 4.0 mm² | 30 a 48 metros |
| 220V | Exclusivo | 2.5 mm² | hasta 70 metros |
| 220V | Exclusivo | 4.0 mm² | 71 a 116 metros |

**Obligatorio:**
- Toma/enchufe con tierra (3 patas)
- Circuito electrico exclusivo (no compartir con otros aparatos)
- NO usar adaptadores, zapatillas, extensiones ni "T"
- Si el cable esta danado, SOLO puede cambiarlo servicio autorizado

### Requisitos de Agua
- Canilla/grifo exclusivo con rosca de 3/4 pulgada
- Presion de agua: 20 a 800 kPa (equivale a 2 a 80 metros de columna)
- Solo agua fria (temperatura ambiente: 5°C a 30°C)
- NO usar agua caliente ni de calefaccion central
- NO usar cinta teflon/veda-rosca en las conexiones de manguera

### Manguera de Entrada
- Roscar en la canilla, apretar lo suficiente para que no gotee
- Si gotea, reapretar (no usar teflon)
- Los conjuntos de manguera nuevos del equipo DEBEN usarse
  (no reutilizar mangueras viejas de otra lavadora)

### Manguera de Salida (desague)
- La punta debe estar entre 0.85m y 1.20m de altura
- Si esta por debajo de 0.85m: la lavadora no completa el nivel de agua
- Si esta por encima de 1.20m: la lavadora no logra evacuar el agua
- Diametro minimo del cano de desague: 5 cm
- NO soltar la manguera de la abrazadera fijada al gabinete
- Si el largo no alcanza: pedir manguera de 2.30m al servicio autorizado

### Posicionamiento
- Superficie plana y nivelada
- Minimo 10 cm separada de paredes u otros muebles (por todos los lados)
- Los 4 pies deben estar apoyados en el piso
- Para nivelar: girar pies a la derecha = sube, izquierda = baja
- Verificar nivelado: apoyar manos en los costados y balancear
- Si se balancea, no esta bien nivelada, ajustar pies
- NO instalar sobre alfombra, carpeta o telgopor/isopor
- NO exponer a sol directo ni lluvia
- NO instalar cerca de fuentes de calor (estufa, parrilla)
- NO poner velas ni objetos con llama encima

---

## 8. MANTENIMIENTO Y LIMPIEZA

### Filtro de Pelusas
- Ubicacion: en la parte superior del agitador central
- Sacar y limpiar despues de cada lavado (recomendado)
- Lavar con agua corriente para sacar las pelusas acumuladas
- Volver a colocar antes del siguiente uso

### Limpieza del Cesto/Tambor
- Ejecutar ciclo de Autolimpieza 1 vez por mes
- Alternativa: ciclo vacio con un poco de lavandina diluida
- Secar con un pano al terminar
- Dejar la tapa abierta un rato para que ventile y no se forme moho

### Limpieza del Dispenser
- Sacarlo y lavarlo con agua corriente periodicamente
- Evitar que se acumule jabon solidificado/endurecido
- Si esta muy obstruido, dejar en remojo con agua tibia

### Limpieza del Gabinete (exterior)
- Limpiar con pano humedo y detergente neutro
- NO usar productos abrasivos, virulana/esponja de acero ni solventes
- NO echar agua directamente sobre el panel de control

---

## 9. DIAGNOSTICO DE PROBLEMAS

| Problema | Causa probable | Solucion |
|----------|---------------|----------|
| No enciende | Sin energia, enchufe flojo, disyuntor cortado | Verificar toma, disyuntor, enchufe |
| No llena de agua | Canilla cerrada, manguera doblada u obstruida | Abrir canilla, revisar manguera |
| No centrifuga | Tapa abierta, carga desbalanceada | Cerrar tapa, redistribuir ropa |
| Pierde agua | Mangueras mal conectadas, abrazadera suelta | Reapretar conexiones |
| Vibra mucho | Mal nivelada, carga desbalanceada, piso irregular | Nivelar pies, redistribuir ropa |
| Ropa queda sucia | Programa inadecuado, exceso de ropa, poco jabon | Usar programa correcto, menos carga |
| Mucha espuma | Exceso de jabon | Reducir cantidad (usar dosificador) |
| No drena/desagota | Manguera salida obstruida o muy alta (>1.20m) | Desobstruir, verificar altura |
| Manchas en la ropa | Contacto directo con jabon/suavizante sin diluir | Usar dispenser correctamente |
| Se detiene a mitad | Tapa se abrio, falta presion agua, corte electrico | Verificar tapa, canilla, disyuntor |
| Ruido fuerte | Objeto metalico en cesto, carga desequilibrada | Revisar bolsillos, redistribuir |

---

## 10. DATOS TECNICOS PARA EL PROYECTO ESP32

### Actuadores que controla la placa electronica

| Componente | Tipo de carga | Voltaje | Corriente estimada |
|-----------|---------------|---------|-------------------|
| Valvula solenoide (entrada agua) | AC | 127/220V | ~300mA |
| Motor de agitacion (bidireccional) | AC | 127/220V | 2-3A |
| Motor de centrifugado | AC | 127/220V | 3-4A |
| Bomba de drenaje | AC | 127/220V | ~500mA |
| Traba de tapa (electroiman) | DC o AC | 12-24V | ~200mA |

**Nota sobre el motor:** En muchos modelos Consul, el motor de agitacion
y centrifugado es el MISMO motor fisico, pero con diferentes conexiones
electricas (bobinados). La transmision mecanica cambia el modo:
- Agitacion: motor gira lento, transmision convierte en vaiven
- Centrifugado: motor gira rapido, transmision conecta directo al cesto

Esto significa que podrian ser solo 3 reles para el motor:
- Comun
- Bobinado agitacion (2 direcciones = 2 reles)
- Bobinado centrifugado (1 rele)

### Sensores que lee la placa

| Sensor | Tipo fisico | Senal electrica | Comportamiento |
|--------|-------------|-----------------|----------------|
| Presostato (nivel agua) | Switch de presion | Digital NO/NC | Se cierra al alcanzar nivel |
| Microswitch de tapa | Mecanico | Digital NO | Se cierra cuando tapa esta cerrada |

**Sobre el presostato:** Es un sensor de presion de aire conectado al
fondo del tanque mediante una manguerita. A medida que sube el agua,
aumenta la presion de aire y el switch cambia de estado. Puede tener
1 o 2 niveles de conmutacion dependiendo del modelo.

### Conectores de la placa original (genericos)

| Conector | Cables | Funcion |
|----------|--------|---------|
| CN1 | 3 cables | Alimentacion AC (Fase, Neutro, Tierra) |
| CN2 | 4-5 cables | Motor (Comun, Dir A, Dir B, Centrifuga) |
| CN3 | 4 cables | Valvula agua + Bomba drenaje |
| CN4 | Flat cable | Panel completo (botones + display) |
| CN5 | 2-3 cables | Sensores (presostato + switch tapa) |
| CN6 | 2 cables | Traba de tapa (electroiman) |

> **IMPORTANTE:** Estos nombres (CN1-CN6) son GENERICOS. Antes de
> desconectar la placa original, FOTOGRAFIAR cada conector con su
> color de cable y posicion. Anotar que funcion cumple cada uno
> midiendo con multimetro.

### Secuencia interna de operacion (lo que hace la placa)

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
6. Para el motor
7. Enciende bomba de drenaje -> drena durante ~90 segundos
8. Apaga bomba
9. SI hay enjuagues pendientes: vuelve al paso 3
   (repite llenado + agitacion suave + drenaje por cada enjuague)
10. Enciende bomba de drenaje + motor en modo centrifugado
    - Si se abre la tapa: PARA TODO INMEDIATAMENTE
11. Tras el tiempo de centrifugado: apaga todo
12. Destraba la tapa (desactiva electroiman)
13. Muestra "LISTO" en display / emite senial sonora
```

### Protecciones de seguridad (REPLICAR en el ESP32)

1. **Tapa abierta durante centrifugado** -> PARAR motor de inmediato
2. **Timeout de llenado** (15 minutos) -> ERROR, apagar todo, destrabar
3. **NUNCA cambiar direccion sin pausa** -> Protege motor y transmision
4. **Verificar tapa antes de iniciar** -> NO arranca si esta abierta
5. **Corte de energia** -> Al volver, ir a estado APAGADO (no retomar ciclo)
6. **Sobrecarga motor** -> Si se bloquea, deberia cortarse (fusible/proteccion termica)

### Tiempos tipicos de cada etapa (APROXIMADOS - MEDIR CON PLACA ORIGINAL)

| Etapa | Tiempo tipico | Notas |
|-------|--------------|-------|
| Llenado (nivel alto) | 5-10 min | Depende de presion de agua |
| Agitacion fuerte | 4s giro + 2s pausa | Patron repetitivo |
| Agitacion suave | 3s giro + 4s pausa | Mas pausa = mas suave |
| Drenaje | 90 segundos | Tiempo fijo |
| Enjuague | 3-5 min agitacion suave | Depende del programa |
| Centrifugado | 3-8 min | Depende del programa |
| Centrifugado extra (Mas Secas) | +5 min | Sumado al centrifugado normal |

---

## 11. GARANTIA Y SERVICIO TECNICO

- Garantia total: 12 meses (3 legales + 9 del fabricante)
- SAC Brasil: 3003-0777 (capitales) / 0800-970-0777 (interior)
- Web: www.consul.com.br/atendimento
- Fabricante: Whirlpool S.A. - Unidad Electrodomesticos
- Codigo documento: W10635052 - Rev. C (16/02/2016)
- Solo servicio tecnico autorizado puede abrir/reparar sin perder garantia

---

## 12. NOTAS ADICIONALES PARA EL PROYECTO

### Sobre el panel original vs. la replica con ESP32
El panel original usa un flat cable (cable plano) que conecta los
botones tactiles, el encoder y el display a la placa principal.
Para replicarlo con ESP32 se puede:
- **Opcion A:** Mantener los botones originales conectandolos a GPIOs
  del ESP32 y reemplazar el display por un LCD I2C 16x2
- **Opcion B:** Reutilizar el flat cable original e ingeniar la
  conexion (requiere identificar cada pin del flat)
- **Opcion C:** Hacer un panel nuevo con encoder KY-040 + LCD + botones

### Sobre la Lavagem Eco en el firmware
La funcion "Reusar Agua" se implementa simplemente NO activando la
bomba de drenaje al final del lavado. El usuario saca la manguera
de salida del desague y la pone en un balde. Luego presiona Inicio
para continuar con el enjuague. Es mas una logica de pausa + aviso
que un mecanismo fisico diferente.

### Sobre la Autolimpieza
Es simplemente ejecutar un ciclo de lavado VACIO (sin ropa) con
nivel de agua Alto y agitacion intensa. Se puede implementar como
un programa mas o como una combinacion de botones especial.
