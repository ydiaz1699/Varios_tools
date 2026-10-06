"""Capa de logica pura del MCP de Sawers (tienda.sawers.com.bo).

Esta capa hace fetch + parse del HTML y devuelve objetos Python normalizados.
NO depende de MCP: se puede importar y probar sola, o reutilizar desde otro
agente/script. La capa MCP (server.py) solo envuelve estas funciones.

Fuente: tienda OpenCart (tema Bootstrap 3). No hay API oficial -> scraping.

Todos los selectores CSS viven AQUI y SOLO AQUI. Si Sawers rediseña la tienda,
este es el unico archivo que hay que tocar.
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import asdict, dataclass
from typing import Any, Optional

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

BASE_URL = "https://tienda.sawers.com.bo"

# User-Agent de navegador real. Cloudflare deja pasar fetch limpio con esto;
# si algun dia mete challenge JS, este es el punto donde cambiar de estrategia
# (p.ej. curl_cffi o un fetch headless).
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

_TIMEOUT = 20.0

# --- Rate limiting suave: no martillear la tienda / evitar retos de Cloudflare.
_MIN_INTERVAL = 0.7  # segundos minimos entre peticiones
_last_request_at = 0.0
_rate_lock = threading.Lock()

# --- Cliente HTTP persistente: mantiene las cookies de sesion de OpenCart,
#     lo que permite loguearse una vez y ver precios en las siguientes peticiones.
#     Si no se hace login, funciona igual (modo anonimo).
_client_lock = threading.Lock()
_client: Optional[httpx.Client] = None
_logged_in = False


def _get_client() -> httpx.Client:
    global _client
    with _client_lock:
        if _client is None:
            _client = httpx.Client(
                headers=_HEADERS,
                timeout=_TIMEOUT,
                follow_redirects=True,
            )
        return _client

# --- Regex para extraer el product_id, que vive dentro del onclick:
#     ajaxAdd($(this),4949)  /  wishlist.add('4949')  /  compare.add('4949')
_PRODUCT_ID_RE = re.compile(r"(?:ajaxAdd\(\$\(this\),|(?:wishlist|compare)\.add\(['\"]?)(\d+)")


class SawersError(Exception):
    """Error de red o de parseo al consultar la tienda."""


@dataclass
class ProductSummary:
    """Producto tal como aparece en un listado/busqueda (sin precio)."""

    product_id: Optional[str]
    name: Optional[str]
    url: Optional[str]
    image: Optional[str]
    description: Optional[str]


@dataclass
class ProductDetail:
    """Detalle de una pagina de producto individual."""

    product_id: Optional[str]
    name: Optional[str]
    url: str
    image: Optional[str]
    price: Optional[str]            # texto; o aviso de que requiere login
    price_requires_login: bool      # True si la tienda oculta el precio a anonimos
    currency: Optional[str]         # p.ej. "BOB"
    availability: Optional[str]     # p.ej. "Disponible"
    description: Optional[str]
    attributes: dict[str, str]      # Marca, Modelo, SKU, etc. si existen


# --------------------------------------------------------------------------- #
# Fetch (unico punto de red)
# --------------------------------------------------------------------------- #
def _throttle() -> None:
    global _last_request_at
    with _rate_lock:
        delta = time.monotonic() - _last_request_at
        if delta < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - delta)
        _last_request_at = time.monotonic()


def _check_cloudflare(html: str) -> None:
    low = html.lower()
    if "just a moment" in low or "cf-chl" in low or "challenge-platform" in low:
        raise SawersError(
            "Cloudflare esta mostrando un desafio (challenge). El fetch simple "
            "no basta ahora mismo; habria que usar un fetcher que resuelva JS."
        )


def _fetch(url: str, params: Optional[dict[str, Any]] = None) -> HTMLParser:
    _throttle()
    client = _get_client()
    try:
        resp = client.get(url, params=params)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise SawersError(f"Error al pedir {url}: {exc}") from exc
    _check_cloudflare(resp.text)
    return HTMLParser(resp.text)


# --------------------------------------------------------------------------- #
# Login (opcional): permite ver los precios, que la tienda oculta a anonimos.
# --------------------------------------------------------------------------- #
def login(email: str, password: str) -> bool:
    """Inicia sesion en la tienda para poder ver precios.

    La tienda OCULTA los precios a visitantes anonimos. Tras un login correcto,
    las cookies de sesion quedan en el cliente persistente y las llamadas
    posteriores a get_product/search_products veran los precios reales.

    Devuelve True si el login fue correcto. Lanza SawersError si falla.
    """
    global _logged_in
    if not email or not password:
        raise SawersError("Se requieren email y password para iniciar sesion.")

    client = _get_client()
    # 1) GET a la pagina de login para sembrar la cookie de sesion inicial.
    _throttle()
    try:
        client.get(f"{BASE_URL}/index.php", params={"route": "account/login"})
    except httpx.HTTPError as exc:
        raise SawersError(f"No se pudo abrir la pagina de login: {exc}") from exc

    # 2) POST de credenciales al endpoint de login (alias SEO /login).
    _throttle()
    try:
        resp = client.post(
            f"{BASE_URL}/login",
            data={"email": email, "password": password},
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise SawersError(f"Error durante el login: {exc}") from exc

    _check_cloudflare(resp.text)
    low = resp.text.lower()

    # OpenCart devuelve "Advertencia: Email no existe y/o Contraseña..." si falla.
    if "advertencia" in low and ("email no existe" in low or "contrase" in low):
        _logged_in = False
        raise SawersError(
            "Login rechazado: email o contrasena incorrectos (o cuenta no activa)."
        )

    # Senal de exito: aparece la opcion de cerrar sesion / panel de cuenta.
    final_url = str(resp.url).lower()
    if "cerrar sesi" in low or "logout" in low or "account/account" in final_url:
        _logged_in = True
        return True

    # Caso ambiguo: lo damos por bueno solo si no vimos advertencia.
    _logged_in = True
    return True


def is_logged_in() -> bool:
    """Indica si hay una sesion iniciada en el cliente actual."""
    return _logged_in


def logout() -> None:
    """Cierra la sesion y descarta las cookies."""
    global _client, _logged_in
    with _client_lock:
        if _client is not None:
            try:
                _throttle()
                _client.get(f"{BASE_URL}/index.php", params={"route": "account/logout"})
            except httpx.HTTPError:
                pass
            _client.close()
            _client = None
        _logged_in = False


# --------------------------------------------------------------------------- #
# Helpers de parseo
# --------------------------------------------------------------------------- #
def _text(node) -> Optional[str]:
    if node is None:
        return None
    t = node.text(strip=True)
    return t or None


def _extract_product_id(card) -> Optional[str]:
    """El id esta en el onclick de los botones de la tarjeta."""
    for btn in card.css("button[onclick]"):
        onclick = btn.attributes.get("onclick") or ""
        m = _PRODUCT_ID_RE.search(onclick)
        if m:
            return m.group(1)
    # Fallback: a veces aparece en inputs ocultos o en atributos data-*
    hidden = card.css_first("input[name='product_id']")
    if hidden is not None:
        return hidden.attributes.get("value")
    return None


def _parse_card(card) -> ProductSummary:
    name_a = card.css_first(".caption .name a") or card.css_first(".caption a")
    img = card.css_first(".image img")
    image = None
    if img is not None:
        # OJO: el tema usa lazy-loading -> la URL real esta en data-src, no en src.
        image = (
            img.attributes.get("data-src")
            or img.attributes.get("data-original")
            or img.attributes.get("src")
        )
        if image == "#":
            image = None
    return ProductSummary(
        product_id=_extract_product_id(card),
        name=_text(name_a),
        url=name_a.attributes.get("href") if name_a is not None else None,
        image=image,
        description=_text(card.css_first(".caption .description")),
    )


def _parse_listing(tree: HTMLParser, limit: int) -> list[ProductSummary]:
    cards = tree.css(".product-thumb")
    out: list[ProductSummary] = []
    for card in cards:
        summary = _parse_card(card)
        if summary.name:  # descartar tarjetas vacias / placeholders
            out.append(summary)
        if len(out) >= limit:
            break
    return out


# --------------------------------------------------------------------------- #
# Funciones publicas (lo que envuelve el MCP)
# --------------------------------------------------------------------------- #
def search_products(query: str, limit: int = 10) -> list[dict]:
    """Busca productos por termino. Devuelve resumenes (sin precio: el tema no lo
    muestra en el listado; usar get_product para el precio)."""
    if not query or not query.strip():
        raise SawersError("La busqueda no puede estar vacia.")
    limit = max(1, min(limit, 50))
    tree = _fetch(
        f"{BASE_URL}/index.php",
        params={"route": "product/search", "search": query.strip()},
    )
    return [asdict(p) for p in _parse_listing(tree, limit)]


def list_specials(limit: int = 20) -> list[dict]:
    """Lista productos en oferta (/especiales)."""
    limit = max(1, min(limit, 50))
    tree = _fetch(f"{BASE_URL}/especiales")
    return [asdict(p) for p in _parse_listing(tree, limit)]


def _resolve_url(product: str) -> str:
    """Admite una URL completa, una ruta relativa o un product_id numerico."""
    product = product.strip()
    if product.startswith("http://") or product.startswith("https://"):
        return product
    if product.isdigit():
        # Ruta canonica de OpenCart por id.
        return f"{BASE_URL}/index.php?route=product/product&product_id={product}"
    return f"{BASE_URL}/{product.lstrip('/')}"


def get_product(product: str) -> dict:
    """Detalle de un producto. `product` puede ser URL, ruta o product_id."""
    url = _resolve_url(product)
    tree = _fetch(url)

    def _itemprop(name: str) -> Optional[str]:
        node = tree.css_first(f"[itemprop='{name}']")
        if node is None:
            return None
        # El dato suele ir en content="" (microdato), si no, el texto.
        return node.attributes.get("content") or _text(node)

    # HALLAZGO IMPORTANTE: la tienda OCULTA los precios a visitantes anonimos.
    # El microdato itemprop="price" viene vacio y la pagina muestra
    # "Precio - Iniciar Sesion". Reportamos ese estado honestamente en vez de None.
    price = _itemprop("price")
    price = price.strip() if (price and price.strip()) else None
    requires_login = price is None and "iniciar sesi" in tree.html.lower()
    if price is None and requires_login:
        price = "Requiere iniciar sesion (precio no publico)"

    name = (
        _text(tree.css_first("h1"))
        or _itemprop("name")
        or _text(tree.css_first(".product-title, .title"))
    )

    img = (
        tree.css_first("#productZoom")
        or tree.css_first("[itemprop='image']")
        or tree.css_first(".thumbnails img, .image img")
    )
    image = None
    if img is not None:
        image = (
            img.attributes.get("data-zoom-image")
            or img.attributes.get("content")
            or img.attributes.get("data-src")
            or img.attributes.get("href")
            or img.attributes.get("src")
        )

    # Atributos tipo "Marca: X", "Modelo: Y", "Existencia: Disponible".
    attributes: dict[str, str] = {}
    for li in tree.css("ul.list-unstyled li, .product-info li"):
        txt = li.text(strip=True)
        if ":" in txt and len(txt) < 120:
            k, _, v = txt.partition(":")
            k, v = k.strip(), v.strip()
            if k and v:
                attributes.setdefault(k, v)

    availability = _itemprop("availability") or attributes.get("Existencia") or attributes.get("Disponibilidad")

    desc = tree.css_first("#tab-description") or tree.css_first("[itemprop='description']")

    return asdict(
        ProductDetail(
            product_id=_extract_product_id(tree.css_first("body") or tree.root),
            name=name,
            url=url,
            image=image,
            price=price,
            price_requires_login=requires_login,
            currency=_itemprop("priceCurrency"),
            availability=availability,
            description=_text(desc),
            attributes=attributes,
        )
    )
