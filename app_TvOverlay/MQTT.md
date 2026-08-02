# TvOverlay - Control por MQTT (Topics Reales Confirmados)

> **Ultima verificacion:** 2026-08-02
> Topics confirmados via MQTT Explorer en Home Assistant contra una instalacion real.

---

## Conexion MQTT

### Configurar desde la app

1. Abrir TvOverlay en el Android TV
2. Ir a **Settings > MQTT**
3. Llenar:
   - **Broker**: IP de tu broker (ej: `192.168.1.100`)
   - **Port**: `1883` (por defecto)
   - **User**: tu usuario MQTT
   - **Password**: tu password MQTT
4. Activar **"Display status on change"** para ver en pantalla si conecta/desconecta

### Configurar via REST API

```bash
curl -X POST http://IP_TV:5001/set/mqtt \
  -H "Content-Type: application/json" \
  -d '{
    "mqttConfig": {
      "broker": "192.168.1.100",
      "port": 1883,
      "user": "mi_usuario",
      "password": "mi_password"
    }
  }'
```

---

## Como encontrar tu DEVICE_ID

Al conectar TvOverlay al broker MQTT, la app se registra automaticamente via MQTT
Auto-Discovery de Home Assistant. Tu `DEVICE_ID` es unico por instalacion/dispositivo.

**Metodo 1 - MQTT Explorer en HA:**
1. Ir a Home Assistant > Ajustes > Dispositivos y servicios > MQTT
2. Clic en "Configurar" > "Escuchar un topic"
3. Suscribirse a `tv_overlay/#`
4. El DEVICE_ID aparecera como parte del topic: `tv_overlay/<DEVICE_ID>/...`

**Metodo 2 - mosquitto_sub:**
```bash
mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tv_overlay/#" -v
```

**Metodo 3 - MQTT Explorer (app de escritorio):**
Conectar al broker y expandir el arbol `tv_overlay/` — veras tu ID como subcarpeta.

> **Ejemplo real:** `TB432B197336788` (modelo TB432-B1).
> Tu ID sera diferente. Usa el placeholder `<DEVICE_ID>` en scripts y reemplazalo.

---

## Estructura REAL de topics

### Prefijo correcto

```
tv_overlay/<DEVICE_ID>/...
```

> **IMPORTANTE:** El prefijo real es `tv_overlay` (con guion bajo), NO `tvoverlay` como
> indicaba documentacion anterior. Esto fue confirmado en instalacion real.

---

## Topics de CONFIGURACION (confirmados)

Estos topics controlan los ajustes del overlay. Los payloads son **texto plano** (no JSON).

### 1. Hot Corner (posicion de notificaciones)

**Topic:** `tv_overlay/<DEVICE_ID>/hot_corner/set`

**Payload:** texto plano con valor en mayusculas y espacio.

| Valor | Posicion |
|-------|----------|
| `Top Left` | Arriba izquierda |
| `Top Right` | Arriba derecha |
| `Bottom Left` | Abajo izquierda |
| `Bottom Right` | Abajo derecha |

```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/hot_corner/set" \
  -m "Top Left"
```

> **Nota:** los valores NO son `top_start`/`bottom_end` como dice la REST API.
> Via MQTT se usan `Top Left`, `Top Right`, `Bottom Left`, `Bottom Right`.

---

### 2. Visibility (opacidad del fondo overlay)

**Topic:** `tv_overlay/<DEVICE_ID>/visibility/level/command`

**Payload:** numero como string (`"0"` a `"95"`)

```bash
# Oscurecer al 50%
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/visibility/level/command" \
  -m "50"

# Quitar oscuridad (transparente)
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/visibility/level/command" \
  -m "0"
```

---

### 3. Clock Visibility (visibilidad del reloj)

**Topic:** `tv_overlay/<DEVICE_ID>/clock_visibility/level/command`

**Payload:** numero como string (`"0"` a `"95"`)

```bash
# Reloj visible al 80%
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/clock_visibility/level/command" \
  -m "80"

# Ocultar reloj
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/clock_visibility/level/command" \
  -m "0"
```

---

### 4. Display Notifications (activar/desactivar notificaciones)

**Topic:** `tv_overlay/<DEVICE_ID>/display_notifications/set`

**Payload:** `"true"` o `"false"` (string)

```bash
# Desactivar notificaciones
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_notifications/set" \
  -m "false"

# Reactivar
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_notifications/set" \
  -m "true"
```

---

### 5. Display Fixed Notifications (activar/desactivar fijas)

**Topic:** `tv_overlay/<DEVICE_ID>/display_fixed_notifications/set`

**Payload:** `"true"` o `"false"` (string)

```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_fixed_notifications/set" \
  -m "true"
```

---

### 6. Pixel Shift (anti burn-in)

