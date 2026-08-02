# TvOverlay - Documentacion y Referencia Rapida

> Documentacion local para controlar la app **TvOverlay** sin tener que leer el repositorio original cada vez.

**Ultima sincronizacion con el repo original:** 2026-08-02

## Que es TvOverlay?

App para Android TV que muestra **overlays** (informacion superpuesta) en tu TV mientras ves contenido.
Permite mostrar notificaciones, notificaciones fijas, reloj, fondo oscuro y mas.

**Repo original:** https://github.com/gugutab/TvOverlay

## Formas de control

| Metodo | Que controla | Protocolo |
|--------|--------------|-----------|
| TvOverlay Remote | Todo | App companion Android |
| REST API | Todo (notificaciones + config) | HTTP POST/GET/DELETE a puerto 5001 |
| MQTT | Solo configuracion (visibility, esquina, switches) | Pub/Sub texto plano |
| Home Assistant | Todo (REST para notif, MQTT para config) | Combinado |

> **Descubrimiento clave:** Las notificaciones (texto, imagen, video) solo se envian
> por REST API. MQTT solo controla ajustes de configuracion del overlay.

## Requisitos

- Android TV con Android 12+ (API 31+)
- TvOverlay instalado desde Play Store
- Permiso "Draw over other apps" habilitado
- (Opcional) Broker MQTT (Mosquitto, HA addon, etc.)
- (Opcional) Home Assistant con integracion MQTT

## Estructura de esta documentacion

| Archivo | Contenido |
|---------|-----------|
| [MQTT.md](./MQTT.md) | Topics REALES confirmados, payloads, descubrimiento de DEVICE_ID |
| [REST_API.md](./REST_API.md) | Referencia completa de la REST API (notificaciones + config) |
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
6. **Encontrar tu DEVICE_ID**: Suscribirse a `tv_overlay/#` y buscar tu ID (ver MQTT.md)

## Puertos / Protocolos

- **REST API**: puerto `5001` (configurable) — para notificaciones y todo lo demas
- **MQTT broker**: puerto `1883` (por defecto) — para ajustes de configuracion
- **Prefijo MQTT real**: `tv_overlay` (con guion bajo, NO `tvoverlay`)

## Resumen rapido MQTT vs REST

| Quiero... | Usar |
|-----------|------|
| Enviar notificacion con texto/imagen/video | REST API: `POST /notify` |
| Mostrar icono fijo (bateria, temp, etc.) | REST API: `POST /notify_fixed` |
| Oscurecer/aclarar la pantalla | MQTT o REST |
| Cambiar esquina de notificaciones | MQTT o REST |
| Activar/desactivar notificaciones | MQTT o REST |
| Activar pixel shift | MQTT o REST |
| Consultar estado actual | REST API: `GET /get` |

---

*Fuente: https://github.com/gugutab/TvOverlay + verificacion en instalacion real*
