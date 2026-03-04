# reglas de conversación - CEREBRO
from responses import ask_name, main_menu, invalid_option
from product_service import (
    get_categories,
    get_products_by_category_and_sede,
    get_products_by_category_origin_and_sede
)
from sheets_service import save_order_header, save_order_detail, get_offers

def build_catalog_list(products, sede):

    text = f"""
📍 Catálogo disponible en: {sede}

Estos son los productos disponibles:

"""

    for i, p in enumerate(products, 1):
        peso_promedio = (p["peso_min_kg"] + p["peso_max_kg"]) / 2

        text += f"""
{i}. {p["nombre"]} ({p["referencia"]})
   {p["origen"]} | {p["tipo_unidad"]}
   Peso aproximado por {p["tipo_unidad"]}: {peso_promedio:.2f} kg
   ${p["precio_kg"]:,.0f}/kg
"""

    text += """

¿Qué deseas hacer ahora?

1️⃣ Realizar un pedido
2️⃣ Ver otra categoría
3️⃣ Cambiar sede
0️⃣ Volver al menú principal
"""

    return text

def build_product_list(products, sede):

    text = f"""
📍 Sede: {sede}

Selecciona el producto:
"""

    for i, product in enumerate(products, 1):

        # calcular peso promedio por unidad
        peso_promedio = (
            product["peso_min_kg"] + product["peso_max_kg"]
        ) / 2

        text += (
            f"{i}. {product['nombre']} ({product['referencia']})\n"
            f"   {product['origen']} | {product['tipo_unidad']}\n"
            f"   Peso aproximado por {product['tipo_unidad']}: "
            f"{peso_promedio:.2f} kg\n"
            f"   ${product['precio_kg']:,.0f}/kg\n\n"
        )

    return text

def calculate_order_summary(cart):

    total_precio = 0
    total_peso = 0

    for item in cart:
        total_precio += item["precio_aprox"]
        total_peso += item["peso_aprox_total"]

    tipo_cliente = "mayorista" if total_peso >= 50 else "minorista"

    return total_precio, total_peso, tipo_cliente

