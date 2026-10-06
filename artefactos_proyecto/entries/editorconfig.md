---
slug: editorconfig
title: .editorconfig — estilo consistente entre editores
artifact: .editorconfig
problem: >
  Unifica indentación, fin de línea y charset entre distintos editores/IDEs sin depender
  de la config personal de cada uno.
applies_to:
  - proyecto tocado por varios editores o colaboradores
  - repos donde importa que la indentación no se mezcle (tabs vs espacios)
  - mezcla de lenguajes con estilos distintos (Python 4 espacios, YAML 2, etc.)
not_for:
  - script de un archivo de un solo uso
tags: [editorconfig, estilo, indentacion, formato, editores]
template: templates/editorconfig
owner_source: null
status: ESTABLE
---

# .editorconfig

## Qué es

Archivo que la mayoría de editores/IDEs leen automáticamente para aplicar reglas básicas
de estilo (indentación, charset, fin de línea, quitar espacios finales) sin depender de
la configuración personal de cada persona.

## Cuándo SÍ aplica

- Varios colaboradores o varios editores tocan el repo.
- Mezcla de lenguajes con convenciones distintas de indentación.

## Cuándo NO aplica

- Un único script trivial.

## Cómo usarlo

Copiar `templates/editorconfig` a `.editorconfig` en la raíz. Ajustar por tipo de archivo
(la plantilla trae Python 4 espacios, YAML/JSON 2, Makefile con tabs obligatorios).

## Fuente / plantilla

- Plantilla: `templates/editorconfig`
- Referencia: https://editorconfig.org
