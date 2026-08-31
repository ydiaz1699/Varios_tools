# Referencia: entorno de desarrollo compartido

## Propósito

Define cómo documentar un entorno de IDE, toolchain, build y monitor sin convertir un default en requisito universal. El scaffold canónico es [`templates/project-context-bundle/shared/SOFTWARE.md`](../templates/project-context-bundle/shared/SOFTWARE.md).

## Reglas

- `platformio.ini`, el sistema de build, CI y los scripts son la fuente de verdad.
- PlatformIO, VS Code, Arduino, el monitor serial, extensiones y baudrate deben declararse como observados, propuestos o pendientes.
- `115200` puede conservarse como default editable cuando no existe una configuración del proyecto; no sustituye el valor configurado por el target.
- Las recomendaciones de extensiones no deben implicar instalación automática.
- El entorno de desarrollo se mantiene separado de hardware, wiring, protocolos, secretos y comportamiento de producto.
- Los comandos deben registrar si fueron declarados, ejecutados y con qué resultado.
