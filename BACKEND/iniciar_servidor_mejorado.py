"""
Script mejorado para iniciar el servidor con mejor manejo de errores
"""
import sys
import socket
import uvicorn
import os

def verificar_puerto_disponible(host: str, port: int) -> bool:
    """Verifica si el puerto está disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            if result == 0:
                return False  # Puerto en uso
            return True  # Puerto disponible
    except Exception:
        return True  # Asumir disponible si hay error

def main():
    """Función principal para iniciar el servidor"""
    host = "0.0.0.0"
    port = 8000
    
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR BACKEND - SISTEMA RRHH")
    print("="*70)
    print()
    
    # Verificar puerto
    print(f"🔍 Verificando puerto {port}...")
    if not verificar_puerto_disponible("localhost", port):
        print(f"❌ ERROR: El puerto {port} ya está en uso")
        print()
        print("💡 SOLUCIONES:")
        print("1. Cierra otros procesos que usen el puerto 8000")
        print("2. Para ver qué proceso usa el puerto, ejecuta:")
        print("   netstat -ano | findstr :8000")
        print("3. O cambia el puerto en este script")
        print()
        sys.exit(1)
    
    print(f"✅ Puerto {port} disponible")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("main.py"):
        print("❌ ERROR: No se encontró main.py")
        print("💡 Asegúrate de ejecutar este script desde la carpeta BACKEND")
        print()
        sys.exit(1)
    
    print("✅ Archivo main.py encontrado")
    print()
    
    # Información del servidor
    print("📋 CONFIGURACIÓN DEL SERVIDOR:")
    print(f"   - Host: {host} (escucha en todas las interfaces)")
    print(f"   - Puerto: {port}")
    print(f"   - URL Local: http://localhost:{port}")
    print(f"   - URL Red: http://127.0.0.1:{port}")
    print(f"   - Documentación: http://localhost:{port}/docs")
    print(f"   - Health Check: http://localhost:{port}/api/health")
    print()
    print("="*70)
    print("🔄 Iniciando servidor...")
    print("="*70)
    print()
    print("💡 Presiona CTRL+C para detener el servidor")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info",
            access_log=True,
            reload_dirs=["."] if os.getcwd().endswith("BACKEND") else None
        )
    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("🛑 Servidor detenido por el usuario")
        print("="*70)
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
            print("\n" + "="*70)
            print("❌ ERROR: El puerto está en uso")
            print("="*70)
            print(f"\nDetalles: {e}\n")
            print("💡 SOLUCIONES:")
            print("1. Cierra otros procesos que usen el puerto 8000")
            print("2. Reinicia este script")
            print()
        else:
            print(f"\n❌ ERROR del sistema: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        print(f"\nTraceback:\n{traceback.format_exc()}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

