"""
Script para diagnosticar los endpoints de contratos y nómina
Verifica que los endpoints estén devolviendo datos correctamente
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(url, name, requires_auth=False, token=None):
    """Probar un endpoint y mostrar resultados"""
    print(f"\n{'='*70}")
    print(f"Probando: {name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    headers = {}
    if requires_auth and token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Formato de respuesta: {type(data)}")
                
                # Verificar estructura
                if isinstance(data, dict):
                    print(f"Keys en respuesta: {list(data.keys())}")
                    
                    # Verificar si tiene 'data' o 'status' o 'success'
                    if 'data' in data:
                        data_array = data['data']
                        if isinstance(data_array, list):
                            print(f"✅ Datos encontrados: {len(data_array)} registros")
                            if len(data_array) > 0:
                                print(f"Primer registro (keys): {list(data_array[0].keys())}")
                        else:
                            print(f"⚠️ 'data' no es un array: {type(data_array)}")
                    else:
                        print("⚠️ No tiene campo 'data'")
                    
                    if 'status' in data:
                        print(f"Status: {data['status']}")
                    if 'success' in data:
                        print(f"Success: {data['success']}")
                    if 'count' in data:
                        print(f"Count: {data['count']}")
                else:
                    print(f"⚠️ Respuesta no es un diccionario: {type(data)}")
                
                # Mostrar respuesta completa (limitada)
                print(f"\nRespuesta completa (primeros 500 caracteres):")
                response_str = json.dumps(data, indent=2, ensure_ascii=False)
                print(response_str[:500])
                if len(response_str) > 500:
                    print("... (truncado)")
                    
            except json.JSONDecodeError:
                print(f"⚠️ Error: La respuesta no es JSON válido")
                print(f"Respuesta (primeros 200 caracteres): {response.text[:200]}")
        elif response.status_code == 401:
            print("❌ Error 401: No autenticado")
            print("Necesitas un token de autenticación")
        elif response.status_code == 403:
            print("❌ Error 403: Sin permisos")
        elif response.status_code == 404:
            print("❌ Error 404: Endpoint no encontrado")
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle: {error_data.get('detail', 'Sin detalle')}")
            except:
                print(f"Respuesta: {response.text[:200]}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("Asegúrate de que el backend esté corriendo en http://localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout - El servidor tardó demasiado en responder")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    print("="*70)
    print("DIAGNÓSTICO DE ENDPOINTS - CONTRATOS Y NÓMINA")
    print("="*70)
    
    # Probar endpoint de contratos (sin autenticación)
    test_endpoint(
        f"{BASE_URL}/api/contratos",
        "Listar Contratos",
        requires_auth=False
    )
    
    # Probar endpoint de nómina (requiere autenticación)
    # Primero intentar sin token
    test_endpoint(
        f"{BASE_URL}/api/nomina",
        "Listar Nóminas (sin token)",
        requires_auth=True,
        token=None
    )
    
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print("""
Para probar nómina con autenticación:
1. Obtén un token haciendo login:
   POST http://localhost:8000/api/usuarios/login
   Body: {"email": "admin@rrhh.com", "password": "admin123"}

2. Usa el token en el header:
   Authorization: Bearer <token>

3. O ejecuta este script con un token:
   python diagnosticar_endpoints.py <token>
    """)

if __name__ == "__main__":
    import sys
    token = sys.argv[1] if len(sys.argv) > 1 else None
    if token:
        test_endpoint(
            f"http://localhost:8000/api/nomina",
            "Listar Nóminas (con token)",
            requires_auth=True,
            token=token
        )
    else:
        main()

