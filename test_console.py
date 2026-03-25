from flow import handle_message

# simulamos sesiones igual que en Flask
session = {}

print("Chat iniciado (escribe 'salir' para terminar)\n")

while True:
    user_input = input("Tú: ")

    if user_input.lower() == "salir":
        print("Chat finalizado.")
        break

    response = handle_message(session, user_input)

    print("\nBot:")

    if isinstance(response, dict):
        # convertir listas/botones a texto (igual que Twilio sandbox)
        print(response.get("body", ""))

        if "rows" in response:
            for i, row in enumerate(response["rows"], 1):
                print(f"{i}. {row['title']}")

        if "buttons" in response:
            for i, btn in enumerate(response["buttons"], 1):
                print(f"{i}. {btn['title']}")

    else:
        print(response)

    print("\n" + "-"*40 + "\n")