from flow import handle_message

# sesiones por usuario (igual que en Flask)
sessions = {}

current_user = None

print("Simulador multiusuario iniciado")
print("Comandos:")
print("/user <numero>  → cambiar de usuario")
print("/reset          → resetear usuario actual")
print("/exit           → salir\n")

while True:

    user_input = input(">>> ")

    # salir
    if user_input == "/exit":
        print("Simulación terminada.")
        break

    # cambiar usuario
    if user_input.startswith("/user"):
        try:
            phone = user_input.split(" ")[1]
            current_user = phone

            if phone not in sessions:
                sessions[phone] = {}

            print(f"👤 Usuario activo: {phone}\n")
        except:
            print("❌ Usa: /user 12345\n")
        continue

    # resetear sesión
    if user_input == "/reset":
        if current_user:
            sessions[current_user] = {}
            print("🔄 Sesión reiniciada\n")
        else:
            print("❌ No hay usuario activo\n")
        continue

    # validar usuario activo
    if not current_user:
        print("❌ Primero selecciona usuario con /user <numero>\n")
        continue

    # obtener sesión
    session = sessions[current_user]

    # enviar mensaje al bot
    response = handle_message(session, user_input)

    print("\n🤖 Bot:")

    if isinstance(response, dict):
        print(response.get("body", ""))

        if "rows" in response:
            for i, row in enumerate(response["rows"], 1):
                print(f"{i}. {row['title']}")

        if "buttons" in response:
            for i, btn in enumerate(response["buttons"], 1):
                print(f"{i}. {btn['title']}")
    else:
        print(response)

    # 🔍 DEBUG PRO
    print("\n🧠 Estado actual:")
    print(session)

    print("\n" + "="*50 + "\n")