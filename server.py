from flask import Flask, request, Response
from flow import handle_message

app = Flask(__name__)

sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():

    phone = request.form.get("From")
    message = request.form.get("Body")

    # 🔒 Validación de seguridad
    if not phone or not message:
    return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>""", mimetype="text/xml")

    if phone not in sessions:
        sessions[phone] = {
            "state": "START",
            "cart": [],
            "phone": phone
        }
        return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
👋 Bienvenido a BIFF

Para comenzar, ¿cuál es tu nombre?
    </Message>
</Response>""", mimetype="text/xml")

    reply = handle_message(sessions[phone], message)

    if not reply:
        reply = "Ocurrió un error interno."

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""

    return Response(twiml, mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)