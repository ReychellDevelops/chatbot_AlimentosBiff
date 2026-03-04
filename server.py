from flask import Flask, request, Response
from flow import handle_message
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():

    phone = request.form.get("From")
    message = request.form.get("Body")

    print("PHONE:", phone)
    print("MESSAGE:", message)

    # 🔒 Validación básica
    if not phone or not message:
        resp = MessagingResponse()
        return Response(str(resp), mimetype="application/xml")

    # 🆕 Usuario nuevo
    if phone not in sessions:
        sessions[phone] = {
            "state": "START",
            "cart": [],
            "phone": phone
        }

        resp = MessagingResponse()
        resp.message("👋 Bienvenido a BIFF\n\nPara comenzar, ¿cuál es tu nombre?")
        return Response(str(resp), mimetype="application/xml")

    # 🔁 Usuario existente
    reply = handle_message(sessions[phone], message)

    print("REPLY:", reply)

    if not reply:
        reply = "Ocurrió un error interno."

    resp = MessagingResponse()
    resp.message(reply)

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)