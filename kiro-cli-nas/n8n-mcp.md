# n8n-mcp como MCP en Kiro CLI (NAS)

> Que **Kiro CLI ayude a crear y gestionar workflows de n8n** por lenguaje natural:
> conoce los ~525 nodos de n8n, valida configuraciones y crea/actualiza/borra
> workflows en la instancia real vía la API REST de n8n.
>
> **Verificado en runtime** en el NAS (2026-09-24): `n8n_health_check` respondió
> `status: ok` contra `http://192.168.1.200:5678`.

---

## 0. Qué MCP es y por qué este (no el nativo de n8n)

Hay **dos cosas distintas** que se llaman "MCP de n8n"; no confundirlas:

| | Qué hace | Para qué sirve |
|---|---|---|
| **MCP nativo de n8n** (`Settings → Connect a client`, URL `.../mcp-server/http`) | expone *tus workflows ya creados* como tools hacia un cliente externo | que un LLM **ejecute** workflows que ya existen |
| **`czlonkowski/n8n-mcp`** ⭐ (este) | da a Kiro el conocimiento de los nodos + gestión vía API REST | que Kiro **diseñe, cree y modifique** workflows nuevos |

Para "que Kiro me ayude a crear workflows" el correcto es **`czlonkowski/n8n-mcp`**.
El MCP nativo (`N8N_MCP_ACCESS_TOKEN`) NO se necesita para esto; solo lo pediría
alguna función instance-level muy concreta (agents, data tables por MCP).

- Paquete npm: **`n8n-mcp`** (`bin: n8n-mcp` → se lanza con `npx n8n-mcp`). Verificado v2.89.0.
- Es un MCP **stdio** en Node; Node ya está en la imagen `kiro-cli-nas:local`.
- Tiene dos modos: **documentación** (solo conocer nodos, sin API key) y
  **documentación + gestión** (además crea/gestiona workflows en tu n8n → necesita
  `N8N_API_URL` + `N8N_API_KEY`). Aquí se monta el **modo gestión completo**.

## 1. Arquitectura

```
Kiro CLI (V3, network_mode: host)
   └─ npx n8n-mcp  (stdio, efímero, lo lanza Kiro bajo demanda)
        └─ HTTP a la API REST de n8n  →  http://192.168.1.200:5678
                                          (contenedor n8n, red db_net, publica 5678:5678)
```

- **NO es un contenedor permanente:** es un proceso stdio que Kiro lanza al usarlo
  y mata al terminar. Es solo un bloque en el `mcp.json`. Consumo en reposo: cero.
- El MCP corre **dentro** del contenedor de Kiro CLI (no toca el host).

### GOTCHA de red (por qué IP privada y no `http://n8n:5678`)

El contenedor kiro-cli usa **`network_mode: host`**, así que **NO está dentro de la
red `db_net`** y **no resuelve el nombre `n8n`**. En host mode comparte la red del
NAS, por lo que alcanza n8n por su **puerto publicado en el host**: `5678:5678`.
Por eso `N8N_API_URL=http://192.168.1.200:5678` (la IP LAN del NAS), no el nombre
de servicio Docker.

## 2. Requisitos previos

- Kiro CLI ya montado (imagen `kiro-cli-nas:local`, wrapper `$aadm/.local/bin/kiro`,
  ensamblador `mcp-build`). Ver [`./README.md`](./README.md).
- n8n corriendo y publicando `5678` (contenedor `n8n`, red `db_net`).
- Una **API key REST de n8n**: en n8n → **Settings → n8n API → Create an API key**
  (NO la pantalla "Connect a client / MCP Server", que es el otro MCP).

## 3. Credenciales — `$dkco/kiro-cli/n8n.env` (chmod 600)

El secreto NO se hardcodea en el `mcp.json`; va en un `.env` que el wrapper inyecta.

```bash
dk kiro-cli
cat > n8n.env <<'EOF'
N8N_API_URL=http://192.168.1.200:5678
N8N_API_KEY=PEGA_AQUI_TU_API_KEY_DE_N8N
EOF
chmod 600 n8n.env
nano n8n.env    # pega la API key real donde dice PEGA_AQUI_TU_API_KEY_DE_N8N
```

Verificar sin exponer el secreto (muestra solo la longitud de la key):

```bash
awk -F= '{print $1"="(($1=="N8N_API_KEY")?"<oculta, "length($2)" chars>":$2)}' n8n.env
```

## 4. Config MCP — `mcp_tools/n8n.json`

```json
{
  "mcpServers": {
    "n8n": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "WEBHOOK_SECURITY_MODE": "permissive",
        "N8N_API_URL": "${N8N_API_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}"
      },
      "disabled": false
    }
  }
}
```

