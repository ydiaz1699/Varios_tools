# Profundizacion en los 16 Programas de Lavado - Consul CWH15AB

> Guia detallada de cada programa con parametros tecnicos, comportamiento
> del agitador, enjuagues y datos criticos para la implementacion en firmware ESP32.

---

## Indice de Programas

| # | Programa | Tiempo | Remojo | Para que sirve |
|---|----------|--------|:------:|----------------|
| 1 | Cama e Banho | 1h 36min | SI | Sabanas, toallas, fundas |
| 2 | Edredom | 1h 33min | SI | Edredon matrimonial |
| 3 | Limpeza Pesada | 2h 04min | SI | Ropa de trabajo muy sucia |
| 4 | Panos de Limpeza | 2h 27min | NO | Panos de limpieza (max 2kg) |
| 5 | Tira Odores | 0h 36min | NO | Eliminar olores persistentes |
| 6 | Rapido | 0h 29min | NO | Ropa poco sucia, apuro |
| 7 | Lavagem Eco | 0h 46min | NO | Reutilizar agua del lavado |
| 8 | Brancas | 1h 42min | SI | Ropa blanca, manchas dificiles |
| 9 | Coloridas | 0h 51min | NO | Ropa de color diaria |
| 10 | Escuras | 0h 43min | NO | Ropa oscura, evita decoloracion |
| 11 | Jeans | 1h 21min | SI | Denim, mezclilla |
| 12 | Uniforme | 1h 55min | SI | Uniformes de trabajo |
| 13 | Roupas Intimas | 1h 03min | NO | Ropa interior delicada |
| 14 | Roupas Leves | 1h 46min | SI | Telas finas, delicadas |
| 15 | Roupas de Bebe | 2h 20min | SI | Ropa de bebe, alergias |
| 16 | Limpeza da Lavadora | 0h 54min | NO | Autolimpieza mensual (SIN ropa) |



---

## 1. Cama e Banho - Cama y Bano

**Tiempo total:** 1h 36min (96 min)
**Nivel de agua default:** Extra (4 barras)
**Remojo:** Si
**Enjuagues:** 2 (default, modificable)

### Descripcion
Programa para prendas voluminosas de alto absorbencia: sabanas, toallas, fundas de almohada, manteles. Necesitan mucha agua para saturarse y un ciclo largo para eliminar acaros, celulas muertas y residuos.

### Comportamiento del agitador
- Agitacion: Fuerte y prolongada.
- Patron: 4s giro derecha -> 2s pausa -> 4s giro izquierda -> 2s pausa.
- Tiempo de lavado efectivo: ~25-30 min.
- Remojo: ~10 min de inmersion antes de agitar.

### Enjuague
- 2 enjuagues completos con agitacion suave (3s giro -> 3s pausa).

### Centrifugado
- Duracion: ~7 min. Velocidad: Maxima (~750 rpm).

### Notas criticas
- Usar siempre nivel Alto o Extra.
- No sobrecargar (12 kg para sabanas gruesas).
- No exceder suavizante en toallas (reduce absorbencia).

### Variables firmware
```cpp
programa_cama_banho = {
  .tiempoRemojo_ms     = 600000,   // 10 min
  .tiempoLavado_ms     = 1800000,  // 30 min
  .tiempoGiro_ms       = 4000,     // 4 s
  .pausaGiro_ms        = 2000,     // 2 s
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 420000, // 7 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_EXTRA
};
```



---

## 2. Edredom - Edredon

**Tiempo total:** 1h 33min (93 min)
**Nivel de agua default:** Extra (4 barras) - OBLIGATORIO
**Remojo:** Si
**Enjuagues:** 2

### Descripcion
Ciclo suave y largo para edredones voluminosos. Agitacion muy suave con pausas largas para que el edredon se reacomode. Se desbalancea facilmente.

### Comportamiento del agitador
- Agitacion: MUY suave. Mucha pausa, poco giro.
- Patron: 3s giro -> 5s pausa -> 3s giro -> 5s pausa.
- Tiempo de lavado efectivo: ~20 min.
- Remojo: ~12 min.

### Centrifugado
- Duracion: ~5 min. Velocidad: Moderada (~500 rpm).
- Normal que haga multiples intentos por desbalanceo.

### Notas criticas
- SOLO edredon tamano "Casal" (matrimonial). No king size.
- Nivel 4 OBLIGATORIO. Jabon nivel "muy sucias".
- Test: doble faz casal, 200 hilos, 100% algodon, relleno poliester, 2,2x2,4m o 2,8m.

### Variables firmware
```cpp
programa_edredom = {
  .tiempoRemojo_ms     = 720000,   // 12 min
  .tiempoLavado_ms     = 1200000,  // 20 min
  .tiempoGiro_ms       = 3000,     // 3 s
  .pausaGiro_ms        = 5000,     // 5 s
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 300000,   // 5 min c/u
  .tiempoCentrifugado_ms = 300000, // 5 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_EXTRA
};
```

