---
slug: alexa-remote2-nodered
title: Hacer hablar a Alexa desde Node-RED sin servicio externo (alexa-remote2 y sim.)
type: repo
problem: >
  Que un Echo (Alexa) hable/anuncie desde Node-RED de forma proactiva SIN un servicio de
  terceros (VoiceMonkey), usando nodos como node-red-contrib-alexa-remote2.
applies_to:
  - notificaciones proactivas n8n/Node-RED → Alexa habla (solo esa dirección)
not_for:
  - comandos de voz Alexa → backend (esto es unidireccional; para bidireccional se necesita Custom Skill + Lambda)
  - producción estable: los nodos usan API NO oficial de Amazon, sin mantenimiento
tags: [alexa, node-red, tts, voicemonkey-alternativa, no-oficial, descartado, domotica]
reference:
  url: https://github.com/ajithvasudevan/node-red-contrib-alexa-remote2
  kind: github
related: []
status: DESCARTADO
evaluated_on: 2026-09-25
---

# alexa-remote2 (Node-RED) — alternativa local a Voice Monkey

## Idea central

Nodos de Node-RED (`node-red-contrib-alexa-remote2`, `node-red-contrib-amazon-echo`, y el
"cakebaked") que hacen que un Echo **hable un texto** directamente, sin pasar por un servicio
externo como Voice Monkey. Se autentican con tu cuenta Amazon (cookie/token). Método visto en
un video de "Diego" (Gmail → MQTT → Node-RED → Alexa habla).

## Qué problema resuelve

Notificaciones proactivas por voz (ej. "llegó un email") sin depender de un tercero.

## Cuándo SÍ aplica

- Solo si quisieras evitar Voice Monkey a toda costa y aceptas la fragilidad — poco recomendable.

## Cuándo NO aplica (por qué está DESCARTADO)

- **API NO oficial de Amazon, sin mantenimiento:** la comunidad de Home Assistant reporta
  (2021→2026) que el nodo "isn't maintained" y el problema recurrente de tener que
  **re-loguearse para renovar la cookie** "a veces cada semanas, a veces cada horas".
  `node-red-contrib-amazon-echo` sigue "unstable or broken" en 2026.
- **Unidireccional:** solo n8n/Node-RED → Alexa (no recibe comandos de voz). El proyecto
  `alexa_y_n8n` del usuario ya lo SUPERA con Custom Skill + AWS Lambda (bidireccional).
- Voice Monkey depende de un tercero pero es **más estable** para este uso puntual.

## Qué llevarte si aplica

- Solo el CONOCIMIENTO de que existe esta vía local (por si algún día sale un nodo mantenido).
- Comparación: para proactivo Alexa, hoy **Voice Monkey > alexa-remote2** por estabilidad.
- El proyecto propio `alexa_y_n8n` ya cubre ambas direcciones; este método sería un downgrade.

## Referencia

- Nodo: https://github.com/ajithvasudevan/node-red-contrib-alexa-remote2
- Nota y motivo en el proyecto propio: `alexa_y_n8n/README.md` (Paso 4, alternativa a Voice Monkey).
- DESCARTADO se conserva para NO re-evaluar este video/método en el futuro.
