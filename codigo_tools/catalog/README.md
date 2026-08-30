# Catálogo híbrido de hardware

Esta familia usa un motor común con catálogos separados por tipo de objeto:

```text
catalog/
├── boards/       # modelos físicos de placas y sus variantes
├── peripherals/  # módulos, sensores, displays, radios y actuadores
├── compatibility/# reglas generales y advertencias de interoperabilidad
└── schemas/      # contratos de datos
```

## Regla de separación

- Si un dato es verdadero para una placa aunque ningún proyecto la use, pertenece a `boards/`.
- Si un dato describe un módulo independientemente de cómo se conecte, pertenece a `peripherals/`.
- Si describe qué se conectó, a qué pin, con qué dirección o adaptador, pertenece al manifest de wiring del proyecto.
- Si describe una regla de compatibilidad reutilizable, pertenece a `compatibility/` y debe indicar su evidencia.

Una ficha genérica nunca debe contener el wiring de un proyecto concreto. Un proyecto referencia una placa y sus periféricos; no copia sus tablas.

## Procedencia y estados

Cada campo técnico importante debe incluir procedencia cuando sea posible: fuente, referencia y estado. Los valores dependientes de variante, breakout, datasheet o medición no deben presentarse como universales.

Estados permitidos para hechos técnicos:

```text
OBSERVADO_EN_CODIGO
OBSERVADO_EN_BUILD
DOCUMENTADO
ESTIMADO
CONTRADICTORIO
PENDIENTE_DE_VERIFICAR
VERIFICADO_EN_HARDWARE
```

La ficha es contexto reusable, no una autoridad para sobrescribir el código del proyecto. Si el catálogo y el firmware difieren, el resultado es `CONTRADICTORIO` o `PENDIENTE_DE_VERIFICAR`.

## Flujo

1. Seleccionar o crear la ficha de la placa física.
2. Seleccionar o crear las fichas de periféricos y variantes exactas.
3. Crear el manifest de wiring del proyecto.
4. Ejecutar `hardware_catalog.py validate` sobre cada ficha y el wiring.
5. Ejecutar `hardware_catalog.py check-project` para referencias, pines y señales.
6. Comparar contra el código/configuración y añadir procedencia.
7. Generar notas y diagrama desde el wiring validado, nunca desde el catálogo solo.

## Variantes

Un mismo MCU no implica la misma placa: un breakout diferente puede cambiar pinout, flash, USB, alimentación o pines de boot. Modelar las variantes explícitamente y no fusionar fichas por nombre comercial parecido.

## Herramienta

```bash
python3 codigo_tools/tools/hardware_catalog.py validate --type board catalog/boards/_template-board.json
python3 codigo_tools/tools/hardware_catalog.py validate --type peripheral catalog/peripherals/_template-peripheral.json
python3 codigo_tools/tools/hardware_catalog.py validate --type wiring templates/project-wiring.json
python3 codigo_tools/tools/hardware_catalog.py search --type board --catalog-root catalog esp32
python3 codigo_tools/tools/hardware_catalog.py check-project --catalog-root catalog path/to/project-wiring.json
```

La herramienta valida estructura, referencias y conflictos obvios. No sustituye el datasheet, el análisis del código ni una prueba física.
