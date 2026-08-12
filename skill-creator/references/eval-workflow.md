# Flujo de evaluación y mejora iterativa

---

## Ciclo principal

```
Escribir/mejorar skill
       ↓
Definir test cases (2-5 prompts realistas)
       ↓
Ejecutar test cases con la skill
       ↓
Revisar outputs (humano + métricas)
       ↓
Identificar fallas y patrones
       ↓
Corregir skill (generalizar, no overfit)
       ↓
Repetir hasta satisfacción
```

---

## Paso 1: Definir test cases

Buenos test cases son:
- Realistas (algo que un usuario real diría)
- Concretos (con detalles: paths, nombres, contexto)
- Variados (diferentes formulaciones, edge cases)
- Verificables (se puede evaluar si el output es correcto)

Guardar en `evals/evals.json`:
```json
{
  "skill_name": "mi-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Prompt realista del usuario con contexto",
      "expected_output": "Descripción de qué debería producir",
      "expectations": [
        "El output incluye X",
        "Se usó el script Y",
        "El formato es Z"
      ]
    }
  ]
}
```

---

## Paso 2: Ejecutar test cases

### Con subagents (Kiro, Claude Code)

Spawn un subagent por test case:
```
Ejecuta esta tarea:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Save outputs to: <workspace>/iteration-N/eval-ID/with_skill/outputs/
```

Opcionalmente, ejecutar baseline (sin skill) para comparar:
- Skill nueva → baseline = sin skill
- Skill mejorada → baseline = versión anterior

### Sin subagents (Claude.ai, sesión simple)

Leer la skill, seguir sus instrucciones, ejecutar la tarea.
Menos riguroso pero útil como sanity check.

---

## Paso 3: Revisar outputs

### Revisión cualitativa (humano)

Presentar outputs al usuario y pedir feedback:
- ¿El output es correcto?
- ¿Falta algo?
- ¿Sobra algo?
- ¿El formato está bien?

Feedback vacío = el usuario está conforme.

### Revisión cuantitativa (assertions)

Para cada expectation, evaluar PASS/FAIL con evidencia:

```json
{
  "expectations": [
    {
      "text": "El output incluye el nombre 'John Smith'",
      "passed": true,
      "evidence": "Encontrado en línea 15 del output"
    }
  ],
  "summary": {
    "passed": 4,
    "failed": 1,
    "total": 5,
    "pass_rate": 0.80
  }
}
```

---

## Paso 4: Identificar fallas y patrones

Al revisar múltiples test cases, buscar:

- **Trabajo repetido**: ¿Todos los tests escriben el mismo helper script?
  → Bundlear como `scripts/` en la skill
- **Instrucciones ignoradas**: ¿El LLM no sigue un paso?
  → Explicar el porqué, no solo el qué
- **Ambigüedad**: ¿El LLM interpreta diferente cada vez?
  → Ser más específico en ese paso
- **Over-engineering**: ¿El LLM hace pasos innecesarios?
  → Eliminar la instrucción que lo causa
- **Transcripts**: Leer los transcripts, no solo los outputs finales

---

## Paso 5: Corregir la skill

### Principios de corrección

1. **Generalizar, no overfit** — No corregir solo para el test case que falló.
   Preguntarse: "¿Esta corrección ayuda en otros prompts similares?"

2. **Mantener lean** — Cada corrección agrega tokens. Si algo no mejora
   los resultados, quitarlo.

3. **Explicar el porqué** — En lugar de ALWAYS/NEVER en mayúsculas,
   explicar la razón. El LLM generaliza mejor con entendimiento.

4. **Scripts para trabajo repetitivo** — Si 3/3 test cases hacen lo mismo
   manualmente, crear un script que lo haga bien una vez.

5. **Leer los transcripts** — Si el LLM pierde tiempo en algo improductivo,
   eliminar la parte de la skill que lo causa.

---

## Criterios de terminación

Dejar de iterar cuando:

- [ ] El usuario dice que está satisfecho
- [ ] El feedback de todos los test cases es vacío
- [ ] No hay mejoras significativas entre iteraciones
- [ ] El pass_rate es >90% en assertions cuantitativas

---

## Evaluación de descriptions (trigger eval)

Separado del eval de outputs. Evalúa si la skill triggerea correctamente.

### Crear eval set de triggering

20 queries: 10 should-trigger + 10 should-NOT-trigger.

