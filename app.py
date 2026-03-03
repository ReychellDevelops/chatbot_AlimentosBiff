from session_manager import get_session
from flow import handle_message
from responses import ask_name

print("Chat iniciado (escribe 0 para terminar)\n")

phone = None
session = None
waiting_phone = True

while True:
    user = input("Tú: ").strip()

    # Primera interacción: pedir teléfono
    if waiting_phone:
        print("Bot: 👋 Bienvenido a Alimentos Biff.")
        print("Bot: Por favor ingresa tu número de teléfono:")

        phone_input = input("Número: ").strip()

        if not phone_input.isdigit() or len(phone_input) < 10:
            print("Bot: ❌ Número inválido. Debe tener al menos 10 dígitos y solo números.\n")
            continue

        phone = phone_input
        session = get_session(phone)

        print("Bot:", ask_name())

        waiting_phone = False
        continue

    # Flujo normal después de validar teléfono
    reply = handle_message(session, user)

    if reply == "EXIT":
        print("Bot: Gracias por escribir a Alimentos Biff 🥩 ¡Hasta pronto!")
        break

    print("Bot:", reply)