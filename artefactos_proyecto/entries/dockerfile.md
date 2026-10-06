---
slug: dockerfile
title: Dockerfile — imagen contenedor del proyecto
artifact: Dockerfile
problem: >
  Define cómo empaquetar el proyecto en una imagen Docker reproducible, para desplegarlo
  igual en cualquier máquina.
applies_to:
  - servicio/app que se despliega en contenedor (tu ecosistema NAS es Docker)
  - MCP server o herramienta que quieres aislar/portar
not_for:
  - librería que se instala por package manager (pip/npm), sin runtime propio
  - script local de un solo uso
tags: [docker, dockerfile, contenedor, despliegue, imagen, nas]
template: templates/Dockerfile
owner_source: null
status: ESTABLE
---

# Dockerfile

## Qué es

Receta para construir una imagen Docker: base, dependencias, copia del código y comando
de arranque. El contenido concreto es **muy dependiente del lenguaje**, así que la
plantilla es un esqueleto genérico comentado (no la copia específica de Prowler).

## Cuándo SÍ aplica

- Despliegas el proyecto en contenedor (encaja con tu NAS, que es Docker).
- Quieres aislar/portar un servicio o MCP.

## Cuándo NO aplica

- Es una librería que se instala por pip/npm sin runtime propio.
- Script local trivial.

## Cómo usarlo

Copiar `templates/Dockerfile`, elegir la imagen base de tu lenguaje y ajustar. Buenas
prácticas: fijar versiones (no `latest`), usuario no-root, multi-stage si el build es
pesado, y un `.dockerignore` para no meter basura en la imagen.

## Fuente / plantilla

- Plantilla: `templates/Dockerfile` (esqueleto genérico, elige tu base).
- Referencia real (muy específica, solo mirar): `tools/_referencias/prowler-cloud__prowler/Dockerfile`.
