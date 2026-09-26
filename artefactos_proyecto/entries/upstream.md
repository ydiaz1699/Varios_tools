---
slug: upstream
title: UPSTREAM.md — procedencia de un espejo/fork
artifact: UPSTREAM.md
problem: >
  Documenta de dónde viene una copia (mirror/fork) de un repo ajeno: fuente, autor,
  licencia, commit espejado y motivo, para no perder la atribución ni el origen.
applies_to:
  - hacer un mirror o fork de un repo de otra persona
  - preservar un proyecto ajeno "por si el original se borra"
  - vendorizar código externo dentro de un repo propio
not_for:
  - repos 100% propios sin código de terceros
  - dependencias gestionadas por un package manager (ya tienen su lockfile)
tags: [procedencia, mirror, fork, licencia, atribucion, upstream]
template: templates/UPSTREAM.md
owner_source: null
status: ESTABLE
---

# UPSTREAM.md

## Qué es

Un archivo en la raíz de un espejo/fork que registra su **procedencia**: repo original,
autor, licencia, commit exacto espejado, fecha y motivo. Es la forma de respetar la
atribución (sobre todo con licencias MIT/BSD) y de saber contra qué re-sincronizar.

## Cuándo SÍ aplica

- Copias un repo ajeno a tu cuenta (mirror/fork) por si desaparece.
- Metes código de terceros dentro de un repo tuyo (vendoring).

## Cuándo NO aplica

- El repo es enteramente tuyo.
- El código externo entra como dependencia versionada (npm/pip/go.mod).

## Cómo usarlo

Copiar `templates/UPSTREAM.md` a la raíz del mirror y rellenar: URL original, autor,
licencia, commit (`git rev-parse HEAD` del original), fecha y motivo. **Conservar el
`LICENSE` original intacto.**

## Fuente / plantilla

- Plantilla: `templates/UPSTREAM.md`
- Caso real: espejo `ydiaz1699/tasker-mcp-dceluis` (de `dceluis/tasker-mcp`, MIT).
