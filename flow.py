# reglas de conversación - CEREBRO
from responses import ask_name, main_menu, invalid_option
from product_service import (
    get_categories,
    get_products_by_category_and_sede,
    get_products_by_category_origin_and_sede
)
from sheets_service import save_order_header, save_order_detail, get_offers

def build_catalog_list(products, sede, categoria):
    """Construye la lista de productos para el catálogo."""
    if not products:
        return f"❌ No hay productos disponibles en la categoría *{categoria}* para {sede}."

    text = f"""
📋 *Catálogo* 📋
📍 *Sede:* {sede}
🗂️ *Categoría:* {categoria}

"""
    for i, p in enumerate(products, 1):
        peso_promedio = (p["peso_min_kg"] + p["peso_max_kg"]) / 2
        text += f"""
{i}. *{p["nombre"]}* ({p["referencia"]})
   🌎 {p["origen"]} | 📦 {p["tipo_unidad"]}
   ⚖️ Peso aprox. por {p["tipo_unidad"]}: {peso_promedio:.2f} kg
   💰 ${p["precio_kg"]:,.0f}/kg
---
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
    """Construye la lista de productos para el pedido."""
    text = f"📍 *Sede:* {sede}\n\n"
    text += "🔢 *Selecciona el producto:*\n\n"

    for i, product in enumerate(products, 1):
        text += f"{i}. {product['nombre']} ({product['referencia']})\n"

    text += "\n0. Volver al menú anterior"
    return text

def calculate_order_summary(cart):
    """Calcula el total y tipo de cliente."""
    total_precio = 0
    total_peso = 0

    for item in cart:
        total_precio += item["precio_aprox"]
        total_peso += item["peso_aprox_total"]

    tipo_cliente = "mayorista" if total_peso >= 50 else "minorista"
    return total_precio, total_peso, tipo_cliente

def handle_message(session, message):
    """Función principal que maneja el flujo de conversación."""

    # Inicializar valores por defecto de forma segura
    session.setdefault("cart", [])
    session.setdefault("state", "START")

    state = session.get('state')
    
    print(f"DEBUG - Estado actual: {state}")  # Línea de depuración temporal
    print(f"DEBUG - Mensaje: {message}")      # Línea de depuración temporal

    # ---------------- COMANDO ESPECIAL: VACIAR CARRITO ----------------
    if message == "clear_cart":
        session["cart"] = []
        session["state"] = "MENU"
        return "🗑️ *Carrito vaciado* con éxito.\n\n" + main_menu(
            session.get("name", "Usuario"),
            session.get("sede", "Sin sede")
        )

    # ---------------- INICIO ----------------
    if state == "START":
        print("DEBUG - Entrando a START")
        session["state"] = "ASK_NAME"
        return "👋 *Bienvenido a BIFF*\n\nPara comenzar, ¿cuál es tu nombre?"

    # ---------------- PEDIR NOMBRE ----------------
    if state == 'ASK_NAME':
        print("DEBUG - Entrando a ASK_NAME")
        name = message.strip()
        if len(name) < 2 or any(char.isdigit() for char in name):
            return "❌ *Nombre inválido.*\nPor favor, ingresa solo letras y al menos 2 caracteres."

        session['name'] = name
        session['state'] = 'ASK_SEDE'
        print(f"DEBUG - Nombre guardado: {name}, nuevo estado: ASK_SEDE")
        return """
📍 *Selecciona tu sede:* 📍

