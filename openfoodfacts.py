"""Functions that talk to the OpenFoodFacts API (the external API)."""
import requests

BASE_URL = "https://world.openfoodfacts.org"


def get_product_by_barcode(barcode):
    """Look up one product by its barcode.
    Returns a small dictionary, or None if not found / API is down."""
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception:
        return None  # network problem or bad response

    if data.get("status") != 1:
        return None  # product not found

    product = data["product"]
    return {
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
    }


def search_product_by_name(name):
    """Search for a product by name. Returns the first match or None."""
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception:
        return None

    products = data.get("products", [])
    if not products:
        return None

    product = products[0]
    return {
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
    }
