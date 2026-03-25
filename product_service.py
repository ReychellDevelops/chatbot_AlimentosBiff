from sheets_service import get_products

def normalize(text):
    return str(text).strip().lower()

# ---------------- CATEGORIAS ----------------
def get_categories():
    products = get_products()

    categories = []
    for p in products:
        cat = normalize(p["categoria"])
        if cat not in categories:
            categories.append(cat)

    return categories

# ---------------- FILTROS ----------------
def get_products_by_category_origin_and_sede(category, origin_prefix, sede):
    products = get_products()

    return [
        p for p in products
        if normalize(p["categoria"]) == normalize(category)
        and normalize(p["origen"]).startswith(normalize(origin_prefix))
        and (normalize(p["sede"]) == normalize(sede) or normalize(p["sede"]) == "todas")
    ]

def get_products_by_category_and_sede(category, sede):
    products = get_products()

    return [
        p for p in products
        if normalize(p["categoria"]) == normalize(category)
        and (normalize(p["sede"]) == normalize(sede) or normalize(p["sede"]) == "todas")
    ]

# ---------------- PRODUCTO POR ID ----------------
def get_product_by_id(product_id):
    products = get_products()
    
    for p in products:
        if int(p["id"]) == int(product_id):
            return p
    return None