from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, Response
from flow import handle_message
from twilio.twiml.messaging_response import MessagingResponse
import traceback
import os

app = Flask(__name__)

sessions = {}

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint de verificación de salud para Render"""
    return "OK - Bot funcionando", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        phone = request.form.get("From")
        message = (
            request.form.get("ButtonReplyId")
            or request.form.get("ListRowId")
            or request.form.get("Body")
        )

        # Logging para depuración (puedes comentarlo en producción)
        print(f"📱 Phone: {phone}")
        print(f"💬 Message: {message}")

        # Validación básica
        if not phone:
            print("⚠️ No se recibió el número de teléfono.")
            resp = MessagingResponse()
            return Response(str(resp), mimetype="application/xml")
        if not message:
            print("⚠️ Mensaje vacío recibido.")
            # No responder nada para no crear un bucle
            resp = MessagingResponse()
            return Response(str(resp), mimetype="application/xml")

        # Nuevo usuario
        if phone not in sessions:
            sessions[phone] = {
                "state": "START",
                "cart": [],
                "phone": phone  # Guardamos el número en la sesión
            }
            resp = MessagingResponse()
            resp.message("👋 *Bienvenido a BIFF*\n\nPara comenzar, ¿cuál es tu nombre?")
            return Response(str(resp), mimetype="application/xml")

        # Usuario existente
        session = sessions[phone]
        print(f"🧠 Estado previo: {session.get('state')}")

        # Llamar al cerebro del bot
        reply = handle_message(session, message)

        # Si la respuesta es None o vacía, usar un mensaje de error
        if not reply:
            reply = "⚠️ *Ocurrió un error.* Por favor, intenta nuevamente."
            print("⚠️ handle_message devolvió una respuesta vacía.")

        print(f"🤖 Respuesta: {reply[:100]}...") # Muestra los primeros 100 caracteres
        print(f"🧠 Nuevo estado: {session.get('state')}")
        print("-" * 50)

        # --- Manejo de respuestas interactivas (listas/botones) ---
        # (Mantenemos la lógica por si en el futuro Twilio las soporta mejor)
        if isinstance(reply, dict) and reply.get("type") == "list":
            # ... (código para listas, igual que antes) ...
            rows_xml = ""
            for r in reply["rows"]:
                rows_xml += f"<Row><Id>{r['id']}</Id><Title>{r['title']}</Title></Row>"
            twiml = f"""
            <Response>
            <Message>
            <Interactive>
            <Type>list</Type>
            <Body><![CDATA[{reply['body']}]]></Body>
            <Action><Button>{reply['button']}</Button><Sections><Section><Title>Opciones</Title><Rows>{rows_xml}</Rows></Section></Sections></Action>
            </Interactive>
            </Message>
            </Response>
            """
            return Response(twiml, mimetype="application/xml")

        if isinstance(reply, dict) and reply.get("type") == "buttons":
            # ... (código para botones, igual que antes) ...
            buttons_xml = ""
            for b in reply["buttons"]:
                buttons_xml += f"<Button><Reply><Id>{b['id']}</Id><Title>{b['title']}</Title></Reply></Button>"
            twiml = f"""
            <Response>
            <Message>
            <Interactive>
            <Type>button</Type>
            <Body><![CDATA[{reply['body']}]]></Body>
            <Action><Buttons>{buttons_xml}</Buttons></Action>
            </Interactive>
            </Message>
            </Response>
            """
            return Response(twiml, mimetype="application/xml")

        # --- Respuesta de texto simple ---
        resp = MessagingResponse()
        resp.message(reply)
        return Response(str(resp), mimetype="application/xml")

    except Exception as e:
        # Captura cualquier error inesperado para no romper el webhook
        print("🔥 ERROR CRÍTICO:")
        traceback.print_exc()
        resp = MessagingResponse()
        resp.message("⚠️ *Ocurrió un error inesperado.* Por favor, intenta de nuevo más tarde.")
        return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    # Obtener el puerto de la variable de entorno PORT (Render la asigna)
    # Si no existe, usar 5000 para desarrollo local
    port = int(os.environ.get("PORT", 5000))
    
    # En producción con gunicorn, no se ejecuta este bloque
    # pero lo dejamos para pruebas locales
    app.run(host="0.0.0.0", port=port, debug=True)