---
slug: artemis-android-automation
title: ARTEMIS (google/artemis) — automatización de Android por lenguaje natural + MCP
type: repo
origin: external
problem: >
  Que un LLM/IDE de IA maneje un teléfono Android real (o emulador) desde lenguaje natural,
  con servidor MCP nativo, para automatizar apps y testing de UI end-to-end.
applies_to:
  - dar a un agente/LLM control de un dispositivo Android real por MCP (Antigravity, Claude Code, Codex, Cursor, Windsurf)
  - testing de UI / QA móvil end-to-end desde lenguaje natural (planes, logs, capturas, reportes)
  - automatizar flujos cotidianos entre apps Android (Maps, YouTube, Ajustes...)
  - integrar automatización móvil en pytest / CI-CD vía SDK Python
not_for:
  - control de Android por ADB SIN un LLM/agente (usar android_agent_bridge o scripts ADB propios)
  - Tasker / automatización on-device declarativa (ver Tasker_mcp)
  - firmware/embebidos ESP sin dispositivo Android ni agente
  - iOS (en roadmap, aún no soportado)
tags: [android, automatizacion, mcp, adb, testing, ui, llm, google, scrcpy, uiautomator, vlm]
reference:
  url: https://github.com/google/artemis
  kind: github
related:
  - "Control Android por ADB (agent-first) — repos/android_agent_bridge (ecosistema ydiaz1699)"
  - "Tasker por MCP — repos/Tasker_mcp (ecosistema ydiaz1699)"
  - "AndroidWorld (benchmark) — https://github.com/google-research/android_world"
status: REVISADO_PARCIAL
evaluated_on: 2026-09-25
---

# ARTEMIS — automatización de Android por lenguaje natural + MCP

## Idea central

Herramienta de Google (Apache-2.0) que convierte instrucciones en lenguaje natural
en acciones reales sobre un teléfono/emulador Android, para que asistentes de IA y
suites de testing "usen el móvil como un humano". Trae un servidor MCP nativo, una
consola web con espejo de pantalla en vivo, CLI y SDK de Python. Localiza elementos
de forma multimodal (jerarquía de accesibilidad + OCR + modelos visuales, con
fallback a coordenadas). Afirma 99%+ en el benchmark AndroidWorld de Google Research.

## Qué problema resuelve

El asistente de IA no puede "tocar" un móvil real: ARTEMIS pone el dispositivo dentro
del bucle del agente (vía MCP) para reproducir bugs, ejecutar tests de UI y automatizar
tareas entre apps, recogiendo Logcat y capturas como diagnóstico — sin escribir un
harness de ADB a mano.

## Cuándo SÍ aplica

- Quieres que Antigravity / Claude Code / Codex / Cursor / Windsurf conduzcan un teléfono real por MCP.
- QA/testing de UI móvil end-to-end desde una frase ("abre login, verifica popups, devuelve capturas").
- Automatizar flujos cotidianos multi-app en Android por lenguaje natural.
- Integrar automatización móvil en pytest/CI-CD con salidas tipadas (Pydantic) vía SDK Python.

## Cuándo NO aplica

- Solo necesitas control ADB programático sin un LLM → `android_agent_bridge` o scripts ADB.
- Automatización on-device declarativa tipo Tasker → `Tasker_mcp`.
- Dispositivos iOS (en roadmap, aún no).
- Sin dispositivo Android/emulador ni depuración USB disponible.

## Qué llevarte si aplica

- **Patrón MCP para dispositivos físicos**: tools `mobile_run_task`, `mobile_manage_task`,
  `mobile_get_device_state`, `mobile_inspect_trace`, `mobile_diagnose` (config Codex/Antigravity/Claude en README).
- **Perfiles de ejecución Flash vs Pro**: Flash = bucle reactivo rápido (~3–5s/paso, sin plan);
  Pro = grafo multi-agente Planner/Operator/Checker con safety-net y verificación. Idea reutilizable de arquitectura.
- **`mcp_server/rules.md`**: "Mobile Testing Mindset" (exploración activa antes de actuar, locator
  dynamic-first con fallback a coordenadas, compensación de latencia) — patrón de reglas para agentes.
- **Localización multimodal** (accesibilidad + OCR + VLM para Canvas/Compose/Flutter) y compresión
  de historial (screenshots → resúmenes visuales) para no saturar contexto.
- **Comparar con `android_agent_bridge`** (propio): ARTEMIS es más completo (NL+MCP+benchmark)
  pero pesado (instala helper de accesibilidad, ADB/scrcpy/FFmpeg/uv); el propio es más ligero y a medida.

## Referencia

- Fuente: https://github.com/google/artemis
- Leer completo SOLO si vas a integrar automatización de Android por MCP en un agente.
  Ojo: instala un "Artemis Accessibility Helper" en el teléfono en la primera tarea (desinstalable).
