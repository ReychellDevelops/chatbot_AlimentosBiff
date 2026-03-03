from sheets_service import get_products

products = get_products()

for p in products:
    print(p)