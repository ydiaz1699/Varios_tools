# Bundle de contexto de proyecto

Scaffold coordinado para proyectos que mantienen contexto compartido y contexto específico del target. Es una plantilla: no contiene valores de un producto concreto y no debe copiarse al proyecto sin completar los marcadores y validar la evidencia.

## Estructura

```text
project-context-bundle/
├── README.md
├── shared/
│   ├── CODING_STYLE.md
│   └── SOFTWARE.md
└── project/
    ├── .ai/
    │   ├── PROJECT_CONTEXT.md       # obligatorio
    │   ├── HARDWARE.md               # condicional
    │   ├── SOFTWARE.md               # condicional
    │   ├── SKILL.md                  # condicional
    │   ├── TASKS.md                  # condicional
    │   ├── DECISIONS.md              # condicional
    │   ├── ROADMAP.md                # condicional
    │   ├── CHANGELOG.md              # condicional
    │   ├── ARCHITECTURE.md           # condicional
    │   ├── PROTOCOL.md               # condicional
    │   └── TESTING.md                # condicional
    └── project-context-bundle-manifest.json
```

## Uso

1. Copia `shared/` al nivel común que realmente comparta el workspace.
2. Copia `project/.ai/PROJECT_CONTEXT.md` al proyecto o target concreto.
3. Completa los marcadores entre corchetes leyendo el código, la configuración y el historial autorizado.
4. Conserva `SOFTWARE.md` para herramientas y build; documenta hardware, wiring y protocolo en artefactos separados cuando existan.
5. Ajusta las reglas de `CODING_STYLE.md` al lenguaje, framework y restricciones reales del target.
6. Ejecuta el preflight antes de decidir qué archivos condicionales conservar.
7. Valida los enlaces relativos y registra el snapshot usado para generar el bundle.

## Reglas de adaptación

- `shared/` define defaults y políticas comunes; no demuestra que todos los proyectos usen la misma plataforma.
- Un proyecto puede sobrescribir un default en su `.ai/SOFTWARE.md` o `.ai/CODING_STYLE.md`, siempre que indique la fuente y el alcance.
- El archivo `PROJECT_CONTEXT.md` es el punto de entrada mínimo; no debe duplicar fichas de hardware, wiring ni documentación completa.
- Los resultados de build, tests, simulación y hardware deben marcarse como no ejecutados si no existe evidencia.
- Sustituye nombres, rutas, comandos, extensiones y valores entre corchetes; nunca arrastres valores del proyecto que sirvió como procedencia.

Las reglas de extracción de tags están resumidas en [`../../references/coding-style-tags.md`](../../references/coding-style-tags.md), el entorno de desarrollo en [`../../references/shared-platformio-environment.md`](../../references/shared-platformio-environment.md) y el contrato completo del bundle en [`../../references/context-bundle-contract.md`](../../references/context-bundle-contract.md).

Para validar un bundle sin modificarlo:

```bash
python3 codigo_tools/tools/validate_context_bundle.py validate /ruta/proyecto \
  --output /ruta/reports/context-bundle.json
```

Para revisar referencias de catálogo desde un `project-wiring.json`:

```bash
python3 codigo_tools/tools/validate_context_bundle.py catalog-gap /ruta/proyecto \
  --catalog-root codigo_tools/catalog \
  --output /ruta/reports/catalog-gap.json
```

La herramienta es report-only: no corrige enlaces, no crea fichas y no promociona archivos.
