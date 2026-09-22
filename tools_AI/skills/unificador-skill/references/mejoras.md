# Auto-mejora — registro de lecciones aprendidas

La skill se mejora con cada uso. Después de cada unificación, registrar
las correcciones y patrones nuevos aquí.

---

## Ciclo de feedback

```
Usuario sube drafts
      ↓
Agente detecta problemas → Avisa ANTES de unificar
      ↓
Usuario confirma/corrige
      ↓
Agente unifica con las reglas
      ↓
Usuario revisa resultado
      ↓
┌─── OK → borrar drafts, listo
└─── Corrección → agregar lección a esta tabla
```

---

## Lo que el agente sugiere antes de unificar

- "Los fragmentos se contradicen en X — ¿cuál es la versión correcta?"
- "Hay IPs hardcodeadas — ¿las reemplazo por variables?"
- "Usas comandos genéricos — ¿corrijo para tu entorno?"
- "No veo info de backup/permisos — ¿la agrego o la marco pendiente?"
- "Hay 3 versiones del mismo contenido — uso la más completa, ¿OK?"

---

## Lo que el usuario puede decir para enseñar

- "Agrega esta regla: [nueva regla]" → se agrega a SKILL.md o aquí
- "Eso está mal, lo correcto es [X]" → se corrige y se registra
- "Siempre incluir [sección Y]" → se agrega al formato estándar

---

## Registro de mejoras

| Fecha | Mejora | Origen |
|-------|--------|--------|
| 2026-08-13 | Deduplicación agresiva (UNA versión, no alternativas) | filebrowser: 3 versiones del mismo contenido |
| 2026-08-13 | Reemplazar IPs por variables (`${SERVER_IP}`) | filebrowser: IP hardcodeada 192.168.1.200 |
| 2026-08-13 | Secciones estándar para guías Docker (10 secciones) | filebrowser: estructura final post-unificación |
| 2026-08-13 | Usar wrappers del framework (svc, dk, bat, instal) | filebrowser: tenía docker compose directo |
| 2026-08-13 | Verificar disponibilidad de variables de entorno del proyecto | filebrowser: ${SERVER_IP} no disponible sin .env global |

---

## Reglas acumuladas (extraídas de mejoras)

Estas reglas se aplican SIEMPRE al unificar, además de las del SKILL.md:

1. **Variables del proyecto** — Si el proyecto tiene variables de entorno
   (`$SERVER_IP`, `$dkco`, `$NAS_DOTFILES`), usarlas en vez de valores literales.

2. **Wrappers** — Si el proyecto tiene CLI propios (`svc`, `dk`, `instal`),
   usar esos en la guía en vez de los comandos genéricos.

3. **Una sola versión** — Si hay N versiones del mismo contenido de distintos
   LLMs, elegir la más completa/correcta. No mantener alternativas a menos
   que sea una decisión sin resolver.

4. **Tabla de problemas** — Siempre incluir una tabla de problemas comunes
   al final (síntoma | causa | solución). Extraer de los fragmentos.

5. **Verificación por paso** — Cada paso debe tener al menos un comando
   para verificar que se ejecutó correctamente.
