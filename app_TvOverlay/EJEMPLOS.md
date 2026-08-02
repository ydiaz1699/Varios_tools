# TvOverlay - Ejemplos Practicos y Automatizaciones

## Home Assistant - Automatizaciones YAML

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
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify"
      payload: >-
        {
          "title": "{{ trigger.from_state.attributes.friendly_name }} llego!",
          "message": "Acaba de llegar a casa",
          "smallIcon": "mdi:home-account",
          "color": "#4CAF50",
          "duration": 8
        }
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
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify"
      payload: >-
        {
          "title": "Movimiento detectado!",
          "message": "Camara frontal",
          "image": "http://TU_HA_IP:8123{{ state_attr('camera.frontal', 'entity_picture') }}",
          "smallIcon": "mdi:motion-sensor",
          "color": "#FF0000",
          "duration": 12
        }
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
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify"
      payload: >-
        {
          "title": "Timbre!",
          "message": "Alguien en la puerta",
          "video": "rtsp://192.168.1.60:554/live",
          "smallIcon": "mdi:doorbell-video",
          "color": "#2196F3",
          "duration": 25
        }
mode: single
```

### 4. Notificacion fija - Luz encendida

Aparece un icono fijo mientras la luz esta encendida, desaparece al apagar.

```yaml
alias: TV Overlay - Indicador luz sala
trigger:
  - platform: state
    entity_id: light.sala
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify_fixed"
      payload: >-
        {% if trigger.to_state.state == 'on' %}
        {
          "id": "luz_sala",
          "icon": "mdi:lightbulb",
          "message": "Sala",
          "iconColor": "#FFEB3B",
          "borderColor": "#FFEB3B",
          "visible": true
        }
        {% else %}
        {
          "id": "luz_sala",
          "visible": false
        }
        {% endif %}
mode: single
```

### 5. Notificacion fija - Bateria del telefono

```yaml
alias: TV Overlay - Bateria telefono
trigger:
  - platform: numeric_state
    entity_id: sensor.telefono_battery_level
    below: 30
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify_fixed"
      payload: >-
        {
          "id": "bateria_tel",
          "icon": "mdi:battery-alert",
          "message": "{{ states('sensor.telefono_battery_level') }}%",
          "iconColor": "#FF5722",
          "borderColor": "#FF5722",
          "expiration": "30m"
        }
mode: single
```


### 6. Notificacion fija - Clima/Temperatura

```yaml
alias: TV Overlay - Temperatura exterior
trigger:
  - platform: time_pattern
    minutes: "/15"
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify_fixed"
      payload: >-
        {
          "id": "temp_exterior",
          "icon": "mdi:thermometer",
          "message": "{{ states('sensor.temperatura_exterior') }}C",
          "iconColor": "{% if states('sensor.temperatura_exterior') | float > 30 %}#FF5722{% elif states('sensor.temperatura_exterior') | float < 15 %}#2196F3{% else %}#4CAF50{% endif %}",
          "borderColor": "{% if states('sensor.temperatura_exterior') | float > 30 %}#FF5722{% elif states('sensor.temperatura_exterior') | float < 15 %}#2196F3{% else %}#4CAF50{% endif %}",
          "expiration": "20m"
        }
mode: single
```

### 7. Oscurecer TV automaticamente de noche

```yaml
alias: TV Overlay - Modo nocturno
trigger:
  - platform: sun
    event: sunset
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/set/overlay"
      payload: '{"overlayVisibility": 40}'
mode: single
---
alias: TV Overlay - Modo diurno
trigger:
  - platform: sun
    event: sunrise
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/set/overlay"
      payload: '{"overlayVisibility": 0}'
mode: single
```

### 8. Alerta de puerta/ventana abierta

```yaml
alias: TV Overlay - Puerta abierta mucho tiempo
trigger:
  - platform: state
    entity_id: binary_sensor.puerta_principal
    to: "on"
    for:
      minutes: 5
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify"
      payload: >-
        {
          "title": "Puerta abierta!",
          "message": "La puerta principal lleva 5 min abierta",
          "smallIcon": "mdi:door-open",
          "color": "#FF9800",
          "duration": 15
        }