---

## 3. Limpeza Pesada - Limpieza Pesada

**Tiempo total:** 2h 04min (124 min) - El mas largo
**Nivel de agua default:** Extra (4 barras)
**Remojo:** Si
**Enjuagues:** 2

### Descripcion
El programa mas intenso. Para ropa de trabajo, overoles, prendas con grasa, barro o manchas dificiles. Maximiza agitacion, fuerza y centrifugado.

### Comportamiento del agitador
- Agitacion: Maxima fuerza, maximo tiempo.
- Patron: 5s giro -> 1s pausa -> 5s giro -> 1s pausa.
- Tiempo de lavado efectivo: ~35-40 min.
- Remojo: ~15 min.

### Centrifugado
- Duracion: ~8 min (el mas largo). Velocidad: Maxima (~750 rpm).

### Notas criticas
- No usar para ropa delicada.
- Jabon en polvo de buena calidad.
- Pre-tratar manchas de grasa con tira manchas 10 min antes.

### Variables firmware
```cpp
programa_limpieza_pesada = {
  .tiempoRemojo_ms     = 900000,   // 15 min
  .tiempoLavado_ms     = 2400000,  // 40 min
  .tiempoGiro_ms       = 5000,     // 5 s
  .pausaGiro_ms        = 1000,     // 1 s
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 300000,   // 5 min c/u
  .tiempoCentrifugado_ms = 480000, // 8 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_EXTRA
};
```



---

## 4. Panos de Limpeza - Panos de Limpieza

**Tiempo total:** 2h 27min (147 min) - El mas largo de todos
**Nivel de agua default:** Alto (3 barras)
**Remojo:** No
**Enjuagues:** 3

### Descripcion
Para panos, trapos de piso, bayetas. Acumulan mucha suciedad y bacterias. 3 enjuagues para eliminar toda la suciedad liberada.

### Comportamiento del agitador
- Patron: 4s giro -> 2s pausa. Fuerte y continua.
- Tiempo de lavado efectivo: ~30 min. Sin remojo.

### Notas criticas
- MAX 2 kg de carga. NO usar suavizante.
- Considerar agregar blanqueador para desinfectar.

### Variables firmware
```cpp
programa_panos_limpeza = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 1800000,  // 30 min
  .tiempoGiro_ms       = 4000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 3,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 360000, // 6 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_ALTO,
  .maxCargaKg          = 2
};
```

---

## 5. Tira Odores - Quita Olores

**Tiempo total:** 0h 36min (36 min) - Corto y efectivo
**Nivel de agua default:** Alto (3 barras)
**Remojo:** No
**Enjuagues:** 3

### Descripcion
Elimina olores persistentes: humo, transpiracion, humedad, comida, moho. No quita manchas, solo "refresca". La clave son los 3 enjuagues.

### Comportamiento del agitador
- Patron: 3s giro -> 3s pausa. Moderada.
- Tiempo de lavado efectivo: ~10 min.

### Notas criticas
- Para olores fuertes: agregar 1/2 taza bicarbonato.
- Poco jabon (el objetivo es enjuagar, no espumar).
- No esperar que quite manchas visibles.

### Variables firmware
```cpp
programa_tira_odores = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 600000,   // 10 min
  .tiempoGiro_ms       = 3000,
  .pausaGiro_ms        = 3000,
  .numEnjuagues        = 3,
  .tiempoEnjuague_ms   = 120000,   // 2 min c/u
  .tiempoCentrifugado_ms = 240000, // 4 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_ALTO
};
```

---

## 6. Rapido - Rapido / Economico

**Tiempo total:** 0h 29min (29 min) - El mas corto
**Nivel de agua default:** Bajo (1 barra)
**Remojo:** No
**Enjuagues:** 1

### Descripcion
Express para ropa poco sucia. Poco agua, poco tiempo, poca energia. Para prendas usadas 1 vez, ropa de dormir, verano liviano.

### Comportamiento del agitador
- Patron: 3s giro -> 2s pausa. Moderada, corta.
- Tiempo de lavado efectivo: ~8 min.

### Notas criticas
- Solo ropa POCO sucia. Max 5 kg de carga.
- Poco jabon (ciclo corto, no enjuaga mucho).

### Variables firmware
```cpp
programa_rapido = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 480000,   // 8 min
  .tiempoGiro_ms       = 3000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 1,
  .tiempoEnjuague_ms   = 60000,    // 1 min
  .tiempoCentrifugado_ms = 180000, // 3 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_BAJO
};
```



---

## 7. Lavagem Eco - Lavado Eco (Reuso de Agua)

