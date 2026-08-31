# Referencia: gobernanza de tags de código

## Propósito

Define el contrato reusable para extraer la convención de comentarios de un workspace sin imponer una herramienta, lenguaje o plataforma. El scaffold canónico es [`templates/project-context-bundle/shared/CODING_STYLE.md`](../templates/project-context-bundle/shared/CODING_STYLE.md).

## Decisiones que debe registrar el proyecto

1. Lista exacta de tags aceptados y herramienta que los reconoce.
2. Significado operativo de cada tag y condición de cierre.
3. Reglas para `BUG`, `FIXME` y workarounds temporales.
4. Alcance de advertencias: software, hardware, seguridad o todos, sin asumirlo.
5. Restricciones de recursos y estrategia de memoria solo para los targets afectados.
6. Fuente, snapshot y estado de evidencia de cada regla.

La macro `F()` es un ejemplo condicionado a targets AVR y frameworks compatibles; nunca debe aparecer como una regla universal. Una convención de tags no demuestra propiedades de hardware ni de ejecución.
