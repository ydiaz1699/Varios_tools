# Varios_tools

Coleccion de herramientas y scripts organizados por proyecto.

## Proyectos

| Carpeta | Descripcion |
|---------|-------------|
| `adb_controller/` | Control de DNS Privado en Android por ADB (script, chatbot, documentacion) |
| `artefactos_proyecto/` | Catálogo de archivos-artefacto estándar de un proyecto (UPSTREAM.md, CONTRIBUTING.md, .env.example, CHANGELOG.md, ADR, SECURITY.md): qué es, cuándo aplica y plantilla lista |
| `codigo_tools/` | Prompts y herramientas para analizar código y generar/auditar documentación técnica |
| `tool_catalog/` | Catálogo de recursos EXTERNOS (repos, videos, dotfiles): fichas ligeras para decidir si vale la pena leer la fuente completa sin gastar tokens |
| `tools_AI/` | Artefactos de IA PROPIOS y reutilizables: skills (skill-creator, unificador-skill), recursos de diseño (nas-agent-memory) y skills globales de Kiro |

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
