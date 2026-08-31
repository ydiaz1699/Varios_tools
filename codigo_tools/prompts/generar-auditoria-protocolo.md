# Generar auditoría de protocolo y decisión tecnológica

## Propósito

Audita un protocolo, API de comunicación o contrato de interoperabilidad existente y produce una decisión trazable sobre si conviene conservarlo, adaptarlo, reemplazarlo o diseñar uno propio. El prompt obliga a comparar alternativas antes de imponer una tecnología nueva.

Este prompt no implementa protocolos, no genera wire format aplicable, no escribe patches y no convierte una propuesta en decisión aprobada. Su salida es un informe de decisión con evidencia y revisión humana.

## Entradas obligatorias

```text
PROJECT_ROOT: [raíz absoluta]
TARGET_ID: [target, variante o sistema exacto]
SNAPSHOT: [commit/tag/branch/fecha o UNKNOWN]
OUTPUT_PATH: [ruta del informe]
```

## Entradas opcionales

```text
PROTOCOL_SOURCES: [headers, schemas, serializadores, docs, tests o NONE]
ALTERNATIVES: [estándares, protocolos o tecnologías a comparar]
ARCHITECTURE_PATH: [ruta o NONE]
MIGRATION_CONSTRAINTS: [compatibilidad, dispositivos, transporte, despliegue o NONE]
SECURITY_EVIDENCE: [threat model, pruebas, tickets o NONE]
EXTERNAL_SOURCES: [especificaciones oficiales, RFC, datasheets o NONE]
VALIDATION_EVIDENCE: [fixtures, captures, tests, integración o NONE]
LANGUAGE: [idioma]
```

No asumas que el nombre de una biblioteca prueba que el protocolo está integrado. No mezcles contratos de laboratorio, producción, versiones o targets.

## Estados separados

### Estado de evidencia

```text
OBSERVED_IN_CODE
OBSERVED_IN_WIRE_FORMAT
OBSERVED_IN_TEST
DOCUMENTED
INFERRED
CONTRADICTED
UNKNOWN
INCOMPLETE_READ
EXTERNAL_UNVERIFIED
```

### Estado de decisión

```text
PENDING
GO_REUSE
GO_ADAPT
GO_NEW
NO_GO_NEW
BLOCKED
REJECTED
```

### Estado de ejecución

```text
NOT_EXECUTED
COMPILED
TESTED
INTEROPERABILITY_TESTED
INTEGRATION_VERIFIED
HARDWARE_VERIFIED
```

`GO_NEW` es una decisión de diseño pendiente de aprobación, no una implementación. `INTEROPERABILITY_TESTED` requiere casos y evidencia concretos; no se deduce de una compilación.

## Fase 0 — Alcance y cierre de dependencia

Entrega primero:

```text
Target seleccionado:
Snapshot y método de identificación:
Variantes incluidas/excluidas:
Productores y consumidores identificados:
Transportes incluidos/excluidos:
Fuentes de protocolo disponibles:
Fuentes externas autorizadas:
Evidencia de validación:
Preguntas de alcance:
```

Lee completamente el código/configuración, build, módulos locales, schemas, serializadores, parsers, handlers, tests, fixtures, documentación y captures autorizadas. Sigue el camino real desde producción hasta consumo y desde error hasta recuperación.

Registra:

```text
FILE_ID | ruta | tipo | target | bytes/líneas | hash |
read_state | chunks | productores/consumidores afectados
```

Si falta una fuente necesaria, devuelve `INCOMPLETE_READ`/`LECTURA_INCOMPLETA`, lista los contratos afectados y no emitas una recomendación final.

## Fase 1 — Modelo del contrato actual

Antes de comparar tecnologías, construye matrices separadas:

```text
PROTOCOL_ID | capacidad | productor | consumidor | transporte |
formato | versión | límites | errores | timeout/retry |
seguridad | compatibilidad | evidencia | estado
```

```text
MESSAGE_ID | dirección | tipo abstracto | campos | encoding |
endianness | longitud máxima | opcionalidad | validación |
ACK/resultado | replay/deduplicación | fuente | estado
```

```text
CONTRACT_ID | requisito | actual | evidencia | variante |
compatibilidad requerida | riesgo | estado
```

Distingue al menos:

- existencia de una función frente a invocación real;
- capacidad disponible frente a integración;
- conexión de transporte frente a entrega/validación del mensaje;
- autenticación frente a autorización;
- integridad frente a confidencialidad;
- ACK frente a procesamiento exitoso;
- deduplicación frente a anti-replay;
- versión declarada frente a compatibilidad probada.

## Fase 2 — Requisitos y amenazas

Extrae requisitos funcionales y no funcionales antes de puntuar alternativas:

```text
REQUIREMENT_ID | requisito normalizado | tipo |
prioridad | fuente | aceptación | estado
```

Construye un threat model abstracto:

```text
THREAT_ID | activo | actor/capacidad | escenario |
control existente | limitación | evidencia | riesgo residual
```

