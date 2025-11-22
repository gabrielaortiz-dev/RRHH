"""Script para probar el login del sistema"""
import requests
import json

def probar_login():
    """Probar el endpoint de login"""
    print("=" * 60)
    print("PROBANDO LOGIN")
    print("=" * 60)
    
    url = "http://localhost:8000/api/usuarios/login"
    
    # Credenciales de prueba
    credentials = {
        "email": "admin@rrhh.com",
        "password": "admin123"
    }
    
    print(f"\n[INFO] URL: {url}")
    print(f"[INFO] Credenciales:")
    print(f"  Email: {credentials['email']}")
    print(f"  Password: {credentials['password']}")
    
    try:
        print("\n[INFO] Enviando petición...")
        response = requests.post(url, json=credentials, timeout=5)
        
        print(f"\n[INFO] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] LOGIN EXITOSO")
            print(f"\nRespuesta:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success') and data.get('data'):
                usuario = data['data']
                print(f"\n[OK] Usuario autenticado:")
                print(f"  ID: {usuario.get('id')}")
                print(f"  Nombre: {usuario.get('nombre')}")
                print(f"  Email: {usuario.get('email')}")
                print(f"  Rol: {usuario.get('rol')}")
        else:
            print(f"[ERROR] Login falló con código {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('detail', 'Error desconocido')}")
            except:
                print(f"Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar al servidor")
        print("[INFO] Asegúrate de que el servidor backend esté corriendo en http://localhost:8000")
        print("[INFO] Ejecuta: python main.py")
    except requests.exceptions.Timeout:
        print("\n[ERROR] Timeout al conectar con el servidor")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    probar_login()

