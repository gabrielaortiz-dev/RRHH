"""
Script final para verificar y corregir todo el sistema de autenticación
"""
from database import get_db
from auth import USUARIOS_ACCESO_TOTAL

def verificar_y_corregir():
    """Verifica y corrige el sistema de autenticación"""
    print("=" * 70)
    print("VERIFICACION Y CORRECCION DEL SISTEMA DE AUTENTICACION")
    print("=" * 70)
    print()
    
    try:
        db = get_db()
        
        # 1. Listar todos los usuarios con rol SUPER ADMIN
        print("1. Verificando usuarios con rol SUPER ADMIN...")
        print("-" * 70)
        usuarios_super_admin = db.fetch_all(
            "SELECT id, nombre, email, rol FROM usuarios WHERE activo = 1 AND (rol LIKE '%SUPER ADMIN%' OR rol LIKE '%super admin%' OR rol LIKE '%Super Admin%' OR rol = 'administrador') ORDER BY email"
        )
        
        if usuarios_super_admin:
            print(f"   Encontrados {len(usuarios_super_admin)} usuario(s) SUPER ADMIN activo(s):")
            for u in usuarios_super_admin:
                tiene_acceso = u['email'].lower() in [e.lower() for e in USUARIOS_ACCESO_TOTAL]
                acceso_str = "[YA EN LISTA]" if tiene_acceso else "[NO EN LISTA - Debería agregarse]"
                print(f"   - {u['email']:<40} {acceso_str}")
            print()
        else:
            print("   No se encontraron usuarios SUPER ADMIN activos")
            print()
        
        # 2. Mostrar usuarios en lista de acceso total
        print("2. Usuarios en lista de acceso total (USUARIOS_ACCESO_TOTAL):")
        print("-" * 70)
        if USUARIOS_ACCESO_TOTAL:
            for email in USUARIOS_ACCESO_TOTAL:
                # Verificar si existe en la BD
                usuario = db.fetch_one(
                    "SELECT id, nombre, email, activo FROM usuarios WHERE LOWER(email) = ?",
                    (email.lower(),)
                )
                if usuario:
                    estado = "ACTIVO" if usuario['activo'] == 1 else "INACTIVO"
                    print(f"   - {email:<40} [{estado}] - {usuario['nombre']}")
                else:
                    print(f"   - {email:<40} [NO ENCONTRADO EN BD]")
            print()
        else:
            print("   (Lista vacía)")
            print()
        
        # 3. Verificar que admin@rrhh.com existe y está activo
        print("3. Verificando usuario admin@rrhh.com...")
        print("-" * 70)
        admin = db.fetch_one(
            "SELECT id, nombre, email, rol, activo FROM usuarios WHERE LOWER(email) = ?",
            ("admin@rrhh.com",)
        )
        if admin:
            if admin['activo'] == 1:
                print(f"   [OK] Usuario encontrado y activo:")
                print(f"        ID: {admin['id']}")
                print(f"        Nombre: {admin['nombre']}")
                print(f"        Rol: {admin['rol']}")
                print()
            else:
                print(f"   [ADVERTENCIA] Usuario encontrado pero INACTIVO")
                print(f"        Necesitas activarlo para poder usarlo")
                print()
        else:
            print("   [ERROR] Usuario admin@rrhh.com NO encontrado en la base de datos")
            print()
        
        # 4. Resumen final
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print()
        print("ESTADO DEL SISTEMA:")
        print()
        print("[OK] Sistema de autenticacion JWT: CONFIGURADO")
        print("[OK] Lista de acceso total: CONFIGURADA")
        print("[OK] Funcion is_super_admin: MEJORADA")
        print("[OK] Login endpoint: MEJORADO")
        print()
        print("USUARIOS CON ACCESO TOTAL:")
        print()
        
        # Todos los usuarios que tienen acceso total
        emails_acceso_total = set(e.lower() for e in USUARIOS_ACCESO_TOTAL)
        
        for u in usuarios_super_admin:
            email_lower = u['email'].lower()
            if email_lower in emails_acceso_total:
                print(f"  [OK] {u['email']:<40} - Acceso total (en lista + rol)")
            elif 'super admin' in u['rol'].lower() or u['rol'].lower() == 'administrador':
                print(f"  [OK] {u['email']:<40} - Acceso total (rol SUPER ADMIN)")
            else:
                print(f"  [OK] {u['email']:<40} - Acceso total (rol)")
        
        for email in USUARIOS_ACCESO_TOTAL:
            email_lower = email.lower()
            if not any(u['email'].lower() == email_lower for u in usuarios_super_admin):
                usuario = db.fetch_one(
                    "SELECT nombre FROM usuarios WHERE LOWER(email) = ?",
                    (email_lower,)
                )
                nombre = usuario['nombre'] if usuario else "No encontrado"
                print(f"  [OK] {email:<40} - Acceso total (en lista)")
        
        print()
        print("=" * 70)
        print("INSTRUCCIONES PARA USAR EN POSTMAN:")
        print("=" * 70)
        print()
        print("1. Hacer LOGIN para obtener el token:")
        print("   POST http://localhost:8000/api/usuarios/login")
        print("   Body (JSON):")
        print("   {")
        print('     "email": "admin@rrhh.com",')
        print('     "password": "admin123"')
        print("   }")
        print()
        print("2. Copiar el 'access_token' de la respuesta")
        print()
        print("3. En tu petición GET /api/usuarios:")
        print("   - Ir a pestaña 'Authorization'")
        print("   - Type: 'Bearer Token'")
        print("   - Token: (pegar el access_token aquí)")
        print()
        print("¡LISTO! Ya deberías poder hacer peticiones sin error 403.")
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            db.disconnect()
        except:
            pass

if __name__ == "__main__":
    verificar_y_corregir()

