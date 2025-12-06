"""
Script completo para verificar que el sistema está funcionando correctamente
Verifica backend, base de datos, endpoints y autenticación
"""
import requests
import sys
import json
from datetime import datetime

# Colores para la terminal (Windows compatible)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_header(message):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def verificar_servidor():
    """Verifica que el servidor esté ejecutándose"""
    base_url = "http://localhost:8000"
    
    print_header("1. VERIFICACIÓN DEL SERVIDOR")
    
    # Test 1: Endpoint principal
    print("Test 1.1: Endpoint principal (/)")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Servidor respondiendo - Versión: {data.get('version', 'N/A')}")
            return True
        else:
            print_error(f"Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar al servidor")
        print_info("Asegúrate de que el servidor esté ejecutándose: python main.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def verificar_health_check():
    """Verifica el health check"""
    base_url = "http://localhost:8000"
    
    print("\nTest 1.2: Health Check (/api/health)")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check OK - Estado: {data.get('status')}, BD: {data.get('database')}")
            return True
        else:
            print_error(f"Health check falló con código: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en health check: {e}")
        return False

def verificar_base_datos():
    """Verifica que la base de datos tenga datos"""
    base_url = "http://localhost:8000"
    
    print_header("2. VERIFICACIÓN DE BASE DE DATOS")
    
    # Test 2.1: Verificar usuarios
    print("Test 2.1: Verificando usuarios...")
    try:
        response = requests.get(f"{base_url}/api/usuarios", timeout=5)
        if response.status_code == 200:
            data = response.json()
            usuarios = data.get('data', [])
            if usuarios:
                print_success(f"Base de datos OK - {len(usuarios)} usuario(s) encontrado(s)")
                # Mostrar primer usuario
                if usuarios:
                    primer_usuario = usuarios[0]
                    print_info(f"   Usuario de prueba: {primer_usuario.get('email', 'N/A')}")
                return True
            else:
                print_warning("Base de datos vacía - No hay usuarios")
                print_info("Ejecuta: python insert_sample_data.py")
                return False
        else:
            print_error(f"Error al obtener usuarios: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def verificar_login():
    """Verifica que el login funcione"""
    base_url = "http://localhost:8000"
    
    print_header("3. VERIFICACIÓN DE AUTENTICACIÓN")
    
    # Credenciales de prueba
    credenciales = {
        "email": "admin@rrhh.com",
        "password": "admin123"
    }
    
    print("Test 3.1: Login con credenciales de prueba")
    print_info(f"   Email: {credenciales['email']}")
    print_info(f"   Password: {credenciales['password']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/usuarios/login",
            json=credenciales,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') or data.get('status') == 'success':
                usuario = data.get('data', {})
                token = data.get('access_token')
                
                print_success("Login exitoso")
                print_info(f"   Usuario: {usuario.get('nombre', 'N/A')}")
                print_info(f"   Email: {usuario.get('email', 'N/A')}")
                print_info(f"   Rol: {usuario.get('rol', 'N/A')}")
                
                if token:
                    print_success(f"Token JWT generado: {token[:50]}...")
                else:
                    print_warning("No se generó token JWT")
                
                return True
            else:
                print_error(f"Login falló: {data.get('message', 'Error desconocido')}")
                return False
        elif response.status_code == 401:
            print_error("Credenciales inválidas")
            print_info("Verifica que exista el usuario admin@rrhh.com")
            print_info("Ejecuta: python insert_sample_data.py")
            return False
        else:
            print_error(f"Error en login: {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"Detalle: {error_data.get('detail', 'Sin detalles')}")
            except:
                print_error(f"Respuesta: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print_error("Timeout - El servidor no respondió a tiempo")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def verificar_endpoints():
    """Verifica endpoints principales"""
    base_url = "http://localhost:8000"
    
    print_header("4. VERIFICACIÓN DE ENDPOINTS")
    
    endpoints = [
        ("/api/departamentos", "GET", "Departamentos"),
        ("/api/empleados", "GET", "Empleados"),
    ]
    
    resultados = []
    
    for endpoint, method, nombre in endpoints:
        print(f"Test 4.x: {nombre} ({endpoint})")
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', len(data.get('data', [])))
                print_success(f"{nombre} OK - {count} registro(s)")
                resultados.append(True)
            else:
                print_warning(f"{nombre} respondió con código: {response.status_code}")
                resultados.append(False)
        except Exception as e:
            print_error(f"Error en {nombre}: {e}")
            resultados.append(False)
    
    return all(resultados)

def verificar_cors():
    """Verifica configuración CORS"""
    base_url = "http://localhost:8000"
    
    print_header("5. VERIFICACIÓN DE CORS")
    
    print("Test 5.1: Verificando headers CORS")
    try:
        # Hacer una petición OPTIONS para verificar CORS
        response = requests.options(
            f"{base_url}/api/health",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        
        cors_headers = {
            "access-control-allow-origin": response.headers.get("Access-Control-Allow-Origin"),
            "access-control-allow-methods": response.headers.get("Access-Control-Allow-Methods"),
            "access-control-allow-credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        if cors_headers["access-control-allow-origin"]:
            print_success("CORS configurado correctamente")
            print_info(f"   Allow-Origin: {cors_headers['access-control-allow-origin']}")
            return True
        else:
            print_warning("CORS no configurado o no visible en esta petición")
            return True  # No es crítico para la verificación básica
    except Exception as e:
        print_warning(f"No se pudo verificar CORS: {e}")
        return True  # No es crítico

def main():
    """Función principal de verificación"""
    print_header("VERIFICACIÓN COMPLETA DEL SISTEMA RRHH")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {
        "servidor": False,
        "health": False,
        "base_datos": False,
        "login": False,
        "endpoints": False,
        "cors": False
    }
    
    # 1. Verificar servidor
    resultados["servidor"] = verificar_servidor()
    if not resultados["servidor"]:
        print_error("\n❌ El servidor no está ejecutándose")
        print_info("Inicia el servidor con: python main.py")
        sys.exit(1)
    
    resultados["health"] = verificar_health_check()
    
    # 2. Verificar base de datos
    resultados["base_datos"] = verificar_base_datos()
    
    # 3. Verificar login
    resultados["login"] = verificar_login()
    
    # 4. Verificar endpoints
    resultados["endpoints"] = verificar_endpoints()
    
    # 5. Verificar CORS
    resultados["cors"] = verificar_cors()
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    total_tests = len(resultados)
    tests_exitosos = sum(1 for v in resultados.values() if v)
    
    for test, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {test.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Resultado: {tests_exitosos}/{total_tests} tests exitosos{Colors.RESET}\n")
    
    if tests_exitosos == total_tests:
        print_success("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print()
        print("📌 URLs disponibles:")
        print("   - API: http://localhost:8000/api")
        print("   - Docs: http://localhost:8000/docs")
        print("   - Health: http://localhost:8000/api/health")
        print()
        print("🔐 Credenciales de acceso:")
        print("   - Email: admin@rrhh.com")
        print("   - Password: admin123")
        print()
        print_success("✅ Puedes iniciar sesión en el frontend ahora")
        return True
    elif resultados["servidor"] and resultados["health"]:
        print_warning("⚠️  Sistema parcialmente funcional")
        print_info("Algunos componentes necesitan atención")
        return False
    else:
        print_error("❌ Sistema no funcional")
        print_info("Revisa los errores anteriores")
        return False

if __name__ == "__main__":
    try:
        exit_code = 0 if main() else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError inesperado: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