def handle_message(session, message):

    state = session['state']

    # -----pedir nombre-----
    if state == 'ASK_NAME':

        name = message.strip()

        if len(name) < 2 or any(char.isdigit() for char in name):
            return "❌ Nombre inválido. Ingresa solo letras y al menos 2 caracteres."

        session['name'] = name
        session['state'] = 'ASK_SEDE'

        return """
    Selecciona tu sede:

    1️⃣ Duitama (Minorista)
    2️⃣ Sogamoso (Minorista y bodega)
    3️⃣ Bogotá (Bodega mayorista)
    """
    
    elif state == "ASK_SEDE":

        sedes = {
            "1": "Duitama",
            "2": "Sogamoso",
            "3": "Bogotá"
        }

        if message not in sedes:
            return "❌ Selecciona 1, 2 o 3."

        session["sede"] = sedes[message]
        session["state"] = "MENU"

        return f"""
        Sede seleccionada: {session['sede']}
        """ + main_menu(session["name"], session["sede"])
    
    # ---- MENÚ PRINCIPAL ----
    elif state == "MENU":

        if message == "1":
            ofertas = get_offers(session["sede"])

            if not ofertas:
                return "📢 No hay ofertas activas en este momento.\n\n" + main_menu(session["name"], session["sede"])

            text = f"""
            🔥 OFERTAS DISPONIBLES 🔥
            📍 Sede: {session["sede"]}

            ⚠️ Las ofertas aplican hasta agotar existencias.
            La compra de ofertas se realiza directamente en el punto físico.
            Aplican términos y condiciones.

            """

            for i, o in enumerate(ofertas, 1):
                text += (
                    f"{i}. {o['nombre']} ({o['referencia']})\n"
                    f"   {o['origen']} | {o['tipo_unidad']}\n"
                    f"   Antes: ${o['precio_normal_kg']:,.0f}/kg\n"
                    f"   Ahora: ${o['precio_oferta_kg']:,.0f}/kg\n\n"
                    f"   Descripción de la oferta: ${o['descripcion']}\n\n"
                )

            text += "0️⃣ Volver al menú"

            session["state"] = "OFFERS_VIEW"

            return text

        elif message == "2":

            categories = get_categories()

            text = f"""
            📍 Estás consultando el catálogo de: {session["sede"]}

            Selecciona categoría:

             """

            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"

            text += "\n0. Volver al menú"

            session["categories"] = categories
            session["state"] = "CATALOG_CATEGORY"

            return text

        elif message == "3":

            categories = get_categories()

            text = f"""
                📍 Estás comprando desde: {session["sede"]}

                Selecciona categoría:

                """

            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"

            session["categories"] = categories
            session["state"] = "ORDER_CATEGORY"

            return text  

        elif message == "4":

            if not session["cart"]:
                return "Tu carrito está vacío 🛒\n" + main_menu(session["name"], session["sede"])

            cart_text = "🛒 Tu pedido:\n"
            for i, item in enumerate(session["cart"], 1):
                cart_text += f"{i}. {item['product']} - {item['quantity']} kg\n"

            return cart_text + "\n" + main_menu(session["name"], session["sede"])

        elif message == "5":
            return "Un asesor te atenderá pronto"
        
        elif message == "6":
            session["state"] = "ASK_SEDE"
            return """
                Selecciona nueva sede:

                1️⃣ Duitama
                2️⃣ Sogamoso
                3️⃣ Bogotá
                """
        
        elif message == "0":
            return "EXIT"
        
        else:
            return invalid_option()
    

    #ESTADOS
    #-------ofertas------------
    elif state == "OFFERS_VIEW":

        if message == "0":
            session["state"] = "MENU"
            return main_menu(session["name"], session["sede"])

        return "Escribe 0 para volver al menú."
    
    # ------- elegir categoría ------------
    elif state == "ORDER_CATEGORY":

        categorias = {
            "1": "Carne de res",
            "2": "Carne de cerdo",
            "3": "Visceras y madejas"
        }

        if message not in categorias:
            return "❌ Opción inválida. Selecciona 1, 2 o 3."

        categoria = categorias[message]
        session["selected_category"] = categoria

        # Si es vísceras no necesita origen
        if categoria == "Visceras y madejas":

            products = get_products_by_category_and_sede(
                categoria,
                session["sede"]
            )

            session["filtered_products"] = products
            session["state"] = "ORDER_PRODUCT"

            return build_product_list(products, session["sede"])

        # Si es res o cerdo → pedir origen
        session["state"] = "ORDER_ORIGIN"

        return """
    Selecciona origen:

        1️⃣ Nacional
        2️⃣ Importada
        """
    
    # ----------categoria del catalogo-----------
    elif state == "CATALOG_CATEGORY":

        if message == "0":
            session["state"] = "MENU"
            return main_menu(session["name"], session["sede"])
        

        categorias = {
            "1": "Carne de res",
            "2": "Carne de cerdo",
            "3": "Visceras y madejas"
        }

        if message not in categorias:
            return "❌ Opción inválida."

        categoria = categorias[message]

        products = get_products_by_category_and_sede(
            categoria,
            session["sede"]
        )

        if not products:
            return "No hay productos disponibles."

        session["catalog_products"] = products
        session["state"] = "CATALOG_VIEW"

        return build_catalog_list(products, session["sede"])
    
    #---------vista de SOLO catalogo-------
    elif state == "CATALOG_VIEW":

        if message == "1":
            session["state"] = "ORDER_CATEGORY"
            categories = get_categories()

            text = f"""
    📍 Estás comprando desde: {session["sede"]}

    Selecciona categoría:

    """
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"

            return text

        elif message == "2":
            session["state"] = "CATALOG_CATEGORY"
            categories = get_categories()

            text = f"""
    📍 Catálogo disponible en: {session["sede"]}

    Selecciona categoría:

    """
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"

            text += "\n0. Volver al menú"

            return text

        elif message == "3":
            session["state"] = "ASK_SEDE"
            return """
    Selecciona nueva sede:

    1️⃣ Duitama
    2️⃣ Sogamoso
    3️⃣ Bogotá
    """

        elif message == "0":
            session["state"] = "MENU"
            return main_menu(session["name"], session["sede"])

        else:
            return "Selecciona una opción válida."
    
