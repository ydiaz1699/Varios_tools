# Instrucciones del repositorio: [nombre del proyecto]

> Estado: [BORRADOR | GENERADA | PENDIENTE_DE_VERIFICAR]
> Target: [target exacto]
> Snapshot: [commit/rama/tag/fecha]
> Fuente de comportamiento: código y configuración actuales

## Objetivo y alcance

[Describe en 2–3 líneas lo que el proyecto implementa realmente.]

- Incluye: [targets/capas cubiertos].
- No incluye: [targets/capas fuera de alcance].
- Evidencia: `[ruta:línea/símbolo]`.

## Plataforma y herramientas

| Elemento | Valor | Fuente | Estado |
|---|---|---|---|
| Lenguaje | [valor] | `[ruta]` | `OBSERVADO_EN_CODIGO` |
| Framework/runtime | [valor] | `[ruta]` | `OBSERVADO_EN_BUILD` |
| Board/entorno | [valor] | `[ruta]` | `OBSERVADO_EN_BUILD` |
| Dependencias | [nombre y versión declarada] | `[ruta]` | [estado] |
| Build/test | [comandos declarados] | `[ruta]` | `DOCUMENTADO` |

## Datos técnicos actuales

| Nombre | Valor documentable | Fuente | Estado |
|---|---|---|---|
| [constante/pin/puerto] | [valor] | `[ruta:línea]` | `OBSERVADO_EN_CODIGO` |
| [secreto] | `[REDACTADO]` | `[ruta/variable]` | `PRESENTE_NO_EXHIBIDO` |

No copiar contraseñas, tokens, claves, SSID, certificados ni otros secretos al archivo.

## Reglas de implementación

- [Regla observada en el código] — fuente: `[ruta:línea/símbolo]`.
- [Patrón de inicialización/estado/callback] — fuente: `[ruta]`.
- No introducir una dependencia, pin, protocolo o comportamiento no demostrado sin marcarlo como `PROPUESTO`.

## Convenciones de estilo

- Idioma de comentarios y respuestas: [valor observado].
- Nombres/formato: [convención observada].
- Organización: [convención observada].
- Nivel de detalle esperado: [valor acordado].

## Verificación obligatoria

- Build: `[comando]` — estado: `EJECUTADO | DECLARADO_NO_EJECUTADO | PENDIENTE`.
- Tests: `[comando]` — estado: `EJECUTADO | NO_EXISTEN | NO_EJECUTADO`.
- Integración/hardware: [evidencia o `PENDIENTE_DE_VERIFICAR`].

No afirmar que el proyecto compila, funciona o fue probado sin registrar el comando, entorno y resultado.

## Límites, contradicciones y pendientes

| Tema | Código/configuración | Documentación | Estado | Acción |
|---|---|---|---|---|
| [tema] | [valor] | [valor] | `CONTRADICTORIO` | [decisión o pendiente] |

## Mantenimiento

Actualizar este archivo cuando cambien el target, la configuración, las dependencias, los comandos, los pines, los estados o las restricciones de seguridad. Compararlo con el código actual y con `SKILL.md`; no corregir un valor en un solo archivo.

## Procedencia

Cada afirmación técnica importante debe poder rastrearse a:

```text
snapshot | target | archivo | línea/símbolo/chunk | estado de evidencia
```

Los valores pendientes deben escribirse como `PENDIENTE_DE_VERIFICAR`, no completarse por conocimiento general del framework.
