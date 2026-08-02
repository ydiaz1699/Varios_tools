# TvOverlay - Control por MQTT

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

## Estructura de topics MQTT

Al conectarse, TvOverlay se registra via **MQTT Auto-Discovery** de Home Assistant.
El dispositivo aparecera como: `TvOverlay - [Modelo]`

### Topics de comando (publicar para controlar)

La estructura general de topics es:

```
tvoverlay/<DEVICE_ID>/notify          -> Enviar notificacion
tvoverlay/<DEVICE_ID>/notify_fixed    -> Enviar notificacion fija
tvoverlay/<DEVICE_ID>/set/overlay     -> Configurar overlay (fondo, reloj, esquina)
tvoverlay/<DEVICE_ID>/set/notifications -> Configurar notificaciones
tvoverlay/<DEVICE_ID>/set/settings    -> Configurar ajustes generales
```

> **Nota:** esta estructura de topics fue inferida por MQTT Auto-Discovery de Home
> Assistant y no aparece confirmada literalmente en el README oficial del repo. Confirmala
> en tu propia instalacion (ver "Como descubrir tu DEVICE_ID" abajo) antes de automatizar
> en base a ella.

### Como descubrir tu DEVICE_ID

**Opcion 1 - MQTT Explorer:**
Conectate a tu broker con [MQTT Explorer](http://mqtt-explorer.com) y busca topics que contengan `tvoverlay`.

**Opcion 2 - Suscribirse a todo:**
```bash
mosquitto_sub -h BROKER_IP -u USUARIO -P PASSWORD -t "#" -v | grep -i tvoverlay
```

**Opcion 3 - Home Assistant:**
Ajustes > Dispositivos y servicios > MQTT > buscar "TvOverlay" > ver entidades y sus topics.

---

## Comandos MQTT detallados

### 1. Enviar notificacion

**Topic:** `tvoverlay/<DEVICE_ID>/notify`

**Payload JSON:**

```json
{
  "id": "mi_notificacion_01",
  "title": "Titulo principal",
  "message": "Texto secundario del mensaje",
  "appTitle": "Info extra",
  "smallIcon": "mdi:bell",
  "color": "#FF5722",
  "largeIcon": "mdi:home",
  "corner": "top_end",
  "duration": 10,
  "image": "https://url-de-imagen.jpg",
  "video": "rtsp://192.168.1.50:554/stream"
}
```

**Campos disponibles:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `id` | string | No | ID unico. Permite editar/reemplazar notificacion activa |
| `title` | string | No | Texto principal grande |
| `message` | string | No* | Texto secundario. *HA lo requiere pero puede ser "null" |
| `appTitle` | string | No | Texto extra informativo |
| `smallIcon` | string | No | Icono pequeno: MDI (`mdi:bell`), URL imagen, o Base64 |
| `color` | string | No | Color del smallIcon. Hex 6 u 8 digitos. `#` opcional |
| `largeIcon` | string | No | Icono grande: MDI, URL imagen, o Base64 |
| `corner` | string | No | Posicion: `top_start`, `top_end`, `bottom_start`, `bottom_end` |
| `duration` | int | No | Segundos visible. Default: usa config de la app |
| `image` | string | No | URL de imagen, MDI, o Base64 |
| `video` | string | No | URL de video: RTSP, HLS, DASH, SmoothStreaming |

**Ejemplo minimo:**
```json
{"title": "Hola!", "message": "Esto es una prueba"}
```

**Ejemplo con icono y color:**
```json
{
  "title": "Puerta abierta",
  "message": "La puerta principal se abrio",
  "smallIcon": "mdi:door-open",
  "color": "#FF0000",
  "duration": 15
}
```

---

### 2. Enviar notificacion fija

**Topic:** `tvoverlay/<DEVICE_ID>/notify_fixed`

Las notificaciones fijas son iconos compactos que permanecen visibles en una esquina.

**Payload JSON:**

```json
{
  "id": "bateria_phone",
  "icon": "mdi:battery-70",
  "message": "70%",
  "iconColor": "#4CAF50",
  "messageColor": "#FFFFFF",
  "borderColor": "#4CAF50",
  "backgroundColor": "#66000000",
  "shape": "rounded",
  "expiration": "5m"
}
```

**Campos disponibles:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `id` | string | No | ID unico para editar/eliminar |
| `visible` | boolean | No | `true`/`false` para mostrar/ocultar (default: true) |
| `icon` | string | No | MDI, URL imagen, o Base64 |
| `message` | string | No | Texto corto junto al icono |
| `messageColor` | string | No | Color del texto (hex). Default: `#FFFFFF` |
| `iconColor` | string | No | Color del icono (hex) |
| `borderColor` | string | No | Color del borde (hex). Default: `#FFFFFF` |
| `backgroundColor` | string | No | Color de fondo con transparencia (hex 8 digitos). Default: `#66000000` |
| `shape` | string | No | Forma: `circle`, `rounded`, `rectangular` |
| `expiration` | string/int | No | Tiempo de vida. Formatos: `60` (seg), `5m`, `1h30m`, `1695693410` (epoch) |

**Eliminar notificacion fija (ocultarla):**
```json
{
  "id": "luz_sala",
  "visible": false
}
```

---

### 3. Configurar overlay (fondo/reloj/esquina)

**Topic:** `tvoverlay/<DEVICE_ID>/set/overlay`

```json
{
  "overlayVisibility": 50,
  "clockOverlayVisibility": 80,
  "hotCorner": "top_start"
}
```

| Campo | Tipo | Rango | Descripcion |
|-------|------|-------|-------------|
| `overlayVisibility` | int | 0-95 | Opacidad del fondo oscuro (0=transparente, 95=casi negro) |
| `clockOverlayVisibility` | int | 0-95 | Visibilidad del reloj |
| `hotCorner` | string | - | Esquina activa: `top_start`, `top_end`, `bottom_start`, `bottom_end` |

---

### 4. Configurar notificaciones

**Topic:** `tvoverlay/<DEVICE_ID>/set/notifications`

```json
{
  "displayNotifications": true,
  "displayFixedNotifications": true,
  "notificationDuration": 8,
  "notificationLayoutName": "Default",
  "fixedNotificationsVisibility": -1
}
```

---

### 5. Configurar ajustes generales

**Topic:** `tvoverlay/<DEVICE_ID>/set/settings`

```json
{
  "deviceName": "TV Sala",
  "displayDebug": false,
  "pixelShift": true
}
```

---

## Probar con mosquitto_pub

### Notificacion basica
```bash
mosquitto_pub -h 192.168.1.100 -u usuario -P password \
  -t "tvoverlay/MI_DEVICE/notify" \
  -m '{"title":"Prueba MQTT","message":"Funciona!","smallIcon":"mdi:check","color":"#4CAF50","duration":8}'
```

### Notificacion fija
```bash
mosquitto_pub -h 192.168.1.100 -u usuario -P password \
  -t "tvoverlay/MI_DEVICE/notify_fixed" \
  -m '{"id":"test1","icon":"mdi:wifi","message":"Online","iconColor":"#2196F3","expiration":"60"}'
```

### Oscurecer pantalla
```bash
mosquitto_pub -h 192.168.1.100 -u usuario -P password \
  -t "tvoverlay/MI_DEVICE/set/overlay" \
  -m '{"overlayVisibility":40}'
```

---

## Debugging

1. **Activar status en la app**: Settings > MQTT > "Display status on change" = ON
2. **Ver mensajes en broker**:
   ```bash
   mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tvoverlay/#" -v
   ```
3. **Verificar conexion**: Si ves `tvoverlay/[device]/status` con payload `online`, esta conectado
4. **Probar REST primero**: Si REST funciona pero MQTT no, el problema es la conexion MQTT
   ```bash
   curl -X POST http://IP_TV:5001/notify -H "Content-Type: application/json" \
     -d '{"title":"Test REST","message":"Funciona"}'
   ```

---

## Iconos MDI disponibles

TvOverlay soporta iconos de Material Design Icons. Formato: `mdi:nombre-del-icono`

Catalogo completo: https://pictogrammers.com/library/mdi/

---

*Fuente: https://github.com/gugutab/TvOverlay*