1️⃣ Duitama (Minorista)
2️⃣ Sogamoso (Minorista y bodega)
3️⃣ Bogotá (Bodega mayorista)
"""
    # ---------------- PEDIR SEDE ----------------
    if state == "ASK_SEDE":
        sedes = {"1": "Duitama", "2": "Sogamoso", "3": "Bogotá"}
        if message not in sedes:
            return "❌ Opción inválida. Selecciona 1, 2 o 3."

        session["sede"] = sedes[message]
        session["state"] = "MENU"
        return f"✅ *Sede seleccionada:* {session['sede']}\n\n" + main_menu(
            session.get("name", "Usuario"),
            session.get("sede", "Sin sede")
        )

    # ---------------- MENÚ PRINCIPAL ----------------
    if state == "MENU":
        # Opción 1: Ofertas
        if message == "1":
            ofertas = get_offers(session["sede"])
            if not ofertas:
                return "📢 *No hay ofertas activas* en este momento.\n\n" + main_menu(
                    session.get("name", "Usuario"),
                    session.get("sede", "Sin sede")
                )

            text = "🔥 *OFERTAS DEL DÍA* 🔥\n" + f"📍 *Sede:* {session['sede']}\n\n"
            for i, o in enumerate(ofertas, 1):
                text += f"""
{i}. *{o['nombre']}* ({o['referencia']})
   🌎 {o['origen']} | 📦 {o['tipo_unidad']}
   🏷️ Antes: ~~${o['precio_normal_kg']:,.0f}/kg~~
   💰 *Ahora: ${o['precio_oferta_kg']:,.0f}/kg*
   📝 {o['descripcion']}
---
"""
            text += "\n0️⃣ Volver al menú principal"
            session["state"] = "OFFERS_VIEW"
            return text

        # Opción 2: Ver Catálogo
        elif message == "2":
            categories = get_categories()
            session["categories"] = categories
            session["state"] = "CATALOG_CATEGORY"

            text = f"📍 *Catálogo* 📍\n🏢 *Sede:* {session['sede']}\n\n"
            text += "🗂️ *Selecciona una categoría:*\n\n"
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"
            text += "\n0. Volver al menú principal"
            return text

        # Opción 3: Realizar Pedido
        elif message == "3":
            categories = get_categories()
            session["categories"] = categories
            session["state"] = "ORDER_CATEGORY"

            text = f"🛒 *Nuevo Pedido* 🛒\n📍 *Sede:* {session['sede']}\n\n"
            text += "🗂️ *Selecciona la categoría:*\n\n"
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"
            text += "\n0. Volver al menú principal"
            return text

        # Opción 4: Ver Carrito
        elif message == "4":
            if not session.get("cart"):
                return "🛒 *Tu carrito está vacío.*\n\n" + main_menu(
                    session.get("name", "Usuario"),
                    session.get("sede", "Sin sede")
                )
            session["state"] = "ORDER_MENU"
            # Mostrar carrito directamente, pero el menú de opciones está en ORDER_MENU
            return build_cart_response(session["cart"])

        # Opción 5: Hablar con asesor
        elif message == "5":
            return "📞 *Un asesor te contactará pronto.* Por favor, espera un momento."

        # Opción 6: Cambiar sede
        elif message == "6":
            session["state"] = "ASK_SEDE"
            return """
📍 *Cambiar sede* 📍
Selecciona la nueva sede:

