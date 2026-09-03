# Skill del proyecto: [nombre de la tarea]

> Estado: [BORRADOR | GENERADA | PENDIENTE_DE_VERIFICAR]
> Target: [target exacto]
> Snapshot: [commit/rama/tag/fecha]
> Fuente: [código/configuración/documentación]

## Propósito y activación

Usar esta skill cuando [tarea recurrente y condición de activación].
No usarla para [targets, tareas o capas fuera de alcance].

## Entradas requeridas

| Entrada | Valor o formato | Fuente/estado |
|---|---|---|
| Target | [valor] | `[ruta:línea]` / `PENDIENTE_DE_VERIFICAR` |
| Configuración del usuario | [valor] | [fuente] |
| Dependencias | [valor] | [fuente] |

## Flujo de trabajo

1. **Leer y validar** — revisar [archivos/configuración] completos antes de cambiar nada.
2. **Confirmar alcance** — separar [targets/versiones] y pedir los datos que falten.
3. **Aplicar la tarea** — seguir el flujo real observado: `[pasos]`.
4. **Revisar consistencia** — comparar contra `copilot-instructions.md`, README y configuración.
5. **Verificar** — ejecutar solo los comandos autorizados y registrar el resultado real.

## Decisiones clave

| Decisión | Valor actual | Evidencia | Estado |
|---|---|---|---|
| [decisión] | [valor] | `[ruta:línea/símbolo]` | `OBSERVADO_EN_CODIGO` |
| [pendiente] | [opciones] | [fuente] | `PENDIENTE_DE_VERIFICAR` |

No sustituir una decisión pendiente por una suposición. Las propuestas deben aparecer como `PROPUESTO`.

## Entradas, salidas y estados

```text
[entrada] → [componente/función] → [estado] → [salida]
```

- Entrada: [qué recibe].
- Salida: [qué produce].
- Estados: [estados y transiciones reales].
- Errores/timeouts/reintentos: [comportamiento observado o `NO_ENCONTRADO`].

## Criterios de salida

La respuesta debe incluir:

- [ ] Archivos completos o diff claramente delimitado.
- [ ] Explicación breve de los cambios.
- [ ] Fuentes para los valores no obvios.
- [ ] Comandos ejecutados y resultado real.
- [ ] Tests, build o hardware marcados como `NO EJECUTADOS` si no se realizaron.
- [ ] Pendientes y riesgos separados de lo implementado.
- [ ] Secretos sustituidos por `[REDACTADO]`.

## Ejemplos de solicitudes

- «[solicitud realista 1]»
- «[solicitud realista 2]»
- «[solicitud realista 3]»

## Limitaciones y mantenimiento

Esta skill es específica de `[target/repo]`. Actualizarla cuando cambien [archivos, comandos, estados o dependencias]. Compararla siempre con `copilot-instructions.md`; si comparten un valor, ambos deben coincidir con el código actual.

No declarar la tarea como verificada solo porque el archivo fue generado. Distinguir `APLICADO`, `COMPILADO`, `VERIFICADO` y `VERIFICADO_EN_HARDWARE`.
