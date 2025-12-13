"""
Script para ver los usuarios actuales en la base de datos
"""
from database import Database, get_db

def ver_usuarios():
    """Muestra todos los usuarios en la base de datos"""
    print("=" * 70)
    print("USUARIOS EN LA BASE DE DATOS")
    print("=" * 70)
    print()
    
    try:
        db = get_db()
        
        usuarios = db.fetch_all(
            "SELECT id, nombre, email, rol, activo, fecha_creacion FROM usuarios ORDER BY id"
        )
        
        if not usuarios:
            print("No hay usuarios en la base de datos.")
            return
        
        print(f"Total de usuarios: {len(usuarios)}")
        print()
        print("-" * 70)
        print(f"{'ID':<5} {'Nombre':<25} {'Email':<30} {'Rol':<20} {'Activo':<10}")
        print("-" * 70)
        
        for usuario in usuarios:
            activo_str = "Sí" if usuario.get('activo') == 1 else "No"
            print(f"{usuario['id']:<5} {usuario['nombre']:<25} {usuario['email']:<30} {usuario.get('rol', 'N/A'):<20} {activo_str:<10}")
        
        print("-" * 70)
        print()
        
        # Mostrar usuarios activos
        usuarios_activos = [u for u in usuarios if u.get('activo') == 1]
        print(f"Usuarios activos: {len(usuarios_activos)}")
        print()
        
        # Verificar acceso total
        from auth import USUARIOS_ACCESO_TOTAL
        print("=" * 70)
        print("USUARIOS CON ACCESO TOTAL CONFIGURADOS:")
        print("=" * 70)
        if USUARIOS_ACCESO_TOTAL:
            for email in USUARIOS_ACCESO_TOTAL:
                print(f"  - {email}")
        else:
            print("  (Ninguno configurado)")
        print()
        
        # Verificar cuáles usuarios activos tienen acceso total
        print("=" * 70)
        print("ESTADO DE ACCESO:")
        print("=" * 70)
        for usuario in usuarios_activos:
            email = usuario['email'].lower()
            tiene_acceso = email in [e.lower() for e in USUARIOS_ACCESO_TOTAL]
            es_admin = 'admin' in usuario.get('rol', '').lower()
            
            if tiene_acceso or es_admin:
                print(f"[OK] {usuario['email']:<30} - Tiene acceso total")
            else:
                print(f"[INFO] {usuario['email']:<30} - Acceso según rol: {usuario.get('rol', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if db:
                db.disconnect()
        except:
            pass

if __name__ == "__main__":
    ver_usuarios()

