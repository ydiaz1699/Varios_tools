---
description: "Conocimiento sobre control de DNS Privado en Android por ADB. Se activa cuando el usuario trabaja con ADB, DNS, o dispositivos Android."
inclusion: auto
globs:
  - "**/adb*"
  - "**/dns*"
---

# DNS Privado Android - Referencia Rapida

## Contexto del usuario
- Dispositivo: Samsung SM-J610G (Galaxy J6+), Android 10
- Conexion: ADB WiFi (192.168.0.8:5555)
- DNS actual: dnsforge.de
- PC: Windows, Python venv en tvbox-controller

## Regla critica: Samsung
Samsung One UI requiere escribir en `global` Y `secure`. Si solo se escribe en `global`, la UI muestra "desactivado" aunque funcione.

## Comandos esenciales

```bash
# Estado
adb shell settings get global private_dns_mode
adb shell settings get global private_dns_specifier
adb shell settings get secure private_dns_mode
adb shell settings get secure private_dns_specifier

# Activar (Samsung = global + secure)
adb shell settings put global private_dns_mode hostname_mode
adb shell settings put global private_dns_specifier <SERVIDOR>
adb shell settings put secure private_dns_mode hostname_mode
adb shell settings put secure private_dns_specifier <SERVIDOR>

# Desactivar
adb shell settings put global private_dns_mode off
adb shell settings put secure private_dns_mode off

# Automatico
adb shell settings put global private_dns_mode opportunistic
adb shell settings put secure private_dns_mode opportunistic

# Conectar WiFi
adb connect <IP>:5555

# Permisos app
adb shell pm grant com.flashsphere.privatednsqs android.permission.WRITE_SECURE_SETTINGS
```

## Servidores DNS
- adguard: dns.adguard.com
- cloudflare: one.one.one.one
- google: dns.google
- quad9: dns.quad9.net
- dnsforge: dnsforge.de
- mullvad_adblock: adblock.dns.mullvad.net
- nextdns: dns.nextdns.io

## Modos
- off = desactivado
- opportunistic = automatico
- hostname_mode = servidor especifico (Android 10+)
- hostname = servidor especifico (Android 9)

## Script local
El usuario tiene `adb_controller/dns_privado_adb.py` con CLI:
```
python dns_privado_adb.py status|on|off|auto|test|info|servers|connect|menu
```
