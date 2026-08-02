# Guía: Creación y Gestión de 100 Service Accounts (Google Cloud)

> **Prerrequisito para**: Módulo 2 (9Drive + AutoRclone) y Módulo 3 (rclone-media)
> **Herramientas**: `gcloud` CLI, Google Cloud Console, Google Groups
> **Tiempo estimado**: 30-45 minutos (primera vez), 5 minutos (automatizado)

---

## 1. Conceptos fundamentales

### 1.1 ¿Qué es una Service Account (SA)?

Una SA es una **identidad no-humana** en Google Cloud Platform que:
- Tiene su propio email: `nombre@proyecto.iam.gserviceaccount.com`
- Se autentica con una **clave privada JSON** (no con usuario/password)
- Tiene su **propia cuota** de Google Drive API (750 GB/día upload, ~10 TB/día download)
- Puede ser miembro de un Shared Drive (como si fuera una persona)

### 1.2 Límites de GCP relevantes

| Recurso | Límite | Notas |
|---------|--------|-------|
| SA por proyecto | 100 | Límite duro, no se puede aumentar fácilmente |
| Keys por SA | 10 | Solo necesitas 1 por SA |
| Proyectos por cuenta | 25 (soft) | Se puede pedir aumento |
| SA en un Google Group | Sin límite práctico | Recomendado para gestión masiva |
| Miembros de un Shared Drive | 600 | Incluye grupos (1 grupo = 1 slot) |


### 1.3 ¿Por qué 100 SA?

```
1 SA  = 750 GB/día upload + ~10 TB/día download
100 SA = 75 TB/día upload + ~1 PB/día download (teórico)
```

Para un homelab con Jellyfin + backups, probablemente 20-50 SA bastarían,
pero crear 100 (el máximo por proyecto) no tiene costo adicional y da margen
para crecimiento sin reconfigurar.

### 1.4 Estructura de naming recomendada

```
Proyecto GCP: mi-nas-storage (o similar)
SA naming:    sa-rclone-001 ... sa-rclone-100
Email:        sa-rclone-001@mi-nas-storage.iam.gserviceaccount.com
Key files:    /etc/rclone/sa-pool/sa-001.json ... sa-100.json
```

---

## 2. Preparación del entorno

### 2.1 Instalar gcloud CLI

```bash
# Debian/Ubuntu
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt update && sudo apt install -y google-cloud-cli
```

### 2.2 Autenticarse

```bash
gcloud auth login
# Se abre un browser para OAuth — usar la cuenta que es owner del proyecto GCP
```

### 2.3 Crear proyecto (si no existe)

```bash
PROJECT_ID="mi-nas-storage"
gcloud projects create ${PROJECT_ID} --name="NAS Storage"
gcloud config set project ${PROJECT_ID}
```

### 2.4 Habilitar APIs necesarias

```bash
gcloud services enable drive.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```


---

## 3. Creación masiva de Service Accounts

### 3.1 Script automatizado

```bash
#!/bin/bash
# create-sa-pool.sh — Crear 100 Service Accounts + descargar keys
set -euo pipefail

PROJECT_ID="${1:?Uso: $0 <project-id> [output-dir]}"
OUTPUT_DIR="${2:-./sa-keys}"
SA_PREFIX="sa-rclone"
SA_COUNT=100

mkdir -p "${OUTPUT_DIR}"

echo "=== Creando ${SA_COUNT} Service Accounts en proyecto '${PROJECT_ID}' ==="

for i in $(seq -w 1 ${SA_COUNT}); do
    SA_NAME="${SA_PREFIX}-${i}"
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    KEY_FILE="${OUTPUT_DIR}/sa-${i}.json"

    # Crear SA (ignorar error si ya existe)
    if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
        echo "[${i}/${SA_COUNT}] SA '${SA_NAME}' ya existe, saltando creación..."
    else
        echo "[${i}/${SA_COUNT}] Creando SA '${SA_NAME}'..."
        gcloud iam service-accounts create "${SA_NAME}" \
            --display-name="Rclone SA ${i}" \
            --description="Service Account ${i} para rclone (NAS storage pool)" \
            --project="${PROJECT_ID}"
    fi

    # Descargar key (si no existe ya)
    if [[ -f "${KEY_FILE}" ]]; then
        echo "  Key ya existe en ${KEY_FILE}, saltando..."
    else
        echo "  Descargando key → ${KEY_FILE}"
        gcloud iam service-accounts keys create "${KEY_FILE}" \
            --iam-account="${SA_EMAIL}" \
            --project="${PROJECT_ID}"
    fi

    # Pequeña pausa para no triggear rate limits de la API de IAM
    sleep 0.5
done

echo ""
echo "=== COMPLETADO ==="
echo "Keys generadas en: ${OUTPUT_DIR}/"
echo "Total SAs: $(ls ${OUTPUT_DIR}/sa-*.json 2>/dev/null | wc -l)"
echo ""
echo "PRÓXIMO PASO: agregar las SA al Shared Drive (ver sección 4)"
```

