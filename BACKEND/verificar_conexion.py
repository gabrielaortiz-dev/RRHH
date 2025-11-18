"""
Script para verificar la conexión del backend
"""
import urllib.request
import urllib.error
import json
import sys
import time

def hacer_peticion(url, timeout=5):
    """Hace una petición HTTP GET y retorna el código de estado y los datos"""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            data = json.loads(response.read().decode())
            return status_code, data
    except urllib.error.URLError as e:
        if "Connection refused" in str(e) or "No connection" in str(e):
            raise ConnectionError("El servidor no está corriendo")
        raise
    except Exception as e:
        raise

def verificar_backend():
    """Verifica si el backend está corriendo y respondiendo"""
    print("=" * 60)
    print("VERIFICACIÓN DE CONEXIÓN DEL BACKEND")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:8000"
    
    # 1. Verificar si el servidor está corriendo
    print("1. Verificando si el servidor está corriendo...")
    try:
        status_code, data = hacer_peticion(f"{base_url}/")
        if status_code == 200:
            print(f"   [OK] Servidor activo")
            print(f"   [OK] Mensaje: {data.get('mensaje', 'N/A')}")
            print(f"   [OK] Version: {data.get('version', 'N/A')}")
        else:
            print(f"   [ERROR] Servidor respondio con codigo: {status_code}")
            return False
    except ConnectionError:
        print("   [ERROR] El servidor NO esta corriendo")
        print("   -> Solucion: Ejecuta 'iniciar-servidor.bat' o 'python main.py'")
        return False
    except Exception as e:
        print(f"   [ERROR] {str(e)}")
        return False
    
    print()
    
    # 2. Verificar health check
    print("2. Verificando health check...")
    try:
        status_code, data = hacer_peticion(f"{base_url}/api/health")
        if status_code == 200:
            print(f"   [OK] Health check OK")
            print(f"   [OK] Estado: {data.get('status', 'N/A')}")
            print(f"   [OK] Base de datos: {data.get('database', 'N/A')}")
        else:
            print(f"   [ERROR] Health check fallo con codigo: {status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] ERROR en health check: {str(e)}")
        return False
    
    print()
    
    # 3. Verificar endpoints principales
    print("3. Verificando endpoints principales...")
    endpoints = [
        ("/api/departamentos", "Departamentos"),
        ("/api/empleados", "Empleados"),
        ("/api/usuarios", "Usuarios"),
    ]
    
    todos_ok = True
    for endpoint, nombre in endpoints:
        try:
            status_code, data = hacer_peticion(f"{base_url}{endpoint}")
            if status_code == 200:
                count = data.get('count', len(data.get('data', [])))
                print(f"   [OK] {nombre}: OK ({count} registros)")
            else:
                print(f"   [ERROR] {nombre}: Error {status_code}")
                todos_ok = False
        except Exception as e:
            print(f"   [ERROR] {nombre}: Error - {str(e)}")
            todos_ok = False
    
    print()
    
    # 4. Verificar documentación
    print("4. Verificando documentación...")
    try:
        status_code, _ = hacer_peticion(f"{base_url}/docs")
        if status_code == 200:
            print(f"   [OK] Documentacion Swagger disponible en: {base_url}/docs")
        else:
            print(f"   [ADVERTENCIA] Documentacion no disponible")
    except Exception as e:
        print(f"   [ADVERTENCIA] No se pudo verificar documentacion: {str(e)}")
    
    print()
    print("=" * 60)
    if todos_ok:
        print("[OK] RESUMEN: Backend esta funcionando correctamente")
        print()
        print("URLs disponibles:")
        print(f"  - API Base: {base_url}")
        print(f"  - Health Check: {base_url}/api/health")
        print(f"  - Documentación: {base_url}/docs")
        print()
        print("El frontend puede conectarse usando:")
        print(f"  const apiUrl = '{base_url}/api';")
    else:
        print("[ADVERTENCIA] RESUMEN: Backend esta corriendo pero algunos endpoints tienen problemas")
    print("=" * 60)
    
    return todos_ok

if __name__ == "__main__":
    try:
        verificar_backend()
    except KeyboardInterrupt:
        print("\n\nVerificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR INESPERADO: {str(e)}")
        sys.exit(1)

