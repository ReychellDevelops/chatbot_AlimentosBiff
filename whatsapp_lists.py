def create_list_message(body, button, rows):

    sections = [{
        "title": "Opciones",
        "rows": rows
    }]

    return {
        "type": "list",
        "body": {"text": body},
        "action": {
            "button": button,
            "sections": sections
        }
    }