### 3.2 Ejecución

```bash
chmod +x create-sa-pool.sh
./create-sa-pool.sh mi-nas-storage /etc/rclone/sa-pool/
```

### 3.3 Verificar resultado

```bash
# Listar todas las SA del proyecto
gcloud iam service-accounts list --project=mi-nas-storage

# Contar keys descargadas
ls /etc/rclone/sa-pool/sa-*.json | wc -l
# Debe dar: 100
```


---

## 4. Agregar SA al Shared Drive

### 4.1 Opción A: Vía Google Group (RECOMENDADO)

Agregar 100 SA individualmente a un Shared Drive es tedioso y ocupa 100 slots de miembro.
Usar un **Google Group** reduce a **1 slot**:

```
1. Crear Google Group: rclone-sas@tudominio.com (o usar un grupo gratuito en groups.google.com)
2. Agregar las 100 SA como miembros del grupo
3. Agregar el grupo al Shared Drive como "Content Manager"
```

#### Paso 1: Crear grupo

```bash
# Si tienes Google Workspace con dominio:
# → admin.google.com → Groups → Create group
# Nombre: rclone-sas
# Email: rclone-sas@tudominio.com
# Tipo: Restricted (solo admins pueden agregar miembros)

# Si NO tienes Workspace (cuenta personal):
# → groups.google.com → Create group
# Configurar: "Who can join" = "Only invited users"
```

#### Paso 2: Agregar SA al grupo (script)

```bash
#!/bin/bash
# add-sa-to-group.sh — Agregar todas las SA a un Google Group
set -euo pipefail

PROJECT_ID="${1:?Uso: $0 <project-id> <group-email>}"
GROUP_EMAIL="${2:?}"
SA_PREFIX="sa-rclone"
SA_COUNT=100

echo "=== Agregando ${SA_COUNT} SA al grupo '${GROUP_EMAIL}' ==="

for i in $(seq -w 1 ${SA_COUNT}); do
    SA_EMAIL="${SA_PREFIX}-${i}@${PROJECT_ID}.iam.gserviceaccount.com"
    echo "[${i}/${SA_COUNT}] Agregando ${SA_EMAIL}..."
    
    # Usando la API de Directory (requiere Workspace admin o Group owner)
    # Alternativa: hacerlo vía Cloud Identity API o manualmente
    gcloud identity groups memberships add \
        --group-email="${GROUP_EMAIL}" \
        --member-email="${SA_EMAIL}" \
        --roles=MEMBER \
        2>/dev/null || echo "  (ya es miembro o error — verificar manualmente)"
    
    sleep 0.3
done

echo ""
echo "=== COMPLETADO ==="
echo "Verificar en: https://groups.google.com/g/$(echo ${GROUP_EMAIL} | cut -d@ -f1)/members"
```

**Nota**: Si no tienes Google Workspace ni Cloud Identity, puedes agregar miembros al grupo
manualmente vía groups.google.com (tedioso para 100, pero factible con copy-paste de emails).

#### Paso 3: Agregar grupo al Shared Drive

```
Google Drive → Shared Drives → [tu drive] → Manage members
→ Add: rclone-sas@tudominio.com → Role: Content Manager
```

### 4.2 Opción B: Agregar SA individualmente (sin grupo)

Si no puedes crear un grupo, agrega cada SA directamente al Shared Drive.

**Limitación**: un Shared Drive acepta máximo 600 miembros. Con 100 SA + tus cuentas
personales + otros servicios, no deberías tener problema.

