# TvOverlay - Cheatsheet (Copy-Paste Rapido)

> Reemplazar `IP_TV`, `BROKER_IP`, `MI_DEVICE`, `USER`, `PASS` con tus valores reales.
>
> Ultima sincronizacion: 2 de agosto de 2026 | App version: 1.0.4

---

## REST API (curl)

### Notificacion simple
```bash
curl -X POST http://IP_TV:5001/notify -H "Content-Type: application/json" \
  -d '{"title":"Titulo","message":"Mensaje","smallIcon":"mdi:bell","color":"#FF5722","duration":7}'
```

### Notificacion con imagen
```bash
curl -X POST http://IP_TV:5001/notify -H "Content-Type: application/json" \
  -d '{"title":"Camara","message":"Movimiento","image":"http://IP_CAMARA/snapshot.jpg","smallIcon":"mdi:cctv","color":"#F44336","duration":10}'
```

### Notificacion con video RTSP
```bash
curl -X POST http://IP_TV:5001/notify -H "Content-Type: application/json" \
  -d '{"title":"Timbre","message":"En la puerta","video":"rtsp://IP_CAMARA:554/live","smallIcon":"mdi:doorbell-video","color":"#2196F3","duration":20}'
```

### Notificacion fija (crear)
```bash
curl -X POST http://IP_TV:5001/notify_fixed -H "Content-Type: application/json" \
  -d '{"id":"mi_id","icon":"mdi:lightbulb","message":"ON","iconColor":"#FFEB3B","borderColor":"#FFEB3B"}'
```

### Notificacion fija (eliminar)
```bash
curl -X POST http://IP_TV:5001/notify_fixed -H "Content-Type: application/json" \
  -d '{"id":"mi_id","visible":false}'
```

### Oscurecer pantalla
```bash
curl -X POST http://IP_TV:5001/set/overlay -H "Content-Type: application/json" \
  -d '{"overlayVisibility":50}'
```

### Quitar oscuridad
```bash
curl -X POST http://IP_TV:5001/set/overlay -H "Content-Type: application/json" \
  -d '{"overlayVisibility":0}'
```

### Cambiar esquina
```bash
curl -X POST http://IP_TV:5001/set/overlay -H "Content-Type: application/json" \
  -d '{"hotCorner":"top_end"}'
```

### Configurar MQTT remotamente
```bash
curl -X POST http://IP_TV:5001/set/mqtt -H "Content-Type: application/json" \
  -d '{"mqttConfig":{"broker":"BROKER_IP","port":1883,"user":"USER","password":"PASS"}}'
```

### Encender pantalla (wake up)
```bash
curl -X POST http://IP_TV:5001/set/screen_on
```

### Reiniciar servicio overlay
```bash
curl -X POST http://IP_TV:5001/set/restart_service
```

### Consultar estado (GET)
```bash
curl http://IP_TV:5001/get                    # Estado general
curl http://IP_TV:5001/get/overlay            # Config overlay actual
curl http://IP_TV:5001/get/mqtt               # Config MQTT actual
curl http://IP_TV:5001/get/fixed_notifications # Notificaciones fijas activas
```

### Eliminar config MQTT
```bash
curl -X DELETE http://IP_TV:5001/delete/mqtt
```

---

## MQTT (mosquitto_pub)

> **Nota:** Los topics `tvoverlay/MI_DEVICE/...` son derivados de auto-discovery.
> Verifica tus topics reales con: `mosquitto_sub -h BROKER_IP -u USER -P PASS -t "#" -v | grep tvoverlay`

### Notificacion
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS -t "tvoverlay/MI_DEVICE/notify" \
  -m '{"title":"Titulo","message":"Mensaje","smallIcon":"mdi:bell","color":"#FF5722","duration":7}'
```

### Notificacion fija
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS -t "tvoverlay/MI_DEVICE/notify_fixed" \
  -m '{"id":"test","icon":"mdi:check","message":"OK","iconColor":"#4CAF50","borderColor":"#4CAF50","expiration":"5m"}'
```

### Quitar notificacion fija
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS -t "tvoverlay/MI_DEVICE/notify_fixed" \
  -m '{"id":"test","visible":false}'
```

### Oscurecer
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS -t "tvoverlay/MI_DEVICE/set/overlay" \
  -m '{"overlayVisibility":50}'
```

### Espiar topics (debug)
```bash
mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tvoverlay/#" -v
```

---

## Home Assistant (Servicios)

### mqtt.publish - Notificacion
```yaml
service: mqtt.publish
data:
  topic: "tvoverlay/MI_DEVICE/notify"
  payload: '{"title":"Test","message":"Desde HA","smallIcon":"mdi:home-assistant","color":"#03A9F4","duration":7}'
```

### mqtt.publish - Notificacion fija
```yaml
service: mqtt.publish
data:
  topic: "tvoverlay/MI_DEVICE/notify_fixed"
  payload: '{"id":"ha_test","icon":"mdi:home","message":"Home","iconColor":"#03A9F4","borderColor":"#03A9F4","expiration":"10m"}'
```

