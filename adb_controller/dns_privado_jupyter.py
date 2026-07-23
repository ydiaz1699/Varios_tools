"""
============================================================
DNS PRIVADO - Modulo para Jupyter Notebook
============================================================
Importa este archivo en cualquier celda de Jupyter y controla
el DNS Privado de tu dispositivo Android por ADB.

Uso en Jupyter:
    from dns_privado_jupyter import dns

    dns.status()              # Ver estado actual
    dns.on("dnsforge")        # Activar con dnsforge.de
    dns.on("adguard")         # Activar con AdGuard
    dns.off()                 # Desactivar
    dns.auto()                # Modo automatico
    dns.test()                # Probar conectividad
    dns.info()                # Info del dispositivo
    dns.servers()             # Ver servidores disponibles
    dns.connect("192.168.0.8")  # Conectar WiFi ADB
    dns.grant()               # Otorgar permiso a app

Compatible con: Samsung (global+secure), Xiaomi, Pixel, etc.
Requiere: ADB instalado y dispositivo conectado
============================================================
"""

import subprocess
from IPython.display import display, HTML, Markdown

# ============================================================
# SERVIDORES DNS
# ============================================================
DNS_SERVERS = {
    "adguard": "dns.adguard.com",
    "adguard_family": "family.adguard-dns.com",
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


def _adb(command: str) -> str:
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


def _resolver_servidor(nombre: str) -> str:
    """Resuelve nombre corto a hostname completo."""
    if nombre in DNS_SERVERS:
        return DNS_SERVERS[nombre]
    # Buscar parcial
    for key, server in DNS_SERVERS.items():
        if nombre.lower() in key:
            return server
    # Si tiene punto, asumir que es un hostname directo
    if "." in nombre:
        return nombre
    return None


def _hay_dispositivo() -> bool:
    """Verifica si hay dispositivo conectado."""
    output = _adb("devices")
    lines = output.strip().split("\n")
    devices = [l for l in lines[1:] if "device" in l and "unauthorized" not in l]
    return len(devices) > 0


class DNSController:
    """Controlador de DNS Privado para usar en Jupyter."""

    def status(self):
        """Muestra el estado actual del DNS Privado."""
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        mode_g = _adb("shell settings get global private_dns_mode")
        spec_g = _adb("shell settings get global private_dns_specifier")
        mode_s = _adb("shell settings get secure private_dns_mode")
        spec_s = _adb("shell settings get secure private_dns_specifier")

        # Interpretar
        if mode_g in ("hostname_mode", "hostname"):
            estado = f"ACTIVADO"
            color = "green"
            detalle = f"Servidor: {spec_g}"
        elif mode_g == "opportunistic":
            estado = "AUTOMATICO"
            color = "orange"
            detalle = "Usa DNS privado si esta disponible"
        elif mode_g == "off":
            estado = "DESACTIVADO"
            color = "red"
            detalle = ""
        else:
            estado = f"DESCONOCIDO ({mode_g})"
            color = "gray"
            detalle = ""

        print(f"{'='*45}")
        print(f"  DNS Privado: {estado}")
        if detalle:
            print(f"  {detalle}")
        print(f"{'='*45}")
        print(f"  [global] mode: {mode_g}")
        print(f"  [global] spec: {spec_g}")
        print(f"  [secure] mode: {mode_s}")
        print(f"  [secure] spec: {spec_s}")
        print(f"{'='*45}")

        return {"mode": mode_g, "server": spec_g, "secure_mode": mode_s}

    def on(self, servidor: str = "dnsforge"):
        """
        Activa DNS Privado con un servidor.

        Ejemplos:
            dns.on("adguard")
            dns.on("cloudflare")
            dns.on("dnsforge")
            dns.on("dns.google")  # hostname directo
        """
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        host = _resolver_servidor(servidor)
        if not host:
            print(f"Servidor '{servidor}' no encontrado. Usa dns.servers() para ver opciones.")
            return

        print(f"Activando DNS: {host}...")

        # Escribir en global Y secure (Samsung)
        _adb(f"shell settings put global private_dns_specifier {host}")
        _adb("shell settings put global private_dns_mode hostname_mode")
        _adb(f"shell settings put secure private_dns_specifier {host}")
        _adb("shell settings put secure private_dns_mode hostname_mode")

        # Verificar
        check = _adb("shell settings get global private_dns_mode")
        if check == "hostname_mode":
            print(f"DNS ACTIVADO: {host}")
        else:
            print(f"[!] Posible error. Modo actual: {check}")

    def off(self):
        """Desactiva DNS Privado."""
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        _adb("shell settings put global private_dns_mode off")
        _adb("shell settings put secure private_dns_mode off")
        print("DNS Privado DESACTIVADO")

    def auto(self):
        """Pone DNS Privado en modo automatico (oportunista)."""
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        _adb("shell settings put global private_dns_mode opportunistic")
        _adb("shell settings put secure private_dns_mode opportunistic")
        print("DNS Privado en modo AUTOMATICO")

    def test(self, servidor: str = None):
        """
        Prueba conectividad con el servidor DNS actual (o uno especificado).

        Ejemplos:
            dns.test()            # Prueba el servidor actual
            dns.test("adguard")   # Prueba AdGuard
        """
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        if servidor:
            host = _resolver_servidor(servidor)
        else:
            host = _adb("shell settings get global private_dns_specifier")
            if host == "null" or not host:
                print("No hay servidor configurado. Especifica uno: dns.test('adguard')")
                return

        print(f"Probando conectividad con {host}...")
        output = _adb(f"shell ping -c 2 {host}")

        if "2 received" in output:
            print(f"FUNCIONA - conectividad OK con {host}")
        elif "1 received" in output:
            print(f"PARCIAL - hay perdida de paquetes con {host}")
        elif "unknown host" in output.lower():
            print(f"FALLA - no se puede resolver {host}")
        else:
            print(f"FALLA - sin conectividad con {host}")
            if "ERROR" in output:
                print(f"  Detalle: {output}")

    def info(self):
        """Muestra informacion del dispositivo conectado."""
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        brand = _adb("shell getprop ro.product.brand")
        model = _adb("shell getprop ro.product.model")
        android = _adb("shell getprop ro.build.version.release")
        sdk = _adb("shell getprop ro.build.version.sdk")
        ip_info = _adb("shell ip route | grep wlan0")

        print(f"{'='*45}")
        print(f"  Marca:    {brand}")
        print(f"  Modelo:   {model}")
        print(f"  Android:  {android} (SDK {sdk})")
        if ip_info and "ERROR" not in ip_info:
            print(f"  Red:      {ip_info}")
        print(f"{'='*45}")

    def servers(self):
        """Muestra todos los servidores DNS disponibles."""
        print(f"{'='*55}")
        print(f"  SERVIDORES DNS DISPONIBLES")
        print(f"  Uso: dns.on('nombre')")
        print(f"{'='*55}")
        for key, server in DNS_SERVERS.items():
            print(f"  {key:22s} -> {server}")
        print(f"{'='*55}")

    def connect(self, ip: str, port: int = 5555):
        """
        Conecta a un dispositivo por ADB WiFi.

        Ejemplo:
            dns.connect("192.168.0.8")
        """
        print(f"Conectando a {ip}:{port}...")
        output = _adb(f"connect {ip}:{port}")
        if "connected" in output.lower():
            print(f"CONECTADO a {ip}:{port}")
        else:
            print(f"Resultado: {output}")

    def disconnect(self, ip: str = None):
        """Desconecta ADB WiFi."""
        if ip:
            output = _adb(f"disconnect {ip}:5555")
        else:
            output = _adb("disconnect")
        print(f"Desconectado: {output}")

    def devices(self):
        """Lista dispositivos ADB conectados."""
        output = _adb("devices")
        print(output)

    def grant(self, paquete: str = "com.flashsphere.privatednsqs"):
        """
        Otorga permiso WRITE_SECURE_SETTINGS a una app.

        Ejemplos:
            dns.grant()  # Play Store version
            dns.grant("com.flashsphere.privatednsqs.nolauncher")  # No-launcher
        """
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        print(f"Otorgando permiso a: {paquete}...")
        output = _adb(f"shell pm grant {paquete} android.permission.WRITE_SECURE_SETTINGS")
        if "ERROR" in output or "Exception" in output:
            print(f"[!] Error: {output}")
        else:
            print(f"Permiso otorgado a {paquete}")

    def toggle(self):
        """Alterna entre activado y desactivado (toggle)."""
        if not _hay_dispositivo():
            print("No hay dispositivo conectado. Usa dns.connect('IP')")
            return

        mode = _adb("shell settings get global private_dns_mode")
        if mode in ("hostname_mode", "hostname"):
            self.off()
        else:
            spec = _adb("shell settings get global private_dns_specifier")
            if spec and spec != "null":
                self.on(spec)
            else:
                self.on("dnsforge")

    def help(self):
        """Muestra ayuda de todos los comandos disponibles."""
        print("""
  DNS Privado - Comandos para Jupyter
  ====================================

  dns.status()              Ver estado actual
  dns.on("servidor")        Activar con servidor
  dns.off()                 Desactivar
  dns.auto()                Modo automatico
  dns.toggle()              Alternar on/off
  dns.test()                Probar conectividad
  dns.test("adguard")       Probar servidor especifico
  dns.info()                Info del dispositivo
  dns.servers()             Ver servidores disponibles
  dns.connect("IP")         Conectar por WiFi ADB
  dns.disconnect()          Desconectar ADB WiFi
  dns.devices()             Listar dispositivos
  dns.grant()               Otorgar permiso a app
  dns.help()                Esta ayuda

  Servidores rapidos:
    adguard, cloudflare, google, quad9,
    dnsforge, mullvad, nextdns, mullvad_adblock
        """)


# ============================================================
# INSTANCIA GLOBAL - Solo importar y usar
# ============================================================
dns = DNSController()

# Auto-mostrar ayuda al importar
print("DNS Privado Controller cargado. Usa: dns.help()")
print("Ejemplo: dns.status(), dns.on('adguard'), dns.off()")
