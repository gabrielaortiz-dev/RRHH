"""
Script para verificar que TODO funcione correctamente
"""
from database import get_db
from auth import USUARIOS_ACCESO_TOTAL, create_access_token, tiene_acceso_total_sin_restricciones
from permissions import is_super_admin
from datetime import timedelta

def verificar_todo():
    """Verifica que todo el sistema funcione"""
    print("=" * 70)
    print("VERIFICACION COMPLETA DEL SISTEMA")
    print("=" * 70)
    print()
    
    try:
        db = get_db()
        
        # 1. Verificar usuarios SUPER ADMIN
        print("1. VERIFICANDO USUARIOS SUPER ADMIN...")
        print("-" * 70)
        super_admins = db.fetch_all(
            """SELECT id, nombre, email, rol, activo 
               FROM usuarios 
               WHERE activo = 1 
               AND (UPPER(rol) LIKE '%SUPER ADMIN%' 
                    OR UPPER(rol) LIKE '%ADMIN%'
                    OR rol = 'administrador')
               ORDER BY id
               LIMIT 10"""
        )
        
        if not super_admins:
            print("[ERROR] No se encontraron usuarios SUPER ADMIN")
            print("        Buscando cualquier usuario activo...")
            usuarios = db.fetch_all(
                "SELECT id, nombre, email, rol FROM usuarios WHERE activo = 1 LIMIT 5"
            )
            if usuarios:
                print("\nUsuarios encontrados (sin rol SUPER ADMIN):")
                for u in usuarios:
                    print(f"  {u['id']}. {u['email']} - {u['nombre']} - Rol: {u['rol']}")
                print("\n[SOLUCION] Actualiza el rol de uno de estos usuarios a 'SUPER ADMIN'")
            return False
        
        print(f"[OK] Encontrados {len(super_admins)} usuario(s) SUPER ADMIN:")
        for u in super_admins:
            # Verificar acceso
            usuario_dict = {
                'id': u['id'],
                'email': u['email'],
                'rol': u['rol'],
                'nombre': u['nombre'],
                'activo': u['activo']
            }
            
            tiene_acceso = tiene_acceso_total_sin_restricciones(usuario_dict)
            es_super = is_super_admin(usuario_dict)
            
            acceso_str = "[ACCESO TOTAL]" if (tiene_acceso or es_super) else "[SIN ACCESO]"
            print(f"  {u['id']}. {u['email']:<40} {acceso_str}")
            print(f"     Nombre: {u['nombre']}")
            print(f"     Rol: {u['rol']}")
            print()
        
        # 2. Verificar lista de acceso total
        print("2. VERIFICANDO LISTA DE ACCESO TOTAL...")
        print("-" * 70)
        if USUARIOS_ACCESO_TOTAL:
            print(f"[OK] {len(USUARIOS_ACCESO_TOTAL)} email(s) en lista:")
            for email in USUARIOS_ACCESO_TOTAL:
                # Verificar si existe en BD
                usuario = db.fetch_one(
                    "SELECT id, nombre, email, activo FROM usuarios WHERE LOWER(email) = ?",
                    (email.lower(),)
                )
                if usuario:
                    estado = "ACTIVO" if usuario['activo'] == 1 else "INACTIVO"
                    print(f"  - {email:<40} [{estado}] - {usuario['nombre']}")
                else:
                    print(f"  - {email:<40} [NO ENCONTRADO EN BD]")
        else:
            print("[INFO] Lista vacía (pero usuarios SUPER ADMIN tienen acceso automático)")
        print()
        
        # 3. Probar creación de token
        print("3. PROBANDO CREACION DE TOKEN...")
        print("-" * 70)
        try:
            test_user = super_admins[0]
            token = create_access_token(
                data={"sub": str(test_user['id']), "email": test_user['email'], "rol": test_user['rol']},
                expires_delta=timedelta(minutes=60 * 24)
            )
            print(f"[OK] Token creado exitosamente")
            print(f"     Token (primeros 50 chars): {token[:50]}...")
            print()
        except Exception as e:
            print(f"[ERROR] No se pudo crear token: {str(e)}")
            print()
        
        # 4. Verificar permisos
        print("4. VERIFICANDO PERMISOS...")
        print("-" * 70)
        test_user = super_admins[0]
        usuario_dict = {
            'id': test_user['id'],
            'email': test_user['email'],
            'rol': test_user['rol'],
            'nombre': test_user['nombre'],
            'activo': test_user['activo']
        }
        
        tiene_acceso = tiene_acceso_total_sin_restricciones(usuario_dict)
        es_super = is_super_admin(usuario_dict)
        
        print(f"Usuario de prueba: {test_user['email']}")
        print(f"  - Tiene acceso total (lista): {tiene_acceso}")
        print(f"  - Es super admin (rol): {es_super}")
        print(f"  - Acceso total final: {tiene_acceso or es_super}")
        print()
        
        # 5. Resumen final
        print("=" * 70)
        print("RESUMEN FINAL")
        print("=" * 70)
        print()
        
        if tiene_acceso or es_super:
            print("[OK] TODO ESTA CONFIGURADO CORRECTAMENTE")
            print()
            print("INSTRUCCIONES:")
            print("1. Reinicia el servidor (si no lo has hecho)")
            print("2. Haz login con uno de estos usuarios:")
            for u in super_admins[:3]:
                print(f"   - {u['email']}")
            print()
            print("3. En Postman:")
            print("   - POST /api/usuarios/login con email y password")
            print("   - Copia el access_token")
            print("   - GET /api/usuarios con Authorization: Bearer TOKEN")
            print()
            print("¡DEBERIA FUNCIONAR!")
        else:
            print("[ERROR] El usuario de prueba no tiene acceso")
            print("        Esto no debería pasar si tiene rol SUPER ADMIN")
            print("        Verifica la función is_super_admin()")
        
        print()
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
    verificar_todo()