### mqtt.publish - Oscurecer
```yaml
service: mqtt.publish
data:
  topic: "tvoverlay/MI_DEVICE/set/overlay"
  payload: '{"overlayVisibility":40}'
```

---

## Referencia rapida de campos

### /notify
```
title        string   Texto principal
message      string   Texto secundario
smallIcon    string   mdi:icono / URL / Base64
color        string   Color del smallIcon (#hex)
largeIcon    string   mdi:icono / URL / Base64
image        string   URL imagen
video        string   URL video (rtsp/hls/dash)
corner       string   top_start|top_end|bottom_start|bottom_end
duration     int      Segundos visible
id           string   ID para reemplazar/editar
```

### /notify_fixed
```
id              string   ID unico (para editar/eliminar)
icon            string   mdi:icono / URL / Base64
message         string   Texto corto
iconColor       string   Color icono (#hex)
messageColor    string   Color texto (#hex)
borderColor     string   Color borde (#hex)
backgroundColor string   Color fondo (#hex 8 digitos ARGB)
shape           string   circle|rounded|rectangular
expiration      string   Segundos, duracion (5m/1h), o epoch
visible         boolean  true/false (false para eliminar)
```

### /set/overlay
```
overlayVisibility       int 0-95    Opacidad fondo
clockOverlayVisibility  int 0-95    Visibilidad reloj
hotCorner               string      top_start|top_end|bottom_start|bottom_end
```

### /set/notifications
```
displayNotifications         boolean  On/Off notificaciones
displayFixedNotifications    boolean  On/Off fijas
notificationLayoutName       string   Default|Minimalist|Icon Only
notificationDuration         int      Segundos default
fixedNotificationsVisibility int      0-95 (-1 = como reloj)
```

### /set/settings
```
deviceName    string   Nombre del dispositivo
remotePort    string   Puerto REST
displayDebug  boolean  Debug en overlay
pixelShift    boolean  Anti burn-in (mover cada 2min)
```

---

## Esquinas (corner / hotCorner)

```
+------------------+------------------+
|   top_start      |      top_end     |
|   (arriba izq)   |   (arriba der)   |
|                  |                  |
|                  |                  |
|                  |                  |
| bottom_start     |    bottom_end    |
| (abajo izq)      |   (abajo der)    |
+------------------+------------------+
```

---

## Colores utiles

| Color | Hex | Uso tipico |
|-------|-----|-----------|
| Rojo | `#F44336` | Alertas, errores |
| Naranja | `#FF9800` | Advertencias |
| Amarillo | `#FFEB3B` | Luces, atencion |
| Verde | `#4CAF50` | OK, conectado |
| Azul | `#2196F3` | Info, agua |
| Purpura | `#9C27B0` | Streaming, media |
| Rosa | `#E91E63` | Timer, urgente |
| Cyan | `#00BCD4` | Clima frio |
| Blanco | `#FFFFFF` | Default |

---

## Iconos MDI mas usados

```
mdi:bell              mdi:home              mdi:door-open
mdi:doorbell-video    mdi:cctv              mdi:motion-sensor
mdi:lightbulb         mdi:thermometer       mdi:water-percent
mdi:battery           mdi:battery-alert     mdi:wifi
mdi:account           mdi:account-group     mdi:alert
mdi:weather-sunny     mdi:weather-rainy     mdi:cloud
mdi:lock              mdi:lock-open         mdi:music
mdi:television        mdi:speaker           mdi:check-circle
mdi:close-circle      mdi:information       mdi:package
mdi:mailbox           mdi:timer             mdi:fire
mdi:car               mdi:robot             mdi:home-assistant
```

Catalogo completo: https://pictogrammers.com/library/mdi/

---

## Troubleshooting rapido

| Problema | Solucion |
|----------|----------|
| No responde curl | Verificar IP, puerto 5001, app corriendo |
| MQTT no conecta | Verificar broker IP/puerto/credenciales en app |
| Notificacion no aparece | Verificar permiso "Draw over apps" |
| App se cierra sola | Desactivar optimizacion de bateria |
| Imagen no carga | Verificar URL accesible desde la red del TV |
| Video no reproduce | Verificar protocolo soportado (RTSP/HLS/DASH) |

---

## ADB utiles

```bash
# Dar permiso de overlay
adb shell appops set com.tabdeveloper.tvoverlay SYSTEM_ALERT_WINDOW allow

# Desactivar optimizacion bateria
adb shell dumpsys deviceidle whitelist +com.tabdeveloper.tvoverlay

# Verificar que la app esta corriendo
adb shell pidof com.tabdeveloper.tvoverlay

# Forzar inicio de la app
adb shell am start -n com.tabdeveloper.tvoverlay/.MainActivity
```

---

*Fuente: https://github.com/gugutab/TvOverlay*
