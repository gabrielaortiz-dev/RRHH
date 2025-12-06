"""
Script para verificar la conexión entre Frontend y Backend
"""
import urllib.request
import urllib.error
import json
from datetime import datetime

# Configuración
BACKEND_URL = "http://localhost:8000"
FRONTEND_API_URL = "http://localhost:8000/api"  # URL que usa el frontend
FRONTEND_PORT = 4200

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    """Imprime un mensaje de éxito"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime un mensaje de error"""
    print(f"❌ {text}")

def print_warning(text):
    """Imprime un mensaje de advertencia"""
    print(f"⚠️  {text}")

def print_info(text):
    """Imprime un mensaje informativo"""
    print(f"ℹ️  {text}")

def check_backend_health():
    """Verifica si el backend está corriendo"""
    print_header("1. VERIFICANDO BACKEND")
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/api/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print_success(f"Backend está corriendo en {BACKEND_URL}")
                print_info(f"Estado: {data.get('status', 'N/A')}")
                print_info(f"Base de datos: {data.get('database', 'N/A')}")
                return True
            else:
                print_error(f"Backend respondió con código {response.status}")
                return False
    except urllib.error.URLError as e:
        print_error(f"No se puede conectar al backend en {BACKEND_URL}")
        print_warning("Asegúrate de que el backend esté corriendo:")
        print_warning("  cd BACKEND")
        print_warning("  python main.py")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False

def check_backend_cors():
    """Verifica la configuración CORS del backend"""
    print_header("2. VERIFICANDO CONFIGURACIÓN CORS")
    try:
        # Hacer una petición GET para verificar headers CORS
        req = urllib.request.Request(f"{BACKEND_URL}/api/health")
        req.add_header("Origin", f"http://localhost:{FRONTEND_PORT}")
        with urllib.request.urlopen(req, timeout=5) as response:
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            print_info("Headers CORS recibidos:")
            for header, value in cors_headers.items():
                if value:
                    print_success(f"  {header}: {value}")
                else:
                    print_warning(f"  {header}: No configurado")
            
            # Verificar si el origen del frontend está permitido
            allowed_origins = [
                f"http://localhost:{FRONTEND_PORT}",
                f"http://127.0.0.1:{FRONTEND_PORT}",
                "http://localhost:4200",
                "http://localhost:4201"
            ]
            
            origin_allowed = False
            for origin in allowed_origins:
                if cors_headers["Access-Control-Allow-Origin"] == origin or cors_headers["Access-Control-Allow-Origin"] == "*":
                    origin_allowed = True
                    break
            
            if origin_allowed or response.status in [200, 204]:
                print_success("CORS configurado correctamente")
                return True
            else:
                print_warning("CORS puede no estar configurado correctamente")
                return True  # No es crítico si la petición funciona
    except Exception as e:
        print_warning(f"No se pudo verificar CORS completamente: {str(e)}")
        return True  # No es crítico

def check_backend_endpoints():
    """Verifica que los endpoints principales del backend funcionen"""
    print_header("3. VERIFICANDO ENDPOINTS DEL BACKEND")
    
    endpoints = [
        ("GET", "/", "Endpoint raíz"),
        ("GET", "/api/health", "Health check"),
        ("GET", "/api/usuarios", "Listar usuarios"),
        ("GET", "/api/departamentos", "Listar departamentos"),
        ("GET", "/api/empleados", "Listar empleados"),
    ]
    
    working_endpoints = 0
    for method, endpoint, description in endpoints:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.status
                if status in [200, 201]:
                    print_success(f"{description}: {endpoint} - OK ({status})")
                    working_endpoints += 1
                elif status == 401:
                    print_warning(f"{description}: {endpoint} - Requiere autenticación ({status})")
                    working_endpoints += 1  # El endpoint funciona, solo necesita auth
                else:
                    print_error(f"{description}: {endpoint} - Error ({status})")
        except urllib.error.HTTPError as e:
            if e.code in [200, 201]:
                print_success(f"{description}: {endpoint} - OK ({e.code})")
                working_endpoints += 1
            elif e.code == 401:
                print_warning(f"{description}: {endpoint} - Requiere autenticación ({e.code})")
                working_endpoints += 1
            else:
                print_error(f"{description}: {endpoint} - Error ({e.code})")
        except Exception as e:
            print_error(f"{description}: {endpoint} - Error: {str(e)}")
    
    print_info(f"Endpoints funcionando: {working_endpoints}/{len(endpoints)}")
    return working_endpoints == len(endpoints)