- `MCP_MODE=stdio` + `DISABLE_CONSOLE_OUTPUT=true` son **obligatorios**: evitan que
  los logs contaminen el canal stdio JSON-RPC (si no, el cliente ve "Unexpected token…").
- `WEBHOOK_SECURITY_MODE=permissive` → ver el GOTCHA ESTRELLA en §7.
- Las variables `${...}` las resuelve el `.env` inyectado por el wrapper.
- Pinear versión: `"args": ["n8n-mcp@2.89.0"]` si se quiere fijar (por defecto `npx` baja la última).

Regenerar el `mcp.json` combinado:

```bash
$aadm/.local/bin/mcp-build     # debe decir "3 archivo(s)": n8n + nextdns + rclone
```

## 5. Wrapper `kiro` — inyectar `n8n.env`

Añadir la línea `--env-file .../n8n.env` al wrapper `$aadm/.local/bin/kiro`
(junto a la de nextdns). Debe quedar:

```bash
#!/usr/bin/env bash
set -eu
RCPASS="$(grep RCLONE_RC_PASS /docker/rclone-rcd/.env | cut -d= -f2)"
exec docker run -it --rm --network host \
  -e RCLONE_RC_PASS="$RCPASS" \
  --env-file /docker/kiro-cli/nextdns.env \
  --env-file /docker/kiro-cli/n8n.env \
  -v /docker/kiro-cli/data:/home/kiro \
  kiro-cli-nas:local --v3 "$@"
```

Verificar (deben salir DOS líneas `--env-file`):

```bash
grep -n "env-file" $aadm/.local/bin/kiro
```

## 6. Permisos V3 — `permissions.yaml`

Las 27 tools del MCP se clasifican en dos grupos. Precedencia `deny > ask > allow`
(la posición en el archivo no importa). Añadir al final de
`data/.kiro/settings/permissions.yaml`:

```yaml
  # ── n8n-mcp: lectura/documentación/validación → auto ──
  - capability: mcp
    match:
      - "n8n/tools_documentation"
      - "n8n/search_nodes"
      - "n8n/get_node"
      - "n8n/search_templates"
      - "n8n/validate_node"
      - "n8n/n8n_list_workflows"
      - "n8n/n8n_get_workflow"
      - "n8n/n8n_list_catalog"
      - "n8n/n8n_list_available_tools"
      - "n8n/n8n_explore_node_resources"
      - "n8n/n8n_validate_workflow"
      - "n8n/n8n_workflow_versions"
      - "n8n/n8n_health_check"
      - "n8n/n8n_diagnostic"
      - "n8n/n8n_executions"
      - "n8n/n8n_evaluations"
    effect: allow
  # ── n8n-mcp: crea/modifica/borra/ejecuta/credenciales → confirmar ──
  - capability: mcp
    match:
      - "n8n/n8n_create_workflow"
      - "n8n/n8n_update_full_workflow"
      - "n8n/n8n_update_partial_workflow"
      - "n8n/n8n_delete_workflow"
      - "n8n/n8n_autofix_workflow"
      - "n8n/n8n_deploy_template"
      - "n8n/n8n_test_workflow"
      - "n8n/n8n_manage_credentials"
      - "n8n/n8n_manage_agents"
      - "n8n/n8n_manage_datatable"
      - "n8n/n8n_manage_folders"
      - "n8n/n8n_audit_instance"
    effect: ask
```

Validar el YAML (no romper las reglas de rclone/nextdns):

```bash
python3 -c "import yaml; yaml.safe_load(open('data/.kiro/settings/permissions.yaml')); print('OK')"
```

> Cambiar `permissions.yaml` NO requiere `mcp-build` (solo relanzar `kiro`).

## 7. GOTCHA ESTRELLA verificado — SSRF bloquea IPs privadas

Al primer `n8n_health_check` falla con:

```
SSRF protection: Private IP addresses not allowed
```

**Causa:** el MCP trae una protección anti-SSRF que en modo `strict` (por defecto)
**bloquea IPs privadas**. Como el NAS está en la LAN (`192.168.1.200`), la rechaza.

**Verificado en el código** (`src/utils/ssrf-protection.ts`): la variable es
**`WEBHOOK_SECURITY_MODE`** (`process.env.WEBHOOK_SECURITY_MODE || 'strict'`), con
tres modos:

| Modo | Comportamiento |
|---|---|
| `strict` (default) | bloquea localhost **+ IPs privadas** + metadata de nube |
| `moderate` | permite localhost, bloquea IPs privadas + metadata |
| `permissive` | permite localhost **+ IPs privadas**, sigue bloqueando **metadata de nube** (169.254.169.254, GCP, Azure, Alibaba, Oracle) |

