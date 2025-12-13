"""
Script para probar la autenticación y obtener el token para usar en Postman
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Prueba el login y muestra el token"""
    print("=" * 60)
    print("PRUEBA DE AUTENTICACIÓN")
    print("=" * 60)
    print()
    
    # Credenciales de prueba
    email = "admin@rrhh.com"
    password = "admin123"
    
    print(f"1. Intentando hacer login con: {email}")
    print()
    
    try:
        # Hacer login
        response = requests.post(
            f"{BASE_URL}/api/usuarios/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ LOGIN EXITOSO")
            print()
            print("   Datos del usuario:")
            print(f"   - ID: {data['data']['id']}")
            print(f"   - Nombre: {data['data']['nombre']}")
            print(f"   - Email: {data['data']['email']}")
            print(f"   - Rol: {data['data']['rol']}")
            print()
            print("   🔑 TOKEN JWT:")
            print("   " + "-" * 56)
            token = data['access_token']
            print(f"   {token}")
            print("   " + "-" * 56)
            print()
            print("=" * 60)
            print("INSTRUCCIONES PARA POSTMAN:")
            print("=" * 60)
            print()
            print("1. Copia el token de arriba")
            print()
            print("2. En Postman, para tu petición GET /api/usuarios:")
            print("   - Ve a la pestaña 'Authorization'")
            print("   - Type: 'Bearer Token'")
            print("   - Token: (pega el token aquí)")
            print()
            print("3. O manualmente en Headers:")
            print(f"   Key: Authorization")
            print(f"   Value: Bearer {token[:50]}...")
            print()
            
            # Ahora probar el endpoint protegido
            print("=" * 60)
            print("PRUEBA DEL ENDPOINT PROTEGIDO")
            print("=" * 60)
            print()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print("2. Probando GET /api/usuarios con el token...")
            response2 = requests.get(
                f"{BASE_URL}/api/usuarios",
                headers=headers
            )
            
            print(f"   Status Code: {response2.status_code}")
            
            if response2.status_code == 200:
                usuarios = response2.json()
                print("   ✅ ÉXITO - Endpoint accesible")
                print(f"   Usuarios encontrados: {usuarios.get('count', 0)}")
                print()
                return token
            else:
                print(f"   ❌ ERROR: {response2.status_code}")
                print(f"   Respuesta: {response2.text}")
                print()
                return None
                
        else:
            print(f"   ❌ ERROR EN LOGIN")
            print(f"   Status: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            print()
            return None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        print()
        return None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        print()
        return None

if __name__ == "__main__":
    test_login()

