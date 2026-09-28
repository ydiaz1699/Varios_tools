# tools/ — artefacto_scan

Herramienta que **descubre archivos-artefacto en repos de referencia** (Prowler y los
que añadas a `sources.txt`), los **compara con el catálogo** y te dice qué **añadir** o
**mejorar**.

## Qué hace

- **(a) Reporta + descarga referencias:** por cada repo, lista los artefactos que tiene y
  los clasifica: `NUEVO` (no está en tu catálogo) o `YA_TIENES` (candidato a MEJORA).
  Descarga los ejemplos reales a `_referencias/<repo>/` como material de consulta.
- **(b) Siembra fichas:** con `--seed`, crea una ficha `BORRADOR` en `entries/` para cada
  artefacto `NUEVO`, lista para completar y **generalizar**.

## Regla importante (filosofía `codigo_tools`)

La herramienta trae los ejemplos como **REFERENCIA**, **nunca** copia el archivo ajeno
tal cual como tu plantilla. La generalización (quitar lo específico del repo fuente,
dejar placeholders) la hace una persona/LLM al revisar. Por eso `_referencias/` está en
`.gitignore` (no se versiona) y las fichas sembradas nacen en `BORRADOR`.

## Uso

```bash
cd artefactos_proyecto/tools

# Escanear los repos de sources.txt (reporte + descarga referencias)
python3 artefacto_scan.py

# Un repo concreto
python3 artefacto_scan.py --repo prowler-cloud/prowler

# Además crear fichas BORRADOR de los artefactos NUEVO
python3 artefacto_scan.py --seed

# Salida machine-readable
python3 artefacto_scan.py --json
```

## Requisitos

- `gh` (GitHub CLI) autenticado — la herramienta usa `gh api`. Sin dependencias externas.

## Configurar fuentes

Edita `sources.txt` (un `owner/name` por línea). Añade cualquier repo con buenos
artefactos que quieras usar de referencia en el futuro.
