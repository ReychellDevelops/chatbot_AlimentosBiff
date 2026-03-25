# diagnostic.py
from flow import handle_message

def test_simple():
    print("=== TEST SIMPLE ===\n")
    
    session = {"cart": [], "state": "START"}
    print(f"Inicial: {session}")
    
    # Paso 1: Enviar nombre
    response = handle_message(session, "Carlos")
    print(f"Despues de 'Carlos':")
    print(f"Estado: {session.get('state')}")
    print(f"Nombre: {session.get('name')}")
    print(f"Respuesta: {response[:100]}...\n")
    
    # Paso 2: Enviar sede
    response = handle_message(session, "1")
    print(f"Despues de '1':")
    print(f"Estado: {session.get('state')}")
    print(f"Sede: {session.get('sede')}")
    print(f"Respuesta: {response[:100]}...\n")
    
    # Paso 3: Enviar pedido
    response = handle_message(session, "3")
    print(f"Despues de '3':")
    print(f"Estado: {session.get('state')}")
    print(f"Respuesta: {response[:100]}...\n")

if __name__ == "__main__":
    test_simple()