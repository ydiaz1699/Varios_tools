# Makefile — atajos del proyecto. Las recetas van indentadas con TAB real, no espacios.
# Uso: make <objetivo>. `make help` lista los disponibles.

.DEFAULT_GOAL := help
.PHONY: help install test lint run clean

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'

install:  ## Instala dependencias
	COMANDO_DE_INSTALACION

test:  ## Ejecuta los tests
	COMANDO_DE_TESTS

lint:  ## Linter / formato
	COMANDO_DE_LINT

run:  ## Arranca el proyecto
	COMANDO_PARA_ARRANCAR

clean:  ## Limpia artefactos generados
	rm -rf build dist *.egg-info .pytest_cache
