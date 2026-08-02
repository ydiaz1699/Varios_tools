# Módulo 2: 9Drive + AutoRclone (Dashboard Web + SA Rotation)

> **Tipo**: Aplicación web Docker (autocontenida) + concepto AutoRclone integrado
> **Destino de implementación**: `docker/9drive/` en el NAS + ficha en catálogo del agente
> **Prioridad**: Media (requiere SA pool creado primero, ver `04-sa-pool-management.md`)

---

## 1. Propósito

Proveer un **dashboard web** para gestionar múltiples cuentas de Google Drive con:

- **Upload routing inteligente**: distribuir archivos automáticamente al Drive con más espacio libre.
- **Bypass de cuota de upload** (750 GB/día/cuenta): usando 100 Service Accounts rotando se alcanza un máximo teórico de **75 TB/día**.
- **API de uploads externa**: otros servicios del NAS pueden subir archivos sin tocar CLI.
- **Visualización de cuota**: saber en todo momento cuánto espacio queda en cada Drive.
- **Gestión centralizada**: un solo panel web para N cuentas de Google Drive.

---

## 2. Conceptos clave

### 2.1 ¿Qué es AutoRclone?

AutoRclone es una técnica (no un software específico) que:

1. Crea **múltiples Service Accounts** (SA) en un proyecto de Google Cloud Platform.
2. Cada SA tiene su propia cuota de 750 GB/día de upload a Google Drive.
3. Un orquestador rota entre SAs cuando una alcanza su límite (error 403 `userRateLimitExceeded`).
4. Resultado: la cuota efectiva se multiplica por el número de SAs.

```
Proyecto GCP
├── SA-001 → 750 GB/día ──┐
├── SA-002 → 750 GB/día   │
├── SA-003 → 750 GB/día   ├── Total: 750 GB × 100 = 75 TB/día
│   ...                    │
└── SA-100 → 750 GB/día ──┘
```

### 2.2 ¿Qué es 9Drive?