### Métricas de triggering

| Métrica | Cálculo | Target |
|---------|---------|--------|
| Precision | triggers correctos / total triggers | >90% |
| Recall | triggers correctos / should-trigger total | >80% |
| Accuracy | correctos / total | >85% |

Para detalles, ver `references/description-optimization.md`.

---

## Organización del workspace

```
mi-skill-workspace/
├── iteration-1/
│   ├── eval-1/
│   │   ├── with_skill/
│   │   │   ├── outputs/        ← archivos generados
│   │   │   ├── grading.json    ← evaluación de assertions
│   │   │   └── timing.json     ← tokens + duración
│   │   └── without_skill/      ← baseline (opcional)
│   │       └── outputs/
│   ├── eval-2/
│   │   └── ...
│   ├── benchmark.json           ← stats agregadas
│   └── feedback.json            ← feedback del usuario
├── iteration-2/
│   └── ...
└── evals/
    └── evals.json               ← definición de test cases
```

---

## Ejemplo real — evaluación de `docker-nas`

Skill de entorno/CLI con 6 archivos (1270 líneas). Evaluada tras su creación.

### Métricas medidas

```bash
# Ejecutado contra la skill finalizada:
SKILL.md:              240 líneas
references/agent.md:   212 líneas
references/entorno.md: 253 líneas
references/estructura: 224 líneas
references/seguridad:  187 líneas
references/svc.md:     154 líneas
Description:           ~496 chars
Tokens estimados/trigger: ~960 (body / 4)
```

### Resultado vs targets

| Métrica | Target | Resultado | Decisión |
|---------|--------|-----------|----------|
| SKILL.md líneas | <200 ideal | 240 | Aceptar: tablas compactas de comandos esenciales (>50% triggers) |
| references/ max | <200 | 253 (entorno.md) | Aceptar: son tablas de aliases, no prosa verbosa |
| Description chars | <500 | 496 | ✅ Dentro del ideal |
| Tokens por trigger | <2000 | 960 | ✅ Muy bien |
| Carga progresiva | Sí/No | Sí | ✅ |
| Punteros con contexto | Sí/No | Sí | ✅ |

### Test cases usados (trigger evaluation)

| Query | Should trigger | Resultado |
|-------|---------------|-----------|
| "Quiero instalar Jellyfin en el NAS" | ✅ | ✅ Triggerea |
| "Reinicia traefik" | ✅ | ✅ Triggerea |
| "¿Cómo veo los logs de emqx?" | ✅ | ✅ Triggerea (responde con `svc logs emqx`) |
| "Quiero crear un script en Python para scraping" | ❌ | ❌ No triggerea |
| "Explícame qué es Docker" | ❌ | ❌ No triggerea |

### Problemas encontrados y decisiones

1. **entorno.md excede 200 líneas (253)**
   - Causa: tablas de aliases + navegación + prompt + git + completions
   - Opciones: (a) split en entorno.md + aliases.md, (b) dejar como está
   - Decisión: dejar — split sería artificial, las tablas son compactas

2. **SKILL.md excede ideal de 200 (240)**
   - Causa: incluye tabla de comandos esenciales
   - Test: ¿se necesitan en >50% de triggers? → Sí (dk, svc, instal)
   - Decisión: mantener en body, moverlos a references causaría carga extra

3. **Algunas reglas sin porqué ("NUNCA /docker/ → USA $dkco")**
   - Causa: el porqué es implícito (portabilidad/configurabilidad)
   - Mejora futura: agregar "(porque $dkco es configurable via DOCKER_BASE)"
   - Decisión: aceptar por ahora, iterar si el LLM falla en seguirlas

### Conclusión

Pass rate: 100% en trigger eval (5/5). Métricas dentro de rangos aceptables.
No se hizo iteración adicional — el usuario confirmó satisfacción.

Para el proceso completo y decisiones de diseño, ver `references/case-study-docker-nas.md`.

---

## Blind comparison (avanzado, opcional)

Para comparaciones rigurosas entre dos versiones de una skill:

1. Ejecutar ambas versiones en los mismos test cases
2. Dar outputs A y B a un evaluador sin decirle cuál es cuál
3. El evaluador juzga calidad y elige ganador
4. Analizar por qué ganó para extraer mejoras

Útil cuando: "¿la versión nueva es realmente mejor?" no tiene
respuesta obvia mirando los outputs.
