"""
Script para configurar un usuario con acceso total
Este script permite agregar tu email a la lista de usuarios con acceso completo
"""
from database import Database, get_db
from auth import USUARIOS_ACCESO_TOTAL

def configurar_acceso_total():
    """Configura un usuario con acceso total"""
    print("=" * 60)
    print("CONFIGURACIÓN DE ACCESO TOTAL")
    print("=" * 60)
    print()
    
    try:
        db = get_db()
        
        # Mostrar usuarios actuales
        print("Usuarios disponibles en la base de datos:")
        print("-" * 60)
        usuarios = db.fetch_all(
            "SELECT id, nombre, email, rol, activo FROM usuarios WHERE activo = 1 ORDER BY id"
        )
        
        if not usuarios:
            print("No hay usuarios activos en la base de datos.")
            return
        
        for usuario in usuarios:
            tiene_acceso = usuario['email'].lower() in [e.lower() for e in USUARIOS_ACCESO_TOTAL]
            acceso_str = "✅ ACCESO TOTAL" if tiene_acceso else ""
            print(f"  {usuario['id']}. {usuario['nombre']} ({usuario['email']}) - Rol: {usuario['rol']} {acceso_str}")
        
        print()
        print("=" * 60)
        print("USUARIOS CON ACCESO TOTAL ACTUALMENTE:")
        print("=" * 60)
        if USUARIOS_ACCESO_TOTAL:
            for email in USUARIOS_ACCESO_TOTAL:
                print(f"  - {email}")
        else:
            print("  (Ninguno configurado)")
        
        print()
        print("=" * 60)
        print("INSTRUCCIONES:")
        print("=" * 60)
        print()
        print("Para dar acceso total a un usuario, edita el archivo:")
        print("  BACKEND/auth.py")
        print()
        print("Busca la línea:")
        print("  USUARIOS_ACCESO_TOTAL = [")
        print()
        print("Y agrega el email del usuario:")
        print("  USUARIOS_ACCESO_TOTAL = [")
        print("      'admin@rrhh.com',")
        print("      'tu-email@ejemplo.com',  # <-- Agrega tu email aquí")
        print("  ]")
        print()
        print("Luego reinicia el servidor para que los cambios surtan efecto.")
        print()
        
        # Opción para actualizar el rol del usuario directamente
        print("=" * 60)
        print("ALTERNATIVA: ACTUALIZAR ROL A 'SUPER ADMIN'")
        print("=" * 60)
        print()
        respuesta = input("¿Quieres actualizar el rol de algún usuario a 'super admin'? (s/n): ")
        
        if respuesta.lower() == 's':
            try:
                usuario_id = int(input("Ingresa el ID del usuario: "))
                
                # Verificar que el usuario existe
                usuario = db.fetch_one(
                    "SELECT id, nombre, email, rol FROM usuarios WHERE id = ?",
                    (usuario_id,)
                )
                
                if not usuario:
                    print(f"❌ Error: Usuario con ID {usuario_id} no encontrado")
                    return
                
                print()
                print(f"Usuario encontrado: {usuario['nombre']} ({usuario['email']})")
                print(f"Rol actual: {usuario['rol']}")
                print()
                
                confirmacion = input(f"¿Actualizar el rol a 'super admin'? (s/n): ")
                
                if confirmacion.lower() == 's':
                    # Actualizar el rol
                    db.execute_query(
                        "UPDATE usuarios SET rol = ? WHERE id = ?",
                        ("super admin", usuario_id)
                    )
                    print()
                    print(f"✅ Rol actualizado exitosamente!")
                    print(f"   Usuario: {usuario['nombre']}")
                    print(f"   Nuevo rol: super admin")
                    print()
                    print("⚠️  IMPORTANTE: Reinicia el servidor para que los cambios surtan efecto.")
                else:
                    print("Operación cancelada.")
            
            except ValueError:
                print("❌ Error: Debes ingresar un número válido")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if db:
            try:
                db.disconnect()
            except:
                pass

if __name__ == "__main__":
    configurar_acceso_total()