[9Drive](https://github.com/ripperdrive/9drive) es una aplicación web open-source que:

- Conecta **múltiples cuentas de Google Drive** en un dashboard virtual.
- Hace **streaming directo** de uploads (no almacena en el servidor).
- Soporta **S3-compatible storage** (MinIO, Cloudflare R2, Wasabi, B2, AWS S3).
- Tiene **políticas de routing**: most-available, round-robin, priority-order.
- Ofrece **API REST de uploads** con API keys.
- Stack: React (Vite) + Express (TypeScript) + MySQL/SQLite + Prisma.

### 2.3 Combinación: 9Drive como frontend de AutoRclone

La idea es usar 9Drive como **interfaz web de gestión** y las Service Accounts como **"cuentas conectadas"** en 9Drive, logrando:

```
Usuario (browser) ──► 9Drive (web UI)
                         │
                         ├── Cuenta Google A (OAuth personal) → uploads normales
                         ├── SA-001 (JSON key) → uploads cuando A está llena
                         ├── SA-002 (JSON key) → uploads cuando SA-001 está llena
                         │   ...
                         └── SA-100 (JSON key)
                              │
                              ▼
                         Shared Drive (Team Drive)
                         └── los 100 SA tienen acceso como Content Manager
```

---

## 3. Arquitectura de deployment

### 3.1 Stack Docker

```yaml
# docker/9drive/compose.yml
services:
  9drive-frontend:
    build: ./frontend
    ports:
      - "5173:80"  # Nginx serving built React app
    depends_on:
      - 9drive-backend
    environment:
      - VITE_API_URL=http://nas-ip:4000
    networks:
      - 9drive-net

  9drive-backend:
    build: ./backend
    ports:
      - "4000:4000"
    depends_on:
      - 9drive-db
    env_file:
      - .env
    volumes:
      - ./sa-keys:/app/sa-keys:ro  # Service Account JSONs (read-only)
    networks:
      - 9drive-net

  9drive-db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: 9drive
    volumes:
      - 9drive-mysql:/var/lib/mysql
    networks:
      - 9drive-net

volumes:
  9drive-mysql:

networks:
  9drive-net:
    driver: bridge
```

### 3.2 Estructura de archivos en el NAS

```
/docker/9drive/
├── compose.yml
├── .env                      ← credenciales (NO en git)
├── .env.example              ← template de ejemplo (SÍ en git)
├── sa-keys/                  ← 100 JSON keys de Service Accounts
│   ├── sa-001.json
│   ├── sa-002.json
│   │   ...
│   └── sa-100.json
├── frontend/
│   └── Dockerfile
├── backend/
│   └── Dockerfile
└── data/
    └── mysql/                ← volumen persistente de MySQL
```

### 3.3 Variables de entorno (`.env`)

```env
# Database
MYSQL_ROOT_PASSWORD=cambiar_esto_password_fuerte
DATABASE_URL="mysql://root:${MYSQL_ROOT_PASSWORD}@9drive-db:3306/9drive"

# Backend
APP_PORT=4000
FRONTEND_URL="http://nas-ip:5173"
JWT_ACCESS_SECRET="generar_con_openssl_rand_base64_32"
TOKEN_ENCRYPTION_KEY="exactamente_32_caracteres_aqui!"
ACCESS_TOKEN_TTL_SECONDS=900
REFRESH_TOKEN_TTL_DAYS=30
MAX_UPLOAD_BYTES=5368709120  # 5 GB por archivo

# Google OAuth (para login via Google y conexión de Drives)
GOOGLE_CLIENT_ID="tu-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="tu-client-secret"
GOOGLE_REDIRECT_URI="http://nas-ip:4000/connected-accounts/google/callback"

# Opcional: reCAPTCHA (dejar vacío para desactivar)
RECAPTCHA_SECRET_KEY=""
VITE_RECAPTCHA_SITE_KEY=""
```

---

## 4. Configuración de Google Cloud Platform

### 4.1 Prerrequisitos

1. **Proyecto GCP** con billing habilitado (plan gratuito es suficiente).
2. **Google Drive API** habilitada en el proyecto.
3. **OAuth consent screen** configurada (External, con scopes de Drive).
4. **OAuth 2.0 Client ID** (Web application) con:
   - Authorized JavaScript origin: `http://nas-ip:5173`
   - Authorized redirect URI: `http://nas-ip:4000/connected-accounts/google/callback`

### 4.2 Service Accounts para AutoRclone

Ver documento completo: [`04-sa-pool-management.md`](04-sa-pool-management.md)

Resumen rápido:
```bash
# Crear 100 SA en el proyecto
for i in $(seq -w 1 100); do
  gcloud iam service-accounts create sa-rclone-${i} \
    --display-name="Rclone SA ${i}" \
    --project=tu-proyecto-gcp
done

# Descargar las keys JSON
for i in $(seq -w 1 100); do
  gcloud iam service-accounts keys create sa-keys/sa-${i}.json \
    --iam-account=sa-rclone-${i}@tu-proyecto-gcp.iam.gserviceaccount.com
done
```

### 4.3 Agregar SAs al Shared Drive

Todas las SA deben tener acceso al Shared Drive como **Content Manager** (mínimo):

```
Google Drive → Shared Drive → Manage members → Add:
  sa-rclone-001@tu-proyecto.iam.gserviceaccount.com (Content Manager)
  sa-rclone-002@tu-proyecto.iam.gserviceaccount.com (Content Manager)
  ...
  sa-rclone-100@tu-proyecto.iam.gserviceaccount.com (Content Manager)
```

**Tip**: usar un **Google Group** para agregar todas las SA de una vez:
1. Crear grupo: `rclone-sas@tudominio.com`
2. Agregar las 100 SA como miembros del grupo.
3. Agregar el grupo al Shared Drive como Content Manager.
4. Resultado: 1 sola entrada en el Shared Drive en vez de 100.

---

## 5. Integración de AutoRclone con 9Drive

### 5.1 Opción A: SA como "cuentas conectadas" nativas

9Drive soporta conectar múltiples cuentas de Google Drive. Cada SA puede registrarse como una cuenta separada:

1. Modificar el backend de 9Drive para aceptar **JSON key authentication** además de OAuth.
2. Cada SA se registra como una "connected account" con su propia cuota (15 GB por SA en Drive personal, ilimitado en Shared Drives).
3. El routing de 9Drive (`most-available`) automáticamente usa la SA con más espacio.

### 5.2 Opción B: Wrapper de SA rotation externo

Si no quieres modificar 9Drive, puedes crear un **proxy/wrapper** que:

1. Recibe uploads del usuario (vía API de 9Drive o directamente).
2. Intenta subir con SA-001.
3. Si recibe `403 userRateLimitExceeded`, cambia a SA-002.
4. Repite hasta encontrar una SA con cuota disponible.

```python
# Pseudocódigo del rotador
class SARotator:
    def __init__(self, sa_keys_dir: str):
        self.keys = sorted(Path(sa_keys_dir).glob("sa-*.json"))
        self.current_index = 0
    
    def get_current_sa(self) -> Path:
        return self.keys[self.current_index]
    
    def rotate(self):
        self.current_index = (self.current_index + 1) % len(self.keys)
    
    def upload_with_rotation(self, file, destination):
        for attempt in range(len(self.keys)):
            try:
                return self._upload(file, destination, self.get_current_sa())
            except RateLimitError:
                self.rotate()
        raise AllSAsExhaustedError("Todas las SA han alcanzado su cuota diaria")
```

### 5.3 Opción C: gclone (fork de rclone con SA rotation nativa)

[gclone](https://github.com/l3v11/gclone) es un fork de rclone que tiene SA rotation integrada:

```ini
# rclone.conf con gclone
[gdrive]
type = drive
scope = drive
service_account_file = /path/to/sa-keys/sa-001.json
service_account_file_path = /path/to/sa-keys/  # ← gclone rota automáticamente entre todos los JSON de este directorio
team_drive = 0ABCxxxxxxxxxx
```

**Ventaja**: no necesitas código custom de rotación.
**Desventaja**: es un fork, puede quedarse atrás respecto a rclone oficial.

---

## 6. Políticas de routing (9Drive)

9Drive soporta 3 modos de distribución de uploads:

| Política | Comportamiento | Caso de uso |
|----------|---------------|-------------|
| **most-available** | Sube al Drive con más espacio libre | Default recomendado — maximiza la vida útil del storage |
| **round-robin** | Distribuye equitativamente entre todas las cuentas | Cuando quieres uso parejo |
| **priority-order** | Usa la primera cuenta disponible, pasa a la siguiente solo si está llena | Cuando una cuenta es preferida |

Para AutoRclone con SA rotation, `most-available` es el más lógico combinado con detección de `403`.

---

## 7. API de uploads (para integración con otros servicios del NAS)

9Drive expone un endpoint de upload que otros servicios pueden usar:

```bash
# Upload vía API key
curl -X POST http://nas-ip:4000/api/v1/uploads \
  -H "Authorization: Bearer TU_API_KEY" \
  -F "sizeBytes=1073741824" \
  -F "fileName=pelicula.mkv" \
  -F "mimeType=video/x-matroska" \
  -F "file=@/path/to/pelicula.mkv"
```

### 7.1 Casos de uso de la API

- **Scripts de descarga** (yt-dlp, aria2) que suben directamente al Drive.
- **Procesamiento de medios** (ffmpeg, HandBrake) que envían el resultado a la nube.
- **Sincronización selectiva**: solo archivos nuevos/modificados se suben.
- **Integración con el agente NAS**: una tool que sube archivos vía la API de 9Drive.

### 7.2 Tool del agente para 9Drive

```python
# agent/tools/9drive_tools.py (futuro)
@tool
def upload_to_9drive(file_path: str, folder_id: str = "") -> str:
    """Sube un archivo al cloud vía 9Drive (routing automático al Drive con más espacio)."""
    ...
```

---

## 8. Seguridad de la instalación Docker

### 8.1 Hardening del compose

```yaml
services:
  9drive-backend:
    # ...
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '2.0'
```

### 8.2 Protección de SA keys

```bash
# Los JSON keys deben ser read-only desde el contenedor
chmod 0600 /docker/9drive/sa-keys/*.json
chown root:root /docker/9drive/sa-keys/*.json
# En compose: montado como :ro (read-only)
```

### 8.3 Red interna

- MySQL **NO** expone puertos al host (solo red interna Docker).
- Backend expone `4000` solo en interfaz local si hay reverse proxy.
- Frontend detrás de reverse proxy (Nginx/Caddy) con HTTPS en producción.

### 8.4 Secretos

- `JWT_ACCESS_SECRET`: generar con `openssl rand -base64 32`
- `TOKEN_ENCRYPTION_KEY`: exactamente 32 caracteres alfanuméricos
- `MYSQL_ROOT_PASSWORD`: generar con `openssl rand -base64 24`
- Nunca commitear `.env` al repositorio

---

## 9. Integración con el catálogo del agente NAS

### 9.1 Ficha del servicio

```yaml
# agent/catalog/services/9drive/ficha.md (frontmatter)
---
id: 9drive
name: 9Drive
category: storage
image: custom-build  # se buildea localmente
ports:
  - "5173:80"    # frontend
  - "4000:4000"  # backend API
volumes:
  - 9drive-mysql:/var/lib/mysql
  - ./sa-keys:/app/sa-keys:ro
env_required:
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - JWT_ACCESS_SECRET
  - TOKEN_ENCRYPTION_KEY
  - MYSQL_ROOT_PASSWORD
healthcheck:
  test: "curl -f http://localhost:4000/health || exit 1"
  interval: 30s
  timeout: 10s
  retries: 3
backup_critical: true
networks:
  - 9drive-net
resources:
  memory: 1G
  cpus: 2.0
---
```

### 9.2 Gestión vía agente

```python
# El agente puede gestionar 9Drive como cualquier otro servicio Docker:
service_start("9drive")
service_stop("9drive")
service_status("9drive")
backup_service("9drive")  # backup del volumen MySQL
```

---

## 10. Consideraciones de TOS y riesgos

### 10.1 Google Terms of Service

| Acción | Riesgo |
|--------|--------|
| Múltiples SA accediendo al mismo Shared Drive | ⚠️ Bajo — técnicamente legítimo si las SA tienen acceso real |
| Rotar SA para bypass de cuota | ⚠️ Medio — Google puede detectar el patrón |
| 100 SA en un proyecto GCP | ✅ Permitido (límite por proyecto es 100) |
| Shared Drive con > 400k archivos | ⚠️ Google puede limitar operaciones |
| Upload > 750 GB/día por SA | ❌ Google aplica el límite automáticamente (error 403) |

### 10.2 Mitigaciones

1. **No abusar**: no intentar 75 TB/día todos los días. Usar rotation solo cuando se necesita (ej: upload masivo inicial de biblioteca).
2. **Shared Drives legítimos**: que las SA realmente tengan acceso otorgado (no forzado).
3. **Monitorear errores 403**: si Google empieza a bloquear más agresivamente, reducir concurrencia.
4. **Plan B**: tener backup en otro proveedor (B2, Wasabi) por si Google revoca acceso.
5. **No mezclar con cuentas personales importantes**: usar un proyecto GCP separado.

### 10.3 Alternativas legítimas

Si la cuota de 750 GB/día es insuficiente a largo plazo:

| Alternativa | Cuota | Costo |
|-------------|-------|-------|
| Google Workspace Enterprise | 5 TB/usuario (pooled) | ~$20/user/mes |
| Backblaze B2 | Ilimitada | $6/TB/mes storage + $10/TB egress |
| Wasabi | Ilimitada | $7/TB/mes (sin egress fees) |
| Hetzner Storage Box | 1-20 TB | €3.50-€39/mes |

---

## 11. Flujo de deployment completo

```bash
# 1. Clonar 9Drive
git clone https://github.com/ripperdrive/9drive.git /docker/9drive/app

# 2. Copiar SA keys al directorio
cp /etc/rclone/sa-pool/*.json /docker/9drive/sa-keys/

# 3. Crear .env desde template
cp /docker/9drive/.env.example /docker/9drive/.env
nano /docker/9drive/.env  # editar con tus credenciales

# 4. Configurar Google Cloud (OAuth client)
# → console.cloud.google.com → APIs & Services → Credentials
# → Authorized origins: http://nas-ip:5173
# → Authorized redirect: http://nas-ip:4000/connected-accounts/google/callback

# 5. Deploy
cd /docker/9drive
docker compose up -d --build

# 6. Seed config de Google OAuth
docker compose exec 9drive-backend npm run seed:google-config

# 7. Verificar
curl http://nas-ip:4000/health
# Abrir http://nas-ip:5173 en browser
```

---

## 12. Diagrama de flujo

```
┌──────────────────────────────────────────────────────────────┐
│                     Usuario (Browser)                          │
│                     http://nas-ip:5173                         │
└──────────────────────────┬───────────────────────────────────┘
                           │ upload / gestión
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  9Drive Frontend (React/Vite)                  │
│                  Nginx serving static build                    │
└──────────────────────────┬───────────────────────────────────┘
                           │ API calls
                           ▼
┌──────────────────────────────────────────────────────────────┐
│               9Drive Backend (Express/TypeScript)              │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ Upload      │  │ SA Rotation  │  │ Quota Tracker       │ │
│  │ Streaming   │  │ (on 403)     │  │ (per account)       │ │
│  └──────┬──────┘  └──────┬───────┘  └─────────────────────┘ │
│         │                 │                                    │
│         ▼                 ▼                                    │
│  ┌─────────────────────────────────┐                          │
│  │ Routing Policy Engine           │                          │
│  │ • most-available                │                          │
│  │ • round-robin                   │                          │
│  │ • priority-order                │                          │
│  └──────────────┬──────────────────┘                          │
└─────────────────┼────────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ SA-001   │ │ SA-002   │ │ SA-100   │
│ 750GB/d  │ │ 750GB/d  │ │ 750GB/d  │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│              Google Shared Drive (Team Drive)                  │
│                                                               │
│  uploads/                                                     │
│  ├── peliculas/                                               │
│  ├── series/                                                  │
│  └── musica/                                                  │
│                                                               │
│  Capacidad efectiva: 75 TB/día upload                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 13. Relación con los otros módulos

| Interacción | Detalle |
|-------------|---------|
| **Con Módulo 1** (backup) | 9Drive NO reemplaza el backup seguro. El backup usa 1 SA con cifrado fuerte. 9Drive es para uploads masivos sin cifrado obligatorio. |
| **Con Módulo 3** (media) | El contenido que sube 9Drive puede ser leído por rclone-media (mount FUSE). Flujo: subir vía 9Drive → leer vía rclone mount → Jellyfin reproduce. |
| **SA Pool compartido** | Las 100 SA pueden ser compartidas entre 9Drive y rclone-media, pero NO simultáneamente en la misma SA (conflicto de cuota). Recomendación: particionar — 50 SA para upload (9Drive), 50 SA para read (rclone-media). |

---

## 14. Decisiones pendientes

- [ ] ¿Usar 9Drive vanilla o forkear para integrar SA rotation nativa?
- [ ] ¿Particionar el pool de SA (upload vs read) o compartirlo con coordinación?
- [ ] ¿Reverse proxy (Caddy/Nginx) delante de 9Drive para HTTPS?
- [ ] ¿Integrar la API de 9Drive como tool del agente NAS?
- [ ] ¿SQLite o MySQL? (SQLite es zero-config pero menos resiliente a crashes)
