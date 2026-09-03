# Política del catálogo híbrido

## Modelo

```text
motor común
  ├── catalog/boards/       # fichas de placas físicas
  ├── catalog/peripherals/  # fichas de módulos/variantes
  ├── catalog/compatibility/# reglas reutilizables
  └── project-wiring.json   # instancia concreta del proyecto
```

La herramienta y las reglas de validación son comunes; los esquemas y fichas se mantienen separados porque board y peripheral tienen campos y riesgos distintos.

## Regla de fuente de verdad

El catálogo es contexto reutilizable. El código/configuración actual del target tiene precedencia sobre una ficha histórica. Si hay diferencia, registrar `CONTRADICTORIO` o `PENDIENTE_DE_VERIFICAR`; no corregir silenciosamente el proyecto ni el catálogo.

## Reglas de crecimiento

- Una nueva placa física o breakout incompatible obtiene una nueva ficha o variante.
- Un nuevo proyecto sobre la misma placa no duplica la ficha: crea wiring propio.
- Un nuevo módulo con protocolo/voltaje/variante diferente obtiene ficha propia.
- Los índices seleccionan; no repiten toda la información de las fichas.
- Las reglas de compatibilidad no se convierten en prueba de hardware.
- Las fichas concretas deben tener procedencia y modelo cuando el dato dependa de una variante.
- La herramienta debe validar estructura y conflictos obvios, pero dejar la verificación eléctrica/física marcada.
