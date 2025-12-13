"""
Script para probar que el acceso funciona realmente
Simula una petición completa al endpoint
"""
from database import get_db
from auth import create_access_token, tiene_acceso_total_sin_restricciones, get_current_user, get_current_active_user
from permissions import is_super_admin, require_super_admin
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
import asyncio

async def probar_acceso():
    """Prueba el acceso completo"""
    print("=" * 70)
    print("PRUEBA DE ACCESO COMPLETO")
    print("=" * 70)
    print()
    
    try:
        db = get_db()
        
        # Obtener un usuario SUPER ADMIN
        usuario = db.fetch_one(
            """SELECT id, nombre, email, rol, activo 
               FROM usuarios 
               WHERE activo = 1 
               AND (UPPER(rol) LIKE '%SUPER ADMIN%' OR UPPER(rol) LIKE '%ADMIN%')
               LIMIT 1"""
        )
        
        if not usuario:
            print("[ERROR] No se encontró usuario SUPER ADMIN")
            return False
        
        print(f"Usuario de prueba: {usuario['email']}")
        print(f"  - Nombre: {usuario['nombre']}")
        print(f"  - Rol: {usuario['rol']}")
        print()
        
        # Crear token
        token = create_access_token(
            data={"sub": str(usuario['id']), "email": usuario['email'], "rol": usuario['rol']},
            expires_delta=timedelta(minutes=60 * 24)
        )
        print(f"[OK] Token creado: {token[:50]}...")
        print()
        
        # Simular credentials
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        credentials = MockCredentials(token)
        
        # Probar get_current_user
        print("Probando get_current_user...")
        try:
            current_user = await get_current_user(credentials, db)
            print(f"[OK] Usuario obtenido: {current_user['email']}")
            print(f"     Rol: {current_user['rol']}")
        except Exception as e:
            print(f"[ERROR] get_current_user falló: {str(e)}")
            return False
        
        # Probar get_current_active_user
        print()
        print("Probando get_current_active_user...")
        try:
            active_user = await get_current_active_user(current_user)
            print(f"[OK] Usuario activo verificado: {active_user['email']}")
        except Exception as e:
            print(f"[ERROR] get_current_active_user falló: {str(e)}")
            return False
        
        # Probar require_super_admin
        print()
        print("Probando require_super_admin...")
        try:
            super_user = await require_super_admin(active_user)
            print(f"[OK] require_super_admin pasó: {super_user['email']}")
        except Exception as e:
            print(f"[ERROR] require_super_admin falló: {str(e)}")
            return False
        
        # Verificar permisos
        print()
        print("Verificando permisos...")
        tiene_acceso = tiene_acceso_total_sin_restricciones(active_user)
        es_super = is_super_admin(active_user)
        
        print(f"  - Tiene acceso total (lista): {tiene_acceso}")
        print(f"  - Es super admin (rol): {es_super}")
        print(f"  - Acceso total: {tiene_acceso or es_super}")
        print()
        
        # Probar consulta de usuarios
        print("Probando consulta de usuarios...")
        try:
            usuarios = db.fetch_all(
                "SELECT id, nombre, email, rol FROM usuarios WHERE activo = 1 LIMIT 5"
            )
            print(f"[OK] Consulta exitosa: {len(usuarios)} usuarios encontrados")
            for u in usuarios[:3]:
                print(f"     - {u['email']} ({u['rol']})")
        except Exception as e:
            print(f"[ERROR] Consulta falló: {str(e)}")
            return False
        
        print()
        print("=" * 70)
        print("[OK] TODO FUNCIONA CORRECTAMENTE!")
        print("=" * 70)
        print()
        print("EL SISTEMA ESTA LISTO PARA USAR")
        print()
        print("INSTRUCCIONES:")
        print("1. Asegúrate de que el servidor esté corriendo")
        print("2. Haz login con: admin@rrhh.com / admin123")
        print("3. Usa el token en Postman o en la aplicación web")
        print()
        print("¡DEBERIA FUNCIONAR PERFECTAMENTE!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db.disconnect()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(probar_acceso())

