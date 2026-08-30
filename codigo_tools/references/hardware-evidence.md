# Evidencia para el catálogo de hardware

## Separación de capas

```text
board       = modelo físico, pinout, MCU, alimentación y restricciones genéricas
peripheral  = módulo/variante, protocolo, señal, alimentación y requisitos
wiring      = instancia concreta del proyecto: qué se conectó y cómo
```

Una ficha no debe afirmar que un periférico está conectado a una placa. Eso solo puede aparecer en el wiring del proyecto con una fuente.

## Estados

- `OBSERVADO_EN_CODIGO`: el firmware usa o configura el dato.
- `OBSERVADO_EN_BUILD`: aparece en `platformio.ini`, manifest o build.
- `DOCUMENTADO`: aparece en un documento, sin verificación independiente.
- `ESTIMADO`: aproximación marcada como tal; no es medición.
- `CONTRADICTORIO`: fuentes actuales difieren.
- `PENDIENTE_DE_VERIFICAR`: requiere datasheet, modelo exacto, medición o hardware.
- `VERIFICADO_EN_HARDWARE`: confirmado físicamente con procedimiento y fecha.

## Reglas de seguridad

- Separar `VCC`, `logic_voltage`, señal y corriente; una columna única de “voltaje” no basta.
- No declarar tolerancia de 5 V por pertenecer a una familia de MCU.
- No declarar aislamiento, corriente de carga, alcance, consumo o precisión sin modelo/variante y fuente.
- Tratar pines de boot, flash, PSRAM, USB y UART como restricciones explícitas.
- Un GPIO en el código demuestra una asignación lógica; no demuestra el componente físico, el cableado, la alimentación ni la polaridad externa.
- Una conexión lógica (WiFi, MQTT, RF, NTP) no es un cable del diagrama físico.
- Redactar identificadores sensibles y secretos.

## Procedencia mínima

```yaml
source: datasheet | code | build | project-document | measurement | hardware-test
file: path/origin
reference: line/symbol/section
state: one-of-the-states-above
verified_at: optional-date
model_variant: optional-exact-model
```

## Decisiones bloqueantes

No aceptar como ficha canónica una entrada que tenga contradicciones de memoria/flash, nivel lógico, pinout o configuración de build. Conservar la fuente y generar una pregunta de resolución. La herramienta puede validar estructura y conflictos obvios, pero no sustituye la revisión técnica.
