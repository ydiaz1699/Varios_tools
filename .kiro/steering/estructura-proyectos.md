# Regla de Estructura: Varios_tools

## Regla principal

**NUNCA** crear archivos ni carpetas directamente en la raiz del repositorio `Varios_tools/`.

Cada proyecto, herramienta o conjunto de scripts DEBE vivir dentro de su **propia subcarpeta** con un nombre descriptivo.

## Estructura obligatoria

```
Varios_tools/
├── .kiro/steering/         ← Reglas globales del repo (UNICA excepcion en la raiz)
├── proyecto_1/
│   ├── .kiro/              ← Agents y skills propios de este proyecto
│   │   ├── agents/
│   │   └── skills/
│   ├── README.md
│   └── (archivos del proyecto)
├── proyecto_2/
│   ├── .kiro/
│   ├── README.md
│   └── (archivos del proyecto)
└── ...
```

## Reglas

1. **Todo proyecto nuevo** va en `Varios_tools/<nombre_proyecto>/`
2. **Cada proyecto** tiene su propia carpeta `.kiro/` con agents y skills relevantes SOLO a ese proyecto
3. **La raiz** del repo solo contiene:
   - `.kiro/steering/` (reglas globales como esta)
   - Subcarpetas de proyectos
   - Opcionalmente un `README.md` raiz que liste los proyectos disponibles
4. **NUNCA** poner archivos sueltos (scripts, docs, configs) directamente en `Varios_tools/`
5. **NUNCA** poner agents ni skills en `.kiro/` de la raiz que pertenezcan a un solo proyecto — van dentro de la subcarpeta del proyecto

## Nombres de carpetas

- Usar snake_case: `adb_controller`, `wifi_tools`, `backup_scripts`
- Nombre descriptivo y corto
- Sin espacios ni caracteres especiales

## Al crear un proyecto nuevo

Antes de escribir cualquier archivo, SIEMPRE:
1. Preguntar: "¿En qué carpeta dentro de Varios_tools quieres este proyecto?"
2. Si el usuario no especifica nombre, sugerir uno descriptivo
3. Crear la estructura: `Varios_tools/<nombre>/` con al menos un `README.md`
4. Si el proyecto necesita agent o skill, crearlo en `Varios_tools/<nombre>/.kiro/`

## Ejemplo

Si el usuario dice "quiero un script para controlar el brillo por ADB":
- CORRECTO: `Varios_tools/brillo_adb/script.py`
- INCORRECTO: `Varios_tools/script.py`
