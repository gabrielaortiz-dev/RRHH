"""
Script para verificar que el código se puede importar y ejecutar correctamente
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_imports():
    """Verificar que todos los módulos se pueden importar"""
    print("="*60)
    print("VERIFICANDO IMPORTS DEL SISTEMA")
    print("="*60)
    print()
    
    errores = []
    
    # Verificar imports estándar
    modulos_estandar = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'uvicorn'),
        ('bcrypt', 'bcrypt'),
        ('sqlite3', 'sqlite3'),
    ]
    
    print("[1/4] Verificando módulos estándar...")
    for modulo, nombre in modulos_estandar:
        try:
            __import__(modulo)
            print(f"   ✓ {nombre}")
        except ImportError as e:
            print(f"   ✗ {nombre}: {e}")
            errores.append(f"{nombre} no está instalado")
    
    print()
    
    # Verificar módulos locales
    print("[2/4] Verificando módulos locales...")
    modulos_locales = [
        ('database', 'Database'),
        ('models', 'Modelos Pydantic'),
        ('auth', 'Autenticación'),
    ]
    
    for modulo, nombre in modulos_locales:
        try:
            __import__(modulo)
            print(f"   ✓ {nombre}")
        except ImportError as e:
            print(f"   ✗ {nombre}: {e}")
            errores.append(f"{nombre} no se puede importar: {e}")
    
    print()
    
    # Verificar helpers
    print("[3/4] Verificando helpers...")
    try:
        from helpers.notification_helper import NotificationHelper
        print("   ✓ NotificationHelper")
    except ImportError as e:
        print(f"   ⚠ NotificationHelper: {e}")
        errores.append(f"NotificationHelper: {e}")
    
    try:
        from helpers.export_helper import ExportHelper
        print("   ✓ ExportHelper")
    except ImportError as e:
        print(f"   ⚠ ExportHelper: {e}")
        errores.append(f"ExportHelper: {e}")
    
    print()
    
    # Verificar main.py
    print("[4/4] Verificando main.py...")
    try:
        import main
        print("   ✓ main.py se importa correctamente")
        print(f"   ✓ FastAPI app creada: {hasattr(main, 'app')}")
        print(f"   ✓ Logger configurado: {hasattr(main, 'logger')}")
    except Exception as e:
        print(f"   ✗ main.py: {e}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        errores.append(f"main.py: {e}")
    
    print()
    print("="*60)
    
    if errores:
        print("❌ SE ENCONTRARON ERRORES:")
        for error in errores:
            print(f"   • {error}")
        print()
        print("SOLUCIONES:")
        print("1. Instala las dependencias: pip install -r requirements.txt")
        print("2. Verifica que todos los archivos estén en la carpeta BACKEND")
        return False
    else:
        print("✅ TODO CORRECTO - El código se puede importar sin errores")
        return True

def verificar_database():
    """Verificar que la base de datos se puede conectar"""
    print()
    print("="*60)
    print("VERIFICANDO CONEXIÓN A BASE DE DATOS")
    print("="*60)
    print()
    
    try:
        from database import Database, get_db
        
        # Verificar que se puede crear una instancia
        db = Database()
        print("✓ Instancia de Database creada")
        
        # Verificar que se puede conectar
        db.connect()
        print("✓ Conexión a base de datos establecida")
        
        # Verificar que se puede ejecutar una query simple
        result = db.fetch_one("SELECT 1 as test")
        if result and result['test'] == 1:
            print("✓ Query de prueba ejecutada correctamente")
        
        # Verificar get_db
        db2 = get_db()
        if db2:
            print("✓ get_db() funciona correctamente")
        
        db.disconnect()
        print("✓ Conexión cerrada correctamente")
        
        print()
        print("="*60)
        print("✅ BASE DE DATOS FUNCIONA CORRECTAMENTE")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        print()
        print("="*60)
        print("❌ ERROR EN BASE DE DATOS")
        return False

if __name__ == "__main__":
    print()
    print("🔍 VERIFICACIÓN COMPLETA DEL CÓDIGO")
    print()
    
    # Verificar imports
    imports_ok = verificar_imports()
    
    if imports_ok:
        # Verificar base de datos
        db_ok = verificar_database()
        
        if db_ok:
            print()
            print("="*60)
            print("✅ TODO EL SISTEMA ESTÁ CORRECTO")
            print("="*60)
            print()
            print("El código está listo para ejecutarse.")
            print("Puedes iniciar el servidor con:")
            print("  python iniciar_servidor_mejorado.py")
            print()
            sys.exit(0)
        else:
            print()
            print("⚠️  Hay problemas con la base de datos")
            print("   Pero el código se puede importar correctamente")
            sys.exit(1)
    else:
        print()
        print("❌ HAY ERRORES EN EL CÓDIGO")
        print("   Corrige los errores antes de iniciar el servidor")
        sys.exit(1)

