#!/usr/bin/env python3
"""
============================================================
DNS PRIVADO - Control Remoto por ADB
============================================================
Script para controlar la configuración de DNS Privado en
dispositivos Android (9+) mediante ADB.

Compatible con: Samsung, Xiaomi, Pixel, OnePlus, Huawei, etc.
Requiere: ADB instalado y dispositivo conectado (USB o WiFi)

Autor: Generado para uso con LLM
Dispositivo probado: Samsung SM-J610G (Android 10)
============================================================
"""

import subprocess
import sys
import os

# ============================================================
# CONFIGURACION - Servidores DNS populares
# ============================================================
DNS_SERVERS = {
    "adguard": "dns.adguard.com",
    "adguard_family": "family.adguard-dns.com",
    "cloudflare": "one.one.one.one",
    "cloudflare_family": "family.cloudflare-dns.com",
    "cloudflare_malware": "security.cloudflare-dns.com",
    "google": "dns.google",
    "quad9": "dns.quad9.net",
    "quad9_unsecured": "dns9.quad9.net",
    "nextdns": "dns.nextdns.io",
    "mullvad": "dns.mullvad.net",
    "mullvad_adblock": "adblock.dns.mullvad.net",
    "dnsforge": "dnsforge.de",
    "cleanbrowsing": "security-filter-dns.cleanbrowsing.org",
    "cleanbrowsing_family": "family-filter-dns.cleanbrowsing.org",
    "controld": "freedns.controld.com",
    "libredns": "dot.libredns.gr",
}

# ============================================================
# MODOS DE DNS PRIVADO
# ============================================================
# off              -> DNS Privado desactivado
# opportunistic    -> Automatico (usa DNS privado si esta disponible)
# hostname_mode    -> Activado con servidor especifico (Android 10+)
# hostname         -> Activado con servidor especifico (Android 9)
# ============================================================


def run_adb(command: str) -> str:
    """Ejecuta un comando ADB y retorna el resultado."""
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
        return "ERROR: Timeout - dispositivo no responde"
    except Exception as e:
        return f"ERROR: {str(e)}"


def check_device():
    """Verifica si hay un dispositivo conectado por ADB."""
    output = run_adb("devices")
    lines = output.strip().split("\n")
    devices = [l for l in lines[1:] if "device" in l and "unauthorized" not in l]
    if not devices:
        print("\n[!] No hay dispositivo conectado o no esta autorizado.")
        print("    Conecta por USB o por WiFi con: adb connect <IP>:5555")
        return False
    print(f"\n[+] Dispositivo conectado: {devices[0].split()[0]}")
    return True


def get_device_info():
    """Muestra informacion del dispositivo."""
    brand = run_adb("shell getprop ro.product.brand")
    model = run_adb("shell getprop ro.product.model")
    android = run_adb("shell getprop ro.build.version.release")
    sdk = run_adb("shell getprop ro.build.version.sdk")
    print(f"\n{'='*50}")
    print(f"  Marca:    {brand}")
    print(f"  Modelo:   {model}")
    print(f"  Android:  {android} (SDK {sdk})")
    print(f"{'='*50}")
    return {"brand": brand.lower(), "model": model, "android": android, "sdk": sdk}


def get_dns_status():
    """Obtiene el estado actual del DNS Privado (global y secure)."""
    mode_global = run_adb("shell settings get global private_dns_mode")
    spec_global = run_adb("shell settings get global private_dns_specifier")
    mode_secure = run_adb("shell settings get secure private_dns_mode")
    spec_secure = run_adb("shell settings get secure private_dns_specifier")

    print(f"\n{'='*50}")
    print(f"  ESTADO ACTUAL DEL DNS PRIVADO")
    print(f"{'='*50}")
    print(f"  [global] Modo:     {mode_global}")
    print(f"  [global] Servidor: {spec_global}")
    print(f"  [secure] Modo:     {mode_secure}")
    print(f"  [secure] Servidor: {spec_secure}")
    print(f"{'='*50}")

    # Interpretar estado
    mode = mode_global
    if mode == "off":
        print("  >> Estado: DESACTIVADO")
    elif mode in ("opportunistic",):
        print("  >> Estado: AUTOMATICO (oportunista)")
    elif mode in ("hostname_mode", "hostname"):
        print(f"  >> Estado: ACTIVADO con servidor: {spec_global}")
    elif mode == "null":
        print("  >> Estado: No configurado (por defecto)")
    else:
        print(f"  >> Estado: Desconocido ({mode})")

    return {
        "mode_global": mode_global,
        "spec_global": spec_global,
        "mode_secure": mode_secure,
        "spec_secure": spec_secure,
    }


