# TvOverlay - Documentacion y Referencia Rapida

> Documentacion local para controlar la app **TvOverlay** sin tener que leer el repositorio original cada vez.

## Que es TvOverlay?

App para Android TV que muestra **overlays** (informacion superpuesta) en tu TV mientras ves contenido.
Permite mostrar notificaciones, notificaciones fijas, reloj, fondo oscuro y mas.

**Repo original:** https://github.com/gugutab/TvOverlay

## Formas de control

| Metodo | Descripcion |
|--------|-------------|
| TvOverlay Remote | App companion para Android |
| REST API | HTTP POST al puerto 5001 del TV |
| MQTT | Pub/Sub compatible con Home Assistant |
| Home Assistant | Integracion via MQTT autodiscovery |

## Requisitos

- Android TV con Android 12+ (API 31+)
- TvOverlay instalado desde Play Store
- Permiso "Draw over other apps" habilitado
- (Opcional) Broker MQTT (Mosquitto, HA addon, etc.)
- (Opcional) Home Assistant con integracion MQTT

## Estructura de esta documentacion

| Archivo | Contenido |
|---------|-----------|
| [MQTT.md](./MQTT.md) | Guia completa de control por MQTT |
| [REST_API.md](./REST_API.md) | Referencia completa de la REST API |
| [EJEMPLOS.md](./EJEMPLOS.md) | Casos de uso y automatizaciones |
| [CHEATSHEET.md](./CHEATSHEET.md) | Resumen rapido copy-paste |

## Setup inicial rapido

1. **Instalar TvOverlay** en Android TV (Play Store)
2. **Habilitar overlay**: Ajustes > Apps > Permisos especiales > Draw over other apps
   - Si no aparece, usar ADB:
     ```bash
     adb shell appops set com.tabdeveloper.tvoverlay SYSTEM_ALERT_WINDOW allow
     ```
3. **Desactivar optimizacion de bateria** (recomendado):
   ```bash
   adb shell dumpsys deviceidle whitelist +com.tabdeveloper.tvoverlay
   ```
4. **Conectar MQTT** (en la app): Ajustes > MQTT > llenar broker, puerto, user, pass
5. **Verificar**: Activar "Display status on change" en MQTT settings para ver si conecta

## Puerto por defecto

- **REST API**: `5001` (configurable en ajustes de la app)
- **MQTT**: Usa el broker que configures (1883 por defecto)

## Nota sobre Home Assistant

Al conectar MQTT, TvOverlay se auto-registra como dispositivo en HA via MQTT Discovery.
El nombre por defecto sera: `TvOverlay - [Modelo del dispositivo]`

---

*Fuente: https://github.com/gugutab/TvOverlay*