**Tiempo total:** 0h 46min (46 min)
**Nivel de agua default:** Medio (2 barras)
**Remojo:** No
**Enjuagues:** 2

### Descripcion
Ahorra agua. Permite reutilizar agua del lavado (regar, limpiar pisos, inodoro). Agua de enjuague NO se reutiliza.

### Comportamiento del agitador
- Patron: 3s giro -> 2s pausa. Moderada.
- Tiempo de lavado efectivo: ~12 min.

### Notas criticas
- Luz parpadea = agua lista para reusar. 35 min timeout.
- Cancelar reuso: 2x "Avanzar Etapas".
- No reusar agua de ropa muy sucia o con blanqueador.

### Variables firmware
```cpp
programa_lavagem_eco = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 720000,   // 12 min
  .tiempoGiro_ms       = 3000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 180000,   // 3 min c/u
  .tiempoCentrifugado_ms = 300000, // 5 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_MEDIO,
  .pausaReuso_ms       = 2100000   // 35 min timeout
};
```

---

## 8. Brancas - Ropa Blanca

**Tiempo total:** 1h 42min (102 min)
**Nivel de agua default:** Alto (3 barras)
**Remojo:** Si
**Enjuagues:** 2

### Descripcion
Intensivo para ropa blanca. Mantiene blanco brillante y elimina manchas. Permite blanqueador con cloro.

### Comportamiento del agitador
- Patron: 4s giro -> 2s pausa. Fuerte.
- Tiempo de lavado efectivo: ~28 min. Remojo: ~12 min.

### Notas criticas
- Blanqueador con cloro SOLO en este programa y solo blanca.
- No mezclar con ropa de color. Secar al sol.

### Variables firmware
```cpp
programa_brancas = {
  .tiempoRemojo_ms     = 720000,   // 12 min
  .tiempoLavado_ms     = 1680000,  // 28 min
  .tiempoGiro_ms       = 4000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 420000, // 7 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_ALTO
};
```

---

## 9. Coloridas - Ropa de Color (EL MAS USADO)

**Tiempo total:** 0h 51min (51 min)
**Nivel de agua default:** Alto (3 barras)
**Remojo:** No
**Enjuagues:** 2

### Descripcion
Programa default para el dia a dia. Balance perfecto entre tiempo, agua y efectividad. Para remeras, pantalones, vestidos.

### Comportamiento del agitador
- Patron: 4s giro -> 2s pausa. Normal.
- Tiempo de lavado efectivo: ~15 min. Sin remojo.

### Notas criticas
- Separar colores fuertes de claros la primera vez.
- Jabon liquido para colores. No sobrecargar.
- Este programa debe ser el mas robusto en el firmware.

### Variables firmware
```cpp
programa_coloridas = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 900000,   // 15 min
  .tiempoGiro_ms       = 4000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 180000,   // 3 min c/u
  .tiempoCentrifugado_ms = 360000, // 6 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_ALTO
};
```

---

## 10. Escuras - Ropa Oscura

**Tiempo total:** 0h 43min (43 min)
**Nivel de agua default:** Alto (3 barras)
**Remojo:** No
**Enjuagues:** 2

### Descripcion
Para ropa oscura (negro, azul marino, gris). Agitacion suave con pausas largas para minimizar friccion y decoloracion.

### Comportamiento del agitador
- Patron: 3s giro -> 4s pausa. Suave.
- Tiempo de lavado efectivo: ~12 min.

### Notas criticas
- Jabon liquido para oscuros. Lavar del reves. No blanqueador. Secar a la sombra.

### Variables firmware
```cpp
programa_escuras = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 720000,   // 12 min
  .tiempoGiro_ms       = 3000,
  .pausaGiro_ms        = 4000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 180000,   // 3 min c/u
  .tiempoCentrifugado_ms = 300000, // 5 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_ALTO
};
```



---

## 11. Jeans - Jeans / Mezclilla

**Tiempo total:** 1h 21min (81 min)
**Nivel de agua default:** Alto (3 barras)
**Remojo:** Si (8 min)
**Enjuagues:** 2

### Descripcion
Optimizado para denim. Remojo ablanda fibras gruesas. Agitacion fuerte.

### Variables firmware
```cpp
programa_jeans = {
  .tiempoRemojo_ms     = 480000,   // 8 min
  .tiempoLavado_ms     = 1200000,  // 20 min
  .tiempoGiro_ms       = 4000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 360000, // 6 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_ALTO
};
```

---

## 12. Uniforme - Uniforme

**Tiempo total:** 1h 55min (115 min)
**Nivel de agua default:** Extra (4 barras)
**Remojo:** Si (12 min)
**Enjuagues:** 2

### Descripcion
Para uniformes de trabajo, overoles, prendas gruesas sinteticas.

