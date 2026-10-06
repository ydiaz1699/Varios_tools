---
slug: codeowners
title: CODEOWNERS — propietarios por ruta (revisores automáticos)
artifact: .github/CODEOWNERS
problem: >
  Asigna automáticamente revisores a los PRs según qué archivos/carpetas se tocan, para
  que los cambios los revise quien conoce esa parte.
applies_to:
  - repo con varias áreas y varios colaboradores/equipos
  - proyecto donde quieres revisión obligatoria por zona
not_for:
  - repo de un solo autor
  - proyectos pequeños sin división por áreas
tags: [codeowners, revisores, github, pr, ownership]
template: templates/CODEOWNERS
owner_source: null
status: ESTABLE
---

# CODEOWNERS

## Qué es

Archivo (`.github/CODEOWNERS`) que mapea rutas → responsables (usuarios/equipos de GitHub).
Cuando un PR toca esas rutas, GitHub pide revisión a esos owners automáticamente. Prowler
lo usa por áreas (SDK, API, dashboard…).

## Cuándo SÍ aplica

- Repo con varias áreas y varios colaboradores/equipos.
- Quieres que ciertas zonas siempre las revise alguien concreto.

## Cuándo NO aplica

- Repo de un solo autor o sin división por áreas.

## Cómo usarlo

Copiar `templates/CODEOWNERS` a `.github/CODEOWNERS`, mapear rutas a tus usuarios/equipos
(`@usuario` o `@org/equipo`). El patrón `*` es el propietario por defecto.

## Fuente / plantilla

- Plantilla: `templates/CODEOWNERS`
- Doc: https://docs.github.com/es/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
