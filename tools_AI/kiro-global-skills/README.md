# Skills globales de Kiro Web

Skills pensadas para instalarse a nivel **global de usuario** (aplican a TODOS
tus proyectos), no dentro de un repo concreto. Se versionan aquí para no
perderlas; la copia "viva" la gestionas tú desde Kiro Web.

## tool-catalog-router

Enruta el uso de tus catálogos personales (`tool_catalog/` y `tools_AI/` de
`ydiaz1699/Varios_tools`): consultar el catálogo ANTES de leer un recurso externo,
usar los artefactos de `tools_AI`, y proponer catalogar lo que sea reutilizable.

### Cómo instalarla como skill global en Kiro Web

Las skills globales de usuario en Kiro Web se gestionan desde la interfaz, no
escribiendo en el filesystem (el sandbox es efímero):

1. En Kiro Web: **Settings → Skills**.
2. Crear una skill nueva llamada `tool-catalog-router`.
3. Pegar el contenido de [`tool-catalog-router/SKILL.md`](tool-catalog-router/SKILL.md).
4. Guardar. A partir de ahí Kiro la auto-activa por sus triggers en cualquier
   proyecto.

> Alternativa (herramientas que leen del filesystem, ej. Claude Code/Gemini CLI):
> copiar `tool-catalog-router/` a `~/.kiro/skills/` (o `~/.claude/skills/`, etc.)
> del entorno correspondiente.

### Mantenerla

La fuente de verdad es este archivo versionado. Si la editas, actualiza aquí y
vuelve a pegarla en Settings/Skills. Para crear/optimizar más skills globales,
usar [`../skills/skill-creator`](../skills/skill-creator/SKILL.md).