1️⃣ Duitama
2️⃣ Sogamoso
3️⃣ Bogotá
"""

        # Opción 0: Salir
        elif message == "0":
            return "👋 *¡Gracias por usar BIFF!* Hasta pronto."

        else:
            return invalid_option() + "\n\n" + main_menu(
                session.get("name", "Usuario"),
                session.get("sede", "Sin sede")
            )

    # ---------------- ESTADO: OFERTAS ----------------
    if state == "OFFERS_VIEW":
        if message == "0":
            session["state"] = "MENU"
            return main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))
        else:
            return "🔢 Para volver al menú, envía *0*. No es posible comprar ofertas directamente desde aquí."

    # ---------------- ESTADO: SELECCIÓN CATEGORÍA PARA CATÁLOGO ----------------
    if state == "CATALOG_CATEGORY":
        categories = session.get("categories", [])
        if message == "0":
            session["state"] = "MENU"
            return main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))

        try:
            index = int(message) - 1
            if index < 0 or index >= len(categories):
                raise IndexError
            categoria = categories[index]
        except (ValueError, IndexError):
            return "❌ *Opción inválida.* Por favor, selecciona un número de la lista.\n\n" + \
                   f"🗂️ *Categorías:*\n" + "\n".join([f"{i+1}. {c.capitalize()}" for i, c in enumerate(categories)]) + "\n\n0. Volver"

        products = get_products_by_category_and_sede(categoria, session.get("sede"))
        if not products:
            return f"❌ No hay productos disponibles en la categoría *{categoria.capitalize()}* para {session['sede']}."

        session["catalog_products"] = products
        session["catalog_category"] = categoria
        session["state"] = "CATALOG_VIEW"

        return build_catalog_list(products, session.get("sede"), categoria)

    # ---------------- ESTADO: VISTA DE CATÁLOGO ----------------
    if state == "CATALOG_VIEW":
        if message == "1":  # Realizar un pedido
            # Redirigir al flujo de pedido, pero manteniendo el contexto de la categoría? O empezar de nuevo.
            # Por simplicidad, empezamos el flujo de pedido desde el inicio.
            session["state"] = "ORDER_CATEGORY"
            categories = get_categories()
            text = f"🛒 *Realizar Pedido* 🛒\n📍 *Sede:* {session['sede']}\n\n"
            text += "🗂️ *Selecciona la categoría:*\n\n"
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"
            text += "\n0. Volver al menú principal"
            return text

        elif message == "2":  # Ver otra categoría
            session["state"] = "CATALOG_CATEGORY"
            categories = session.get("categories", [])
            text = f"📍 *Catálogo* 📍\n🏢 *Sede:* {session['sede']}\n\n"
            text += "🗂️ *Selecciona una categoría:*\n\n"
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"
            text += "\n0. Volver al menú principal"
            return text

        elif message == "3":  # Cambiar sede
            session["state"] = "ASK_SEDE"
            return """
📍 *Cambiar sede* 📍
Selecciona la nueva sede:

1️⃣ Duitama
2️⃣ Sogamoso
3️⃣ Bogotá
"""

        elif message == "0":  # Volver al menú principal
            session["state"] = "MENU"
            return main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))

        else:
            return "❌ *Opción inválida.*\n\n" + build_catalog_list(
                session.get("catalog_products", []),
                session.get("sede"),
                session.get("catalog_category", "esta categoría")
            )

    # ---------------- ESTADO: SELECCIÓN CATEGORÍA PARA PEDIDO ----------------
    if state == "ORDER_CATEGORY":
        if message == "0":
            session["state"] = "MENU"
            return main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))

        categorias_map = {
            "1": "Carne de res",
            "2": "Carne de cerdo",
            "3": "Visceras y madejas"
        }
        # Usar el mapa de categorías fijas o el de la lista dinámica.
        # Por simplicidad y consistencia con tu código actual, usamos el mapa fijo.
        if message not in categorias_map:
            return "❌ *Opción inválida.*\n\nSelecciona una categoría:\n1️⃣ Carne de res\n2️⃣ Carne de cerdo\n3️⃣ Visceras y madejas\n\n0️⃣ Volver al menú"

        categoria = categorias_map[message]
        session["selected_category"] = categoria
        session["state"] = "ORDER_ORIGIN"
        return f"🗂️ *Categoría seleccionada:* {categoria}\n\n🌎 *Selecciona el origen:*\n\n1️⃣ Nacional\n2️⃣ Importada"

    # ---------------- ESTADO: SELECCIÓN ORIGEN ----------------
    if state == "ORDER_ORIGIN":
        if message == "1":
            origen = "Nacional-Colombia"
        elif message == "2":
            origen = "Importada"
        else:
            return "❌ *Opción inválida.*\n\n🌎 Selecciona el origen:\n1️⃣ Nacional\n2️⃣ Importada"

        session["selected_origin"] = origen
        productos = get_products_by_category_origin_and_sede(
            session.get("selected_category"),
            origen,
            session.get("sede")
        )

        if not productos:
            return f"❌ *No hay productos disponibles* para la categoría '{session.get('selected_category')}' con origen '{origen}' en {session['sede']}.\n\nPor favor, selecciona otro origen:\n\n1️⃣ Nacional\n2️⃣ Importada\n\n0️⃣ Volver a categorías"

        session["product_list"] = productos
        session["state"] = "ORDER_PRODUCT"

        lista = "\n".join([f"{i}. {p['nombre']} ({p['referencia']})" for i, p in enumerate(productos, 1)])
        return f"📍 *Sede:* {session['sede']}\n🥩 *Productos disponibles* (origen: {origen}):\n\n{lista}\n\n0️⃣ Volver a categorías"

    # ---------------- ESTADO: SELECCIÓN PRODUCTO ----------------
    if state == "ORDER_PRODUCT":
        products = session.get("product_list", [])
        if message == "0":
            session["state"] = "ORDER_CATEGORY"
            categories = get_categories()
            text = f"🛒 *Realizar Pedido* 🛒\n📍 *Sede:* {session['sede']}\n\n"
            text += "🗂️ *Selecciona la categoría:*\n\n"
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"
            text += "\n0. Volver al menú principal"
            return text

        try:
            index = int(message) - 1
            if index < 0 or index >= len(products):
                raise IndexError
            product = products[index]
        except (ValueError, IndexError):
            return f"❌ *Selecciona un número válido* (1 a {len(products)}).\n\n" + \
                   "\n".join([f"{i+1}. {p['nombre']} ({p['referencia']})" for i, p in enumerate(products)]) + \
                   "\n\n0️⃣ Volver"

        session["current_product"] = product
        session["state"] = "ORDER_QUANTITY"

        peso_promedio = (product["peso_min_kg"] + product["peso_max_kg"]) / 2
        return f"⚙️ *Cantidad*\n\n¿Cuántas *{product['tipo_unidad']}(s)* de *{product['nombre']}* deseas?\n\n⚖️ Peso aprox. por {product['tipo_unidad']}: {peso_promedio:.2f} kg\n💰 Precio: ${product['precio_kg']:,.0f}/kg\n\n*Envía solo el número (ej: 2)*"

    # ---------------- ESTADO: CANTIDAD ----------------
    if state == "ORDER_QUANTITY":
        try:
            units = int(message)
            if units <= 0:
                return "❌ *La cantidad debe ser mayor a 0.* Por favor, ingresa un número válido."
            if units > 100:
                return "❌ *Cantidad máxima permitida es 100.* Por favor, ingresa un número menor."
        except ValueError:
            return "❌ *Entrada inválida.* Debes ingresar un número (ej: 2)."

        product = session.get("current_product")
        if not product:
            session["state"] = "MENU"
            return "⚠️ *Error:* No se pudo recuperar el producto. Volviendo al menú principal.\n\n" + main_menu(
                session.get("name", "Usuario"),
                session.get("sede", "Sin sede")
            )

        peso_promedio_unitario = (product["peso_min_kg"] + product["peso_max_kg"]) / 2
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

        item = session["cart"][-1]
        return f"✅ *Producto agregado al carrito*\n\n📦 *{item['units']}* {item['tipo_unidad']}(s) de *{item['product']}*\n🔖 Ref: {item['referencia']}\n💰 Subtotal aprox: ${item['precio_aprox']:,.0f}\n\n" + \
               build_order_menu(session["cart"])

    # ---------------- ESTADO: MENÚ DEL PEDIDO ----------------
    if state == "ORDER_MENU":
        cart = session.get("cart", [])
        
        # Opción 1: Agregar otro producto
        if message == "1":
            session["state"] = "ORDER_CATEGORY"
            categories = get_categories()
            text = f"🛒 *Agregar otro producto* 🛒\n📍 *Sede:* {session['sede']}\n\n"
            text += "🗂️ *Selecciona la categoría:*\n\n"
            for i, c in enumerate(categories, 1):
                text += f"{i}. {c.capitalize()}\n"
            text += "\n0. Volver al menú del pedido"
            return text
        
        # Opción 2: Ver carrito y opciones (eliminar productos o confirmar pedido)
        elif message == "2":
            if not cart:
                return f"🛒 *Tu carrito está vacío.*\n\n{ build_order_menu(cart) }"
            
            # Ir al estado REMOVE_ITEM para mostrar carrito
            session["state"] = "REMOVE_ITEM"
            # Limpiar cualquier flag previo
            session.pop("awaiting_remove_selection", None)
            
            # Mostrar carrito directamente - NO usar return None
            # Construir el mensaje del carrito manualmente
            text = "🛒 *TU CARRITO* 🛒\n\n"
            total = 0
            for i, item in enumerate(cart, 1):
                text += f"{i}. *{item['product']}*\n"
                text += f"   📦 {item['units']} {item['tipo_unidad']}(s)\n"
                text += f"   ⚖️ {item['peso_aprox_total']:.2f} kg\n"
                text += f"   💰 ${item['precio_aprox']:,.0f}\n\n"
                total += item["precio_aprox"]
            
            text += f"💰 *Total:* ${total:,.0f}\n\n"
            text += "🔢 *¿Qué deseas hacer?*\n"
            text += "1️⃣ Eliminar producto\n"
            text += "2️⃣ Volver al menú del pedido\n\n"
            text += "💡 *Para eliminar, selecciona la opción 1*"
            
            return text
        
        # Opción 3: Confirmar pedido
        elif message == "3":
            if not cart:
                return f"🛒 *No tienes productos en el carrito.*\n\n{ build_order_menu(cart) }"
            
            total_precio, total_peso, tipo_cliente = calculate_order_summary(cart)
            
            # Mostrar resumen detallado del pedido
            resumen = "📋 *RESUMEN DE TU PEDIDO* 📋\n\n"
            resumen += "━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for i, item in enumerate(cart, 1):
                resumen += f"\n{i}. *{item['product']}*\n"
                resumen += f"   📦 Cantidad: {item['units']} {item['tipo_unidad']}(s)\n"
                resumen += f"   ⚖️ Peso aproximado: {item['peso_aprox_total']:.2f} kg\n"
                resumen += f"   💰 Subtotal: ${item['precio_aprox']:,.0f}\n"
            
            resumen += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            resumen += f"⚖️ *Peso total del pedido:* {total_peso:.2f} kg\n"
            resumen += f"💰 *Total a pagar:* ${total_precio:,.0f}\n"
            resumen += f"🏷️ *Tipo de cliente:* {tipo_cliente.capitalize()}\n"
            resumen += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            resumen += "✅ *¿Confirmar este pedido?*\n"
            resumen += "Envía *SI* para confirmar o *NO* para cancelar"
            
            session["pending_order"] = {
                "total_precio": total_precio,
                "total_peso": total_peso,
                "tipo_cliente": tipo_cliente,
                "cart": cart.copy()  # Guardamos copia del carrito para mostrar después
            }
            session["state"] = "CONFIRM_ORDER"
            
            return resumen
        
        # Opción 4: Volver al menú principal
        elif message == "4":
            session["state"] = "MENU"
            return main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))
        
        # Opción 0: Volver al menú principal (alternativa)
        elif message == "0":
            session["state"] = "MENU"
            return main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))
        
        else:
            return f"❌ *Opción inválida.*\n\n{ build_order_menu(cart) }"

    # ---------------- ESTADO: ELIMINAR PRODUCTO ----------------
        # ---------------- ESTADO: ELIMINAR PRODUCTO ----------------
    if state == "REMOVE_ITEM":
        cart = session.get("cart", [])
        
        if not cart:
            session["state"] = "ORDER_MENU"
            return f"🛒 *Tu carrito ya está vacío.*\n\n{ build_order_menu(cart) }"
        
        # Si estamos en modo selección (esperando qué producto eliminar)
        if session.get("awaiting_remove_selection"):
            # Opción 0: Volver al menú del pedido
            if message == "0":
                session.pop("awaiting_remove_selection", None)
                session["state"] = "ORDER_MENU"
                return build_order_menu(cart)
            
            # Validar que sea un número
            if not message.isdigit():
                text = "🗑️ *ELIMINAR PRODUCTO* 🗑️\n\n"
                text += "Selecciona el número del producto que deseas eliminar:\n\n"
                for i, item in enumerate(cart, 1):
                    text += f"{i}. *{item['product']}* - {item['units']} {item['tipo_unidad']}(s) - ${item['precio_aprox']:,.0f}\n"
                total = sum(item["precio_aprox"] for item in cart)
                text += f"\n💰 *Total actual:* ${total:,.0f}\n"
                text += "\n0️⃣ Volver al menú del pedido"
                return text
            
            index = int(message) - 1
            
            if index < 0 or index >= len(cart):
                text = f"❌ *Número inválido.* Selecciona un número entre 1 y {len(cart)}.\n\n"
                text += "🗑️ *ELIMINAR PRODUCTO* 🗑️\n\n"
                text += "Selecciona el número del producto que deseas eliminar:\n\n"
                for i, item in enumerate(cart, 1):
                    text += f"{i}. *{item['product']}* - {item['units']} {item['tipo_unidad']}(s) - ${item['precio_aprox']:,.0f}\n"
                total = sum(item["precio_aprox"] for item in cart)
                text += f"\n💰 *Total actual:* ${total:,.0f}\n"
                text += "\n0️⃣ Volver al menú del pedido"
                return text
            
            # Eliminar el producto seleccionado
            removed = cart.pop(index)
            session.pop("awaiting_remove_selection", None)
            session["state"] = "ORDER_MENU"
            
            if not cart:
                return f"✅ *{removed['product']}* eliminado correctamente.\n\n🛒 *Tu carrito está vacío.*\n\n{ build_order_menu(cart) }"
            else:
                return f"✅ *{removed['product']}* eliminado correctamente.\n\n{ build_order_menu(cart) }"
        
        # Si NO estamos en modo selección, mostrar el carrito con opciones
        else:
            # Opción 1: Activar modo selección
            if message == "1":
                session["awaiting_remove_selection"] = True
                text = "🗑️ *ELIMINAR PRODUCTO* 🗑️\n\n"
                text += "Selecciona el número del producto que deseas eliminar:\n\n"
                for i, item in enumerate(cart, 1):
                    text += f"{i}. *{item['product']}* - {item['units']} {item['tipo_unidad']}(s) - ${item['precio_aprox']:,.0f}\n"
                total = sum(item["precio_aprox"] for item in cart)
                text += f"\n💰 *Total actual:* ${total:,.0f}\n"
                text += "\n0️⃣ Volver al menú del pedido"
                return text
            
            # Opción 2: Volver al menú del pedido
            if message == "2":
                session["state"] = "ORDER_MENU"
                return build_order_menu(cart)
            
            # Si no es opción válida, mostrar el carrito nuevamente
            text = "🛒 *TU CARRITO* 🛒\n\n"
            total = 0
            for i, item in enumerate(cart, 1):
                text += f"{i}. *{item['product']}*\n"
                text += f"   📦 {item['units']} {item['tipo_unidad']}(s)\n"
                text += f"   ⚖️ {item['peso_aprox_total']:.2f} kg\n"
                text += f"   💰 ${item['precio_aprox']:,.0f}\n\n"
                total += item["precio_aprox"]
            
            text += f"💰 *Total:* ${total:,.0f}\n\n"
            text += "🔢 *¿Qué deseas hacer?*\n"
            text += "1️⃣ Eliminar producto\n"
            text += "2️⃣ Volver al menú del pedido\n\n"
            text += "💡 *Para eliminar, selecciona la opción 1*"
            
            return text
    
    # ---------------- ESTADO: CONFIRMAR PEDIDO ----------------
    if state == "CONFIRM_ORDER":
        if message.lower() == "si":
            # Confirmar pedido
            pending = session.get("pending_order", {})
            total_precio = pending.get("total_precio", 0)
            total_peso = pending.get("total_peso", 0)
            tipo_cliente = pending.get("tipo_cliente", "minorista")
            cart_copy = pending.get("cart", [])
            
            phone = session.get("phone", "sin_numero")
            
            # Guardar en Google Sheets (o mock)
            order_id = save_order_header(
                phone,
                session["name"],
                tipo_cliente,
                total_precio,
                total_peso,
                session["sede"]
            )
            save_order_detail(order_id, session["cart"], session["sede"])
            
            # Construir mensaje de confirmación con el listado
            confirmacion = f"""
    🎉 *¡PEDIDO CONFIRMADO!* 🎉

    📋 *Detalle de tu pedido #{order_id}:*
    ━━━━━━━━━━━━━━━━━━━━━━
    """
            for i, item in enumerate(cart_copy, 1):
                confirmacion += f"""
    {i}. *{item['product']}*
    📦 {item['units']} {item['tipo_unidad']}(s)
    ⚖️ {item['peso_aprox_total']:.2f} kg
    💰 ${item['precio_aprox']:,.0f}
    """
            
            confirmacion += f"""
    ━━━━━━━━━━━━━━━━━━━━━━
    ⚖️ *Peso total:* {total_peso:.2f} kg
    💰 *Total:* ${total_precio:,.0f}
    🏷️ *Tipo:* {tipo_cliente.capitalize()}
    ━━━━━━━━━━━━━━━━━━━━━━

    📞 Un asesor se pondrá en contacto para coordinar la entrega.

    {main_menu(session.get("name", "Usuario"), session.get("sede", "Sin sede"))}
    """
            
            # Limpiar carrito y estado
            session["cart"] = []
            session.pop("pending_order", None)
            session["state"] = "MENU"
            
            return confirmacion
        
        elif message.lower() == "no":
            # Cancelar pedido
            session.pop("pending_order", None)
            session["state"] = "ORDER_MENU"
            return f"❌ *Pedido cancelado.* Puedes seguir agregando productos al carrito.\n\n{build_order_menu(session['cart'])}"
        
        else:
            return "❌ *Opción no válida.* Responde *SI* para confirmar el pedido o *NO* para cancelarlo."

def build_cart_response(cart):
    """Construye la respuesta visual del carrito (solo visualización)."""
    if not cart:
        return "🛒 *Tu carrito está vacío.*\n\n"
    
    text = "🛒 *TU CARRITO* 🛒\n\n"
    total = 0
    peso_total = 0
    
    for i, item in enumerate(cart, 1):
        peso_total += item["peso_aprox_total"]
        total += item["precio_aprox"]
        
        text += f"""
{i}. *{item['product']}*
   📦 Cantidad: {item['units']} {item['tipo_unidad']}(s)
   ⚖️ Peso aprox: {item['peso_aprox_total']:.2f} kg
   💰 Subtotal: ${item['precio_aprox']:,.0f}
"""
    
    text += f"""
━━━━━━━━━━━━━━━━━━━━━━
⚖️ *Peso total:* {peso_total:.2f} kg
💰 *Total:* ${total:,.0f}
"""
    
    return text

def build_order_menu(cart):
    """Construye el menú de opciones para el pedido con resumen."""
    if not cart:
        return """
🔢 *¿Qué deseas hacer?*

1️⃣ Agregar producto
2️⃣ Ver carrito (vacío)
3️⃣ Confirmar pedido
4️⃣ Volver al menú principal
"""
    else:
        total_precio = sum(item["precio_aprox"] for item in cart)
        total_peso = sum(item["peso_aprox_total"] for item in cart)
        
        return f"""
📊 *Resumen actual:*
⚖️ Peso total: {total_peso:.2f} kg
💰 Total: ${total_precio:,.0f}

🔢 *¿Qué deseas hacer?*

1️⃣ Agregar otro producto
2️⃣ Ver carrito detallado
3️⃣ Confirmar pedido
4️⃣ Volver al menú principal
"""
