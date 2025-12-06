"""
Script para verificar que el servidor está funcionando correctamente
"""
import requests
import sys
import time

def verificar_servidor():
    """Verifica que el servidor esté respondiendo"""
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("VERIFICACIÓN DEL SERVIDOR BACKEND")
    print("="*60)
    print()
    
    # 1. Verificar endpoint principal
    print("1. Verificando endpoint principal (/)...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Servidor respondiendo")
            print(f"   📝 Mensaje: {data.get('mensaje', 'N/A')}")
            print(f"   📦 Versión: {data.get('version', 'N/A')}")
        else:
            print(f"   ⚠️  Servidor respondió con código: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: No se pudo conectar al servidor")
        print("   💡 Asegúrate de que el servidor esté ejecutándose:")
        print("      cd BACKEND")
        print("      python main.py")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ ERROR: El servidor no respondió a tiempo")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print()
    
    # 2. Verificar health check
    print("2. Verificando health check (/api/health)...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check OK")
            print(f"   📊 Estado: {data.get('status', 'N/A')}")
            print(f"   💾 Base de datos: {data.get('database', 'N/A')}")
        else:
            print(f"   ⚠️  Health check respondió con código: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error en health check: {e}")
    
    print()
    
    # 3. Verificar documentación
    print("3. Verificando documentación (/docs)...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Documentación disponible")
            print(f"   🔗 URL: {base_url}/docs")
        else:
            print(f"   ⚠️  Documentación no disponible (código: {response.status_code})")
    except Exception as e:
        print(f"   ⚠️  Error al verificar documentación: {e}")
    
    print()
    print("="*60)
    print("✅ VERIFICACIÓN COMPLETA")
    print("="*60)
    print()
    print("📌 URLs disponibles:")
    print(f"   - API Base: {base_url}/api")
    print(f"   - Health: {base_url}/api/health")
    print(f"   - Docs: {base_url}/docs")
    print()
    
    return True

if __name__ == "__main__":
    # Esperar un poco para que el servidor termine de iniciar
    print("Esperando 2 segundos para que el servidor termine de iniciar...")
    time.sleep(2)
    print()
    
    if verificar_servidor():
        sys.exit(0)
    else:
        print("\n❌ El servidor no está funcionando correctamente")
        sys.exit(1)