def set_dns(server: str, write_secure: bool = True):
    """
    Activa DNS Privado con un servidor especifico.

    Args:
        server: hostname del servidor DNS (ej: dns.adguard.com)
        write_secure: True para escribir tambien en 'secure' (necesario para Samsung)
    """
    print(f"\n[*] Activando DNS Privado: {server}")

    # Escribir en global (funciona en la mayoria de dispositivos)
    run_adb(f"shell settings put global private_dns_specifier {server}")
    run_adb("shell settings put global private_dns_mode hostname_mode")

    # Escribir en secure (necesario para Samsung y algunos otros)
    if write_secure:
        run_adb(f"shell settings put secure private_dns_specifier {server}")
        run_adb("shell settings put secure private_dns_mode hostname_mode")

    print(f"[+] DNS Privado activado: {server}")
    print(f"    (escrito en global{' y secure' if write_secure else ''})")


def disable_dns(write_secure: bool = True):
    """Desactiva DNS Privado."""
    print("\n[*] Desactivando DNS Privado...")

    run_adb("shell settings put global private_dns_mode off")
    if write_secure:
        run_adb("shell settings put secure private_dns_mode off")

    print("[+] DNS Privado DESACTIVADO")


def set_dns_auto(write_secure: bool = True):
    """Pone DNS Privado en modo automatico (oportunista)."""
    print("\n[*] Configurando DNS Privado en modo AUTOMATICO...")

    run_adb("shell settings put global private_dns_mode opportunistic")
    if write_secure:
        run_adb("shell settings put secure private_dns_mode opportunistic")

    print("[+] DNS Privado en modo AUTOMATICO (oportunista)")


def connect_wifi(ip: str, port: int = 5555):
    """Conecta a un dispositivo por ADB WiFi."""
    print(f"\n[*] Conectando a {ip}:{port}...")
    output = run_adb(f"connect {ip}:{port}")
    print(f"    {output}")
    return "connected" in output.lower()


def disconnect_wifi(ip: str = None, port: int = 5555):
    """Desconecta ADB WiFi."""
    if ip:
        output = run_adb(f"disconnect {ip}:{port}")
    else:
        output = run_adb("disconnect")
    print(f"[*] Desconectado: {output}")


def test_dns_connectivity(server: str):
    """Prueba conectividad con el servidor DNS desde el dispositivo."""
    print(f"\n[*] Probando conectividad con {server}...")
    output = run_adb(f"shell ping -c 2 {server}")
    if "ERROR" in output or "unknown host" in output.lower():
        print(f"[!] No se puede alcanzar {server}")
        print(f"    {output}")
        return False
    else:
        print(f"[+] Conectividad OK con {server}")
        # Extraer tiempo
        for line in output.split("\n"):
            if "avg" in line:
                print(f"    {line}")
        return True


def grant_permission(package: str = "com.flashsphere.privatednsqs"):
    """
    Otorga el permiso WRITE_SECURE_SETTINGS a una app.
    Necesario para apps como Private DNS Quick Settings.
    """
    print(f"\n[*] Otorgando permiso WRITE_SECURE_SETTINGS a: {package}")
    output = run_adb(f"shell pm grant {package} android.permission.WRITE_SECURE_SETTINGS")
    if "ERROR" in output or "Exception" in output:
        print(f"[!] Error al otorgar permiso: {output}")
        return False
    else:
        print(f"[+] Permiso otorgado exitosamente a {package}")
        return True


def list_dns_servers():
    """Muestra la lista de servidores DNS disponibles."""
    print(f"\n{'='*50}")
    print(f"  SERVIDORES DNS DISPONIBLES")
    print(f"{'='*50}")
    for key, server in DNS_SERVERS.items():
        print(f"  {key:20s} -> {server}")
    print(f"{'='*50}")


