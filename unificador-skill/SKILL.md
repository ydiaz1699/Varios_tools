---
name: unificador-skill
description: >
  Unifica fragmentos dispersos (notas, diagnósticos, conversaciones) en una
  guía coherente de ejecución paso a paso. Deduplica contenido repetido,
  detecta contradicciones, respeta orden de ejecución real, y genera documentos
  autocontenidos. Usar cuando el usuario tenga múltiples fragmentos de un tema
  que necesita consolidar en un solo documento, o cuando diga "unificar",
  "consolidar notas", "generar guía de esto", "unir estos documentos".
---

# unificador-skill

Unifica fragmentos dispersos en guías de ejecución coherentes.

---

## 🔴 Reglas no-negociables

```
1. NO RESUMIR     — código, configs y comandos van ÍNTEGROS (nunca "...")
2. NO INVENTAR    — solo info de los fragmentos. Huecos → "⚠️ PENDIENTE"
3. DEDUPLICAR     — N versiones del mismo contenido → UNA (la más completa)
4. ORDEN REAL     — mkdir → archivos → permisos → levantar → verificar
5. AUTOCONTENIDO  — no referenciar fragmentos originales, guía independiente
6. CONTRADICCIONES → listar como "DECISIÓN PENDIENTE" con opciones
7. ANÁLISIS PREVIO — OBLIGATORIO antes de generar. Sin bloque → salida INVÁLIDA
```

---

## 🧠 ANÁLISIS PREVIO (obligatorio ANTES de unificar)

**Este bloque DEBE aparecer antes de generar la guía. Si falta → salida INVÁLIDA.**

```
🧠 ANÁLISIS PREVIO DE FRAGMENTOS
═══════════════════════════════════════════════════

【1. Material recibido】
- Fragmentos: [cantidad]
- Fuentes: [ChatGPT / Kimi / notas propias / logs / otro]
- Tamaño total estimado: [corto <5K / medio 5-30K / largo >30K]

【2. Tema central detectado】
- [Qué se está documentando]

【3. Versiones duplicadas】
- [N fragmentos cubren lo mismo — cuál es la más completa]
- [O "sin duplicados"]

【4. Contradicciones detectadas】
- [Fragmento X dice A, fragmento Y dice B]
- [O "ninguna"]

【5. Información que YA está completa】
- [Secciones que no necesitan más datos]

【6. Brechas detectadas】
- [Qué falta para una guía completa: permisos, backup, verificación, etc.]

【7. Valores hardcodeados para parametrizar】
- [IPs, rutas, usuarios que deberían ser variables]

【8. Orden de ejecución identificado】
- [Dependencias entre pasos]

【9. Acción】
- [ ] Proceder con unificación (info completa)
- [ ] Preguntar antes (contradicciones/brechas críticas)
- [ ] Usar análisis por partes (material >30K)

═══════════════════════════════════════════════════
```

---

## Flujo completo

```
1. Recibir fragmentos
2. Ejecutar ANÁLISIS PREVIO (bloque obligatorio)
3. Si hay problemas → avisar al usuario ANTES de unificar
4. Usuario confirma → generar guía
5. Usuario revisa → feedback → registrar mejoras
```

---

## Antes de unificar — avisar si detectas

- Contradicciones entre fragmentos (preguntar cuál es correcta)
- Valores hardcodeados que deberían ser variables/parámetros
- Información faltante crítica (permisos, dependencias, verificación)
- Fragmentos que repiten lo mismo con distinto formato (cuál usar)
- Pasos sin orden lógico claro (proponer ordenamiento)

**No proceder hasta que el usuario confirme.**

---

## Formato de salida

```markdown
# Guía: [título descriptivo]

## Decisiones tomadas
1. [conclusión firme extraída de los fragmentos]

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

Para formato completo, variantes Docker, y análisis por partes, ver `references/formato.md`.

---

## Después de unificar (feedback loop)

- Si el usuario corrige algo → agregar lección a `references/mejoras.md`
- Si se detecta un patrón nuevo → proponer agregarlo como regla
- Borrar los fragmentos originales una vez aprobada la guía
- Sugerir al usuario: "¿Hay algo que debería agregar como regla para la próxima?"

Para el registro de mejoras y reglas acumuladas, ver `references/mejoras.md`.

---

## ✅ Checklist de validación (antes de entregar)

```
[ ] 1. Bloque "🧠 ANÁLISIS PREVIO" presente y completo
[ ] 2. No hay código parcial ni "..." en la guía
[ ] 3. Contradicciones marcadas como "DECISIÓN PENDIENTE" (no elegidas por mí)
[ ] 4. Orden de pasos respeta dependencias (no se puede chmod antes de mkdir)
[ ] 5. Cada paso tiene verificación
[ ] 6. No se inventó información fuera de los fragmentos
[ ] 7. Valores hardcodeados parametrizados (o marcados para confirmar)
[ ] 8. Guía es autocontenida (no refiere fragmentos originales)
```

**Si CUALQUIER punto falla → DETENER → corregir antes de entregar.**

---

## Variante: documentos muy largos (>30K chars)

Si los fragmentos son extensos, usar análisis por partes:

1. Analizar CADA fragmento por separado (resumen estructurado)
2. Preguntar "¿Genero la guía final?"
3. Combinar los análisis en la guía unificada

Para instrucciones detalladas, ver `references/formato.md`.
