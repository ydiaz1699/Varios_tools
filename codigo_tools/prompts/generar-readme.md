---
name: generar-readme
description: Genera un README operativo para usuarios y desarrolladores a partir del código y configuración actuales.
---

# Generar README operativo desde el código actual

## Objetivo

Genera un `README.md` que permita a una persona instalar, configurar, ejecutar, diagnosticar y contribuir al proyecto. El README es documentación para humanos: debe ser accionable y conciso, pero no debe afirmar capacidades que el código no implementa.

Este prompt no modifica código ni inventa datos. Si falta información para instalar o ejecutar, lo declara como pendiente.

## Entradas obligatorias

- `PROJECT_ROOT`: raíz del proyecto.
- `TARGET_ID`: target o ensamblaje documentado.
- `SNAPSHOT`: commit, rama, tag o fecha.
- `OUTPUT_PATH`: por defecto `README.md` o una ruta indicada por el usuario.
- `BASELINE_README`: README existente, changelog, mapa y documentación relacionada.

Si hay varios targets o versiones, no escribas un README ambiguo. Separa las instrucciones por target o pide que se elija uno.

## Lectura obligatoria

1. Inventaría y lee completamente código, headers, configuración de build, dependencias, documentación, tests, plantillas de secretos y scripts.
2. Sigue imports/includes y rutas de configuración.
3. Comprueba que cada comando propuesto existe en la configuración o en la documentación actual.
4. Si no puedes leer un archivo o dependencia, detente con `LECTURA_INCOMPLETA`.
5. Compara el README anterior con el código; conserva divergencias en una tabla de auditoría.

## Reglas no negociables

- La fuente de comportamiento es el código/configuración actual; README, comentarios y mapas son baseline.
- No inventar versiones mínimas, consumo, tiempos, URLs, licencia, screenshots, métricas ni problemas.
- No presentar estimaciones como mediciones. Etiquetar `ESTIMADO`.
- No presentar propuestas futuras como features existentes. Usar `PROPUESTO`.
- No mostrar secretos. Usar `[REDACTADO]` y explicar solo el nombre de la variable o archivo.
- Los comandos deben ser copiables y respetar el ecosistema real del proyecto.
- No pedir `chmod`, crear archivos o levantar servicios en un orden imposible; documentar dependencias temporales reales.
- La tabla de problemas es condicional: incluir solo problemas documentados o demostrables. Si no existen, escribirlo explícitamente.
- No afirmar que compila, funciona o fue probado si no se ejecutó esa verificación.

## Procedimiento de extracción

Construye antes de redactar una matriz:

```text
ID | afirmación | fuente | línea/símbolo | evidencia | sección README | estado
```

Extrae:

- propósito real;
- targets y hardware;
- requisitos de software y versiones declaradas;
- comandos de instalación, build, upload, ejecución, monitor y tests;
- configuración y secretos;
- flujo principal y arquitectura mínima;
- estructura real de archivos;
- logs y diagnóstico disponibles;
- problemas demostrables y sus workarounds documentados;
- ausencias que impiden una instalación reproducible.

## Estructura de salida

Usa `templates/README-project.md` como plantilla y adapta u omite secciones que no apliquen:

1. Nombre y resumen.
2. Estado y snapshot documentado.
3. Características implementadas.
4. Requisitos de hardware/software.
5. Instalación rápida, en orden real.
6. Configuración y secretos.
7. Arquitectura y flujo principal.
8. Estructura del proyecto.
9. Uso, comandos y diagnóstico.
10. Problemas documentados, solo si existen.
11. Limitaciones y propuestas no implementadas.
12. Referencias verificables.
13. Licencia solo si existe evidencia.
14. Procedencia y diferencias respecto al README anterior.

## Verificación antes de entregar

- Cada comando aparece en configuración, script o documentación fuente.
- Cada feature marcada como implementada tiene evidencia de código.
- Cada requisito tiene fuente o está marcado pendiente.
- No se expusieron secretos.
- Los targets y versiones no se mezclaron.
- La instalación crea directorios/archivos antes de aplicar permisos o ejecutar.
- Los problemas no fueron inventados para completar una tabla.
- El README anterior fue comparado y sus divergencias no se ocultaron.
- Si falta lectura, el README final no se genera.

Termina con: `README generado con lectura completa y sin verificación de ejecución`, o `README no generado: faltan [archivos/chunks]`.