#-----------elegir origen-----------
    elif state == "ORDER_ORIGIN":

        origen_map = {
            "1": "Nacional",
            "2": "Importada"
        }

        if message not in origen_map:
            return "❌ Selecciona 1 o 2."

        origin_prefix = origen_map[message]
        category = session["selected_category"]

        products = get_products_by_category_origin_and_sede(
            category,
            origin_prefix,
            session["sede"]
        )

        if not products:
            return "❌ No hay productos disponibles en esta selección."

        session["filtered_products"] = products
        session["state"] = "ORDER_PRODUCT"

        return build_product_list(products, session["sede"])
    # ------- elegir referencia ------------
    elif state == "ORDER_PRODUCT":

        try:
            index = int(message) - 1
            product = session["filtered_products"][index]
        except:
            return "❌ Selecciona un número válido del listado."

        session["current_product"] = product
        session["state"] = "ORDER_QUANTITY"

        # calcular peso promedio
        peso_promedio = (
            product["peso_min_kg"] + product["peso_max_kg"]
        ) / 2

        return f"""
            ¿Cuántas {product['tipo_unidad']}(s) de {product['nombre']} deseas?

            Peso aproximado por {product['tipo_unidad']}: {peso_promedio:.2f} kg
            Precio: ${product['precio_kg']:,.0f}/kg
            """


    # ------- validar cantidad mínima ------------
    elif state == "ORDER_QUANTITY":

        try:
            units = int(message)
            if units <= 0:
                return "❌ La cantidad debe ser mayor a 0."
        except:
            return "❌ Ingresa un número válido."

        product = session["current_product"]

        # Peso promedio por unidad
        peso_promedio_unitario = (
            product["peso_min_kg"] + product["peso_max_kg"]
        ) / 2

        peso_aprox_total = units * peso_promedio_unitario
        precio_aprox = peso_aprox_total * product["precio_kg"]

        session["cart"].append({
            "referencia": product["referencia"],
            "product": product["nombre"],
            "units": units,
            "tipo_unidad": product["tipo_unidad"],
            "precio_kg": product["precio_kg"],
            "peso_promedio_unitario": peso_promedio_unitario,
            "peso_aprox_total": peso_aprox_total,
            "precio_aprox": precio_aprox
        })

        session["state"] = "ORDER_MENU"

        return f"""
            Producto agregado ✅

            {units} {product["tipo_unidad"]}(s)
            Peso aproximado total: {peso_aprox_total:.2f} kg
            Precio aproximado: ${precio_aprox:,.0f}

            1️⃣ Agregar otro producto
            2️⃣ Ver carrito
            3️⃣ Confirmar pedido
            4️⃣ Cancelar pedido
            """


    # ------- menú interno del pedido ------------
    elif state == "ORDER_MENU":

        if message == "1":
            session["state"] = "ORDER_CATEGORY"
            return f"""
                Selecciona categoría:

                1️⃣ Carne de res
                2️⃣ Carne de cerdo
                3️⃣ Visceras y madejas
                """

        elif message == "2":

            cart_text = "🛒 Tu pedido:\n\n"
            total_precio = 0
            total_peso = 0

            for i, item in enumerate(session["cart"], 1):
                cart_text += (
                    f"{i}. {item['product']} ({item['referencia']})\n"
                    f"   {item['units']} {item['tipo_unidad']}(s)\n"
                    f"   Peso aprox: {item['peso_aprox_total']:.2f} kg\n"
                    f"   Precio aprox: ${item['precio_aprox']:,.0f}\n\n"
                )

                total_precio += item["precio_aprox"]
                total_peso += item["peso_aprox_total"]

            cart_text += (
                f"⚖️ Peso total aprox: {total_peso:.2f} kg\n"
                f"💰 Total aprox: ${total_precio:,.0f}\n\n"
                "1️⃣ Agregar otro producto\n"
                "2️⃣ Ver carrito\n"
                "3️⃣ Confirmar pedido\n"
                "4️⃣ Cancelar pedido\n"
            )

            return cart_text

        elif message == "3":

            if not session["cart"]:
                return "No tienes productos en el carrito 🛒"

            total_precio, total_peso, tipo_cliente = calculate_order_summary(session["cart"])

            order_id = save_order_header(
                session["phone"],
                session["name"],
                tipo_cliente,
                total_precio,
                total_peso,
                session["sede"]   
            )

            save_order_detail(order_id, session["cart"], session["sede"])

            # 🔹 Mensaje logístico según tipo
            if tipo_cliente == "minorista":
                mensaje_logistica = f"""
                    🛍 Pedido minorista

                    📍 Tu pedido debe recogerse en la sede {session["sede"]}.
                    ✨ Gracias por confiar en nosotros.
                    Un asesor revisará tu pedido y se comunicará contigo.
                    """
            else:
                mensaje_logistica = f"""
                    📦 Pedido mayorista

                    📍 Pedido realizado desde: {session['sede']}

                    Un asesor humano gestionará:
                    ✔ Confirmación de inventario
                    ✔ Condiciones comerciales
                    ✔ Entrega o despacho

                    ✨ Gracias por confiar en nosotros.
                    Te contactaremos pronto 🤝
                    """

            session["cart"] = []
            session["state"] = "MENU"

            return f"""
            📦 PEDIDO REGISTRADO

            🧾 Orden: {order_id}
            👤 Cliente: {session["name"]}
            📱 Teléfono: {session["phone"]}
            🏷 Tipo: {tipo_cliente}
            🏢 Sede: {session["sede"]}

            ⚖️ Peso total estimado: {total_peso:.2f} kg
            💰 Total estimado: ${total_precio:,.0f}

            ⚠️ El valor final puede variar según peso exacto al despacho.

            {mensaje_logistica}

            """ + main_menu(session["name"], session["sede"])

        elif message == "4":
            session["cart"] = []
            session["state"] = "MENU"
            return "Pedido cancelado ❌\n" + main_menu(session["name"], session["sede"])

        else:
            return "Opción inválida"