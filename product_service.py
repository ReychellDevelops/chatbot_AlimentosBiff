from sheets_service import get_products

#almacena en un array las categorias que trae al recorrer la columna 'categoria' del sheet 'Catalogo_Biff'
def get_categories():
    products = get_products()

    categories = []
    for p in products:
        cat = p["categoria"].lower()
        if cat not in categories:
            categories.append(cat)

    return categories

def get_products_by_category_and_origin(category, origin_prefix):
    products = get_products()

    return [
        p for p in products
        if p["categoria"].strip() == category
        and p["origen"].strip().startswith(origin_prefix)
    ]

def get_products_by_category_origin_and_sede(category, origin_prefix, sede):

    products = get_products()

    return [
        p for p in products
        if p["categoria"] == category
        and p["origen"].startswith(origin_prefix)
        and (p["sede"] == sede or p["sede"] == "Todas")
    ]

# obtiene especificamente los prductos de la categoria que recibe
def get_products_by_category_and_sede(category, sede):

    products = get_products()

    return [
        p for p in products
        if p["categoria"] == category
        and (p["sede"] == sede or p["sede"] == "Todas")
    ]


def get_product_by_id(product_id):
    products = get_products()
    
    for p in products:
        if int(p["id"]) == int(product_id):
            return p
    return None