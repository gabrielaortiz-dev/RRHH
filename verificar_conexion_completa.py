"""
Script completo para verificar la conexión entre Backend (SQLite) y Frontend
"""
import sqlite3
import urllib.request
import urllib.error
import json
import os
import sys

def verificar_base_datos():
    """Verifica la base de datos SQLite"""
    print("\n" + "="*70)
    print("1. VERIFICACIÓN DE BASE DE DATOS SQLite")
    print("="*70)
    
    db_path = os.path.join("BACKEND", "rrhh.db")
    
    if not os.path.exists(db_path):
        print(f"[ERROR] No se encuentra la base de datos en: {db_path}")
        return False
    
    print(f"[OK] Base de datos encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"[OK] Total de tablas: {len(tables)}")
        
        if len(tables) != 33:
            print(f"[ADVERTENCIA] Se esperaban 33 tablas, se encontraron {len(tables)}")
        else:
            print("[OK] Numero correcto de tablas (33)")
        
        # Mostrar algunas tablas importantes
        tablas_importantes = ['usuarios', 'empleados', 'departamentos', 'puestos', 'asistencias']
        print("\nTablas importantes:")
        for tabla in tablas_importantes:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"  - {tabla:20s}: {count:4d} registros")
            except Exception as e:
                print(f"  - {tabla:20s}: ERROR - {e}")
        
        conn.close()
        print("\n[OK] Base de datos SQLite: OK")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al conectar con la base de datos: {e}")
        return False


def verificar_backend():
    """Verifica que el backend esté corriendo y respondiendo"""
    print("\n" + "="*70)
    print("2. VERIFICACIÓN DEL BACKEND (FastAPI)")
    print("="*70)
    
    base_url = "http://localhost:8000"
    
    # Verificar si el servidor está corriendo
    print(f"Verificando servidor en: {base_url}")
    
    try:
        # 1. Verificar endpoint raíz
        print("\n  a) Verificando endpoint raíz (/)...")
        req = urllib.request.Request(f"{base_url}/")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"     [OK] Servidor activo: {data.get('mensaje', 'N/A')}")
    except urllib.error.URLError as e:
        print(f"     [ERROR] El servidor NO esta corriendo")
        print(f"     -> Solucion: Ejecuta 'cd BACKEND && python main.py'")
        return False
    except Exception as e:
        print(f"     [ERROR] {e}")
        return False
    
    # 2. Verificar health check
    try:
        print("\n  b) Verificando health check (/api/health)...")
        req = urllib.request.Request(f"{base_url}/api/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            status = data.get('status', 'N/A')
            database = data.get('database', 'N/A')
            print(f"     [OK] Status: {status}")
            print(f"     [OK] Base de datos: {database}")
    except Exception as e:
        print(f"     [ERROR] Error en health check: {e}")
        return False
    
    # 3. Verificar algunos endpoints importantes
    endpoints = [
        ("/api/departamentos", "Departamentos"),
        ("/api/empleados", "Empleados"),
        ("/api/puestos", "Puestos"),
        ("/api/usuarios", "Usuarios"),
    ]
    
    print("\n  c) Verificando endpoints principales...")
    todos_ok = True
    for endpoint, nombre in endpoints:
        try:
            req = urllib.request.Request(f"{base_url}{endpoint}")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                count = data.get('count', len(data.get('data', [])))
                print(f"     [OK] {nombre:15s}: OK ({count} registros)")
        except Exception as e:
            print(f"     [ERROR] {nombre:15s}: ERROR - {e}")
            todos_ok = False
    
    if todos_ok:
        print("\n[OK] Backend: OK")
        return True
    else:
        print("\n[ADVERTENCIA] Backend: Algunos endpoints tienen problemas")
        return False


def verificar_configuracion_frontend():
    """Verifica la configuración del frontend"""
    print("\n" + "="*70)
    print("3. VERIFICACIÓN DE CONFIGURACIÓN DEL FRONTEND")
    print("="*70)
    
    env_file = os.path.join("RRHH", "src", "environments", "environment.ts")
    
    if not os.path.exists(env_file):
        print(f"[ERROR] No se encuentra el archivo de configuracion: {env_file}")
        return False
    
    print(f"[OK] Archivo de configuracion encontrado: {env_file}")
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar que contenga la URL correcta
        if "http://localhost:8000/api" in content:
            print("[OK] URL del backend configurada correctamente: http://localhost:8000/api")
        else:
            print("[ADVERTENCIA] La URL del backend podria no estar configurada correctamente")
            print(f"   Contenido encontrado: {content[:200]}...")
        
        # Verificar que use environment.apiUrl
        if "apiUrl" in content:
            print("[OK] Variable apiUrl encontrada en la configuracion")
        else:
            print("[ADVERTENCIA] Variable apiUrl no encontrada")
        
        print("\n[OK] Configuracion del Frontend: OK")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al leer configuracion: {e}")
        return False


def verificar_cors():
    """Verifica la configuración CORS en el backend"""
    print("\n" + "="*70)
    print("4. VERIFICACIÓN DE CONFIGURACIÓN CORS")
    print("="*70)
    
    main_py = os.path.join("BACKEND", "main.py")
    
    if not os.path.exists(main_py):
        print(f"[ERROR] No se encuentra main.py: {main_py}")
        return False
    
    try:
        with open(main_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar CORS
        if "CORSMiddleware" in content:
            print("[OK] CORSMiddleware configurado")
        else:
            print("[ERROR] CORSMiddleware no encontrado")
            return False
        
        # Verificar puerto 4200 (puerto por defecto de Angular)
        if "localhost:4200" in content or "127.0.0.1:4200" in content:
            print("[OK] Puerto 4200 permitido en CORS")
        else:
            print("[ADVERTENCIA] Puerto 4200 no encontrado en CORS")
        
        # Verificar puerto 8000
        if "port=8000" in content or "port:8000" in content:
            print("[OK] Backend configurado para puerto 8000")
        else:
            print("[ADVERTENCIA] Puerto 8000 no confirmado en el codigo")
        
        print("\n[OK] Configuracion CORS: OK")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al verificar CORS: {e}")
        return False


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("VERIFICACION COMPLETA: BACKEND (SQLite) <-> FRONTEND")
    print("="*70)
    
    resultados = {
        "Base de Datos": verificar_base_datos(),
        "Backend": verificar_backend(),
        "Configuración Frontend": verificar_configuracion_frontend(),
        "CORS": verificar_cors()
    }
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*70)
    
    todos_ok = True
    for componente, resultado in resultados.items():
        estado = "[OK]" if resultado else "[ERROR]"
        print(f"{componente:30s}: {estado}")
        if not resultado:
            todos_ok = False
    
    print("="*70)
    
    if todos_ok:
        print("\n[OK] TODAS LAS VERIFICACIONES PASARON")
        print("\nEl backend y frontend estan correctamente configurados y conectados.")
        print("\nPara iniciar el sistema:")
        print("  1. Backend:  cd BACKEND && python main.py")
        print("  2. Frontend: cd RRHH && ng serve")
    else:
        print("\n[ADVERTENCIA] ALGUNAS VERIFICACIONES FALLARON")
        print("\nRevisa los errores arriba y corrige los problemas antes de continuar.")
    
    print("\n")


if __name__ == "__main__":
    main()

