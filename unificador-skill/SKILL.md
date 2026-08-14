---
name: unificador-skill
description: >
  Unifica fragmentos dispersos (notas, diagnósticos, conversaciones) en una
  guía coherente de ejecución paso a paso. Deduplica contenido repetido,
  detecta contradicciones, respeta orden de ejecución real, y genera documentos
  autocontenidos. Usar cuando el usuario tenga múltiples fragmentos de un tema
  que necesita consolidar en un solo documento, o cuando diga "unificar",
  "consolidar notas", "generar guía de esto", o suba drafts a _drafts/.
---

# unificador-skill

Unifica fragmentos dispersos en guías de ejecución coherentes.

---

## Reglas estrictas

```
1. NO RESUMIR     — código, configs y comandos van ÍNTEGROS (nunca "...")
2. NO INVENTAR    — solo info de los fragmentos. Huecos → "⚠️ PENDIENTE"
3. DEDUPLICAR     — N versiones del mismo contenido → UNA (la más completa)
4. ORDEN REAL     — mkdir → archivos → permisos → levantar → verificar
5. AUTOCONTENIDO  — no referenciar fragmentos originales, guía independiente
6. CONTRADICCIONES → listar como "DECISIÓN PENDIENTE" con opciones
```

---

## Antes de unificar (avisar al usuario)

Revisar los fragmentos y reportar si detectas:

- Contradicciones entre fragmentos (preguntar cuál es correcta)
- IPs/rutas hardcodeadas (sugerir variables: `${SERVER_IP}`, `$dkco`)
- Comandos genéricos que deberían usar wrappers del entorno del usuario
- Información faltante (permisos, red, backup, verificación)
- Fragmentos que repiten lo mismo con distinto formato

No proceder hasta que el usuario confirme.

---

## Formato de salida

```markdown
# Guía: [título descriptivo]

## Decisiones tomadas
1. [conclusión firme de los fragmentos]

---

## Paso N: [nombre corto]

### Archivo(s) a crear/modificar
- Ruta exacta

### Contenido completo
```[lenguaje]
(ÍNTEGRO — nunca parcial)
```

### Comando de verificación
```bash
(comprobar que el paso se aplicó)
```

### Depende de
- Paso X (si aplica)

---

## Decisiones pendientes
1. [contradicción detectada]
   - Opción A: [lo que dice un fragmento]
   - Opción B: [lo que dice otro]
```

Para el formato completo y variantes, ver `references/formato.md`.

---

## Después de unificar (feedback loop)

- Si el usuario corrige algo → agregar la lección al registro de mejoras
- Si se detecta un patrón nuevo → proponer agregarlo como regla
- Borrar los fragmentos originales del _drafts/ una vez aprobada la guía

Para el registro de mejoras y la tabla histórica, ver `references/mejoras.md`.

---

## Variante: documentos muy largos (>30K chars)

Si los fragmentos son extensos, usar análisis por partes:

1. Analizar CADA fragmento por separado (resumen estructurado)
2. Preguntar "¿Genero la guía final?"
3. Combinar los análisis en la guía unificada

Para instrucciones detalladas, ver `references/formato.md`.