**Topic:** `tv_overlay/<DEVICE_ID>/pixel_shift/set`

**Payload:** `"true"` o `"false"` (string)

```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/pixel_shift/set" \
  -m "true"
```

---

### 7. Display Debug

**Topic:** `tv_overlay/<DEVICE_ID>/display_debug/set`

**Payload:** `"true"` o `"false"` (string)

```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_debug/set" \
  -m "false"
```

---

## Topics de ESTADO (lectura)

TvOverlay publica el estado actual en topics de estado. Puedes suscribirte para leerlos:

```bash
# Ver todos los estados
mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tv_overlay/<DEVICE_ID>/+/state" -v

# O mas especifico
mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tv_overlay/<DEVICE_ID>/visibility/level/state" -v
mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tv_overlay/<DEVICE_ID>/hot_corner/state" -v
```

---

## Resumen de topics confirmados

| Funcion | Topic | Payload | Tipo |
|---------|-------|---------|------|
| Hot corner | `.../hot_corner/set` | `Top Left`, `Top Right`, `Bottom Left`, `Bottom Right` | string |
| Overlay visibility | `.../visibility/level/command` | `0` - `95` | string numerico |
| Clock visibility | `.../clock_visibility/level/command` | `0` - `95` | string numerico |
| Notificaciones on/off | `.../display_notifications/set` | `true` / `false` | string |
| Fijas on/off | `.../display_fixed_notifications/set` | `true` / `false` | string |
| Pixel shift | `.../pixel_shift/set` | `true` / `false` | string |
| Debug | `.../display_debug/set` | `true` / `false` | string |

> Todos los topics usan el prefijo `tv_overlay/<DEVICE_ID>/`

---

## Notificaciones via MQTT — NO CONFIRMADO

> **IMPORTANTE:** A la fecha de esta documentacion, **NO se ha confirmado** que exista un
> topic MQTT para enviar notificaciones directamente (equivalente a `POST /notify` o
> `POST /notify_fixed` de la REST API).
>
> Las notificaciones (con titulo, mensaje, imagen, video, etc.) probablemente solo son
> posibles via:
> - **REST API** (`POST http://IP_TV:5001/notify`)
> - **Home Assistant notify service** (configurado como REST)
>
> Si descubres un topic MQTT para notificaciones, actualizar este documento.

Para enviar notificaciones, usar la REST API documentada en [REST_API.md](./REST_API.md).

---

## Diferencias MQTT vs REST API

| Aspecto | MQTT | REST API |
|---------|------|----------|
| Prefijo topic | `tv_overlay` (guion bajo) | N/A |
| Formato payload | Texto plano | JSON |
| Hot corner valores | `Top Left`, `Bottom Right` | `top_start`, `bottom_end` |
| Enviar notificaciones | **No confirmado** | Si (`POST /notify`) |
| Enviar fixed notifications | **No confirmado** | Si (`POST /notify_fixed`) |
| Cambiar visibility | Si (numero como string) | Si (JSON con int) |
| Switches (on/off) | `"true"`/`"false"` string | `true`/`false` boolean JSON |

---

## Ejemplos Home Assistant (con topics reales)

### Oscurecer TV de noche

```yaml
alias: TV Overlay - Modo nocturno
trigger:
  - platform: sun
    event: sunset
action:
  - service: mqtt.publish
    data:
      topic: "tv_overlay/<DEVICE_ID>/visibility/level/command"
      payload: "40"
mode: single
```

### Quitar oscuridad de dia

```yaml
alias: TV Overlay - Modo diurno
trigger:
  - platform: sun
    event: sunrise
action:
  - service: mqtt.publish
    data:
      topic: "tv_overlay/<DEVICE_ID>/visibility/level/command"
      payload: "0"
mode: single
```

### Mover notificaciones a esquina superior derecha

```yaml
service: mqtt.publish
data:
  topic: "tv_overlay/<DEVICE_ID>/hot_corner/set"
  payload: "Top Right"
```

### Desactivar notificaciones temporalmente

```yaml
service: mqtt.publish
data:
  topic: "tv_overlay/<DEVICE_ID>/display_notifications/set"
  payload: "false"
```

---

## Debugging

1. **Activar status en la app**: Settings > MQTT > "Display status on change" = ON
2. **Ver TODO lo que publica TvOverlay:**
   ```bash
   mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tv_overlay/#" -v
   ```
3. **Si no ves nada:** verificar que la app tiene MQTT conectado (debe mostrar "Connected" en la app)
4. **Si MQTT funciona pero quieres notificaciones:** usar REST API (ver REST_API.md)
   ```bash
   curl -X POST http://IP_TV:5001/notify -H "Content-Type: application/json" \
     -d '{"title":"Test","message":"Funciona"}'
   ```

---

*Fuente: https://github.com/gugutab/TvOverlay + verificacion en instalacion real*