### Variables firmware
```cpp
programa_uniforme = {
  .tiempoRemojo_ms     = 720000,   // 12 min
  .tiempoLavado_ms     = 1800000,  // 30 min
  .tiempoGiro_ms       = 4000,
  .pausaGiro_ms        = 2000,
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 420000, // 7 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_EXTRA
};
```

---

## 13. Roupas Intimas - Ropa Interior

**Tiempo total:** 1h 03min (63 min)
**Nivel de agua default:** Medio (2 barras)
**Remojo:** No
**Enjuagues:** 2

### Descripcion
Suave para ropa interior, corpinos, lycra/elastano. No deforma piezas ni dana elasticos.

### Variables firmware
```cpp
programa_roupas_intimas = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 600000,   // 10 min
  .tiempoGiro_ms       = 2000,     // 2 s
  .pausaGiro_ms        = 4000,     // 4 s
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 120000,   // 2 min c/u
  .tiempoCentrifugado_ms = 240000, // 4 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_MEDIO
};
```

---

## 14. Roupas Leves - Ropa Ligera / Delicada

**Tiempo total:** 1h 46min (106 min)
**Nivel de agua default:** Medio (2 barras)
**Remojo:** Si (15 min)
**Enjuagues:** 2

### Descripcion
Para telas finas: seda, viscosa, gasa, lino delicado. Agitacion minima. Lavado se basa en inmersion mas que friccion.

### Variables firmware
```cpp
programa_roupas_leves = {
  .tiempoRemojo_ms     = 900000,   // 15 min
  .tiempoLavado_ms     = 900000,   // 15 min
  .tiempoGiro_ms       = 2000,     // 2 s
  .pausaGiro_ms        = 6000,     // 6 s
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 120000,   // 2 min c/u
  .tiempoCentrifugado_ms = 180000, // 3 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_MEDIO
};
```

---

## 15. Roupas de Bebe - Ropa de Bebe

**Tiempo total:** 2h 20min (140 min) - El mas largo con ropa
**Nivel de agua default:** Alto (3 barras)
**Remojo:** Si (15 min)
**Enjuagues:** 3

### Descripcion
Ultra-cuidadoso. 3 enjuagues para que no quede rastro de jabon. Remojo elimina manchas de leche, pure y panal.

### Notas criticas
- Jabon hipoalergenico, sin perfume ni colorantes.
- NO suavizante (irritacion, inflamable).
- Lavar separado de adultos. No blanqueador.

### Variables firmware
```cpp
programa_roupas_bebe = {
  .tiempoRemojo_ms     = 900000,   // 15 min
  .tiempoLavado_ms     = 1500000,  // 25 min
  .tiempoGiro_ms       = 3000,
  .pausaGiro_ms        = 3000,
  .numEnjuagues        = 3,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 300000, // 5 min
  .agitacionFuerte     = false,
  .nivelAguaDefault    = NIVEL_ALTO
};
```

---

## 16. Limpeza da Lavadora - Limpieza de Lavadora

**Tiempo total:** 0h 54min (54 min)
**Nivel de agua default:** Alto (3 barras)
**Remojo:** No
**Enjuagues:** 2

### Descripcion
Mantenimiento. Limpia interior eliminando residuos, moho, olores, bacterias. SIN ROPA.

### Notas criticas
- NUNCA poner ropa. 1/2L blanqueador directo en cesto.
- 1 vez por mes. Dejar tapa abierta despues.

### Variables firmware
```cpp
programa_limpeza_lavadora = {
  .tiempoRemojo_ms     = 0,
  .tiempoLavado_ms     = 1200000,  // 20 min
  .tiempoGiro_ms       = 5000,     // 5 s
  .pausaGiro_ms        = 1000,     // 1 s
  .numEnjuagues        = 2,
  .tiempoEnjuague_ms   = 240000,   // 4 min c/u
  .tiempoCentrifugado_ms = 300000, // 5 min
  .agitacionFuerte     = true,
  .nivelAguaDefault    = NIVEL_ALTO,
  .requiereRopa        = false
};
```

---

## Array completo para firmware ESP32

```cpp
const ProgramaLavado PROGRAMAS[16] = {
  programa_cama_banho,       // 1
  programa_edredom,          // 2
  programa_limpieza_pesada,  // 3
  programa_panos_limpeza,    // 4
  programa_tira_odores,      // 5
  programa_rapido,           // 6
  programa_lavagem_eco,      // 7
  programa_brancas,          // 8
  programa_coloridas,        // 9
  programa_escuras,          // 10
  programa_jeans,            // 11
  programa_uniforme,         // 12
  programa_roupas_intimas,   // 13
  programa_roupas_leves,     // 14
  programa_roupas_bebe,      // 15
  programa_limpeza_lavadora  // 16
};
```

---

*Documento generado el 31 de julio de 2026. Datos del PDF oficial Consul CWH15AB.*
