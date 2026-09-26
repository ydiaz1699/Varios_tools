# Contribuir a NOMBRE_DEL_PROYECTO

Gracias por contribuir. Sigue estas convenciones.

## Ramas

- Rama base de los PRs: `RAMA_BASE` (ej. `main`).
- Nombra las ramas: `TIPO/descripcion-corta` (ej. `feat/login`, `fix/timeout`).

## Commits

- Formato: `TIPO: resumen en imperativo` (ej. `feat: añade validación de códigos`).
- Tipos habituales: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

## Pull Requests

- Un PR por cambio lógico; describe QUÉ y POR QUÉ.
- Marca los PRs contra `RAMA_BASE`.
- Enlaza el issue relacionado si existe.

## Calidad antes de abrir el PR

```bash
# tests
COMANDO_DE_TESTS
# linters / formato
COMANDO_DE_LINT
```

## Estilo de código

- REGLAS_DE_ESTILO (ej. formateador, longitud de línea, convenciones de nombres).

## Qué NO hacer

- No commitear secretos ni `.env` (usa `.env.example`).
- No romper la rama base; abre PR.