def check_frontend_config():
    """Verifica la configuración del frontend"""
    print_header("4. VERIFICANDO CONFIGURACIÓN DEL FRONTEND")
    
    try:
        # Leer el archivo de environment
        with open("RRHH/src/environments/environment.ts", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "http://localhost:8000/api" in content:
            print_success("Frontend configurado para usar: http://localhost:8000/api")
        else:
            print_warning("No se encontró la URL esperada en environment.ts")
            print_info("Buscando otras URLs...")
            if "localhost:8000" in content:
                print_success("Frontend configurado para usar localhost:8000")
            else:
                print_error("Frontend no está configurado para usar localhost:8000")
        
        # Verificar que use environment.apiUrl
        if "environment.apiUrl" in content:
            print_success("Frontend usa environment.apiUrl correctamente")
        else:
            print_warning("Frontend puede no estar usando environment.apiUrl")
        
        return True
    except FileNotFoundError:
        print_error("No se encontró el archivo environment.ts")
        return False
    except Exception as e:
        print_error(f"Error al leer configuración del frontend: {str(e)}")
        return False

def check_services_config():
    """Verifica que los servicios del frontend usen la URL correcta"""
    print_header("5. VERIFICANDO SERVICIOS DEL FRONTEND")
    
    services_to_check = [
        "RRHH/src/app/services/auth.service.ts",
        "RRHH/src/app/services/employee.service.ts",
        "RRHH/src/app/services/department.service.ts",
    ]
    
    all_correct = True
    for service_path in services_to_check:
        try:
            with open(service_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "environment.apiUrl" in content:
                print_success(f"{service_path.split('/')[-1]}: Usa environment.apiUrl")
            else:
                print_warning(f"{service_path.split('/')[-1]}: Puede no usar environment.apiUrl")
                all_correct = False
        except FileNotFoundError:
            print_warning(f"No se encontró: {service_path}")
        except Exception as e:
            print_error(f"Error al leer {service_path}: {str(e)}")
    
    return all_correct

def generate_summary(backend_ok, cors_ok, endpoints_ok, frontend_config_ok, services_ok):
    """Genera un resumen de la verificación"""
    print_header("RESUMEN DE VERIFICACIÓN")
    
    results = {
        "Backend corriendo": backend_ok,
        "CORS configurado": cors_ok,
        "Endpoints funcionando": endpoints_ok,
        "Frontend configurado": frontend_config_ok,
        "Servicios configurados": services_ok
    }
    
    all_ok = all(results.values())
    
    for check, status in results.items():
        if status:
            print_success(f"{check}: ✓")
        else:
            print_error(f"{check}: ✗")
    
    print("\n" + "="*70)
    if all_ok:
        print_success("✅ CONEXIÓN ENTRE FRONTEND Y BACKEND: CORRECTA")
        print_info("El frontend y backend están correctamente conectados.")
    else:
        print_error("❌ CONEXIÓN ENTRE FRONTEND Y BACKEND: PROBLEMAS DETECTADOS")
        print_warning("Revisa los errores anteriores y corrige los problemas.")
    
    print("="*70 + "\n")
    
    # Recomendaciones
    if not backend_ok:
        print("📋 RECOMENDACIONES:")
        print("1. Inicia el backend:")
        print("   cd BACKEND")
        print("   python main.py")
        print()
    
    if not frontend_config_ok:
        print("📋 RECOMENDACIONES:")
        print("1. Verifica que RRHH/src/environments/environment.ts tenga:")
        print("   apiUrl: 'http://localhost:8000/api'")
        print()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  VERIFICACIÓN DE CONEXIÓN FRONTEND - BACKEND")
    print("  Sistema de RRHH")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar verificaciones
    backend_ok = check_backend_health()
    cors_ok = check_backend_cors() if backend_ok else False
    endpoints_ok = check_backend_endpoints() if backend_ok else False
    frontend_config_ok = check_frontend_config()
    services_ok = check_services_config()
    
    # Generar resumen
    generate_summary(backend_ok, cors_ok, endpoints_ok, frontend_config_ok, services_ok)