No inventes amenazas ni afirmes que una técnica las resuelve. Si no hay evidencia de replay, downgrade, key rotation, parser limits, nonce/sequence handling, desincronización o error recovery, registra `UNKNOWN` o `EXTERNAL_UNVERIFIED`.

## Fase 3 — Comparación de alternativas

Para cada alternativa —incluida mantener el contrato actual— registra:

```text
ALTERNATIVE_ID | opción parametrizada | requisitos cubiertos |
requisitos no cubiertos | compatibilidad | seguridad |
complejidad | coste de migración | observabilidad |
dependencias | evidencia | incertidumbre | recomendación
```

La comparación debe incluir, cuando aplique:

- estándar existente frente a protocolo propio;
- transporte y payload como decisiones separadas;
- versionado y compatibilidad hacia atrás;
- límites de memoria, tamaño y rendimiento;
- autenticación, autorización, integridad, confidencialidad y replay;
- discovery, capacidades, errores y telemetría;
- coexistencia y migración gradual;
- rollback y compatibilidad con consumidores antiguos;
- herramientas de prueba, fixtures y análisis del wire format;
- dependencia de infraestructura externa.

Cada puntuación debe tener escala, fuente y limitación. No uses una puntuación como verdad automática.

## Fase 4 — Decisión go/no-go

La recomendación debe ser una de estas:

```text
PENDING
GO_REUSE
GO_ADAPT
GO_NEW
NO_GO_NEW
BLOCKED
REJECTED
```

`GO_NEW` solo puede aparecer si:

1. los requisitos no quedan cubiertos de forma suficiente por alternativas existentes;
2. se documentó por qué reutilizar/adaptar no es aceptable;
3. existe un contrato de compatibilidad y migración;
4. existe un threat model y estrategia de validación;
5. existe rollback o coexistencia;
6. las incógnitas críticas tienen plan de resolución;
7. la decisión queda explícitamente pendiente de aprobación humana.

Si esas condiciones no se cumplen, usa `PENDING`, `NO_GO_NEW` o `BLOCKED`. No conviertas entusiasmo arquitectónico en necesidad técnica.

## Fase 5 — Salida mínima

Genera `OUTPUT_PATH` con esta estructura:

```markdown
# Auditoría de protocolo — [TARGET_ID]

> Snapshot: [SNAPSHOT]
> Decisión: PENDING | GO_REUSE | GO_ADAPT | GO_NEW | NO_GO_NEW | BLOCKED | REJECTED
> Cobertura: COMPLETE | INCOMPLETE_READ
> Estado de auditoría: DRAFT | GENERATED | AUDITED | AUDIT_FAILED

## 1. Alcance, variantes y método
## 2. Inventario y cierre de dependencias
## 3. Contrato actual observado
## 4. Requisitos y threat model
## 5. Alternativas comparadas
## 6. Compatibilidad, migración y rollback
## 7. Decisión y condiciones de aprobación
## 8. Plan de validación
## 9. Matriz de claims y procedencia
## 10. Incertidumbres, contradicciones y preguntas
```

La sección de decisión debe indicar qué evidencia cambiaría una recomendación `PENDING`, qué partes son actuales y cuáles son propuestas, y qué no se ha ejecutado.

## Seguridad y generalización

- No copies claves, tokens, hosts, IPs, topics, IDs, payloads privados, wire dumps sensibles ni valores de producto.
- Usa placeholders: `[PROTOCOL]`, `[MESSAGE_TYPE]`, `[TRANSPORT]`, `[VERSION]`, `[FIELD]`, `[CONSUMER]`.
- No diseñes una criptografía nueva ni afirmes que HMAC, firma, cifrado o nonce resuelven un threat model sin evidencia.
- No confundas autenticación, autorización, integridad, confidencialidad, anti-replay y disponibilidad.
- No uses una propuesta de protocolo como fuente de comportamiento actual.
- Las fuentes externas deben estar autorizadas y referenciadas; de lo contrario, marca `EXTERNAL_UNVERIFIED`.

## Fase 6 — Replay y auditoría

Vuelve a comparar el informe contra las fuentes primarias y externas autorizadas. Marca `AUDIT_FAILED` si:

- una alternativa fue descartada sin requisito o evidencia;
- se recomienda crear un protocolo propio sin comparación de estándares;
- una capacidad se declara integrada por la mera existencia de una clase;
- se afirma interoperabilidad sin fixtures/captures/pruebas;
- se oculta una contradicción de versión, encoding, ACK, replay o compatibilidad;
- se confunde conexión con entrega o autenticación con autorización;
- una decisión `GO_*` aparece como implementación aplicada;
- faltan rollback, migración o condiciones de aprobación;
- aparece un secreto o dato privado.

Incluye:

```text
REPLAY_CHECK_ID | claim/alternativa | fuente |
resultado esperado | resultado observado | estado | limitación
```

Toda salida requiere revisión humana. Este prompt no implementa ni promueve ninguna decisión.
