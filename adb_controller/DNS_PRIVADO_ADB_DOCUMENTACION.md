# DNS Privado en Android - Control Completo por ADB

## Documento de Referencia para LLM

> **Proposito:** Este documento contiene TODA la informacion necesaria para que un LLM
> pueda ayudar a controlar el DNS Privado de un dispositivo Android por ADB sin
> necesidad de consultar repositorios externos.

---

## 1. Que es DNS Privado en Android

DNS Privado es la implementacion nativa de Android (desde version 9.0+) del protocolo
**DNS-over-TLS (DoT)**. Cifra las consultas DNS del dispositivo para evitar que el ISP,
administradores de red o atacantes en redes publicas puedan ver que sitios visitas.

### Para que sirve:
- Bloquear anuncios y trackers (con DNS como AdGuard, NextDNS)
- Proteger la privacidad (cifrado de consultas DNS)
- Filtro familiar/parental (con DNS como CleanBrowsing Family)
- Bloquear malware (con DNS como Quad9, Cloudflare Security)

---

## 2. Conceptos Clave

### Settings de Android para DNS Privado

Android almacena la configuracion de DNS Privado en dos "namespaces" de settings:

| Namespace | Descripcion |
|-----------|-------------|
| `global`  | Setting principal en la mayoria de dispositivos Android |
| `secure`  | Setting adicional que Samsung (One UI) y algunos fabricantes leen para la UI |

### Valores de `private_dns_mode`

| Valor | Significado | Equivalente en UI |
|-------|-------------|-------------------|
| `off` | DNS Privado desactivado | "Desactivado" |
| `opportunistic` | Modo automatico, usa DNS privado si esta disponible | "Automatico" |
| `hostname_mode` | Activado con servidor especifico (Android 10+) | "Nombre de host del proveedor de DNS privado" |
| `hostname` | Activado con servidor especifico (Android 9) | Igual que arriba |

### Variables involucradas

| Variable | Funcion |
|----------|---------|
| `private_dns_mode` | Interruptor: activa/desactiva/auto el DNS privado |
| `private_dns_specifier` | Hostname del servidor DNS a utilizar |

---

## 3. Todos los Comandos ADB Disponibles

### 3.1. Consultar estado actual

```bash
# Ver el modo actual (global)
adb shell settings get global private_dns_mode

# Ver el servidor configurado (global)
adb shell settings get global private_dns_specifier

# Ver modo en secure (Samsung)
adb shell settings get secure private_dns_mode

# Ver servidor en secure (Samsung)
adb shell settings get secure private_dns_specifier
```

### 3.2. Activar DNS Privado con servidor especifico

```bash
# En global (funciona en la mayoria de dispositivos)
adb shell settings put global private_dns_mode hostname_mode
adb shell settings put global private_dns_specifier <SERVIDOR>

# En secure (NECESARIO para Samsung One UI)
adb shell settings put secure private_dns_mode hostname_mode
adb shell settings put secure private_dns_specifier <SERVIDOR>
```

**Ejemplo con dnsforge.de:**
```bash
adb shell settings put global private_dns_mode hostname_mode
adb shell settings put global private_dns_specifier dnsforge.de
adb shell settings put secure private_dns_mode hostname_mode
adb shell settings put secure private_dns_specifier dnsforge.de
```

### 3.3. Desactivar DNS Privado

```bash
adb shell settings put global private_dns_mode off
adb shell settings put secure private_dns_mode off
```

### 3.4. Modo automatico (oportunista)

```bash
adb shell settings put global private_dns_mode opportunistic
adb shell settings put secure private_dns_mode opportunistic
```

### 3.5. Verificar conectividad con servidor DNS

```bash
adb shell ping -c 2 dnsforge.de
```

### 3.6. Ver informacion del dispositivo

```bash
adb shell getprop ro.product.brand
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
```

---

## 4. Conexion ADB

### 4.1. Por USB
```bash
# Listar dispositivos
adb devices

# Si no aparece, reiniciar servidor ADB
adb kill-server
adb start-server
adb devices
```

### 4.2. Por WiFi (misma red local)

```bash
# Primero conectar por USB y habilitar TCP
adb tcpip 5555

# Desconectar USB y conectar por IP
adb connect <IP_DEL_DISPOSITIVO>:5555

# Verificar conexion
adb devices

# Desconectar
adb disconnect <IP_DEL_DISPOSITIVO>:5555
```

### 4.3. ADB WiFi sin cable previo (Android 11+)
En Android 11+ con "Depuracion inalambrica" activada:
```bash
# Usar el puerto y codigo de emparejamiento que muestra el dispositivo
adb pair <IP>:<PUERTO_EMPAREJAMIENTO>
# Luego conectar
adb connect <IP>:<PUERTO>
```

---

## 5. Permisos para Apps de DNS

Algunas apps (como Private DNS Quick Settings) necesitan el permiso
`WRITE_SECURE_SETTINGS` para cambiar el DNS desde un tile rapido.

### Otorgar permiso por ADB:

```bash
# Version Play Store
adb shell pm grant com.flashsphere.privatednsqs android.permission.WRITE_SECURE_SETTINGS

# Version sin launcher
adb shell pm grant com.flashsphere.privatednsqs.nolauncher android.permission.WRITE_SECURE_SETTINGS
```

### Si da error SecurityException:
1. Buscar en Opciones de desarrollador: "Depuracion USB (configuracion de seguridad)" y activarlo
2. O buscar "Deshabilitar supervision de permisos" y activarlo
3. Reiniciar el dispositivo
4. Intentar el comando de nuevo

### Alternativa: Shizuku
La app Shizuku puede otorgar el permiso sin necesidad de PC/ADB.
- Instalar Shizuku desde Play Store
- Iniciar Shizuku (requiere ADB la primera vez o root)
- Las apps compatibles pueden solicitar el permiso directamente

---

## 6. Diferencias por Fabricante

### Samsung (One UI)
- **REQUIERE escribir en AMBOS**: `global` Y `secure`
- La interfaz de Ajustes lee de `secure`, no solo de `global`
- Si solo escribes en `global`, funciona pero la UI muestra "desactivado"
- Modelos probados: SM-J610G (Android 10)

### Google Pixel / Android Stock
- Solo necesita `global`
- El namespace `secure` normalmente devuelve `null`

### Xiaomi (MIUI/HyperOS)
- Generalmente funciona con `global`
- Algunos modelos tienen bug visual similar a Samsung
- Verificar con: `adb shell settings get global private_dns_default_mode`

### Huawei (EMUI/HarmonyOS)
- Similar a Android stock, usa `global`
- Versiones antiguas pueden no soportar `hostname_mode`

### Fire TV / Fire Stick (Amazon)
- **PRECAUCION**: Cambiar DNS puede bloquear completamente internet en algunos modelos
- Usar con cuidado en Fire TV Stick 2da generacion y Fire TV 4K MAX
- Probar primero con `opportunistic` antes de `hostname_mode`

### Android 9 vs Android 10+
- Android 9: usar `hostname` como valor del modo
- Android 10+: usar `hostname_mode` como valor del modo
- Si un valor no funciona, probar el otro

---

## 7. Servidores DNS Populares

| Nombre | Hostname | Funcion |
|--------|----------|---------|
| AdGuard | `dns.adguard.com` | Bloqueo de anuncios y trackers |
| AdGuard Family | `family.adguard-dns.com` | Bloqueo + filtro parental |
| Cloudflare | `one.one.one.one` | Rapido, privacidad |
| Cloudflare Family | `family.cloudflare-dns.com` | Rapido + filtro parental |
| Cloudflare Security | `security.cloudflare-dns.com` | Rapido + bloqueo malware |
| Google | `dns.google` | Rapido, confiable |
| Quad9 | `dns.quad9.net` | Bloqueo malware, privacidad |
| NextDNS | `dns.nextdns.io` | Configurable, dashboard |
| Mullvad | `dns.mullvad.net` | Privacidad extrema |
| Mullvad AdBlock | `adblock.dns.mullvad.net` | Privacidad + bloqueo ads |
| DNSForge | `dnsforge.de` | Bloqueo ads, europeo |
| CleanBrowsing Security | `security-filter-dns.cleanbrowsing.org` | Anti-malware |
| CleanBrowsing Family | `family-filter-dns.cleanbrowsing.org` | Filtro parental estricto |
| Control D | `freedns.controld.com` | Configurable |
| LibreDNS | `dot.libredns.gr` | Open source, privacidad |

### NextDNS con ID personalizado:
Si tienes cuenta NextDNS, tu hostname seria: `<TU-ID>.dns.nextdns.io`

---

## 8. Verificar que el DNS Funciona

### Desde el dispositivo (navegador):
- https://dnsleaktest.com (Standard test)
- https://adguard.com/test.html (si usas AdGuard)
- https://test.nextdns.io (si usas NextDNS)

### Desde ADB:
```bash
# Ping al servidor DNS
adb shell ping -c 2 dnsforge.de

# Resolver un dominio (si nslookup esta disponible)
adb shell nslookup google.com

# Alternativa si nslookup no existe:
adb shell ping -c 1 google.com
# Si resuelve la IP, el DNS esta funcionando
```

---

## 9. Troubleshooting (Solucion de Problemas)

### La UI dice "desactivado" pero ADB dice hostname_mode
- **Causa**: Samsung lee de `secure`, no de `global`
- **Solucion**: Escribir tambien en `secure` (ver seccion 3.2)

### Error "Argument expected to be 'default'"
- **Causa**: Se concatenaron comandos incorrectamente en una linea
- **Solucion**: Ejecutar cada comando ADB por separado, o usar `&&` para separar

### DNS activado pero internet no funciona
- **Causa**: El servidor DNS no es alcanzable o esta caido
- **Solucion**: Probar conectividad con `ping`, cambiar a otro servidor, o desactivar con `off`

### "unauthorized" en adb devices
- **Causa**: No se acepto el dialogo de depuracion USB en el dispositivo
- **Solucion**: Desbloquear el telefono, aceptar el dialogo de autorizacion