```python
# Script Python usando Google Drive API para agregar SA como miembros
# (más fiable que hacerlo manualmente para 100 cuentas)

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
SHARED_DRIVE_ID = '0ABCxxxxxxxxxxxxxxxxxx'  # ID del Shared Drive
SA_DIR = '/etc/rclone/sa-pool/'

# Usar una SA existente (o OAuth personal) para autenticarse
creds = service_account.Credentials.from_service_account_file(
    f'{SA_DIR}/sa-001.json', scopes=SCOPES
)
# NOTA: la SA-001 debe tener rol "Manager" en el Shared Drive para agregar miembros

drive = build('drive', 'v3', credentials=creds)

import os, json
for filename in sorted(os.listdir(SA_DIR)):
    if not filename.endswith('.json'):
        continue
    with open(f'{SA_DIR}/{filename}') as f:
        sa_email = json.load(f)['client_email']
    
    try:
        drive.permissions().create(
            fileId=SHARED_DRIVE_ID,
            supportsAllDrives=True,
            body={
                'type': 'user',
                'role': 'writer',  # "writer" = Content Manager en Shared Drives
                'emailAddress': sa_email,
            }
        ).execute()
        print(f"✅ {sa_email} agregada")
    except Exception as e:
        print(f"⚠️ {sa_email}: {e}")
```


---

## 5. Permisos y seguridad de las SA keys

### 5.1 Almacenamiento seguro en el NAS

```bash
# Directorio del pool
sudo mkdir -p /etc/rclone/sa-pool
sudo chown root:rclone /etc/rclone/sa-pool
sudo chmod 0750 /etc/rclone/sa-pool

# Cada key file
sudo chown root:rclone /etc/rclone/sa-pool/*.json
sudo chmod 0640 /etc/rclone/sa-pool/*.json
```

**Por qué estos permisos**:
- `root:rclone` con `0640`: solo root puede modificar, el grupo `rclone` puede leer.
- El usuario `rclone` (miembro del grupo `rclone`) lee las keys para autenticarse.
- Otros usuarios del sistema NO pueden acceder a las keys.

### 5.2 Qué contiene un JSON de SA

```json
{
  "type": "service_account",
  "project_id": "mi-nas-storage",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEo...\n-----END RSA PRIVATE KEY-----\n",
  "client_email": "sa-rclone-001@mi-nas-storage.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**IMPORTANTE**: El campo `private_key` es una **clave RSA privada**. Si se filtra:
- El atacante puede autenticarse como esa SA
- Puede acceder a todo lo que la SA tiene permiso (el Shared Drive en este caso)
- Mitigación: las SA solo tienen scope `drive.readonly` (módulo 3) o `drive` (módulo 2)

### 5.3 Principio de menor privilegio para SA

| Módulo | SA rango | Scope necesario | Rol en Shared Drive |
|--------|----------|-----------------|---------------------|
| 1 (backup) | SA dedicada aparte | `drive` (read+write) | Content Manager |
| 2 (9Drive) | SA-001 a SA-050 | `drive` (read+write) | Content Manager |
| 3 (media) | SA-051 a SA-100 | `drive.readonly` | Viewer o Commenter |

**Nota sobre scope**: El scope se define en la configuración de rclone (campo `scope`),
NO en la SA misma. Una SA puede tener `drive` scope en un remote y `drive.readonly` en otro.
Sin embargo, el rol en el Shared Drive sí limita las operaciones reales:
- Viewer: solo leer (ideal para módulo 3)
- Content Manager: leer + escribir (necesario para módulos 1 y 2)
- Manager: todo incluyendo permisos (NO dar a las SA de rclone)

### 5.4 No dar roles IAM innecesarios

Las SA para rclone **NO necesitan** ningún rol IAM en el proyecto GCP:
- No necesitan `roles/owner`, `roles/editor`, ni `roles/viewer` del proyecto
- Solo necesitan acceso al **Shared Drive** (que se otorga vía Drive, no IAM)
- Dejarlas sin roles IAM minimiza el daño si se comprometen

```bash
# Verificar que las SA no tienen roles IAM (debe estar vacío o solo roles mínimos)
gcloud projects get-iam-policy mi-nas-storage --format=json | \
  jq '.bindings[] | select(.members[] | contains("sa-rclone"))'
# Si aparecen roles → removerlos
```


---

## 6. Rotación de keys (mantenimiento)

### 6.1 ¿Por qué rotar keys?

- Google recomienda rotar keys cada 90 días (no es obligatorio para SA de sistema).
- Si una key se filtra, la rotación la invalida.
- Cada SA puede tener hasta 10 keys simultáneas (facilita rotación sin downtime).

### 6.2 Script de rotación

```bash
#!/bin/bash
# rotate-sa-keys.sh — Rotar keys de todas las SA del pool
set -euo pipefail

