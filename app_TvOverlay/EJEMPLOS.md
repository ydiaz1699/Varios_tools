# TvOverlay - Ejemplos Practicos y Automatizaciones

> **Nota:** Las notificaciones (texto, imagen, video) se envian via REST API.
> MQTT solo controla configuracion (visibility, esquina, switches).
> Ver MQTT.md para detalles.

---

## Home Assistant - Automatizaciones con REST API (notificaciones)

### Configuracion previa en configuration.yaml

```yaml
# Opcion 1: notify service REST
notify:
  - name: tvoverlay_sala
    platform: rest
    method: POST_JSON
    resource: http://IP_TV:5001/notify
    verify_ssl: false
    title_param_name: title
    data:
      id: "{{ data.id | default('default') }}"
      appTitle: "{{ data.appTitle | default('Home Assistant') }}"
      color: "{{ data.color | default('#03A9F4') }}"
      image: "{{ data.image | default(null) }}"
      video: "{{ data.video | default(null) }}"
      smallIcon: "{{ data.smallIcon | default('mdi:home-assistant') }}"
      largeIcon: "{{ data.largeIcon | default(null) }}"
      corner: "{{ data.corner | default(null) }}"
      duration: "{{ data.duration | default(7) }}"

# Opcion 2: rest_command (mas flexible)
rest_command:
  tvoverlay_notify:
    url: "http://IP_TV:5001/notify"
    method: POST
    content_type: "application/json"
    payload: '{{ payload }}'

  tvoverlay_notify_fixed:
    url: "http://IP_TV:5001/notify_fixed"
    method: POST
    content_type: "application/json"
    payload: '{{ payload }}'
```

---

### 1. Notificacion cuando alguien llega a casa

```yaml
alias: Persona llega a casa - TV Overlay
trigger:
  - platform: state
    entity_id:
      - person.papa
      - person.mama
    to: home
    from: not_home
action:
  - service: notify.tvoverlay_sala
    data:
      title: "{{ trigger.from_state.attributes.friendly_name }} llego!"
      message: "Acaba de llegar a casa"
      data:
        smallIcon: "mdi:home-account"
        color: "#4CAF50"
        duration: 8
mode: single
```

### 2. Mostrar camara al detectar movimiento

```yaml
alias: Movimiento camara frontal - TV Overlay
trigger:
  - platform: state
    entity_id: binary_sensor.camara_frontal_motion
    to: "on"
action:
  - service: notify.tvoverlay_sala
    data:
      title: "Movimiento detectado!"
      message: "Camara frontal"
      data:
        image: "http://TU_HA_IP:8123{{ state_attr('camera.frontal', 'entity_picture') }}"
        smallIcon: "mdi:motion-sensor"
        color: "#FF0000"
        duration: 12
mode: single
```

### 3. Timbre - Mostrar video en vivo de la camara

```yaml
alias: Timbre sonando - Video en TV
trigger:
  - platform: state
    entity_id: binary_sensor.timbre_ring
    to: "on"
action:
  - service: notify.tvoverlay_sala
    data:
      title: "Timbre!"
      message: "Alguien en la puerta"
      data:
        video: "rtsp://192.168.1.60:554/live"
        smallIcon: "mdi:doorbell-video"
        color: "#2196F3"
        duration: 25
mode: single
```

### 4. Notificacion fija - Luz encendida (REST)

```yaml
alias: TV Overlay - Indicador luz sala
trigger:
  - platform: state
    entity_id: light.sala
action:
  - service: rest_command.tvoverlay_notify_fixed
    data:
      payload: >-
        {% if trigger.to_state.state == 'on' %}
        {"id":"luz_sala","icon":"mdi:lightbulb","message":"Sala","iconColor":"#FFEB3B","borderColor":"#FFEB3B","visible":true}
        {% else %}
        {"id":"luz_sala","visible":false}
        {% endif %}
mode: single
```

### 5. Notificacion fija - Bateria del telefono (REST)

```yaml
alias: TV Overlay - Bateria telefono
trigger:
  - platform: numeric_state
    entity_id: sensor.telefono_battery_level
    below: 30
action:
  - service: rest_command.tvoverlay_notify_fixed
    data:
      payload: >-
        {"id":"bateria_tel","icon":"mdi:battery-alert","message":"{{ states('sensor.telefono_battery_level') }}%","iconColor":"#FF5722","borderColor":"#FF5722","expiration":"30m"}
mode: single
```

### 6. Notificacion fija - Temperatura (REST)

