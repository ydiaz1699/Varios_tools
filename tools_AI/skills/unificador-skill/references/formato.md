# Formato de salida — referencia completa

---

## Estructura obligatoria de la guía generada

```markdown
# Guía: [título descriptivo]

## Estado: borrador
## Fecha: [hoy]
## Resumen: [1 línea de qué se logra al completar todos los pasos]

---

## Decisiones tomadas

1. [decisión firme extraída de los fragmentos]
2. [otra]

---

## Paso 1: [nombre]

### Archivo(s) a crear/modificar
- Ruta exacta del archivo

### Contenido completo
```[lenguaje]
(código o config ÍNTEGRO — nunca parcial, nunca "...")
```

### Comando de verificación
```bash
(comando que confirma que el paso se aplicó bien)
```

### Depende de
- Paso X (si aplica)

---

## Paso 2: [nombre]
[...]

---

## Decisiones pendientes

1. [contradicción o hueco detectado]
   - Opción A: [qué dice un fragmento]
   - Opción B: [qué dice otro]
```

---

## Reglas del formato

1. Los pasos van en **orden de ejecución real** (no agrupados por tema):
   ```
   1. Crear carpetas          (mkdir -p)
   2. Crear archivos          (touch, nano, cat >)
   3. Aplicar permisos        (chmod, chown)
   4. Levantar/ejecutar       (svc up, systemctl start)
   5. Verificar               (svc ps, curl, test)
   ```

2. NUNCA:
   - chmod a una carpeta que no se creó todavía
   - Crear archivo dentro de un directorio inexistente
   - Aplicar permisos antes del mkdir
   - Levantar un servicio antes de crear su .env

3. Cada paso debe tener verificación (cómo saber que funcionó)

4. Si un paso depende de otro, marcarlo explícitamente

5. Si la guía es demasiado larga para una respuesta, decir al inicio:
   "La guía tiene N pasos, te la doy en M partes."
   No cortar a mitad de un paso.

---

## Variante: guías de servicios Docker

Secciones estándar para guías de servicios:

```
1. Descripción (qué es, para qué sirve, URL de acceso)
2. Arquitectura (diagrama de montaje/red)
3. Estructura de directorios (árbol del stack + datos)
4. Conceptos previos (si aplica: bind mounts, network_mode, etc.)
5. Instalación paso a paso (en orden de ejecución)
6. Gestión operativa (agregar/quitar bind mounts, configurar usuarios)
7. Mantenimiento (backup, restore, update)
8. Verificación y diagnóstico (comandos para comprobar que funciona)
9. Problemas comunes (tabla: síntoma | causa | solución)
10. Notas técnicas (decisiones de diseño, seguridad)
```

---

## Variante: análisis por partes (documentos largos >30K chars)

### Fase 1 — Análisis individual

Para cada fragmento, generar un resumen estructurado con:
- Decisiones tomadas en este fragmento
- Comandos/configs concretos (textual, sin resumir)
- Orden de ejecución detectado
- Contradicciones con fragmentos anteriores

### Fase 2 — Generación final

Cuando el usuario dice "sí, genera", combinar los análisis en la guía
con el formato estándar. Usar los análisis como fuente (no los fragmentos
originales) para evitar pérdida por contexto largo.

---

## Tips para resultados consistentes

- Si el LLM empieza a resumir: "STOP. Código COMPLETO del paso N."
- Si omite un paso: "Falta el paso de [X]. Está en el fragmento que dice [cita]."
- Usar respuestas largas. Priorizar completitud sobre brevedad.
- Idioma: siempre en el mismo idioma que los fragmentos.