PROJECT_ID="${1:?Uso: $0 <project-id> [sa-pool-dir]}"
SA_POOL_DIR="${2:-/etc/rclone/sa-pool}"
SA_PREFIX="sa-rclone"
SA_COUNT=100

echo "=== Rotando keys de ${SA_COUNT} SA ==="
echo "ADVERTENCIA: esto invalida las keys anteriores."
echo "Asegúrate de que ningún servicio está usando las keys actuales activamente."
read -p "¿Continuar? (y/N) " confirm
[[ "${confirm}" =~ ^[yY]$ ]] || exit 0

for i in $(seq -w 1 ${SA_COUNT}); do
    SA_EMAIL="${SA_PREFIX}-${i}@${PROJECT_ID}.iam.gserviceaccount.com"
    KEY_FILE="${SA_POOL_DIR}/sa-${i}.json"
    
    echo "[${i}/${SA_COUNT}] Rotando key de ${SA_EMAIL}..."
    
    # Obtener key ID actual (para borrarla después)
    OLD_KEY_ID=""
    if [[ -f "${KEY_FILE}" ]]; then
        OLD_KEY_ID=$(python3 -c "import json; print(json.load(open('${KEY_FILE}'))['private_key_id'])" 2>/dev/null || true)
    fi
    
    # Crear nueva key
    gcloud iam service-accounts keys create "${KEY_FILE}.new" \
        --iam-account="${SA_EMAIL}" \
        --project="${PROJECT_ID}"
    
    # Reemplazar key vieja
    mv "${KEY_FILE}.new" "${KEY_FILE}"
    
    # Borrar key vieja del lado de Google (si tenemos el ID)
    if [[ -n "${OLD_KEY_ID}" ]]; then
        gcloud iam service-accounts keys delete "${OLD_KEY_ID}" \
            --iam-account="${SA_EMAIL}" \
            --project="${PROJECT_ID}" \
            --quiet 2>/dev/null || true
    fi
    
    sleep 0.5
done