```yaml
alias: TV Overlay - Temperatura exterior
trigger:
  - platform: time_pattern
    minutes: "/15"
action:
  - service: rest_command.tvoverlay_notify_fixed
    data:
      payload: >-
        {"id":"temp_exterior","icon":"mdi:thermometer","message":"{{ states('sensor.temperatura_exterior') }}C","iconColor":"{% if states('sensor.temperatura_exterior') | float > 30 %}#FF5722{% elif states('sensor.temperatura_exterior') | float < 15 %}#2196F3{% else %}#4CAF50{% endif %}","borderColor":"{% if states('sensor.temperatura_exterior') | float > 30 %}#FF5722{% elif states('sensor.temperatura_exterior') | float < 15 %}#2196F3{% else %}#4CAF50{% endif %}","expiration":"20m"}
mode: single
```

---

## Home Assistant - Automatizaciones con MQTT (configuracion)

> Topics confirmados en instalacion real (2026-08-02). El patron repite el nombre
> de la funcion al final del topic (ej. `hot_corner/set/hot_corner`), no es un error
> de tipeo. Reemplazar `<DEVICE_ID>` por el ID real de tu equipo (ver MQTT.md para
> como encontrarlo).

### 7. Oscurecer TV automaticamente de noche

✅ Topic y comportamiento confirmados.

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

### 8. Mover esquina segun hora del dia

✅ Topic y comportamiento confirmados.

```yaml
alias: TV Overlay - Esquina nocturna
trigger:
  - platform: time
    at: "22:00:00"
action:
  - service: mqtt.publish
    data:
      topic: "tv_overlay/<DEVICE_ID>/hot_corner/set/hot_corner"
      payload: "Bottom Right"
mode: single
```

### 9. Desactivar notificaciones durante pelicula

> ⚠️ **No probado en esta sesion.** El topic se infiere por analogia con la entidad
> `display_notification` que vimos en MQTT Discovery, pero el patron exacto
> (`set/display_notification` al final, singular) no fue verificado enviando el
> comando y confirmando el cambio de estado. Probar antes de confiar en produccion.

```yaml
alias: TV Overlay - Silenciar durante pelicula
trigger:
  - platform: state
    entity_id: media_player.tv_sala
    to: "playing"
action:
  - service: mqtt.publish
    data:
      topic: "tv_overlay/<DEVICE_ID>/display_notification/set/display_notification"
      payload: "false"
mode: single
```

```yaml
alias: TV Overlay - Reactivar al pausar
trigger:
  - platform: state
    entity_id: media_player.tv_sala
    from: "playing"
action:
  - service: mqtt.publish
    data:
      topic: "tv_overlay/<DEVICE_ID>/display_notification/set/display_notification"
      payload: "true"
mode: single
```

---

## Home Assistant - Combinando REST + MQTT

### 10. Alerta de puerta abierta + oscurecer pantalla

✅ Ambas partes (REST y MQTT) confirmadas por separado.

```yaml
alias: TV Overlay - Puerta abierta mucho tiempo
trigger:
  - platform: state
    entity_id: binary_sensor.puerta_principal
    to: "on"
    for:
      minutes: 5
action:
  # Notificacion via REST
  - service: notify.tvoverlay_sala
    data:
      title: "Puerta abierta!"
      message: "La puerta principal lleva 5 min abierta"
      data:
        smallIcon: "mdi:door-open"
        color: "#FF9800"
        duration: 15
  # Bajar brillo via MQTT
  - service: mqtt.publish
    data:
      topic: "tv_overlay/<DEVICE_ID>/visibility/level/command"
      payload: "30"
mode: single
```

---

## Scripts Bash - Notificaciones desde terminal

### Script: notificar_tv.sh

```bash
#!/bin/bash
# Uso: ./notificar_tv.sh "Titulo" "Mensaje" [icono] [color] [duracion]

TV_IP="192.168.1.50"
TV_PORT="5001"

TITLE="${1:-Notificacion}"
MESSAGE="${2:-Sin mensaje}"
ICON="${3:-mdi:information}"
COLOR="${4:-#03A9F4}"
DURATION="${5:-7}"

curl -s -X POST "http://${TV_IP}:${TV_PORT}/notify" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"${TITLE}\",
    \"message\": \"${MESSAGE}\",
    \"smallIcon\": \"${ICON}\",
    \"color\": \"${COLOR}\",
    \"duration\": ${DURATION}
  }"

echo " -> Notificacion enviada"
```

**Uso:**
```bash
chmod +x notificar_tv.sh
./notificar_tv.sh "Backup completo" "NAS backup terminado" "mdi:cloud-check" "#4CAF50" 10
```

### Script: oscurecer_tv.sh (via MQTT)

✅ Topic confirmado.

