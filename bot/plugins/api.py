import requests

PRODUCT_BY_SLUG_API = "http://127.0.0.1:8000/products/api/products/slug/"
CATEGORIES_API = "http://127.0.0.1:8000/products/api/categories/"
PRODUCTS_BY_CATEGORY_API = "http://127.0.0.1:8000/products/api/products/by_category/"
PRODUCTS_API = "http://127.0.0.1:8000/products/api/products/"
PRODUCTS_PAGE = "http://127.0.0.1:8000/products"

def get_product_by_slug(slug):
    url = f"{PRODUCT_BY_SLUG_API}{slug}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_categories():
    response = requests.get(CATEGORIES_API)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_products_by_category(category_id):
    response = requests.get(f"{PRODUCTS_BY_CATEGORY_API}?category_id={category_id}")
    if response.status_code == 200:
        return response.json()
    return []

def get_latest_products():
    response = requests.get(f"{PRODUCTS_API}?ordering=-id&page=1")
    if response.status_code == 200:
        return response.json().get('results', [])
    return []