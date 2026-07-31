# Ciclos de Lavado - Consul CWM15AB

## Importante: Calibracion

> **ANTES de reemplazar la placa original**, ejecutar CADA programa con un
> cronometro y documentar los tiempos exactos en la tabla de abajo.
> Los valores aqui son aproximados basados en lavadoras Consul similares.

## Secuencia General de un Ciclo Completo

```
[INICIO] -> [LLENADO] -> [LAVADO/AGITACION] -> [DRENAJE]
    -> [LLENADO ENJUAGUE] -> [ENJUAGUE] -> [DRENAJE]
    -> (repetir enjuague si hay mas de 1)
    -> [CENTRIFUGADO + DRENAJE] -> [FIN]
```

## Detalle de Cada Etapa

### 1. Llenado
- Se abre la valvula solenoide de entrada de agua
- El presostato detecta cuando se alcanza el nivel seleccionado
- Se cierra la valvula
- **Timeout de seguridad:** 15 minutos (si no llena, corta y da error)

### 2. Lavado (Agitacion)
- El motor de agitacion gira alternadamente en ambas direcciones
- Patron: X segundos Dir.A -> pausa -> X segundos Dir.B -> pausa
- La intensidad y tiempo dependen del programa seleccionado
- **NUNCA** cambiar direccion sin pausa (protege el motor y transmision)

### 3. Drenaje
- Se activa la bomba de drenaje
- Tiempo fijo de 90 segundos (asegura vaciado completo)

### 4. Enjuague
- Similar a lavado pero con agitacion mas suave
- Menos tiempo de agitacion, mas pausa
- Se repite segun el programa (1 o 2 veces)

### 5. Centrifugado
- Drenaje activo + motor de centrifugado
- Velocidad unica (la transmision mecanica determina RPM)
- **INTERLOCK:** Se detiene si la tapa se abre

## Tabla de Parametros por Programa

### PESADO (Roupas Pesadas)
| Parametro | Valor | Notas |
|-----------|-------|-------|
| Tiempo lavado | 15 min | Agitacion fuerte |
| Dir. agitacion | 4 seg | Cada direccion |
| Pausa agitacion | 2 seg | Entre cambios |
| Enjuagues | 2 | |
| Tiempo c/ enjuague | 4 min | Agitacion suave |
| Centrifugado | 7 min | Velocidad maxima |

### NORMAL
| Parametro | Valor | Notas |
|-----------|-------|-------|
| Tiempo lavado | 12 min | Agitacion fuerte |
| Dir. agitacion | 4 seg | Cada direccion |
| Pausa agitacion | 2 seg | Entre cambios |
| Enjuagues | 2 | |
| Tiempo c/ enjuague | 3 min | Agitacion suave |
| Centrifugado | 5 min | Velocidad maxima |

### DELICADO (Roupas Delicadas)
| Parametro | Valor | Notas |
|-----------|-------|-------|
| Tiempo lavado | 7 min | Agitacion suave |
| Dir. agitacion | 3 seg | Cada direccion |
| Pausa agitacion | 4 seg | Pausa larga = suave |
| Enjuagues | 1 | |
| Tiempo c/ enjuague | 3 min | Agitacion suave |
| Centrifugado | 3 min | Menor tiempo |

### RAPIDO
| Parametro | Valor | Notas |
|-----------|-------|-------|
| Tiempo lavado | 5 min | Agitacion fuerte |
| Dir. agitacion | 3 seg | Cada direccion |
| Pausa agitacion | 2 seg | |
| Enjuagues | 1 | |
| Tiempo c/ enjuague | 2 min | |
| Centrifugado | 3 min | |

### SOLO CENTRIFUGADO
| Parametro | Valor | Notas |
|-----------|-------|-------|
| Tiempo lavado | 0 | No hay lavado |
| Enjuagues | 0 | No hay enjuague |
| Centrifugado | 7 min | Directo al centrifugado |

### SOLO ENJUAGUE
| Parametro | Valor | Notas |
|-----------|-------|-------|
| Tiempo lavado | 0 | No hay lavado |
| Enjuagues | 2 | |
| Tiempo c/ enjuague | 3 min | |
| Centrifugado | 3 min | |

## Niveles de Agua

| Nivel | Presostato | Uso Tipico |
|-------|-----------|-----------|
| Bajo | Solo sensor bajo | Pocas prendas |
| Medio | Solo sensor bajo | Carga normal |
| Alto | Sensor alto | Carga completa |
| Extra | Sensor alto + tiempo | Edredones/voluminosos |

## Plantilla para Medicion (llenar con placa original)

```
Fecha de medicion: ___/___/______
Modelo exacto: Consul CWM15AB ___V

PROGRAMA PESADO:
  - Tiempo llenado (nivel alto): ___ min ___ seg
  - Tiempo agitacion total: ___ min ___ seg
  - Segundos en cada direccion: ___ seg
  - Pausa entre direcciones: ___ seg
  - Tiempo drenaje: ___ min ___ seg
  - Numero de enjuagues: ___
  - Tiempo cada enjuague: ___ min ___ seg
  - Tiempo centrifugado: ___ min ___ seg
  - Tiempo TOTAL del ciclo: ___ min

PROGRAMA NORMAL:
  - Tiempo llenado (nivel medio): ___ min ___ seg
  - Tiempo agitacion total: ___ min ___ seg
  - Segundos en cada direccion: ___ seg
  - Pausa entre direcciones: ___ seg
  - Tiempo drenaje: ___ min ___ seg
  - Numero de enjuagues: ___
  - Tiempo cada enjuague: ___ min ___ seg
  - Tiempo centrifugado: ___ min ___ seg
  - Tiempo TOTAL del ciclo: ___ min

PROGRAMA DELICADO:
  (completar igual)

PROGRAMA RAPIDO:
  (completar igual)
```
