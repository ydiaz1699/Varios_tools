"""Capa MCP: expone el scraper de Sawers como tools para un LLM (FastMCP, stdio).

Todas las tools son de SOLO LECTURA (scraping). En Kiro CLI V3 (permissions.yaml)
se pueden marcar todas como `allow`.
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

from . import scraper

mcp = FastMCP(
    name="sawers-mcp",
    instructions=(
        "Consulta el catalogo de la tienda Sawers Bolivia (tienda.sawers.com.bo): "
        "modulos electronicos, microcontroladores, Arduino, kits de robotica e "
        "impresion 3D. Los datos se obtienen por scraping (la tienda no tiene API). "
        "IMPORTANTE: la tienda oculta los PRECIOS a visitantes anonimos; para "
        "productos sin login el precio se reporta como 'Requiere iniciar sesion'. "
        "El resto de datos (nombre, descripcion, imagen, disponibilidad, atributos) "
        "si estan disponibles."
    ),
)


@mcp.tool()
def search_products(query: str, limit: int = 10) -> list[dict]:
    """Busca productos en la tienda Sawers por termino de busqueda.

    Devuelve una lista con: product_id, name, url, image y una descripcion corta.
    El precio NO aparece en el listado (usa get_product). `limit` entre 1 y 50.
    """
    return scraper.search_products(query, limit)


@mcp.tool()
def get_product(product: str) -> dict:
    """Obtiene el detalle de un producto de la tienda Sawers.

    `product` puede ser: la URL completa, la ruta/slug, o el product_id numerico
    (p.ej. "4949"). Devuelve name, url, image, price, currency (BOB),
    availability, description y attributes (Marca, Codigo, etc.).
    NOTA: la tienda oculta el precio a usuarios no logueados; en ese caso
    `price_requires_login` sera true y `price` llevara un aviso.
    """
    return scraper.get_product(product)


@mcp.tool()
def list_specials(limit: int = 20) -> list[dict]:
    """Lista los productos en oferta / especiales de la tienda Sawers.

    Mismo formato que search_products. `limit` entre 1 y 50.
    """
    return scraper.list_specials(limit)


@mcp.tool()
def login(email: str, password: str) -> dict:
    """Inicia sesion en la tienda Sawers para poder VER LOS PRECIOS.

    La tienda oculta los precios a visitantes anonimos. Tras un login correcto,
    las siguientes llamadas a get_product devolveran el precio real.
    Si prefieres no pasar credenciales por aqui, define las variables de entorno
    SAWERS_EMAIL y SAWERS_PASSWORD y la sesion se iniciara sola al arrancar.
    """
    ok = scraper.login(email, password)
    return {"logged_in": ok, "message": "Sesion iniciada. Ya puedes ver precios."}


@mcp.tool()
def session_status() -> dict:
    """Indica si hay una sesion iniciada (y por tanto si se veran los precios)."""
    return {"logged_in": scraper.is_logged_in()}


def _auto_login_from_env() -> None:
    """Si SAWERS_EMAIL / SAWERS_PASSWORD estan definidas, inicia sesion al arrancar.

    Patron de secretos por entorno (no se hardcodean credenciales)."""
    email = os.environ.get("SAWERS_EMAIL")
    password = os.environ.get("SAWERS_PASSWORD")
    if email and password:
        try:
            scraper.login(email, password)
        except scraper.SawersError:
            # No abortamos el arranque: el MCP sigue util en modo anonimo.
            pass


def main() -> None:
    """Entry point para `sawers-mcp` (stdio)."""
    _auto_login_from_env()
    mcp.run()


if __name__ == "__main__":
    main()
