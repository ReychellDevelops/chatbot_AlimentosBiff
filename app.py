from flow import handle_message
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# simulamos sesiones (luego lo mejoras)
sessions = {}

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():

    incoming_msg = request.values.get("Body", "").strip()
    phone = request.values.get("From", "")

    if phone not in sessions:
        sessions[phone] = {}

    session = sessions[phone]

    # 🔥 AQUÍ USAS TU CEREBRO
    response = handle_message(session, incoming_msg)

    resp = MessagingResponse()

    # manejar distintos tipos
    if isinstance(response, dict):

        if response["type"] == "list":
            # Twilio sandbox no soporta listas reales → fallback a texto
            text = response["body"] + "\n\n"
            for row in response["rows"]:
                text += f"- {row['title']}\n"
            resp.message(text)

        elif response["type"] == "buttons":
            text = response["body"] + "\n\n"
            for btn in response["buttons"]:
                text += f"- {btn['title']}\n"
            resp.message(text)

    else:
        resp.message(response)

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)