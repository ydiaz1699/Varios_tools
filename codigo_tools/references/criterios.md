# Criterios de `codigo_tools`

## Regla central

La documentación se deriva de una lectura completa del target y de sus dependencias. Un README, un comentario o un diagrama anterior no reemplazan la inspección de `src`, `include`, `lib`, configuración de build y archivos compartidos.

## Alcance y targets

Un target es una unidad que puede tener placa, firmware, entorno de compilación y conexiones físicas propios. Si un repositorio tiene varios targets, se deben inventariar y documentar por separado. Solo se puede producir una vista conjunta si se distingue claramente:

- **Físico:** placa, módulo, alimentación, tierra, señales y buses.
- **Lógico:** WiFi, UDP, MQTT, OTA, topics, endpoints y protocolos.
- **Histórico/propuesto:** notas, roadmap o diagramas que no coinciden con el código actual.

## Estados de evidencia

- `OBSERVADO_EN_CODIGO`: aparece en una instrucción, constante, tipo de placa o dependencia leída.
- `OBSERVADO_EN_BUILD`: aparece en `platformio.ini`, `library.json`, flags o configuración equivalente.
- `DOCUMENTADO`: aparece en documentación del proyecto, pero todavía no se confirma en código.
- `INFERIDO`: conclusión razonable, no una afirmación física comprobada.
- `PENDIENTE_DE_CONFIRMAR`: requiere datasheet, inspección de hardware, medición o respuesta del usuario.
- `CONTRADICTORIO`: dos fuentes actuales no coinciden; conservar ambas y explicar el conflicto.

Nunca presentar `INFERIDO` o `DOCUMENTADO` como equivalente a `OBSERVADO_EN_CODIGO`.

## Inventario mínimo por afirmación

Registrar, cuando sea posible:

```text
ID | afirmación | target | fuente | línea/símbolo | evidencia | estado | destino
```

Para archivos largos, usar IDs estables de chunk, por ejemplo `F03-C02`, además de la ruta.

## Pinout

Para cada pin distinguir:

- nombre de la placa (`D2`, `D3`, `A0`, etc.);
- GPIO o canal físico si está explícito o confirmado;
- uso (`PIR`, `buzzer`, `LED`, botón, bus, etc.);
- modo (`INPUT`, `OUTPUT`, `INPUT_PULLUP`, ...);
- nivel activo;
- dirección de señal;
- target y variante;
- procedencia.

Si solo se conoce el nombre de la constante y no el cableado físico, no inventar la correspondencia.

## Energía y voltajes

El código puede revelar un pin de alimentación o un nivel lógico, pero normalmente no demuestra por sí solo el voltaje permitido del módulo. Documentar por separado:

1. lo escrito en el código;
2. lo indicado por notas/datasheet;
3. lo que falta confirmar;
4. el riesgo si se conecta sin confirmación.

## Cambios y regeneración

Cuando cambie un pin, placa, componente, entorno de build o dependencia:

1. regenerar las notas;
2. regenerar el diagrama;
3. ejecutar la auditoría;
4. revisar manualmente los datos eléctricos y las conexiones físicas;
5. guardar el commit o versión usada para la generación.
