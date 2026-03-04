reply = handle_message(sessions[phone], message)

if not reply:
    reply = "Error: no response generated."

print("DEBUG REPLY:", reply)