def interactive_menu():
    """Menu interactivo para controlar DNS."""
    while True:
        print(f"\n{'='*50}")
        print("  DNS PRIVADO - CONTROL POR ADB")
        print(f"{'='*50}")
        print("  1. Ver estado actual del DNS")
        print("  2. Activar DNS con servidor especifico")
        print("  3. Desactivar DNS Privado")
        print("  4. Modo automatico (oportunista)")
        print("  5. Ver servidores disponibles")
        print("  6. Probar conectividad con servidor DNS")
        print("  7. Info del dispositivo")
        print("  8. Conectar por WiFi (ADB TCP)")
        print("  9. Otorgar permiso a app DNS")
        print("  0. Salir")
        print(f"{'='*50}")

        choice = input("\n  Opcion: ").strip()

        if choice == "1":
            get_dns_status()

        elif choice == "2":
            list_dns_servers()
            print("\n  Escribe el nombre corto (ej: adguard) o el hostname completo:")
            server_input = input("  Servidor: ").strip()
            server = DNS_SERVERS.get(server_input, server_input)
            if server:
                set_dns(server)
                get_dns_status()

        elif choice == "3":
            disable_dns()
            get_dns_status()

        elif choice == "4":
            set_dns_auto()
            get_dns_status()

        elif choice == "5":
            list_dns_servers()

        elif choice == "6":
            server_input = input("  Servidor a probar (o enter para actual): ").strip()
            if not server_input:
                status = get_dns_status()
                server_input = status["spec_global"]
            server = DNS_SERVERS.get(server_input, server_input)
            test_dns_connectivity(server)

        elif choice == "7":
            get_device_info()

        elif choice == "8":
            ip = input("  IP del dispositivo: ").strip()
            connect_wifi(ip)

        elif choice == "9":
            print("  Paquetes disponibles:")
            print("    1. com.flashsphere.privatednsqs (Play Store)")
            print("    2. com.flashsphere.privatednsqs.nolauncher (sin launcher)")
            print("    3. Otro (escribir manualmente)")
            pkg_choice = input("  Opcion: ").strip()
            if pkg_choice == "1":
                grant_permission("com.flashsphere.privatednsqs")
            elif pkg_choice == "2":
                grant_permission("com.flashsphere.privatednsqs.nolauncher")
            elif pkg_choice == "3":
                pkg = input("  Paquete: ").strip()
                grant_permission(pkg)

        elif choice == "0":
            print("\n  Adios!")
            break

        else:
            print("\n  [!] Opcion no valida")


# ============================================================
# USO DIRECTO DESDE LINEA DE COMANDOS
# ============================================================
# python dns_privado_adb.py status        -> Ver estado
# python dns_privado_adb.py on <servidor> -> Activar con servidor
# python dns_privado_adb.py off           -> Desactivar
# python dns_privado_adb.py auto          -> Modo automatico
# python dns_privado_adb.py test <server> -> Probar conectividad
# python dns_privado_adb.py info          -> Info del dispositivo
# python dns_privado_adb.py menu          -> Menu interactivo
# python dns_privado_adb.py servers       -> Listar servidores
# python dns_privado_adb.py connect <ip>  -> Conectar WiFi ADB
# ============================================================

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "menu":
        if check_device():
            interactive_menu()
        sys.exit()

    cmd = args[0].lower()

    if cmd == "status":
        if check_device():
            get_dns_status()

    elif cmd == "on":
        if len(args) < 2:
            print("[!] Uso: python dns_privado_adb.py on <servidor>")
            print("    Ejemplo: python dns_privado_adb.py on adguard")
            print("    Ejemplo: python dns_privado_adb.py on dns.adguard.com")
            list_dns_servers()
            sys.exit(1)
        server = DNS_SERVERS.get(args[1], args[1])
        if check_device():
            set_dns(server)

    elif cmd == "off":
        if check_device():
            disable_dns()

    elif cmd == "auto":
        if check_device():
            set_dns_auto()

    elif cmd == "test":
        server = args[1] if len(args) > 1 else "dnsforge.de"
        server = DNS_SERVERS.get(server, server)
        if check_device():
            test_dns_connectivity(server)

    elif cmd == "info":
        if check_device():
            get_device_info()

    elif cmd == "servers":
        list_dns_servers()

    elif cmd == "connect":
        if len(args) < 2:
            print("[!] Uso: python dns_privado_adb.py connect <IP>")
            sys.exit(1)
        connect_wifi(args[1])

    elif cmd == "disconnect":
        disconnect_wifi(args[1] if len(args) > 1 else None)

    elif cmd == "grant":
        pkg = args[1] if len(args) > 1 else "com.flashsphere.privatednsqs"
        if check_device():
            grant_permission(pkg)

    else:
        print(f"[!] Comando desconocido: {cmd}")
        print("    Comandos: status, on, off, auto, test, info, servers, connect, disconnect, grant, menu")
