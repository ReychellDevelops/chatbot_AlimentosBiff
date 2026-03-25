# respuestas del bot generales

def ask_name():
    return '👋 ¡Hola! Bienvenido a Alimentos Biff 🥩\n¿Me indicas tu nombre?'

def main_menu(name, sede):
    # Usamos triple comillas para respetar el formato
    return f"""
🏠 *Menú Principal* 🏠
📍 *Sede actual:* {sede}

👤 *Hola {name}*, ¿qué deseas hacer?

1️⃣ Ver ofertas del día
2️⃣ Ver catálogo
3️⃣ Realizar pedido
4️⃣ Ver carrito
5️⃣ Hablar con asesor
6️⃣ Cambiar sede
0️⃣ Salir
"""

def invalid_option():
    return "❌ *Opción no válida.* Por favor, selecciona una opción del menú usando los números."