# TvOverlay - REST API

## Informacion general

- **Puerto por defecto:** `5001` (configurable en ajustes)
- **Metodo:** `POST` (todos los endpoints)
- **Content-Type:** `application/json`
- **Base URL:** `http://<IP_TV>:5001`

No requiere autenticacion. Solo necesitas estar en la misma red.

---

## Endpoints disponibles

| Endpoint | Descripcion |
|----------|-------------|
| `POST /notify` | Enviar notificacion |
| `POST /notify_fixed` | Enviar notificacion fija |
| `POST /set/overlay` | Configurar overlay (fondo, reloj, esquina) |
| `POST /set/notifications` | Configurar comportamiento de notificaciones |
| `POST /set/settings` | Configurar ajustes generales |
| `POST /set/mqtt` | Configurar conexion MQTT |

---

## 1. Notificaciones - `POST /notify`

Muestra una notificacion emergente temporal en la pantalla del TV.

### Campos

| Campo | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| `id` | string | random | ID unico. Permite editar notificacion activa |
| `title` | string | null | Texto principal |
| `message` | string | null | Texto secundario |
| `source` | string | null | Texto extra informativo (equivale a `appTitle` en HA) |
| `smallIcon` | string | null | Icono pequeno: `mdi:nombre`, URL, o Base64 |
| `smallIconColor` | string | null | Color del smallIcon (hex 6/8 digitos, `#` opcional) |
| `largeIcon` | string | null | Icono grande: `mdi:nombre`, URL, o Base64 |
| `corner` | string | hot corner | Posicion: `top_start`, `top_end`, `bottom_start`, `bottom_end` |
| `duration` | int | config app | Segundos visible |
| `image` | string | null | Imagen: URL, MDI, o Base64 |
| `video` | string | null | Video: RTSP, HLS, DASH, SmoothStreaming |

### Ejemplos curl

**Notificacion basica:**
```bash
curl -X POST http://192.168.1.50:5001/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hola!",
    "message": "Esto es una prueba"
  }'
```

**Con icono y color:**
```bash
curl -X POST http://192.168.1.50:5001/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Puerta abierta",
    "message": "Puerta principal",
    "smallIcon": "mdi:door-open",
    "smallIconColor": "#FF0000",
    "largeIcon": "mdi:home",
    "duration": 12
  }'
```

**Con imagen (snapshot camara):**
```bash
curl -X POST http://192.168.1.50:5001/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Movimiento detectado",
    "message": "Camara frontal",
    "image": "http://192.168.1.60/snapshot.jpg",
    "smallIcon": "mdi:cctv",
    "smallIconColor": "#B00020",
    "duration": 10
  }'
```

**Con video RTSP (camara en vivo):**
```bash
curl -X POST http://192.168.1.50:5001/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Timbre",
    "message": "Alguien en la puerta",
    "video": "rtsp://192.168.1.60:554/live",
    "smallIcon": "mdi:doorbell-video",
    "smallIconColor": "#2196F3",
    "duration": 20
  }'
```

**En esquina especifica:**
```bash
curl -X POST http://192.168.1.50:5001/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Info",
    "message": "Esquina inferior derecha",
    "corner": "bottom_end",
    "duration": 5
  }'
```

**Reemplazar notificacion existente (mismo ID):**
```bash
curl -X POST http://192.168.1.50:5001/notify \
  -H "Content-Type: application/json" \
  -d '{
    "id": "alerta_temp",
    "title": "Temperatura actualizada",
    "message": "35C - Muy caliente!",
    "smallIcon": "mdi:thermometer-alert",
    "smallIconColor": "#FF5722"
  }'
```

---

## 2. Notificaciones fijas - `POST /notify_fixed`

Iconos compactos permanentes en una esquina. Utiles para estado: bateria, temperatura, luces, etc.

### Campos

| Campo | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| `id` | string | random | ID unico para editar/eliminar |
| `visible` | boolean | true | Mostrar u ocultar |
| `icon` | string | null | MDI, URL, o Base64 |
| `message` | string | null | Texto corto junto al icono |
| `messageColor` | string | #FFFFFF | Color del texto (hex) |
| `iconColor` | string | null | Color del icono (hex) |
| `borderColor` | string | #FFFFFF | Color del borde (hex) |
| `backgroundColor` | string | #66000000 | Fondo con transparencia (hex 8 digitos) |
| `shape` | string | rounded | Forma: `circle`, `rounded`, `rectangular` |
| `expiration` | string/int | null | Tiempo de vida. Formatos abajo |

