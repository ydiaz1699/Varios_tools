#!/usr/bin/env python3
"""
============================================================
DNS PRIVADO - Chatbot Local (Agente Autonomo)
============================================================
Un mini chatbot de terminal que entiende lenguaje natural
y ejecuta comandos ADB para controlar el DNS Privado.

Uso: python dns_chatbot.py
Luego escribe comandos en lenguaje natural como:
  - "activa adguard"
  - "desactiva el dns"
  - "que estado tiene"
  - "conecta al telefono"
  - "prueba si funciona"
  - "ponlo en automatico"
  - "cambia a cloudflare"
  - "info del dispositivo"

Compatible con: Samsung, Xiaomi, Pixel, etc.
Requiere: ADB instalado y dispositivo conectado
============================================================
"""

import subprocess
import sys
import re

# ============================================================
# SERVIDORES DNS
# ============================================================
DNS_SERVERS = {
    "adguard": "dns.adguard.com",
    "adguard_family": "family.adguard-dns.com",
    "family": "family.adguard-dns.com",
    "cloudflare": "one.one.one.one",
    "cloudflare_family": "family.cloudflare-dns.com",
    "cloudflare_security": "security.cloudflare-dns.com",
    "google": "dns.google",
    "quad9": "dns.quad9.net",
    "nextdns": "dns.nextdns.io",
    "mullvad": "dns.mullvad.net",
    "mullvad_adblock": "adblock.dns.mullvad.net",
    "dnsforge": "dnsforge.de",
    "cleanbrowsing": "security-filter-dns.cleanbrowsing.org",
    "cleanbrowsing_family": "family-filter-dns.cleanbrowsing.org",
    "controld": "freedns.controld.com",
    "libredns": "dot.libredns.gr",
}

# Aliases en español
ALIASES = {
    "adguard": "adguard",
    "ad guard": "adguard",
    "cloudflare": "cloudflare",
    "cloud flare": "cloudflare",
    "google": "google",
    "quad9": "quad9",
    "quad 9": "quad9",
    "nextdns": "nextdns",
    "next dns": "nextdns",
    "mullvad": "mullvad",
    "dnsforge": "dnsforge",
    "dns forge": "dnsforge",
    "forge": "dnsforge",
    "libredns": "libredns",
    "controld": "controld",
    "control d": "controld",
    "familia": "adguard_family",
    "parental": "cleanbrowsing_family",
    "seguridad": "cloudflare_security",
    "malware": "quad9",
}


