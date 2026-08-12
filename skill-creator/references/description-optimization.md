# Optimización de description para triggering

La description es el mecanismo principal que determina si un LLM activa
una skill. Este documento cubre cómo optimizarla.

---

## Cómo funciona el triggering

Las skills aparecen en la lista de `available_skills` del LLM con su
name + description. El LLM decide si consultar una skill basándose en
esa description vs. el intent del usuario.

Importante:
- El LLM tiende a **under-trigger** (no usar skills que debería)
- Queries simples de un paso rara vez triggean skills (el LLM las resuelve solo)
- Queries complejas, multi-paso o especializadas triggean más confiablemente

---

## Reglas para escribir descriptions

### DO

- Capacidad + cuándo usar en 1-2 oraciones
- Tercera persona ("Administra...", "Genera...", "Diagnostica...")
- Keywords que matcheen el intent del usuario
- Ser "un poco pushy" para compensar el under-triggering
- Incluir el tipo de output esperado si es relevante

### DON'T

- No listar todas las frases posibles del usuario
- No incluir detalles de implementación
- No exceder 200 palabras (hard limit: 1024 chars)
- No usar angle brackets (`<` o `>`)
- No repetir el name en la description

---

## Patrón: description efectiva

```
[Qué hace] + [Cuándo usarla] + [Keywords de triggering opcionales]
```

### Ejemplos

**Skill de Docker/NAS:**
```yaml
description: >
  Administra un NAS/Homelab Debian con Docker mediante tres capas: shell
  personalizado, CLI Docker (svc), y agente IA Python. Usar cuando el usuario
  mencione NAS, homelab, contenedor, servicio, compose, dk, adm, svc, agent,
  o cualquier comando del entorno bash personalizado.
```

**Skill de API design:**
```yaml
description: >
  Diseña APIs RESTful siguiendo convenciones de la empresa: naming, versionado,
  paginación, manejo de errores. Usar para nuevos endpoints, revisión de APIs
  existentes, o generación de specs OpenAPI.
```

**Skill de code review:**
```yaml
description: >
  Revisa cambios de código a nivel semántico: analiza el comportamiento del
  cambio, no la sintaxis. Produce un narrative organizado por concern, no por
  archivo. Usar antes de crear un PR o cuando se necesite review profundo.
```

---

## Flujo de optimización (con eval set)

### 1. Crear eval set (20 queries)

```json
[
  {"query": "prompt realista del usuario", "should_trigger": true},
  {"query": "prompt que NO debería triggear", "should_trigger": false}
]
```

**Should-trigger (8-10 queries):**
- Diferentes formulaciones del mismo intent
- Casos donde el usuario NO nombra la skill explícitamente
- Casos edge o poco comunes que sí aplican
- Mix de formal/casual, largo/corto

**Should-NOT-trigger (8-10 queries):**
- Near-misses: comparten keywords pero necesitan algo diferente
- Dominios adyacentes que compiten por las mismas palabras
- Queries ambiguas donde otra tool es más apropiada
- NO incluir queries obviamente irrelevantes (eso no testea nada)

### 2. Evaluar la description actual

Para cada query, verificar si la skill triggerea o no.
Calcular: precision, recall, accuracy.

### 3. Iterar sobre la description

Basándose en los fallos:
- **Failed to trigger** → agregar keywords o ampliar el scope
- **False triggers** → ser más específico o excluir dominios
- **No overfit** → generalizar, no listar queries específicos

### 4. Validar con test set

Separar 40% del eval set como holdout. Optimizar solo con el 60% de train.
El test score es el que importa para evitar overfitting.

---

## Métricas

| Métrica | Target |
|---------|--------|
| Precision (triggers correctos / total triggers) | >90% |
| Recall (triggers correctos / total should-trigger) | >80% |
| Accuracy (correctos / total queries) | >85% |
| Chars de description | <500 (ideal), <1024 (hard limit) |

---

## Tips avanzados

- **Competencia entre skills**: Si tienes varias skills que compiten por
  keywords similares, hacer que cada description sea más específica sobre
  su dominio exacto.

- **Under-triggering persistente**: Si después de varias iteraciones la
  skill no triggerea, cambiar la estructura completa de la descripción
  (no solo agregar palabras).

- **Description vs. body**: La description decide SI se usa la skill.
  El body decide CÓMO se usa. No mezclar.
