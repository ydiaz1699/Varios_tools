# Ciclos de Lavado - Consul CWH15AB (16 Programas)

## Importante: Calibracion

> **ANTES de reemplazar la placa original**, ejecutar CADA programa con un
> cronometro y documentar los tiempos exactos. Los valores aqui son
> aproximados basados en las especificaciones del modelo CWH15AB.

## Especificaciones del Modelo

| Dato | Valor |
|------|-------|
| Modelo | CWH15AB |
| Capacidad | 15 kg |
| Programas | 16 |
| Niveles de agua | 4 (Baixo, Medio, Alto, Extra) |
| Panel | Digital (Tact) + Boton giratorio |
| Potencia | 620W |
| Centrifugacion | ~750 rpm |
| Eficiencia | Classe A (Procel) |
| Consumo agua/ciclo | ~186 L |
| Dispenser | Dual (Sabao + Amaciante) |

## Secuencia General de un Ciclo

```
[INICIO] -> [ENCHIMENTO] -> [LAVAGEM/AGITACAO] -> [DRENAGEM]
    -> [ENCHIMENTO ENXAGUE] -> [ENXAGUE] -> [DRENAGEM]
    -> (repetir enxague si hay mas de 1)
    -> [CENTRIFUGACAO + DRENAGEM] -> [MAIS SECAS opcional]
    -> [PRONTO]
```

## Los 16 Programas

### 1. Roupas Brancas
Ciclo intenso para ropa blanca con agitacion fuerte.

| Parametro | Valor |
|-----------|-------|
| Lavado | 14 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 2x 4 min |
| Centrifugado | 7 min |
| Nivel default | Alto |

### 2. Roupas Coloridas
Ciclo normal para ropa de colores, uso diario.

| Parametro | Valor |
|-----------|-------|
| Lavado | 12 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 2x 3 min |
| Centrifugado | 6 min |
| Nivel default | Alto |

### 3. Roupas Escuras
Ciclo suave para evitar decoloracion de ropa oscura.

| Parametro | Valor |
|-----------|-------|
| Lavado | 10 min |
| Agitacion | 3s/dir, pausa 3s (suave) |
| Enjuagues | 2x 3 min |
| Centrifugado | 5 min |
| Nivel default | Alto |

### 4. Jeans
Ciclo fuerte para tela denim pesada.

| Parametro | Valor |
|-----------|-------|
| Lavado | 13 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 2x 4 min |
| Centrifugado | 7 min |
| Nivel default | Alto |

### 5. Cama e Banho
Ciclo largo para sabanas, toallas, fundas.

| Parametro | Valor |
|-----------|-------|
| Lavado | 15 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 2x 4 min |
| Centrifugado | 8 min |
| Nivel default | Extra |

### 6. Roupas Delicadas
Ciclo suave y corto para telas finas.

| Parametro | Valor |
|-----------|-------|
| Lavado | 7 min |
| Agitacion | 3s/dir, pausa 4s (muy suave) |
| Enjuagues | 1x 3 min |
| Centrifugado | 3 min |
| Nivel default | Medio |

### 7. Roupas de Bebe
Ciclo suave con enjuagues extra para eliminar residuos.

| Parametro | Valor |
|-----------|-------|
| Lavado | 12 min |
| Agitacion | 3s/dir, pausa 3s (suave) |
| Enjuagues | 3x 4 min (triple!) |
| Centrifugado | 6 min |
| Nivel default | Alto |

### 8. Casacos e Moletons
Ciclo fuerte largo para prendas pesadas gruesas.

| Parametro | Valor |
|-----------|-------|
| Lavado | 14 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 2x 4 min |
| Centrifugado | 7 min |
| Nivel default | Extra |

### 9. Tenis
Ciclo suave para zapatillas (evita dano mecanico).

| Parametro | Valor |
|-----------|-------|
| Lavado | 10 min |
| Agitacion | 3s/dir, pausa 4s (suave) |
| Enjuagues | 1x 3 min |
| Centrifugado | 4 min |
| Nivel default | Medio |