def adb(command: str) -> str:
    """Ejecuta un comando ADB."""
    try:
        result = subprocess.run(
            f"adb {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            return f"ERROR: {result.stderr.strip()}"
        return output
    except subprocess.TimeoutExpired:
        return "ERROR: Timeout - el dispositivo no responde"
    except Exception as e:
        return f"ERROR: {str(e)}"


def hay_dispositivo() -> bool:
    """Verifica si hay dispositivo conectado."""
    output = adb("devices")
    lines = output.strip().split("\n")
    devices = [l for l in lines[1:] if "device" in l and "unauthorized" not in l]
    return len(devices) > 0


def estado():
    """Muestra el estado actual del DNS."""
    mode_g = adb("shell settings get global private_dns_mode")
    spec_g = adb("shell settings get global private_dns_specifier")
    mode_s = adb("shell settings get secure private_dns_mode")
    spec_s = adb("shell settings get secure private_dns_specifier")

    print(f"\n  Estado DNS Privado:")
    print(f"  -------------------")

    if mode_g in ("hostname_mode", "hostname"):
        print(f"  ACTIVADO con: {spec_g}")
    elif mode_g == "opportunistic":
        print(f"  AUTOMATICO (oportunista)")
    elif mode_g == "off":
        print(f"  DESACTIVADO")
    else:
        print(f"  Modo: {mode_g}")

    # Verificar coherencia Samsung
    if mode_g != mode_s and mode_s != "null":
        print(f"  [!] Nota: global={mode_g}, secure={mode_s} (desincronizados)")

    print()


def activar(servidor: str):
    """Activa DNS con un servidor."""
    print(f"\n  Activando DNS: {servidor}...")
    adb(f"shell settings put global private_dns_specifier {servidor}")
    adb("shell settings put global private_dns_mode hostname_mode")
    adb(f"shell settings put secure private_dns_specifier {servidor}")
    adb("shell settings put secure private_dns_mode hostname_mode")
    print(f"  DNS activado: {servidor}")
    # Verificar
    test = adb(f"shell ping -c 1 {servidor}")
    if "1 received" in test:
        print(f"  Conectividad OK")
    else:
        print(f"  [!] No se pudo verificar conectividad")
    print()


def desactivar():
    """Desactiva DNS Privado."""
    print(f"\n  Desactivando DNS Privado...")
    adb("shell settings put global private_dns_mode off")
    adb("shell settings put secure private_dns_mode off")
    print(f"  DNS DESACTIVADO")
    print()


def automatico():
    """Modo automatico."""
    print(f"\n  Configurando modo automatico...")
    adb("shell settings put global private_dns_mode opportunistic")
    adb("shell settings put secure private_dns_mode opportunistic")
    print(f"  DNS en modo AUTOMATICO")
    print()


def conectar(ip: str):
    """Conecta por WiFi."""
    print(f"\n  Conectando a {ip}:5555...")
    output = adb(f"connect {ip}:5555")
    print(f"  {output}")
    print()


def info():
    """Info del dispositivo."""
    brand = adb("shell getprop ro.product.brand")
    model = adb("shell getprop ro.product.model")
    android = adb("shell getprop ro.build.version.release")
    print(f"\n  Dispositivo: {brand} {model}")
    print(f"  Android: {android}")
    print()


def test_dns():
    """Prueba conectividad DNS."""
    spec = adb("shell settings get global private_dns_specifier")
    if spec and spec != "null":
        print(f"\n  Probando conectividad con {spec}...")
        output = adb(f"shell ping -c 2 {spec}")
        if "2 received" in output:
            print(f"  FUNCIONA - conectividad OK")
        elif "1 received" in output:
            print(f"  PARCIAL - hay algo de perdida de paquetes")
        else:
            print(f"  FALLA - no hay conectividad con {spec}")
    else:
        print(f"\n  No hay servidor DNS configurado")
    print()


def listar_servidores():
    """Lista servidores disponibles."""
    print(f"\n  Servidores disponibles:")
    print(f"  -----------------------")
    for key, server in DNS_SERVERS.items():
        print(f"  {key:20s} -> {server}")
    print()


def resolver_servidor(texto: str) -> str:
    """Intenta encontrar un servidor DNS en el texto del usuario."""
    texto_lower = texto.lower()

    # Primero buscar aliases en español
    for alias, key in ALIASES.items():
        if alias in texto_lower:
            return DNS_SERVERS[key]

    # Buscar nombre directo en DNS_SERVERS
    for key, server in DNS_SERVERS.items():
        if key in texto_lower:
            return server

    # Buscar si parece un hostname (tiene punto)
    match = re.search(r'[\w.-]+\.\w{2,}', texto)
    if match:
        return match.group()

    return None


def procesar_input(texto: str):
    """Procesa el input del usuario en lenguaje natural."""
    texto_lower = texto.lower().strip()

    # Salir
    if texto_lower in ("salir", "exit", "quit", "q", "chao", "adios"):
        print("\n  Adios!")
        sys.exit(0)

    # Estado
    if any(p in texto_lower for p in ["estado", "status", "como esta", "que tiene", "ver", "mostrar", "consultar"]):
        estado()
        return

    # Desactivar
    if any(p in texto_lower for p in ["desactiva", "apaga", "quita", "off", "desactivar", "apagar"]):
        desactivar()
        return

    # Automatico
    if any(p in texto_lower for p in ["automatico", "auto", "oportunista", "opportunistic"]):
        automatico()
        return

    # Activar/Cambiar DNS
    if any(p in texto_lower for p in ["activa", "pon", "cambia", "usa", "on", "activar", "cambiar", "poner", "switch"]):
        servidor = resolver_servidor(texto)
        if servidor:
            activar(servidor)
        else:
            print("\n  No entendi que servidor quieres. Opciones:")
            listar_servidores()
        return

    # Conectar
    if any(p in texto_lower for p in ["conecta", "connect", "enlaza"]):
        match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', texto)
        if match:
            conectar(match.group(1))
        else:
            ip = input("  IP del dispositivo: ").strip()
            conectar(ip)
        return

    # Info
    if any(p in texto_lower for p in ["info", "informacion", "dispositivo", "modelo", "marca"]):
        info()
        return

    # Test/Probar
    if any(p in texto_lower for p in ["test", "prueba", "probar", "funciona", "ping"]):
        test_dns()
        return

    # Listar servidores
    if any(p in texto_lower for p in ["servidor", "lista", "disponible", "opciones", "cual", "cuales"]):
        listar_servidores()
        return

    # Ayuda
    if any(p in texto_lower for p in ["ayuda", "help", "comando", "que puedo"]):
        print("""
  Puedes decirme cosas como:
  ---------------------------
  "ver estado"           - Ver configuracion actual
  "activa adguard"       - Activar DNS con AdGuard
  "cambia a cloudflare"  - Cambiar a Cloudflare
  "desactiva"            - Desactivar DNS Privado
  "automatico"           - Modo automatico
  "prueba"               - Probar si el DNS funciona
  "info"                 - Info del dispositivo
  "conecta 192.168.0.8"  - Conectar por WiFi
  "servidores"           - Ver servidores disponibles
  "salir"                - Salir
""")
        return

    # No entendio
    print(f"\n  No entendi '{texto}'. Escribe 'ayuda' para ver opciones.")
    print()


def main():
    """Bucle principal del chatbot."""
    print("""
  ╔══════════════════════════════════════════════╗
  ║   DNS PRIVADO - Chatbot ADB Controller      ║
  ║   Escribe en español lo que necesites        ║
  ║   Escribe 'ayuda' para ver comandos          ║
  ╚══════════════════════════════════════════════╝
    """)

    # Verificar dispositivo
    if hay_dispositivo():
        print("  [+] Dispositivo conectado")
        estado()
    else:
        print("  [!] No hay dispositivo conectado")
        print("  Conecta por USB o escribe: conecta <IP>")
        print()

    # Bucle principal
    while True:
        try:
            texto = input("  dns> ").strip()
            if texto:
                procesar_input(texto)
        except KeyboardInterrupt:
            print("\n\n  Adios!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
