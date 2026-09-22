# AGENTS.md multinivel y subagentes

Ideas del video de Gentleman Programming (ver ficha
`tool_catalog/entries/gentleman-programming/agents-skills-video.md`) que complementan a
`references/auto-invoke-and-metadata.md`. Aquí: cómo dimensionar y dividir el
AGENTS.md, y cuándo delegar en subagentes.

## La arquitectura completa (de un vistazo)

```text
                    Usuario
                       │
                       ▼
              Agente / Orquestador
                       │
                 AGENTS.md raíz            ← mapa: enruta al contexto necesario
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       UI/API      Auth/etc.     (área N)   ← un AGENTS.md por feature (monorepo)
          │
     ┌────┼─────┐
     ▼    ▼     ▼
  Skills Skills Skills                       ← conocimiento/tareas bajo demanda
  React  Tests  Next.js                        (trigger + auto-invoke)
          │
          ▼
      Subagentes                              ← contexto aislado; devuelven un resumen
          │
          ▼
       Codebase
```

Filosofía: **no darle al agente todo el proyecto de golpe**. Darle un *mapa*
(AGENTS.md), *instrucciones específicas* (skills bajo demanda) y *delegación
aislada* (subagentes). El resto de esta reference detalla cada pieza.

## AGENTS.md = el README para agentes

`AGENTS.md` es el archivo que el agente lee para entender "la cultura del
proyecto": arquitectura, estructura de carpetas, tecnologías, dónde va cada cosa,
cómo trabajar. Se sitúa entre el agente y el codebase para que NO tenga que leer
todo el código en cada consulta.

### Regla de tamaño

- **Objetivo ~250 líneas, máximo ~500.** Más contexto NO es mejor: un AGENTS.md
  enorme obliga al modelo a procesar demasiado y **alucina** más.
- Si el proyecto es grande, no crezcas el AGENTS.md: **divídelo** (siguiente
  sección).

## Un AGENTS.md o varios (por feature)

| Situación | Estructura |
|---|---|
| Proyecto pequeño/mediano | **Un solo** `AGENTS.md` en la raíz |
| Monorepo / muchas áreas | **Un `AGENTS.md` por feature** + un **`AGENTS.md` root que enruta** |

En un monorepo, cada área tiene su propio AGENTS.md dentro de su carpeta
(`ui/AGENTS.md`, `api/AGENTS.md`, `auth/AGENTS.md`, ...). El **root** actúa de
router: cuando el usuario pregunta algo de UI, el agente entra al AGENTS.md root
y este le dice "lo de UI está en `ui/AGENTS.md`". Así se carga solo el contexto
necesario, no todo a la vez.

> Esto es el mismo principio de las skills (carga bajo demanda por trigger),
> aplicado a la documentación del proyecto. El `scope` de una skill (ver
> `auto-invoke-and-metadata.md`) indica a qué AGENTS.md pertenece.

### Cuándo NO dividir

Si el proyecto NO es un monorepo por features (p. ej. un framework organizado por
dominios, no por carpetas), un solo AGENTS.md raíz basta; los `scope` de las
skills mapean todos a ese archivo. No inventes carpetas solo para tener varios
AGENTS.md.

## Subagentes / orquestador

Para **tareas repetitivas o en paralelo** (ej. "editar 500 archivos",
"explorar toda una carpeta"), el agente principal actúa de **orquestador** y
delega en **subagentes**.

Cómo funciona y por qué ayuda al contexto:

- Cada subagente tiene su **propio contexto aislado** (una "burbuja").
- El subagente hace su trabajo y **devuelve solo un RESUMEN** al orquestador
  (no todo el proceso intermedio).
- Resultado: el contexto del orquestador crece muy poco → **no se ensucia** con
  búsquedas, lecturas y pasos intermedios.

### Cuándo delegar en un subagente

| Delegar (subagente) | Hacer directo |
|---|---|
| Explorar/mapear una parte grande del codebase | Un cambio puntual y localizado |
| Tarea repetitiva sobre muchos archivos | Una edición de 1–2 archivos |
| Trabajo independiente que solo necesita devolver un resumen | Algo que necesita todo el contexto de la sesión |

Regla: si el resultado que necesitas del trabajo es un **resumen** (no el detalle
paso a paso), es candidato a subagente. Combinar **subagentes + skills bien
organizadas + AGENTS.md** es la arquitectura completa del video.

## Cómo se relaciona con skill-creator

Al crear una skill, decide su `scope` pensando a qué AGENTS.md pertenece, y si el
flujo que documenta es de los que conviene ejecutar vía subagente (tarea
repetitiva/exploración), dilo en el cuerpo de la skill para que el agente delegue
en vez de ensuciar su contexto.
