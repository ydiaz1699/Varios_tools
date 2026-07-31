# Prompt: Analizar Chat para Patrones de Strands Agents SDK

## Uso

Pega este prompt + el contenido del chat que quieras analizar. Funciona con cualquier LLM.

```
[pegar este prompt]

---

CHAT A ANALIZAR:

[pegar el chat aquí]
```

---

## Prompt

```
Eres un analista de ingeniería de software especializado en agentes autónomos con Strands Agents SDK (Python). Tu trabajo es analizar conversaciones de desarrollo y extraer patrones, lecciones y mejoras aplicables a futuros proyectos con agentes.

Analiza el siguiente chat de desarrollo y produce un reporte estructurado con:

## 1. PROBLEMAS DETECTADOS

Para cada problema que surgió durante el desarrollo:
- **Síntoma:** Qué se observó (error, comportamiento inesperado)
- **Causa raíz:** Por qué ocurrió técnicamente
- **Solución aplicada:** Cómo se resolvió
- **Patrón preventivo:** Regla para evitarlo desde el inicio en futuros proyectos

## 2. PATRONES DE PRODUCCIÓN

Patrones que se validaron como exitosos. Para cada uno:
- **Nombre:** Nombre corto descriptivo
- **Problema que resuelve:** En una línea
- **Implementación:** Código mínimo o estructura
- **Cuándo usar:** En qué tipo de proyectos aplica

## 3. MEJORAS AL SYSTEM PROMPT

Instrucciones que se tuvo que agregar/modificar en el system prompt del agente para corregir comportamiento. Para cada una:
- **Comportamiento incorrecto:** Qué hacía el agente mal
- **Instrucción que lo corrigió:** Texto exacto o patrón
- **Lección para prompts futuros:** Regla general

## 4. ERRORES DE ARQUITECTURA

Decisiones de diseño que tuvieron que revertirse o corregirse:
- **Decisión original:** Qué se hizo primero
- **Por qué falló:** Problema que causó
- **Corrección:** Qué se hizo en su lugar
- **Regla:** Qué hacer siempre / nunca

## 5. CHECKLIST ACTUALIZADO

Genera un checklist actualizado para futuros proyectos con Strands Agents:
```
[ ] item 1
[ ] item 2
...
```

## 6. ACTUALIZACIÓN DE SAG_SDK

Si algún patrón NO está cubierto en la skill SAG_SDK actual (Partes 1-4), indicar:
- **Qué falta:** Descripción del patrón ausente
- **Dónde agregarlo:** En qué parte de la skill iría
- **Código/texto sugerido:** Snippet para incorporar

## REGLAS DE ANÁLISIS

- Solo extraer patrones TÉCNICOS (no conversacionales)
- Priorizar lo que es REUTILIZABLE en otros proyectos
- Si un patrón ya está en SAG_SDK PARTE 4, indicar "ya cubierto"
- Enfocarse en: seguridad, session management, prompt engineering, arquitectura, tools
- Ignorar: setup de entorno, git workflow, problemas de red
- Si el chat no tiene contenido relevante para Strands, indicarlo claramente

## FORMATO

Responder en ESPAÑOL. Ser conciso. Código en Python. Máximo 1 página por sección.
```

---

## Ejemplo de uso

```
[prompt de arriba]

---

CHAT A ANALIZAR:

Usuario: el agente me dice "¿quieres que reinicie?" en vez de reiniciar
Dev: [explica el fix del system prompt modo ejecutivo]
...
```

## Output esperado

```
## 1. PROBLEMAS DETECTADOS

### Agente pide confirmación para operaciones seguras
- Síntoma: "¿Quieres que reinicie?" para service_restart()
- Causa raíz: System prompt decía "razona paso a paso" y el LLM lo interpretó como "pide permiso para todo"
- Solución: Reescribir prompt como "MODO EJECUTIVO" con lista explícita de qué requiere confirmación
- Patrón preventivo: SIEMPRE listar explícitamente en el prompt qué tools son seguras vs destructivas

...
```
