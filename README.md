# Varios_tools

Coleccion de herramientas y scripts organizados por proyecto.

## Proyectos

| Carpeta | Descripcion |
|---------|-------------|
| `adb_controller/` | Control de DNS Privado en Android por ADB (script, chatbot, documentacion) |
| `codigo_tools/` | Prompts y herramientas para analizar código y generar/auditar documentación técnica |

## Estructura

Cada proyecto vive en su propia subcarpeta con su configuracion independiente:

```
Varios_tools/
├── .kiro/steering/    ← Reglas globales del repo
├── adb_controller/    ← Proyecto 1
│   ├── .kiro/         ← Config propia (agents, skills)
│   └── ...
├── otro_proyecto/     ← Proyecto 2
│   ├── .kiro/
│   └── ...
└── README.md          ← Este archivo
```

## Regla

**No se crean archivos sueltos en la raiz.** Todo va dentro de una subcarpeta de proyecto.