### Formatos de expiration

| Formato | Ejemplo | Descripcion |
|---------|---------|-------------|
| Segundos | `60` | Desaparece en 60 segundos |
| Duracion | `1h30m` | 1 hora 30 minutos |
| Duracion | `5m` | 5 minutos |
| Duracion | `2d` | 2 dias |
| Epoch | `1695693410` | Timestamp Unix exacto |
| Complejo | `1y2w3d4h5m6s` | Combinacion completa |

### Ejemplos curl

**Indicador de luz encendida:**
```bash
curl -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{
    "id": "luz_sala",
    "icon": "mdi:lightbulb",
    "message": "Sala",
    "iconColor": "#FFEB3B",
    "borderColor": "#FFEB3B",
    "shape": "rounded"
  }'
```

**Bateria del telefono:**
```bash
curl -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{
    "id": "bateria_cel",
    "icon": "mdi:battery-70",
    "message": "70%",
    "iconColor": "#4CAF50",
    "borderColor": "#4CAF50",
    "expiration": "10m"
  }'
```

**Temperatura exterior:**
```bash
curl -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{
    "id": "temp_ext",
    "icon": "mdi:thermometer",
    "message": "28C",
    "iconColor": "#FF9800",
    "borderColor": "#FF9800",
    "shape": "circle",
    "expiration": "30m"
  }'
```

**Canal de Twitch online:**
```bash
curl -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{
    "id": "twitch_fav",
    "icon": "mdi:twitch",
    "message": "En vivo!",
    "iconColor": "#9C27B0",
    "borderColor": "#9C27B0",
    "backgroundColor": "#99000000"
  }'
```

**Actualizar notificacion fija existente:**
```bash
curl -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{
    "id": "bateria_cel",
    "icon": "mdi:battery-30",
    "message": "30%",
    "iconColor": "#FF5722",
    "borderColor": "#FF5722"
  }'
```

**Eliminar/ocultar notificacion fija:**
```bash
curl -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{
    "id": "luz_sala",
    "visible": false
  }'
```

---

## 3. Configurar overlay - `POST /set/overlay`

Controla el fondo oscuro, visibilidad del reloj y esquina activa.

### Campos

| Campo | Tipo | Rango | Descripcion |
|-------|------|-------|-------------|
| `overlayVisibility` | int | 0-95 | Opacidad del fondo (0=transparente, 95=casi negro) |
| `clockOverlayVisibility` | int | 0-95 | Visibilidad del reloj |
| `hotCorner` | string | - | Esquina: `top_start`, `top_end`, `bottom_start`, `bottom_end` |

### Ejemplos

**Oscurecer pantalla al 50%:**
```bash
curl -X POST http://192.168.1.50:5001/set/overlay \
  -H "Content-Type: application/json" \
  -d '{"overlayVisibility": 50}'
```

**Modo nocturno (muy oscuro):**
```bash
curl -X POST http://192.168.1.50:5001/set/overlay \
  -H "Content-Type: application/json" \
  -d '{"overlayVisibility": 80, "clockOverlayVisibility": 30}'
```

**Volver a normal:**
```bash
curl -X POST http://192.168.1.50:5001/set/overlay \
  -H "Content-Type: application/json" \
  -d '{"overlayVisibility": 0, "clockOverlayVisibility": 0}'
```

**Mover notificaciones a esquina superior izquierda:**
```bash
curl -X POST http://192.168.1.50:5001/set/overlay \
  -H "Content-Type: application/json" \
  -d '{"hotCorner": "top_start"}'
```

---

## 4. Configurar notificaciones - `POST /set/notifications`

### Campos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `displayNotifications` | boolean | Activar/desactivar notificaciones |
| `displayFixedNotifications` | boolean | Activar/desactivar fijas |
| `notificationLayoutName` | string | Layout: `Default`, `Minimalist`, `Icon Only` |
| `notificationDuration` | int | Duracion default en segundos |
| `fixedNotificationsVisibility` | int (-1~95) | Visibilidad fijas. `-1` = misma que reloj |

