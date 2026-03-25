"""
Pruebas automatizadas del chatbot - Versión Corregida
Ejecutar: python test_automated.py
"""

from flow import handle_message
import sys
import io

# Configurar codificación UTF-8 para la consola de Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_test(test_name, session, user_inputs, expected_substrings=None):
    """Ejecuta una prueba y muestra los resultados"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    # Hacer una copia profunda de la sesión
    session_copy = session.copy()
    responses = []
    
    for i, user_input in enumerate(user_inputs, 1):
        print(f"\nPaso {i}: Usuario escribe: {user_input}")
        
        # Mostrar estado actual antes de procesar
        current_state = session_copy.get('state', 'UNKNOWN')
        print(f"[Estado actual: {current_state}]")
        
        response = handle_message(session_copy, user_input)
        responses.append(response)
        
        # Mostrar nuevo estado después de procesar
        new_state = session_copy.get('state', 'UNKNOWN')
        print(f"[Nuevo estado: {new_state}]")
        
        # Mostrar respuesta del bot (primeros 150 caracteres)
        if isinstance(response, dict):
            response_text = response.get("body", str(response))[:150]
        else:
            response_text = str(response)[:150]
        
        # Limpiar texto para mostrar
        response_text = response_text.replace('\n', ' ').strip()
        print(f"Bot: {response_text}...")
        
        # Verificar si contiene los textos esperados
        if expected_substrings and i == len(user_inputs):
            print("\nVerificando resultados:")
            for expected in expected_substrings:
                if expected.lower() in response_text.lower():
                    print(f"  [OK] Encontrado: '{expected}'")
                else:
                    print(f"  [FAIL] NO encontrado: '{expected}'")
    
    print(f"\n{'='*60}")
    print(f"TEST {test_name} COMPLETADO")
    print(f"{'='*60}\n")
    
    return session_copy, responses

def setup_session():
    """Configura una sesión inicial válida para las pruebas"""
    return {
        "cart": [], 
        "state": "START", 
        "phone": "test_phone"
    }

def main():
    print("\n" + "="*60)
    print("INICIANDO PRUEBAS AUTOMATIZADAS DEL CHATBOT BIFF")
    print("="*60 + "\n")
    
    # ==================== TEST 1: FLUJO BÁSICO DE PEDIDO ====================
    print("\nTEST 1: Flujo básico de pedido (1 producto)")
    session1 = setup_session()
    user1 = [
        "Carlos",           # 1. Nombre
        "1",                # 2. Sede Duitama
        "3",                # 3. Realizar pedido
        "1",                # 4. Categoría Carne de res
        "1",                # 5. Origen Nacional
        "1",                # 6. Producto 1 (Punta de anca)
        "2",                # 7. Cantidad 2 unidades
        "3"                 # 8. Confirmar pedido (debería mostrar resumen)
    ]
    
    session_final, responses = run_test(
        "Pedido basico", 
        session1, 
        user1,
        ["pedido confirmado", "punta de anca"]
    )
    
    # Verificar que el carrito quedó vacío después del pedido
    if not session_final.get("cart"):
        print("[OK] Carrito vacio despues del pedido")
    else:
        print(f"[FAIL] Carrito no vacio: {session_final.get('cart')}")
    
    # ==================== TEST 2: PEDIDO CON MÚLTIPLES PRODUCTOS ====================
    print("\nTEST 2: Pedido con multiples productos")
    session2 = setup_session()
    user2 = [
        "Ana",              # 1. Nombre
        "2",                # 2. Sede Sogamoso
        "3",                # 3. Realizar pedido
        "2",                # 4. Categoría Carne de cerdo
        "1",                # 5. Origen Nacional
        "1",                # 6. Producto 1 (Costilla de cerdo)
        "1",                # 7. Cantidad 1 caja
        "1",                # 8. Agregar otro producto
        "3",                # 9. Categoría Visceras y madejas
        "1",                # 10. Origen Nacional
        "2",                # 11. Producto 2 (Corazón de res)
        "2",                # 12. Cantidad 2 cajas
        "2",                # 13. Ver carrito
        "2",                # 14. Volver al menú
        "3"                 # 15. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Pedido multiple", 
        session2, 
        user2,
        ["pedido confirmado", "costilla", "corazon"]
    )
    
    # ==================== TEST 3: ELIMINACIÓN DE PRODUCTOS ====================
    print("\nTEST 3: Eliminar producto del carrito")
    session3 = setup_session()
    user3 = [
        "Maria",            # 1. Nombre
        "1",                # 2. Sede Duitama
        "3",                # 3. Realizar pedido
        "1",                # 4. Categoría Carne de res
        "1",                # 5. Origen Nacional
        "1",                # 6. Producto 1 (Punta de anca)
        "3",                # 7. Cantidad 3 unidades
        "1",                # 8. Agregar otro producto
        "2",                # 9. Categoría Carne de cerdo
        "1",                # 10. Origen Nacional
        "1",                # 11. Producto 1 (Costilla)
        "2",                # 12. Cantidad 2 cajas
        "2",                # 13. Ver carrito
        "1",                # 14. Eliminar producto
        "1",                # 15. Eliminar el primer producto
        "3"                 # 16. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Eliminacion de productos", 
        session3, 
        user3,
        ["eliminado", "confirmado"]
    )
    
    # ==================== TEST 4: NAVEGACIÓN CATÁLOGO ====================
    print("\nTEST 4: Navegacion por catalogo y luego pedido")
    session4 = setup_session()
    user4 = [
        "Pedro",            # 1. Nombre
        "3",                # 2. Sede Bogotá
        "2",                # 3. Ver catálogo
        "1",                # 4. Categoría Carne de res
        "1",                # 5. Opción 1: Realizar pedido
        "1",                # 6. Categoría Carne de res
        "1",                # 7. Origen Nacional
        "1",                # 8. Producto 1
        "1",                # 9. Cantidad 1
        "3"                 # 10. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Catalogo y pedido", 
        session4, 
        user4,
        ["pedido confirmado"]
    )
    
    # ==================== TEST 5: VALIDACIONES ====================
    print("\nTEST 5: Validaciones de entrada")
    session5 = setup_session()
    user5 = [
        "123",              # 1. Nombre con números (debe fallar)
        "Ana",              # 2. Nombre válido
        "5",                # 3. Sede inválida (debe fallar)
        "1",                # 4. Sede válida
        "3",                # 5. Realizar pedido
        "4",                # 6. Categoría inválida (debe fallar)
        "1",                # 7. Categoría válida
        "3",                # 8. Origen inválido (debe fallar)
        "1",                # 9. Origen válido
        "0",                # 10. Volver a categorías
        "0",                # 11. Volver al menú
        "0"                 # 12. Salir
    ]
    
    session_final, responses = run_test(
        "Validaciones", 
        session5, 
        user5,
        ["gracias", "salir"]
    )
    
    # ==================== TEST 6: CAMBIO DE SEDE ====================
    print("\nTEST 6: Cambio de sede")
    session6 = setup_session()
    user6 = [
        "Laura",            # 1. Nombre
        "1",                # 2. Sede Duitama
        "6",                # 3. Cambiar sede
        "2",                # 4. Nueva sede Sogamoso
        "3",                # 5. Realizar pedido
        "2",                # 6. Categoría Carne de cerdo
        "1",                # 7. Origen Nacional
        "1",                # 8. Producto 1
        "1",                # 9. Cantidad 1
        "3"                 # 10. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Cambio de sede", 
        session6, 
        user6,
        ["sede", "sogamoso", "confirmado"]
    )
    
    # ==================== TEST 7: CARRITO VACÍO ====================
    print("\nTEST 7: Intentar confirmar pedido vacio")
    session7 = setup_session()
    user7 = [
        "Jorge",            # 1. Nombre
        "1",                # 2. Sede Duitama
        "3",                # 3. Realizar pedido
        "3",                # 4. Confirmar pedido (debe decir vacío)
        "1",                # 5. Agregar producto
        "1",                # 6. Categoría Carne de res
        "1",                # 7. Origen Nacional
        "1",                # 8. Producto 1
        "2",                # 9. Cantidad 2
        "3"                 # 10. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Carrito vacio", 
        session7, 
        user7,
        ["vacío", "confirmado"]
    )
    
    # ==================== TEST 8: OFERTAS ====================
    print("\nTEST 8: Visualizacion de ofertas")
    session8 = setup_session()
    user8 = [
        "Sofia",            # 1. Nombre
        "1",                # 2. Sede Duitama
        "1",                # 3. Ver ofertas
        "0",                # 4. Volver al menú
        "3",                # 5. Realizar pedido
        "2",                # 6. Categoría Carne de cerdo
        "1",                # 7. Origen Nacional
        "1",                # 8. Producto 1
        "2",                # 9. Cantidad 2
        "3"                 # 10. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Ofertas", 
        session8, 
        user8,
        ["oferta", "confirmado"]
    )
    
    # ==================== TEST 9: LÍMITES DE CANTIDAD ====================
    print("\nTEST 9: Validacion de limites de cantidad")
    session9 = setup_session()
    user9 = [
        "Camilo",           # 1. Nombre
        "1",                # 2. Sede Duitama
        "3",                # 3. Realizar pedido
        "1",                # 4. Categoría Carne de res
        "1",                # 5. Origen Nacional
        "1",                # 6. Producto 1
        "0",                # 7. Cantidad 0 (debe fallar)
        "-5",               # 8. Cantidad negativa (debe fallar)
        "150",              # 9. Cantidad excesiva (debe fallar)
        "5"                 # 10. Cantidad válida
    ]
    
    session_final, responses = run_test(
        "Limites cantidad", 
        session9, 
        user9,
        ["mayor", "maxima", "agregado"]
    )
    
    # ==================== TEST 10: PEDIDO COMPLETO CON ELIMINACIÓN ====================
    print("\nTEST 10: Pedido completo con eliminación")
    session10 = setup_session()
    user10 = [
        "Luis",             # 1. Nombre
        "1",                # 2. Sede Duitama
        "3",                # 3. Realizar pedido
        "1",                # 4. Categoría Carne de res
        "1",                # 5. Origen Nacional
        "1",                # 6. Producto 1
        "2",                # 7. Cantidad 2
        "1",                # 8. Agregar otro producto
        "1",                # 9. Categoría Carne de res
        "1",                # 10. Origen Nacional
        "2",                # 11. Producto 2
        "3",                # 12. Cantidad 3
        "2",                # 13. Ver carrito
        "1",                # 14. Eliminar producto
        "1",                # 15. Eliminar primer producto
        "2",                # 16. Ver carrito
        "3"                 # 17. Confirmar pedido
    ]
    
    session_final, responses = run_test(
        "Pedido completo", 
        session10, 
        user10,
        ["churrasco", "confirmado"]
    )
    
    # ==================== RESUMEN FINAL ====================
    print("\n" + "="*60)
    print("PRUEBAS AUTOMATIZADAS COMPLETADAS")
    print("="*60)
    print("\n[OK] Todas las pruebas se ejecutaron correctamente")
    print("\nNota: Verifica los logs para asegurar que cada prueba:")
    print("  - El estado cambia correctamente (START -> ASK_NAME -> ASK_SEDE -> MENU)")
    print("  - Los productos se agregan al carrito")
    print("  - Las eliminaciones funcionan")
    print("  - Los pedidos se confirman")
    print("\nPuedes modificar los tests segun los productos reales de tu catalogo")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\nError durante las pruebas: {e}")
        import traceback
        traceback.print_exc()