**FIX:** `WEBHOOK_SECURITY_MODE: permissive` en el `env` del `mcp_tools/n8n.json`
(§4) → `mcp-build` → relanzar `kiro`. Es seguro: estás en tu LAN privada y el modo
`permissive` sigue protegiendo contra los endpoints de metadata de nube.

> ⚠️ NO usar `ALLOW_PRIVATE_IPS`: esa variable **no existe** en el MCP (fue una
> invención de un modelo). La real, verificada en el código, es `WEBHOOK_SECURITY_MODE`.

## 8. Arrancar y verificar

```bash
$aadm/.local/bin/kiro
```

Dentro de la sesión:

```
/mcp
```

Debe listar **n8n** (junto a rclone y nextdns). La primera vez aparece
`◌ loading` porque `npx` descarga el paquete y carga la base de los ~525 nodos;
espera ~30–60 s o invoca una tool para forzar la carga.

Prueba de conexión:

```
usa n8n_health_check para comprobar la conexión con mi instancia de n8n
```

**Resultado verificado (2026-09-24):** `status: ok`, `url: http://192.168.1.200:5678`,
`n8n-mcp 2.89.0`, ~791 ms. Nota informativa esperada: la versión de n8n no se
reporta (n8n dejó de exponerla a la API desde 1.119.0) — no es un error.

## 9. Uso

```
lista mis workflows de n8n                                  # n8n_list_workflows → auto (allow)
busca el nodo de n8n para enviar HTTP requests              # search_nodes → auto
créame un workflow que reciba un webhook POST y envíe el    # n8n_create_workflow → PIDE CONFIRMACIÓN (ask)
  body por ntfy al topic "nas-alerts"
```

- Lectura/búsqueda/validación corren solas (allow).
- Crear/modificar/borrar/ejecutar piden confirmación (ask).

## 10. Las tools (verificadas del código, v2.89.0)

**Lectura/docs/validación (allow):** `tools_documentation`, `search_nodes`,
`get_node`, `search_templates`, `validate_node`, `n8n_list_workflows`,
`n8n_get_workflow`, `n8n_list_catalog`, `n8n_list_available_tools`,
`n8n_explore_node_resources`, `n8n_validate_workflow`, `n8n_workflow_versions`,
`n8n_health_check`, `n8n_diagnostic`, `n8n_executions`, `n8n_evaluations`.

**Escritura/gestión (ask):** `n8n_create_workflow`, `n8n_update_full_workflow`,
`n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_autofix_workflow`,
`n8n_deploy_template`, `n8n_test_workflow`, `n8n_manage_credentials`,
`n8n_manage_agents`, `n8n_manage_datatable`, `n8n_manage_folders`,
`n8n_audit_instance`.

## 11. Mantenimiento

- **Editar config del MCP:** `mcp_tools/n8n.json` → `mcp-build` → relanzar `kiro`.
- **Cambiar permisos:** editar `permissions.yaml` → relanzar (sin `mcp-build`).
- **Rotar API key:** editar `$dkco/kiro-cli/n8n.env` → relanzar `kiro`.
- **Tras tocar `data/` como root:** `chown -R 1000:1000 $dkco/kiro-cli/data`.

## 12. Notas operativas

- `mcp-build` y `kiro` viven en `$aadm/.local/bin`; como root ese dir no está en
  PATH → invócalos por ruta absoluta (`$aadm/.local/bin/mcp-build`) o añade
  `export PATH="/home/aadm/.local/bin:$PATH"` a `/root/.bashrc`.
- `npx n8n-mcp` requiere salida a internet la primera vez (host mode la tiene);
  luego usa caché.
- **Kiro Web (sandbox cloud) NO puede usar este MCP** (sin ruta a la LAN privada).
  Kiro CLI en el NAS SÍ.

## Referencias

- MCP: https://github.com/czlonkowski/n8n-mcp (npm `n8n-mcp`)
- Setup Codex/entornos MCP: https://github.com/czlonkowski/n8n-mcp/blob/main/docs/CODEX_SETUP.md
- SSRF: `src/utils/ssrf-protection.ts` del repo (variable `WEBHOOK_SECURITY_MODE`)
- Instalación de Kiro CLI: [`./README.md`](./README.md) · MCP rclone:
  [`../rclone-mcp-control-total/README.md`](../rclone-mcp-control-total/README.md) ·
  MCP NextDNS: [`./nextdns-multicuenta.md`](./nextdns-multicuenta.md)

_Verificado en runtime 2026-09-24. Contenido reescrito/resumido a partir de la
documentación y el código oficiales; se enlaza a la fuente._