### 10. Roupas Pesadas
Ciclo maximo para ropa muy sucia/pesada.

| Parametro | Valor |
|-----------|-------|
| Lavado | 15 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 2x 4 min |
| Centrifugado | 8 min |
| Nivel default | Extra |

### 11. Edredom
Ciclo suave muy largo para edredones voluminosos.

| Parametro | Valor |
|-----------|-------|
| Lavado | 17 min |
| Agitacion | 3s/dir, pausa 5s (muy suave) |
| Enjuagues | 2x 5 min |
| Centrifugado | 6 min |
| Nivel default | Extra |

### 12. Tira Odores
Ciclo con extra enjuagues para eliminar malos olores.

| Parametro | Valor |
|-----------|-------|
| Lavado | 13 min |
| Agitacion | 4s/dir, pausa 2s |
| Enjuagues | 3x 4 min (triple!) |
| Centrifugado | 6 min |
| Nivel default | Alto |

### 13. Ciclo Rapido
Ciclo corto para ropa poco sucia.

| Parametro | Valor |
|-----------|-------|
| Lavado | 5 min |
| Agitacion | 3s/dir, pausa 2s |
| Enjuagues | 1x 2 min |
| Centrifugado | 3 min |
| Nivel default | Baixo |

### 14. Enxague (Solo Enjuague)
Solo enjuague + centrifugado, sin lavado.

| Parametro | Valor |
|-----------|-------|
| Lavado | 0 (no hay) |
| Enjuagues | 2x 3 min |
| Centrifugado | 5 min |
| Nivel default | Medio |

### 15. Centrifugacao (Solo Centrifugado)
Solo centrifugado, sin agua.

| Parametro | Valor |
|-----------|-------|
| Lavado | 0 |
| Enjuagues | 0 |
| Centrifugado | 8 min |
| Nivel default | - |

### 16. Molho (Remojo)
Solo llena y deja en reposo sin agitacion.

| Parametro | Valor |
|-----------|-------|
| Tiempo remojo | 30 min |
| Agitacion | Ninguna |
| Enjuagues | 0 |
| Centrifugado | 0 |
| Nivel default | Alto |

## Funcion Especial: Mais Secas

Cuando esta activada, agrega **5 minutos extra** de centrifugado
al final de cualquier programa. Util para dejar la ropa menos
humeda y que seque mas rapido en el tendedero.

## Niveles de Agua

| Nivel | Sensor | Uso tipico |
|-------|--------|-----------|
| Baixo | Presostato bajo | Pocas prendas, ciclo rapido |
| Medio | Presostato bajo | Carga media, delicadas |
| Alto | Presostato alto | Carga completa |
| Extra | Presostato alto | Edredom, cama/banho, pesadas |

## Plantilla de Medicion (completar con placa original)

```
Fecha: ___/___/______
Modelo: Consul CWH15AB ___V

ROUPAS COLORIDAS (programa mas usado):
  Llenado hasta nivel Alto: ___ min ___ seg
  Agitacion total: ___ min ___ seg
  Segundos en cada dir: ___ seg
  Pausa entre dir: ___ seg
  Tiempo drenaje: ___ min ___ seg
  Enjuagues: ___ veces
  Tiempo cada enjuague: ___ min ___ seg
  Centrifugado: ___ min ___ seg
  TOTAL ciclo: ___ min

CICLO RAPIDO:
  Llenado: ___ min ___ seg
  Agitacion total: ___ min ___ seg
  Enjuagues: ___
  Centrifugado: ___ min ___ seg
  TOTAL: ___ min

EDREDOM:
  Llenado (Extra): ___ min ___ seg
  Agitacion total: ___ min ___ seg
  Patron agitacion (suave): ___ seg ON / ___ seg OFF
  Enjuagues: ___
  TOTAL: ___ min

DELICADAS:
  Llenado (Medio): ___ min ___ seg
  Agitacion total: ___ min ___ seg
  Enjuagues: ___
  Centrifugado: ___ min ___ seg
  TOTAL: ___ min
```