### No se puede otorgar permiso (SecurityException)
- **Causa**: Xiaomi/Samsung bloquean permisos de seguridad por defecto
- **Solucion**: 
  1. Activar "Depuracion USB (config. seguridad)" en Opciones de desarrollador
  2. O activar "Deshabilitar supervision de permisos"
  3. Reiniciar y volver a intentar

### El DNS se desactiva solo al reiniciar
- **Causa**: Alguna app de optimizacion o el sistema reinicia la configuracion
- **Solucion**: Usar una app como Private DNS Quick Settings que mantiene la config activa

---

## 10. Automatizacion

### Script rapido para Windows (.bat) - Toggle DNS:
```batch
@echo off
for /F %%i in ('adb shell settings get global private_dns_mode') do set dnsmode=%%i
echo Estado actual: %dnsmode%
if "%dnsmode%"=="hostname_mode" (
    echo Desactivando DNS Privado...
    adb shell settings put global private_dns_mode off
    adb shell settings put secure private_dns_mode off
) else (
    echo Activando DNS Privado con dnsforge.de...
    adb shell settings put global private_dns_mode hostname_mode
    adb shell settings put global private_dns_specifier dnsforge.de
    adb shell settings put secure private_dns_mode hostname_mode
    adb shell settings put secure private_dns_specifier dnsforge.de
)
```

### Comando rapido Linux/Mac:
```bash
# Activar
adb shell "settings put global private_dns_specifier dnsforge.de && settings put global private_dns_mode hostname_mode && settings put secure private_dns_specifier dnsforge.de && settings put secure private_dns_mode hostname_mode"

# Desactivar
adb shell "settings put global private_dns_mode off && settings put secure private_dns_mode off"
```

---

## 11. Limitaciones del Control por ADB

### Lo que SI se puede hacer:
- Activar/desactivar DNS Privado
- Cambiar servidor DNS
- Ver estado actual
- Otorgar permisos a apps
- Conectar por WiFi (misma red)
- Todo lo anterior de forma remota (ADB WiFi)

### Lo que NO se puede hacer:
- Controlar desde internet (fuera de la red local) sin VPN/tuneles
- Cambiar DNS si ADB esta deshabilitado en el dispositivo
- Sobrescribir politicas MDM/empresariales
- Garantizar que la UI de Samsung refleje el cambio (bug visual)

### Requisitos:
- Depuracion USB activada en el dispositivo
- ADB instalado en la PC (Android Platform Tools)
- Conexion USB o WiFi en la misma red
- Para apps: permiso WRITE_SECURE_SETTINGS otorgado

---

## 12. Referencia Rapida de Comandos

```
CONSULTAR:
  adb shell settings get global private_dns_mode
  adb shell settings get global private_dns_specifier
  adb shell settings get secure private_dns_mode
  adb shell settings get secure private_dns_specifier

ACTIVAR (con servidor):
  adb shell settings put global private_dns_mode hostname_mode
  adb shell settings put global private_dns_specifier <SERVIDOR>
  adb shell settings put secure private_dns_mode hostname_mode
  adb shell settings put secure private_dns_specifier <SERVIDOR>

DESACTIVAR:
  adb shell settings put global private_dns_mode off
  adb shell settings put secure private_dns_mode off

AUTOMATICO:
  adb shell settings put global private_dns_mode opportunistic
  adb shell settings put secure private_dns_mode opportunistic

CONECTAR WIFI:
  adb tcpip 5555
  adb connect <IP>:5555

PERMISOS APP:
  adb shell pm grant <PAQUETE> android.permission.WRITE_SECURE_SETTINGS

INFO DISPOSITIVO:
  adb shell getprop ro.product.brand
  adb shell getprop ro.product.model
  adb shell getprop ro.build.version.release

TEST:
  adb shell ping -c 2 <SERVIDOR_DNS>
  adb devices
```

---

## 13. Sobre el Repositorio Original

**Repositorio**: https://github.com/flashsphere/private-dns-qs

Es una app Android de codigo abierto que:
- Agrega un tile (boton) en los ajustes rapidos para alternar DNS Privado
- Soporta multiples servidores DNS configurados
- Permite iconos personalizados por servidor
- Tiene opcion de requerir desbloqueo para cambiar
- Soporta Shizuku para otorgar permisos sin PC
- Tiene backup/restauracion de configuracion

La app necesita `WRITE_SECURE_SETTINGS` que se otorga por ADB o Shizuku.

---

## 14. Contexto del Usuario

- **Dispositivo**: Samsung SM-J610G (Galaxy J6+)
- **Android**: 10 (One UI)
- **Conexion ADB**: WiFi (192.168.0.8:5555)
- **DNS actual**: dnsforge.de
- **Nota importante**: Samsung requiere escribir en `global` Y `secure` para que la UI refleje el cambio
- **Carpeta de trabajo**: `C:\Users\Alex\Desktop\tvbox-controller`
- **Entorno**: Python venv activo en Windows

---

*Documento generado como referencia completa para uso con LLMs.*
*No requiere acceso a repositorios externos para funcionar.*
