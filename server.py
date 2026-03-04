from flask import Flask, request, Response
from flow import handle_message

app = Flask(__name__)

sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    phone = request.form.get("From")
    message = request.form.get("Body")

    if phone not in sessions:
        sessions[phone] = {
            "state": "START",
            "cart": []
        }

    reply = handle_message(sessions[phone], message)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""

    return Response(twiml, mimetype="text/xml")