# Generar una arquitectura verificable y parametrizable

## Propósito

Genera un documento de arquitectura para `[PROJECT_ROOT]` a partir del proyecto completo y de la evidencia disponible. El resultado debe orientar a mantenedores y a otros agentes sin presentar como hechos los datos que solo aparecen en documentación, comentarios o configuración no ejecutada.

Este prompt recrea un mapa arquitectónico; no copia firmware, hardware, nombres, endpoints, pines, topics, credenciales ni valores de otro proyecto.

## Entradas

```text
PROJECT_ROOT: [raíz absoluta del proyecto]
TARGET_ID: [target, variante o sistema analizado]
SNAPSHOT: [commit/tag/fecha o UNKNOWN]
RELATED_DOCUMENTS: [documentos de arquitectura, changelog, plan, roadmap y README]
VALIDATION_EVIDENCE: [builds, tests, logs, despliegue o NONE]
OUTPUT_PATH: [ruta del documento generado]
LANGUAGE: [idioma]
```

## Procedimiento obligatorio

1. Lee todos los archivos del proyecto de forma progresiva. Incluye código, headers, módulos locales, configuración, build, tests, CI, scripts y documentación relacionada.
2. Sigue imports, includes, llamadas entre módulos, handlers, colas, interfaces, protocolos y dependencias. No infieras una relación solo porque dos nombres parezcan relacionados.
3. Lee completamente los documentos relacionados y clasifica cada afirmación como `CURRENT`, `HISTORICAL`, `PROPOSED`, `VALIDATION_REQUIRED`, `EXTERNAL_UNVERIFIED` o `UNKNOWN`.
4. Construye una matriz de claims: afirmación, fuente, rango/símbolo, estado, confianza y limitación.
5. Usa esta jerarquía para resolver contradicciones: código/configuración actual; tests/builds/logs reproducibles; decisiones aprobadas; plan con estado; arquitectura; changelog; roadmap; drafts.
6. Si un archivo requerido no existe, está truncado o no puede leerse, marca `LECTURA_INCOMPLETA` y no inventes el contenido faltante.

## Estructura de salida

Produce un Markdown con estas secciones:

1. **Identidad, snapshot y alcance**: target, variantes incluidas y excluidas, límites del análisis.
2. **Resumen del sistema**: propósito y límites, con claims separados de inferencias.
3. **Componentes y responsabilidades**: módulos, procesos, servicios, dispositivos o capas; cada uno con evidencia.
4. **Flujos principales**: secuencias de entrada, procesamiento, salida, errores y recuperación.
5. **Interfaces y contratos**: APIs, mensajes, formatos, buses, storage y dependencias; solo lo observado.
6. **Versiones o variantes coexistentes**: separar targets incompatibles y declarar qué es actual, histórico o experimental.
7. **Configuración y despliegue**: solo si está respaldado; parametrizar valores de entorno y redactar secretos.
8. **Invariantes y riesgos**: reglas de orden, límites, timeouts, prioridades y condiciones de fallo.
9. **Diagrama abstracto**: representar relaciones verificadas; no convertir conectividad lógica en cableado físico.
10. **Contradicciones y pendientes**: documento versus código, interfaces no encontradas, claims sin pruebas y decisiones abiertas.
11. **Matriz de evidencia y validación**: tests/builds ejecutados y no ejecutados.
12. **Parámetros para reutilización**: nombres, rutas, targets y valores que otro proyecto debe completar.

## Reglas de seguridad y generalización

- Sustituye nombres de dispositivos, hosts, IPs, pines, topics, IDs, rutas privadas y versiones particulares por placeholders tipados.
- Nunca copies cuerpos completos de firmware ni bloques que incluyan secretos.
- No afirmes “funciona”, “está desplegado”, “está flasheado”, “es no bloqueante” o una latencia concreta sin evidencia de ejecución.
- Diferencia arquitectura observada de arquitectura propuesta.
- No uses una documentación histórica para sobrescribir el código actual.
- Si una relación no puede demostrarse, escribe `UNKNOWN` o `VALIDATION_REQUIRED`.
- Las dependencias declaradas en build prueban intención/configuración, no un build exitoso.
- Los datos de hardware deben permanecer separados de las relaciones físicas concretas del target.

## Validación antes de entregar

Comprueba que cada componente y relación tiene procedencia; que no se mezclaron variantes; que cada claim importante tiene estado; que las contradicciones quedaron visibles; que no aparecen secretos/valores identificables; que el diagrama solo contiene relaciones verificadas; y que se declara explícitamente qué build, test o prueba física no se ejecutó.
