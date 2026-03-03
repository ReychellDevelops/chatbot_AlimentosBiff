from flask import Flask, request
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

    return f"""
<Response>
    <Message>{reply}</Message>
</Response>
"""
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)