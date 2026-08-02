# TvOverlay - Cheatsheet (Copy-Paste Rapido)

> Reemplazar `IP_TV`, `BROKER_IP`, `<DEVICE_ID>`, `USER`, `PASS` con tus valores reales.
> Para encontrar tu DEVICE_ID ver MQTT.md seccion "Como encontrar tu DEVICE_ID".

---

## REST API — Notificaciones (curl)

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

---

## REST API — Configuracion (curl)

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

### Cambiar esquina (REST usa formato diferente a MQTT)
```bash
curl -X POST http://IP_TV:5001/set/overlay -H "Content-Type: application/json" \
  -d '{"hotCorner":"top_end"}'
```

### Consultar estado actual
```bash
curl http://IP_TV:5001/get
curl http://IP_TV:5001/get/overlay
curl http://IP_TV:5001/get/fixed_notifications
```

### Configurar MQTT remotamente
```bash
curl -X POST http://IP_TV:5001/set/mqtt -H "Content-Type: application/json" \
  -d '{"mqttConfig":{"broker":"BROKER_IP","port":1883,"user":"USER","password":"PASS"}}'
```

### Eliminar config MQTT / reiniciar servicio
```bash
curl -X DELETE http://IP_TV:5001/delete/mqtt
curl -X POST http://IP_TV:5001/set/restart_service
```


---

## MQTT — Topics REALES (mosquitto_pub)

> Prefijo real: `tv_overlay` (con guion bajo). Payloads: texto plano.

### Oscurecer pantalla (0-95)
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/visibility/level/command" -m "50"
```

### Quitar oscuridad
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/visibility/level/command" -m "0"
```

### Visibilidad del reloj (0-95)
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/clock_visibility/level/command" -m "80"
```

### Cambiar esquina (MQTT usa mayusculas con espacio)
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/hot_corner/set" -m "Top Left"
```

Valores: `Top Left` | `Top Right` | `Bottom Left` | `Bottom Right`

### Desactivar notificaciones
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_notifications/set" -m "false"
```

### Activar notificaciones
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_notifications/set" -m "true"
```

### Activar/desactivar fijas
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/display_fixed_notifications/set" -m "true"
```

### Pixel shift (anti burn-in)
```bash
mosquitto_pub -h BROKER_IP -u USER -P PASS \
  -t "tv_overlay/<DEVICE_ID>/pixel_shift/set" -m "true"
```

### Espiar todos los topics (debug)
```bash
mosquitto_sub -h BROKER_IP -u USER -P PASS -t "tv_overlay/#" -v
```

---

## Tabla resumen MQTT

| Funcion | Topic (despues de tv_overlay/DEVICE_ID/) | Payload |
|---------|------------------------------------------|---------|
| Oscurecer | `visibility/level/command` | `0`-`95` |
| Reloj | `clock_visibility/level/command` | `0`-`95` |
| Esquina | `hot_corner/set` | `Top Left` / `Top Right` / `Bottom Left` / `Bottom Right` |
| Notificaciones | `display_notifications/set` | `true` / `false` |
| Fijas | `display_fixed_notifications/set` | `true` / `false` |
| Pixel shift | `pixel_shift/set` | `true` / `false` |
| Debug | `display_debug/set` | `true` / `false` |

---

## MQTT vs REST — Diferencias clave

| | MQTT | REST API |
|-|------|----------|
| Prefijo | `tv_overlay` | `http://IP:5001` |
| Payloads | Texto plano | JSON |
| Esquinas | `Top Left`, `Bottom Right` | `top_start`, `bottom_end` |
| Notificaciones | **NO disponible via MQTT** | `POST /notify` |
| Fixed notifications | **NO disponible via MQTT** | `POST /notify_fixed` |

> Para enviar notificaciones (texto, imagen, video) usar SIEMPRE la REST API.
> MQTT solo controla ajustes de configuracion (visibility, esquina, switches).


---

## Home Assistant (Servicios) — Topics reales

### Oscurecer TV
```yaml
service: mqtt.publish
data:
  topic: "tv_overlay/<DEVICE_ID>/visibility/level/command"
  payload: "40"
```

### Mover esquina
```yaml
service: mqtt.publish
data:
  topic: "tv_overlay/<DEVICE_ID>/hot_corner/set"
  payload: "Top Right"
```

### Enviar notificacion (via REST, no MQTT)
```yaml
service: rest_command.tvoverlay_notify
# Requiere configurar rest_command en configuration.yaml
# O usar el notify service REST (ver EJEMPLOS.md)
```

---

## Esquinas

```
+------------------+------------------+
|   Top Left       |     Top Right    |
|   (MQTT)         |     (MQTT)       |
|   top_start      |     top_end      |
|   (REST)         |     (REST)       |
|                  |                  |
|   Bottom Left    |   Bottom Right   |
|   (MQTT)         |     (MQTT)       |
|   bottom_start   |     bottom_end   |
|   (REST)         |     (REST)       |
+------------------+------------------+
```

---

## Referencia rapida de campos REST /notify

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
| Blanco | `#FFFFFF` | Default |

---

## Iconos MDI mas usados

```
mdi:bell              mdi:home              mdi:door-open
mdi:doorbell-video    mdi:cctv              mdi:motion-sensor
mdi:lightbulb         mdi:thermometer       mdi:water-percent
mdi:battery           mdi:battery-alert     mdi:wifi
mdi:account           mdi:alert             mdi:weather-sunny
mdi:lock              mdi:television        mdi:home-assistant
```

Catalogo completo: https://pictogrammers.com/library/mdi/

---

## Troubleshooting rapido

| Problema | Solucion |
|----------|----------|
| curl no responde | Verificar IP, puerto 5001, app corriendo |
| MQTT no conecta | Verificar broker IP/puerto/credenciales en app |
| Topic no hace nada | Verificar prefijo `tv_overlay` (con guion bajo) |
| Esquina no cambia via MQTT | Usar `Top Left` (mayusculas+espacio), no `top_start` |
| Notificacion via MQTT no funciona | Normal — notificaciones solo van por REST API |
| Notificacion no aparece (REST) | Verificar permiso "Draw over apps" |
| App se cierra sola | Desactivar optimizacion de bateria |

---

## ADB utiles

```bash
adb shell appops set com.tabdeveloper.tvoverlay SYSTEM_ALERT_WINDOW allow
adb shell dumpsys deviceidle whitelist +com.tabdeveloper.tvoverlay
adb shell pidof com.tabdeveloper.tvoverlay
adb shell am start -n com.tabdeveloper.tvoverlay/.MainActivity
```

---

*Fuente: https://github.com/gugutab/TvOverlay + verificacion en instalacion real (2026-08-02)*
