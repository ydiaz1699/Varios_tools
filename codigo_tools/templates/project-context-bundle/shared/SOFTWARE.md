# SOFTWARE.md — Entorno de desarrollo compartido

> Plantilla reusable para herramientas y configuración de desarrollo. No describe hardware ni demuestra que todos los proyectos usen la misma plataforma.

## Identidad del entorno

| Elemento | Default de referencia | Valor confirmado | Fuente | Estado |
|---|---|---|---|---|
| IDE/editor | `[EDITOR_DEFAULT]` | `[EDITOR_VALUE]` | `[PATH_OR_COMMAND]` | `[OBSERVADO | PROPUESTO | PENDIENTE_DE_VERIFICAR]` |
| Sistema de build | `[BUILD_SYSTEM_DEFAULT]` | `[BUILD_SYSTEM_VALUE]` | `[PATH]` | `[estado]` |
| Framework/runtime | `[FRAMEWORK_DEFAULT]` | `[FRAMEWORK_VALUE]` | `[PATH]` | `[estado]` |
| Monitor de ejecución | `[MONITOR_DEFAULT]` | `[MONITOR_VALUE]` | `[PATH]` | `[estado]` |
| Baudrate | `115200` solo como default editable | `[SERIAL_BAUDRATE]` | `[BUILD_CONFIG_OR_NONE]` | `[estado]` |

Los defaults son orientativos. La configuración del proyecto —por ejemplo `platformio.ini`, `package.json`, `Makefile`, scripts o CI— es la fuente de verdad. No afirmar que una herramienta está instalada solo porque aparezca en esta plantilla.

## Perfil PlatformIO/VS Code (opcional)

Usa esta sección únicamente si el proyecto declara PlatformIO y VS Code. Si usa otra toolchain, reemplaza el perfil y conserva la misma estructura de evidencia.

| Extensión | Identificador | Motivo | Requerida |
|---|---|---|---|
| PlatformIO IDE | `platformio.platformio-ide` | Build, upload, monitor y dependencias PlatformIO | `[SÍ | NO]` |
| VS Code Serial Monitor | `ms-vscode.vscode-serial-monitor` | Monitor serial integrado | `[SÍ | NO]` |
| C/C++ tooling | `[EXTENSION_ID]` | IntelliSense, navegación o diagnóstico | `[SÍ | NO]` |
| Diagramas | `[EXTENSION_ID]` | Solo si el proyecto mantiene diagramas editables | `[SÍ | NO]` |
| Gestión de tags | `[EXTENSION_ID]` | Solo si el equipo revisa tags desde el editor | `[SÍ | NO]` |

No instales extensiones automáticamente desde este documento. Registra recomendaciones en `.vscode/extensions.json` y deja la instalación a cargo del flujo autorizado.

## Configuración editable de VS Code

El siguiente JSONC es un ejemplo de configuración, no una afirmación sobre el proyecto. Sustituye el baudrate y elimina claves que no correspondan:

```jsonc
{
  // El archivo de build del proyecto tiene prioridad sobre este default.
  "vscode-serial-monitor.default.baudRate": 115200,
  "vscode-serial-monitor.default.lineEnding": "LF",
  "vscode-serial-monitor.default.timestamp": true,

  // Habilitar solo si el proyecto usa una herramienta compatible.
  "todo-tree.general.tags": ["TODO", "FIXME", "HACK", "BUG", "NOTE", "WARN"],
  "todo-tree.tree.showCountsInTree": true
}
```

Si el editor no soporta JSONC o la extensión no está instalada, no copies estas claves a ciegas. La configuración final debe validarse con el editor/toolchain reales.

## Comandos y estados

| Operación | Comando declarado | Ejecutado | Resultado |
|---|---|---|---|
| Configuración | `[COMMAND]` | `[SÍ | NO]` | `[RESULT_OR_PENDING]` |
| Build | `[COMMAND]` | `[SÍ | NO]` | `[RESULT_OR_PENDING]` |
| Tests | `[COMMAND]` | `[SÍ | NO | NO_EXISTEN]` | `[RESULT_OR_PENDING]` |
| Upload/flash | `[COMMAND_OR_N/A]` | `[SÍ | NO]` | `[RESULT_OR_PENDING]` |
| Monitor | `[COMMAND_OR_N/A]` | `[SÍ | NO]` | `[RESULT_OR_PENDING]` |

No marques `COMPILADO`, `TESTED`, `UPLOADED` o `VERIFICADO` sin comando, entorno y resultado registrados.

## Separación de responsabilidades

- Este archivo: IDE, toolchain, dependencias, comandos y configuración de desarrollo.
- `HARDWARE.md`: placas, alimentación, pines y periféricos confirmados.
- `PROTOCOL.md`: contratos de comunicación y compatibilidad.
- `PROJECT_CONTEXT.md`: propósito, alcance, entradas, referencias y estado de lectura.

Actualiza este archivo cuando cambien las herramientas o el proceso de build. Si un proyecto necesita excepciones, documenta el override en su contexto específico con una fuente y un estado de evidencia.
