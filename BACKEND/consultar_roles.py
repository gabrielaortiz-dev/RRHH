"""Script para consultar roles de usuario del sistema"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def consultar_roles():
    """Consulta todos los roles del sistema desde la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Consultar roles de la tabla Roles
        try:
            cursor.execute("""
                SELECT 
                    id_rol,
                    nombre,
                    descripcion,
                    nivel_acceso,
                    es_sistema,
                    fecha_creacion
                FROM Roles
                ORDER BY nivel_acceso DESC, nombre
            """)
            roles = cursor.fetchall()
            
            if roles:
                print("\n" + "="*80)
                print("ROLES DE USUARIO DEL SISTEMA")
                print("="*80 + "\n")
                
                for rol in roles:
                    print(f"ID: {rol['id_rol']}")
                    print(f"Nombre: {rol['nombre'].upper()}")
                    print(f"Descripción: {rol['descripcion']}")
                    print(f"Nivel de Acceso: {rol['nivel_acceso']}/100")
                    print(f"Es Sistema: {'Sí' if rol['es_sistema'] else 'No'}")
                    if rol['fecha_creacion']:
                        print(f"Fecha Creación: {rol['fecha_creacion']}")
                    print("-" * 80)
                    print()
                
                print(f"\nTotal: {len(roles)} rol(es) definido(s)\n")
            else:
                print("\nNo se encontraron roles en la tabla Roles\n")
                # Intentar consultar roles desde la tabla usuarios
                cursor.execute("SELECT DISTINCT rol FROM usuarios WHERE rol IS NOT NULL")
                roles_usuarios = cursor.fetchall()
                if roles_usuarios:
                    print("Roles encontrados en la tabla usuarios:")
                    for r in roles_usuarios:
                        print(f"  - {r['rol']}")
                    print()
        except sqlite3.OperationalError as e:
            print(f"\nError al consultar tabla Roles: {e}\n")
            # Intentar consultar roles desde la tabla usuarios
            try:
                cursor.execute("SELECT DISTINCT rol FROM usuarios WHERE rol IS NOT NULL ORDER BY rol")
                roles_usuarios = cursor.fetchall()
                if roles_usuarios:
                    print("Roles encontrados en la tabla usuarios:")
                    for r in roles_usuarios:
                        print(f"  - {r['rol']}")
                    print()
            except Exception as e2:
                print(f"Error: {e2}\n")
        
        # Consultar también usuarios y sus roles asignados
        try:
            cursor.execute("""
                SELECT 
                    u.id,
                    u.nombre,
                    u.email,
                    u.rol,
                    u.activo
                FROM usuarios u
                ORDER BY u.rol, u.nombre
            """)
            usuarios = cursor.fetchall()
            
            if usuarios:
                print("\n" + "="*80)
                print("USUARIOS Y SUS ROLES ASIGNADOS")
                print("="*80 + "\n")
                
                roles_agrupados = {}
                for usuario in usuarios:
                    rol = usuario['rol'] or 'Sin rol'
                    if rol not in roles_agrupados:
                        roles_agrupados[rol] = []
                    estado = 'Activo' if usuario['activo'] else 'Inactivo'
                    roles_agrupados[rol].append({
                        'nombre': usuario['nombre'],
                        'email': usuario['email'],
                        'estado': estado
                    })
                
                for rol, usuarios_list in roles_agrupados.items():
                    print(f"\n{rol.upper()} ({len(usuarios_list)} usuario(s)):")
                    print("-" * 80)
                    for u in usuarios_list:
                        print(f"  • {u['nombre']} ({u['email']}) - {u['estado']}")
                
                print()
        except Exception as e:
            print(f"Error al consultar usuarios: {e}\n")
        
        conn.close()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}\n")

if __name__ == "__main__":
    consultar_roles()

