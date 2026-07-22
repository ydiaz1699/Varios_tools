# ADB Controller - DNS Privado

Herramientas para controlar la configuracion de DNS Privado en dispositivos Android mediante ADB.

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `dns_privado_adb.py` | Script Python con menu interactivo y CLI para controlar DNS Privado |
| `DNS_PRIVADO_ADB_DOCUMENTACION.md` | Documentacion completa para uso con LLMs (teoria, comandos, troubleshooting) |

## Uso Rapido

```bash
# Menu interactivo
python dns_privado_adb.py

# Comandos directos
python dns_privado_adb.py status          # Ver estado actual
python dns_privado_adb.py on dnsforge     # Activar con dnsforge.de
python dns_privado_adb.py on adguard      # Activar con AdGuard
python dns_privado_adb.py off             # Desactivar
python dns_privado_adb.py auto            # Modo automatico
python dns_privado_adb.py servers         # Ver servidores disponibles
python dns_privado_adb.py test            # Probar conectividad
python dns_privado_adb.py connect 192.168.0.8  # Conectar WiFi ADB
```

## Requisitos

- Python 3.6+
- ADB instalado (Android Platform Tools)
- Dispositivo con depuracion USB activada
- Conexion USB o WiFi (misma red)

## Compatibilidad

- Samsung (One UI) - escribe en `global` y `secure`
- Google Pixel / Android Stock
- Xiaomi (MIUI/HyperOS)
- Cualquier Android 9+
