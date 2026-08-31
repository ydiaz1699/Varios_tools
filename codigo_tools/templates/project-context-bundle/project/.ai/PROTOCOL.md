# PROTOCOL — [PROJECT_ID]

> Artefacto condicional. Crear solo si existe un contrato de comunicación que deba mantenerse.

## Alcance y compatibilidad

- Transporte: `[OBSERVED_TRANSPORT_OR_PENDING]`
- Participantes: `[ENDPOINTS_OR_ROLES]`
- Versión/capacidad: `[VERSION_OR_NONE]`
- Fuente: `[PATH:SYMBOL/CONFIG]`
- Estado: `[OBSERVADO | DOCUMENTADO | CONTRADICTORIO | PENDIENTE_DE_VERIFICAR]`

## Mensajes/operaciones observadas

| Operación | Entrada/formato redactado | Respuesta/efecto | Errores/timeouts | Fuente | Estado |
|---|---|---|---|---|---|
| `[OPERATION]` | `[FORMAT_WITHOUT_SECRETS]` | `[EFFECT]` | `[BEHAVIOR]` | `[PATH:SYMBOL]` | `[estado]` |

## Seguridad y evolución

- Autenticación: `[OBSERVED | NOT_FOUND | PENDING]`.
- Integridad/confidencialidad: `[OBSERVED | NOT_FOUND | PENDING]`.
- Replay/versionado/compatibilidad: `[OBSERVED | NOT_FOUND | PENDING]`.
- No decidir un protocolo nuevo sin comparar requisitos, amenazas, coste y migración.

## Verificación

| Criterio | Método | Estado | Resultado |
|---|---|---|---|
| Compatibilidad | `[TEST/ANALYSIS]` | `[NO_EJECUTADO | EJECUTADO | PENDIENTE]` | `[RESULT]` |