```bash
#!/bin/bash
# Uso: ./oscurecer_tv.sh [nivel 0-95]

BROKER="192.168.1.100"
USER="mqtt_user"
PASS="mqtt_pass"
DEVICE_ID="TU_DEVICE_ID"
NIVEL="${1:-0}"

mosquitto_pub -h "$BROKER" -u "$USER" -P "$PASS" \
  -t "tv_overlay/${DEVICE_ID}/visibility/level/command" \
  -m "$NIVEL"

echo " -> Overlay: ${NIVEL}%"
```

---

## Python - Enviar notificaciones (REST)

```python
import requests

TV_IP = "192.168.1.50"
TV_PORT = 5001
BASE_URL = f"http://{TV_IP}:{TV_PORT}"

def notify(title, message, icon="mdi:information", color="#03A9F4", duration=7):
    """Enviar notificacion a TvOverlay via REST"""
    payload = {
        "title": title,
        "message": message,
        "smallIcon": icon,
        "color": color,
        "duration": duration
    }
    r = requests.post(f"{BASE_URL}/notify", json=payload)
    return r.status_code

def notify_fixed(id, icon, message, icon_color="#FFFFFF", expiration=None):
    """Enviar notificacion fija via REST"""
    payload = {
        "id": id,
        "icon": icon,
        "message": message,
        "iconColor": icon_color,
        "borderColor": icon_color
    }
    if expiration:
        payload["expiration"] = expiration
    r = requests.post(f"{BASE_URL}/notify_fixed", json=payload)
    return r.status_code

def set_overlay(visibility=0):
    """Configurar opacidad del fondo via REST"""
    r = requests.post(f"{BASE_URL}/set/overlay", json={"overlayVisibility": visibility})
    return r.status_code

# Ejemplos de uso
notify("Hola!", "Desde Python", "mdi:language-python", "#3F51B5", 8)
notify_fixed("temp", "mdi:thermometer", "24C", "#FF9800", "15m")
set_overlay(40)
```

---

## ESPHome - Controlar config via MQTT desde ESP32

```yaml
mqtt:
  broker: 192.168.1.100
  username: mqtt_user
  password: mqtt_pass

binary_sensor:
  - platform: gpio
    pin: GPIO4
    name: "Boton oscurecer"
    on_press:
      then:
        - mqtt.publish:
            topic: "tv_overlay/TU_DEVICE_ID/visibility/level/command"
            payload: "50"
    on_release:
      then:
        - mqtt.publish:
            topic: "tv_overlay/TU_DEVICE_ID/visibility/level/command"
            payload: "0"
```

> Para enviar notificaciones desde ESP32, usar HTTP POST (REST API) en vez de MQTT:
> ```yaml
> http_request:
>   - platform: esphome
>     url: "http://IP_TV:5001/notify"
>     method: POST
>     headers:
>       Content-Type: application/json
>     body: '{"title":"Timbre!","message":"Alguien toco","smallIcon":"mdi:doorbell","color":"#2196F3","duration":15}'
> ```

---

## Casos de uso avanzados

### Dashboard de estado con notificaciones fijas (REST)

```bash
# Temperatura
curl -s -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{"id":"dash_temp","icon":"mdi:thermometer","message":"24C","iconColor":"#4CAF50","borderColor":"#4CAF50"}'

# Humedad
curl -s -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{"id":"dash_hum","icon":"mdi:water-percent","message":"65%","iconColor":"#2196F3","borderColor":"#2196F3"}'

# Personas en casa
curl -s -X POST http://192.168.1.50:5001/notify_fixed \
  -H "Content-Type: application/json" \
  -d '{"id":"dash_home","icon":"mdi:account-group","message":"3","iconColor":"#9C27B0","borderColor":"#9C27B0"}'
```

---

## Resumen de estado de verificacion (2026-08-02)

| # | Ejemplo | Estado |
|---|---------|--------|
| 1-3 | Notificaciones REST via `notify.tvoverlay_sala` | ✅ Patron base confirmado (title/message/duration) |
| 4-6 | Notificaciones fijas REST | ⚠️ No probado en esta sesion, hereda campos de `/notify_fixed` documentados |
| 7 | Oscurecer/aclarar por MQTT (`visibility`) | ✅ Confirmado |
| 8 | Hot corner por MQTT | ✅ Confirmado |
| 9 | Silenciar notificaciones por MQTT | ⚠️ No probado, topic inferido |
| 10 | Combinado REST + MQTT | ✅ Cada parte confirmada por separado |

---

*Fuente: https://github.com/gugutab/TvOverlay + verificacion en instalacion real (2026-08-02)*