# Restaurar permisos
sudo chown root:rclone ${SA_POOL_DIR}/*.json
sudo chmod 0640 ${SA_POOL_DIR}/*.json

echo ""
echo "=== Keys rotadas exitosamente ==="
echo "Reiniciar servicios que usan las SA:"
echo "  sudo systemctl restart rclone-media@media.service"
echo "  # (9Drive se reconfigura automáticamente si lee del directorio)"
```

### 6.3 Automatizar con systemd timer

```ini
# /etc/systemd/system/rclone-sa-rotate-keys.timer
[Unit]
Description=Rotate SA keys every 90 days

[Timer]
OnCalendar=*-01,04,07,10-01 02:00:00
Persistent=true
RandomizedDelaySec=3600

[Install]
WantedBy=timers.target
```

---

## 7. Health check del pool

### 7.1 Verificar que las SA tienen acceso al Shared Drive

```bash
#!/bin/bash
# sa-health-check.sh — Verificar acceso de cada SA al Shared Drive
set -euo pipefail

SA_POOL_DIR="${1:-/etc/rclone/sa-pool}"
SHARED_DRIVE_ID="${2:?Uso: $0 <sa-pool-dir> <shared-drive-id>}"
FAILURES=0

echo "=== Health check del pool de SA ==="

for key_file in $(ls ${SA_POOL_DIR}/sa-*.json | sort); do
    sa_num=$(basename "${key_file}" .json | sed 's/sa-//')
    
    # Intentar listar el root del Shared Drive con esta SA
    result=$(rclone lsd "test-sa-${sa_num}:" \
        --drive-service-account-file="${key_file}" \
        --drive-team-drive="${SHARED_DRIVE_ID}" \
        --drive-scope=drive.readonly \
        -q 2>&1) || true
    
    if echo "${result}" | grep -qi "error\|failed\|denied"; then
        echo "❌ SA-${sa_num}: FALLO — ${result}"
        ((FAILURES++))
    else
        echo "✅ SA-${sa_num}: OK"
    fi
done

echo ""
echo "=== Resultado: $((100 - FAILURES))/100 SA funcionando ==="
[[ ${FAILURES} -eq 0 ]] && echo "Pool 100% saludable" || echo "⚠️ ${FAILURES} SA con problemas"
```

### 7.2 Tool del agente para health check

```python
@tool
def rclone_sa_pool_health() -> str:
    """Verifica que todas las SA del pool tienen acceso al Shared Drive.
    Reporta cuántas están funcionando, cuántas en cooldown, y cuántas fallaron.
    Útil después de rotación de keys o cambios de permisos en el Shared Drive."""
```


---

## 8. Gestión de múltiples proyectos GCP

### 8.1 ¿Cuándo necesitas más de 1 proyecto?

- **100 SA no son suficientes**: crear otro proyecto con 100 SA más (200 total).
- **Aislamiento**: un proyecto para backup (crítico), otro para media (menos crítico).
- **Límites de cuota del proyecto**: si Google limita el proyecto entero (raro pero posible).

### 8.2 Límite de proyectos

- Cuentas nuevas: ~5-12 proyectos (soft limit).
- Después de historial de uso: hasta 25-50.
- Se puede pedir aumento vía Google Cloud support.

### 8.3 Nomenclatura multi-proyecto

```
Proyecto 1: mi-nas-storage-01
  SA: sa-rclone-001 ... sa-rclone-100
  Keys: /etc/rclone/sa-pool/p01/sa-001.json ... sa-100.json

Proyecto 2: mi-nas-storage-02
  SA: sa-rclone-001 ... sa-rclone-100
  Keys: /etc/rclone/sa-pool/p02/sa-001.json ... sa-100.json
```

---

## 9. Shared Drives: creación y configuración

### 9.1 Crear Shared Drive

```
Google Drive → Shared Drives → New → Nombre: "NAS Media Library"
```

O vía API:

```python
from googleapiclient.discovery import build
drive = build('drive', 'v3', credentials=creds)

shared_drive = drive.drives().create(
    requestId='unique-request-id-123',
    body={'name': 'NAS Media Library'}
).execute()

print(f"Shared Drive ID: {shared_drive['id']}")
# Guardar este ID — se usa en rclone.conf como team_drive
```

### 9.2 Estructura recomendada del Shared Drive

```
NAS Media Library (Shared Drive)
├── media/                    ← directorio raíz del crypt remote (módulo 3)
│   ├── [archivos cifrados]   ← Jellyfin (vía rclone mount + crypt)
│   └── ...
├── backups/                  ← directorio del backup offsite (módulo 1)
│   ├── [archivos cifrados]
│   └── ...
└── uploads/                  ← directorio de 9Drive (módulo 2, sin cifrar o con cifrar)
    └── ...
```

### 9.3 Límites de Shared Drives

| Recurso | Límite |
|---------|--------|
| Archivos totales | 400,000 |
| Niveles de anidamiento | 20 |
| Tamaño total | Sin límite (si tienes storage suficiente) |
| Miembros (directos + grupos) | 600 |
| Shared Drives por organización | 500,000 |

**IMPORTANTE**: El límite de 400k archivos es **por Shared Drive**. Si tu biblioteca
supera esto, necesitas múltiples Shared Drives (ej: uno para películas, otro para series).

### 9.4 Shared Drive vs Google Drive personal

| Aspecto | Shared Drive | Drive Personal |
|---------|-------------|----------------|
| SA como miembro | ✅ Nativo | ⚠️ Requiere `--drive-impersonate` |
| Cuota de storage | Pooled (organización) o ilimitado con Workspace | 15 GB por SA (inútil) |
| SA rotation | ✅ Funciona directo | ❌ Cada SA ve su propio Drive vacío |
| Propiedad de archivos | Del Shared Drive (no se pierden si se borra una SA) | De la SA (se pierden si se borra) |
| **Recomendación** | ✅ Usar siempre para este proyecto | ❌ No usar para pool de SA |

**Conclusión**: Para este proyecto, necesitas **Shared Drives** (Team Drives).
Un Drive personal no funciona con SA rotation porque cada SA tiene su propio espacio de 15 GB.


---

## 10. Limpieza y eliminación de SA

### 10.1 Eliminar SA individuales

```bash
SA_EMAIL="sa-rclone-050@mi-nas-storage.iam.gserviceaccount.com"
gcloud iam service-accounts delete "${SA_EMAIL}" --project=mi-nas-storage --quiet
rm -f /etc/rclone/sa-pool/sa-050.json
```

### 10.2 Eliminar TODO el pool (nuclear)

```bash
#!/bin/bash
# delete-all-sa.sh — DESTRUCTIVO: elimina todas las SA del proyecto
set -euo pipefail
PROJECT_ID="${1:?Uso: $0 <project-id>}"

echo "⚠️ ESTO ELIMINARÁ TODAS LAS SA DE RCLONE DEL PROYECTO '${PROJECT_ID}'"
echo "Los archivos en el Shared Drive NO se borran (son propiedad del Drive, no de la SA)"
read -p "¿Estás SEGURO? (escribir 'DELETE'): " confirm
[[ "${confirm}" == "DELETE" ]] || exit 1

for i in $(seq -w 1 100); do
    SA_EMAIL="sa-rclone-${i}@${PROJECT_ID}.iam.gserviceaccount.com"
    echo "Eliminando ${SA_EMAIL}..."
    gcloud iam service-accounts delete "${SA_EMAIL}" --project="${PROJECT_ID}" --quiet 2>/dev/null || true
done

echo "Limpiando keys locales..."
rm -f /etc/rclone/sa-pool/sa-*.json

echo "=== Pool eliminado ==="
```

---

## 11. Automatización vía el agente NAS

### 11.1 Tool para crear el pool

```python
@tool
def rclone_sa_pool_create(project_id: str, count: int = 100) -> str:
    """Crea N Service Accounts en el proyecto GCP indicado y descarga sus keys
    a /etc/rclone/sa-pool/. Requiere gcloud CLI autenticado en el NAS.
    
    IMPORTANTE: Requiere que el usuario haya ejecutado 'gcloud auth login' previamente
    en el NAS (el agente NO maneja credenciales de GCP directamente).
    
    Args:
        project_id: ID del proyecto GCP, ej. "mi-nas-storage"
        count: Número de SA a crear (1-100, default 100)
    """
```

### 11.2 Tool para health check

```python
@tool
def rclone_sa_pool_status() -> str:
    """Muestra el estado del pool de SA: total de keys en disco, cuántas están
    en cooldown, SA activa actual para cada módulo (media/upload), y resultado
    del último health check.
    
    No requiere argumentos — lee de /etc/rclone/sa-pool/ y /var/lib/rclone/sa-state.json.
    """
```

### 11.3 Tool para agregar SA al Shared Drive

```python
@tool
def rclone_sa_pool_add_to_drive(shared_drive_id: str, role: str = "writer") -> str:
    """Agrega todas las SA del pool como miembros del Shared Drive indicado.
    Usa la Google Drive API (requiere una SA con rol 'Manager' en el Drive).
    
    Args:
        shared_drive_id: ID del Shared Drive (obtener de la URL o con rclone lsd)
        role: Rol a asignar ('writer' = Content Manager, 'reader' = Viewer)
    """
```

---

## 12. Costos

| Recurso | Costo |
|---------|-------|
| Service Accounts | Gratis |
| Keys de SA | Gratis |
| Google Drive API calls | Gratis (dentro de cuota generosa) |
| Shared Drive storage | Depende del plan Workspace (o ilimitado con Enterprise) |
| Proyecto GCP (sin servicios pagos) | Gratis |

**Total para 100 SA**: $0/mes (asumiendo que ya tienes storage en Google Drive vía Workspace o similar).

**Nota sobre storage**: Para tener storage ilimitado en Shared Drives, necesitas al menos
Google Workspace Business Standard ($12/user/mes) con 5+ usuarios, o Enterprise.
Con cuentas personales (@gmail.com) los Shared Drives no están disponibles.

---

## 13. Checklist de implementación

- [ ] Instalar `gcloud` CLI en el NAS
- [ ] Crear proyecto GCP (o usar uno existente)
- [ ] Habilitar Drive API + IAM API
- [ ] Ejecutar `create-sa-pool.sh` (crear 100 SA + descargar keys)
- [ ] Crear Google Group y agregar las 100 SA
- [ ] Crear Shared Drive(s) para media + backups
- [ ] Agregar el Google Group al Shared Drive como Content Manager
- [ ] Configurar permisos de archivos en el NAS (`0640 root:rclone`)
- [ ] Verificar acceso con `sa-health-check.sh`
- [ ] Configurar partición: SA-001-050 para write, SA-051-100 para read
- [ ] Documentar el Shared Drive ID (necesario para rclone.conf)

---

## 14. Referencias

- [gcloud iam service-accounts create](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/create)
- [gcloud iam service-accounts keys create](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/keys/create)
- [Shared Drive limits](https://support.google.com/a/answer/7338880)
- [SA guide (88lex)](https://github.com/88lex/sa-guide) — guía comunitaria de referencia
- [Google Groups API](https://developers.google.com/admin-sdk/directory/reference/rest/v1/members)
- [Rclone Google Drive backend](https://rclone.org/drive/)
