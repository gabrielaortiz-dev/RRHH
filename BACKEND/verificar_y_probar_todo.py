"""
Script para verificar y probar que TODO funcione correctamente
"""
import requests
import json
from database import get_db
from auth import USUARIOS_ACCESO_TOTAL, create_access_token
from datetime import timedelta

BASE_URL = "http://localhost:8000"

def verificar_servidor():
    """Verifica que el servidor esté corriendo"""
    print("=" * 70)
    print("VERIFICANDO SERVIDOR")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("[OK] Servidor está corriendo")
            return True
        else:
            print(f"[ERROR] Servidor respondió con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] El servidor NO está corriendo")
        print("       Ejecuta: python main.py")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

def verificar_usuarios():
    """Verifica usuarios disponibles"""
    print()
    print("=" * 70)
    print("VERIFICANDO USUARIOS")
    print("=" * 70)
    
    try:
        db = get_db()
        
        # Buscar usuarios SUPER ADMIN
        super_admins = db.fetch_all(
            """SELECT id, nombre, email, rol, activo 
               FROM usuarios 
               WHERE activo = 1 
               AND (rol LIKE '%SUPER ADMIN%' 
                    OR rol LIKE '%super admin%' 
                    OR rol LIKE '%Super Admin%'
                    OR rol = 'administrador'
                    OR rol LIKE '%ADMIN%')
               ORDER BY id
               LIMIT 10"""
        )
        
        if super_admins:
            print(f"[OK] Encontrados {len(super_admins)} usuario(s) SUPER ADMIN:")
            for u in super_admins:
                print(f"  - {u['email']:<40} ({u['nombre']}) - Rol: {u['rol']}")
            return super_admins[0]  # Retornar el primero
        else:
            print("[ADVERTENCIA] No se encontraron usuarios SUPER ADMIN")
            # Buscar cualquier usuario activo
            usuarios = db.fetch_all(
                "SELECT id, nombre, email, rol FROM usuarios WHERE activo = 1 LIMIT 5"
            )
            if usuarios:
                print("\nUsuarios activos encontrados:")
                for u in usuarios:
                    print(f"  - {u['email']:<40} ({u['nombre']}) - Rol: {u['rol']}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None
    finally:
        try:
            db.disconnect()
        except:
            pass

def probar_login(email, password):
    """Prueba hacer login"""
    print()
    print("=" * 70)
    print(f"PROBANDO LOGIN CON: {email}")
    print("=" * 70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Login exitoso!")
            print(f"   Usuario: {data['data']['nombre']}")
            print(f"   Email: {data['data']['email']}")
            print(f"   Rol: {data['data']['rol']}")
            print(f"   Token recibido: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"[ERROR] Login falló")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

def probar_endpoint_usuarios(token):
    """Prueba el endpoint de usuarios con el token"""
    print()
    print("=" * 70)
    print("PROBANDO ENDPOINT GET /api/usuarios")
    print("=" * 70)
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Endpoint funciona correctamente!")
            print(f"   Usuarios encontrados: {data.get('count', len(data.get('data', [])))}")
            return True
        else:
            print(f"[ERROR] Endpoint falló")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("VERIFICACION Y PRUEBA COMPLETA DEL SISTEMA")
    print("=" * 70 + "\n")
    
    # 1. Verificar servidor
    if not verificar_servidor():
        print("\n[IMPORTANTE] El servidor no está corriendo.")
        print("            Ejecuta: cd BACKEND && python main.py")
        return
    
    # 2. Verificar usuarios
    usuario = verificar_usuarios()
    
    if not usuario:
        print("\n[ERROR] No se encontró ningún usuario SUPER ADMIN para probar")
        return
    
    # 3. Probar login (intentar con diferentes contraseñas comunes)
    email = usuario['email']
    passwords = ["admin123", "admin", "pass123", "password", "123456"]
    
    token = None
    for password in passwords:
        token = probar_login(email, password)
        if token:
            break
    
    if not token:
        print("\n[ERROR] No se pudo hacer login con ninguna contraseña común")
        print(f"        Intenta manualmente con el email: {email}")
        return
    
    # 4. Probar endpoint
    if probar_endpoint_usuarios(token):
        print()
        print("=" * 70)
        print("[OK] TODO FUNCIONA CORRECTAMENTE!")
        print("=" * 70)
        print()
        print("INSTRUCCIONES PARA POSTMAN:")
        print(f"1. Login: POST {BASE_URL}/api/usuarios/login")
        print(f"   Body: {{\"email\": \"{email}\", \"password\": \"[tu-password]\"}}")
        print()
        print("2. Copia el 'access_token' de la respuesta")
        print()
        print("3. En GET /api/usuarios:")
        print("   - Authorization → Bearer Token → Pega el token")
        print()
        print("¡LISTO! Ya debería funcionar.")
    else:
        print()
        print("=" * 70)
        print("[ERROR] El endpoint no funciona correctamente")
        print("=" * 70)
        print("Verifica que el servidor esté corriendo y reinícialo si es necesario")

if __name__ == "__main__":
    main()