### Ejemplos

**Cambiar a layout minimalista con 10 seg:**
```bash
curl -X POST http://192.168.1.50:5001/set/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "notificationLayoutName": "Minimalist",
    "notificationDuration": 10
  }'
```

**Desactivar todas las notificaciones:**
```bash
curl -X POST http://192.168.1.50:5001/set/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "displayNotifications": false,
    "displayFixedNotifications": false
  }'
```

**Reactivar todo:**
```bash
curl -X POST http://192.168.1.50:5001/set/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "displayNotifications": true,
    "displayFixedNotifications": true
  }'
```

---

## 5. Configurar ajustes - `POST /set/settings`

### Campos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `deviceName` | string | Nombre del dispositivo |
| `remotePort` | string | Puerto del servidor REST |
| `displayDebug` | boolean | Mostrar info debug en overlay |
| `pixelShift` | boolean | Mover overlay cada 2min (anti burn-in) |

### Ejemplo

```bash
curl -X POST http://192.168.1.50:5001/set/settings \
  -H "Content-Type: application/json" \
  -d '{
    "deviceName": "TV Sala Principal",
    "pixelShift": true,
    "displayDebug": false
  }'
```

---

## 6. Configurar MQTT - `POST /set/mqtt`

### Campos

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `displayMqttStatusChange` | boolean | No | Mostrar mensaje al conectar/desconectar |
| `mqttConfig` | object | No | Configuracion completa del broker |
| `mqttConfig.broker` | string | Si* | IP/URL del broker |
| `mqttConfig.port` | int | Si* | Puerto (normalmente 1883) |
| `mqttConfig.user` | string | No | Usuario |
| `mqttConfig.password` | string | No | Password |

*Requeridos solo si envias `mqttConfig`

### Ejemplos

**Configurar broker MQTT:**
```bash
curl -X POST http://192.168.1.50:5001/set/mqtt \
  -H "Content-Type: application/json" \
  -d '{
    "displayMqttStatusChange": true,
    "mqttConfig": {
      "broker": "192.168.1.100",
      "port": 1883,
      "user": "mqtt_user",
      "password": "mqtt_pass"
    }
  }'
```

**Solo activar/desactivar mensaje de status:**
```bash
curl -X POST http://192.168.1.50:5001/set/mqtt \
  -H "Content-Type: application/json" \
  -d '{"displayMqttStatusChange": false}'
```

---

## Formatos de imagen/icono soportados

Todos los campos de icono e imagen aceptan:

| Formato | Ejemplo |
|---------|---------|
| MDI icon | `mdi:home`, `mdi:bell-ring` |
| URL imagen | `http://192.168.1.60/foto.jpg`, `https://picsum.photos/300` |
| Base64 | `data:image/png;base64,iVBORw0KGgo...` |

---

## Formatos de video soportados

| Protocolo | Ejemplo |
|-----------|---------|
| RTSP | `rtsp://192.168.1.60:554/live` |
| HLS | `http://server/stream.m3u8` |
| DASH | `http://server/manifest.mpd` |
| SmoothStreaming | `http://server/manifest` |

---

## Codigos de respuesta

| Codigo | Significado |
|--------|-------------|
| 200 | OK - Comando ejecutado |
| 400 | Bad Request - JSON malformado |
| 404 | Not Found - Endpoint no existe |
| Sin respuesta | TV apagado o app no corriendo |

---

## Tips

1. **Verificar que la app corre:** `curl http://IP_TV:5001/` (deberia responder algo)
2. **Si no responde:** Verificar que TvOverlay esta corriendo y no fue cerrado por el sistema
3. **Imagenes de camaras:** Agregar timestamp para evitar cache: `?t=1234567890`
4. **Videos RTSP:** Asegurar que el TV puede alcanzar la camara por red
5. **Colores:** Se puede usar con o sin `#`. Hex de 6 digitos (RGB) u 8 digitos (ARGB)

---

*Fuente: https://github.com/gugutab/TvOverlay*