mode: single
```

### 9. Notificacion al recibir paquete (sensor de correo)

```yaml
alias: TV Overlay - Paquete recibido
trigger:
  - platform: state
    entity_id: binary_sensor.buzon_correo
    to: "on"
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify"
      payload: >-
        {
          "title": "Correo!",
          "message": "Tienes algo en el buzon",
          "smallIcon": "mdi:mailbox-up",
          "color": "#795548",
          "largeIcon": "mdi:package-variant-closed",
          "duration": 10
        }
mode: single
```

### 10. Recordatorio con timer

```yaml
alias: TV Overlay - Timer cocina terminado
trigger:
  - platform: event
    event_type: timer.finished
    event_data:
      entity_id: timer.cocina
action:
  - service: mqtt.publish
    data:
      topic: "tvoverlay/MI_DEVICE/notify"
      payload: >-
        {
          "title": "Timer terminado!",
          "message": "La comida esta lista",
          "smallIcon": "mdi:timer-alert",
          "color": "#E91E63",
          "duration": 20
        }
mode: single
```


---

## Home Assistant - Usando notify service (REST)

Si prefieres usar la integracion REST en vez de MQTT, configura en `configuration.yaml`:

```yaml
notify:
  - name: tvoverlay_sala
    platform: rest
    method: POST_JSON
    resource: http://192.168.1.50:5001/notify
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
```

Luego usarlo en automatizaciones:

```yaml
action:
  - service: notify.tvoverlay_sala
    data:
      title: "Titulo"
      message: "Mensaje"
      data:
        smallIcon: "mdi:bell"
        color: "#FF0000"
        duration: 10
```

---

## Node-RED

### Nodo MQTT Out - Notificacion basica

```json
{
  "topic": "tvoverlay/MI_DEVICE/notify",
  "payload": {
    "title": "Desde Node-RED",
    "message": "Automatizacion funcionando",
    "smallIcon": "mdi:robot",
    "color": "#9C27B0",
    "duration": 8
  }
}
```

Configurar nodo **mqtt out**:
- Server: tu broker MQTT
- Topic: `tvoverlay/MI_DEVICE/notify`
- QoS: 0
- Conectar un nodo **inject** o **function** que genere el payload JSON

---

## ESPHome - Enviar notificacion desde ESP32

Si tienes un ESP32 con ESPHome conectado al mismo broker MQTT:

```yaml
# En tu archivo ESPHome .yaml
mqtt:
  broker: 192.168.1.100
  username: mqtt_user
  password: mqtt_pass

binary_sensor:
  - platform: gpio
    pin: GPIO4
    name: "Boton timbre"
    on_press:
      then:
        - mqtt.publish:
            topic: "tvoverlay/MI_DEVICE/notify"
            payload: '{"title":"Timbre!","message":"Alguien toco el timbre","smallIcon":"mdi:doorbell","color":"#2196F3","duration":15}'
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

---

## Python - Enviar notificaciones

```python
import requests

TV_IP = "192.168.1.50"
TV_PORT = 5001
BASE_URL = f"http://{TV_IP}:{TV_PORT}"

def notify(title, message, icon="mdi:information", color="#03A9F4", duration=7):
    """Enviar notificacion a TvOverlay"""
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
    """Enviar notificacion fija"""
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
    """Configurar opacidad del fondo"""
    r = requests.post(f"{BASE_URL}/set/overlay", json={"overlayVisibility": visibility})
    return r.status_code

# Ejemplos de uso
notify("Hola!", "Desde Python", "mdi:language-python", "#3F51B5", 8)
notify_fixed("temp", "mdi:thermometer", "24C", "#FF9800", "15m")
set_overlay(40)  # Oscurecer 40%
```

---

## Casos de uso avanzados

### Multiples TVs - Enviar a todos

```bash
for DEVICE in "tv_sala" "tv_cuarto" "tv_cocina"; do
  mosquitto_pub -h 192.168.1.100 -u user -P pass \
    -t "tvoverlay/${DEVICE}/notify" \
    -m '{"title":"Alerta general","message":"Mensaje para todos","smallIcon":"mdi:alert","color":"#FF0000"}'
done
```

### Dashboard de estado con notificaciones fijas

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

*Fuente: https://github.com/gugutab/TvOverlay*
