# almacena las sesiones de los usuarios, inicialmente se comienza con sesion='ASK_NAME'

sessions = {} #diccionario que alamacena los usuarios y su estado actual en la conversacion

def get_session(phone):

    if phone not in sessions:
        sessions[phone] = {
            'phone': phone,
            'state': 'ASK_NAME',
            'name': None,
            'cart': [],
            'client_type': None
        }

    return sessions[phone]