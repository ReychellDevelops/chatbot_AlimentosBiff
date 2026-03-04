from flask import Flask, request, Response
from flow import handle_message

app = Flask(__name__)

sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    print("PHONE:", phone)
    print("MESSAGE:", message)
    return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
<Message>Bot activo correctamente ✅</Message>
</Response>""", mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)