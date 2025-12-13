"""Script para consultar empleados y sus puestos"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def consultar_empleados():
    """Consulta empleados y sus puestos desde la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Primero verificar qué tablas existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        
        # Intentar primero con tabla Empleados (mayúscula) y Puestos
        try:
            # Verificar si existe tabla Puestos
            if 'Puestos' in tablas:
                cursor.execute("""
                    SELECT 
                        e.nombre, 
                        e.apellido, 
                        COALESCE(p.nombre_puesto, 
                            CASE 
                                WHEN e.id_puesto IS NOT NULL THEN 'Puesto ID: ' || CAST(e.id_puesto AS TEXT)
                                ELSE 'Sin puesto asignado'
                            END
                        ) as puesto
                    FROM Empleados e
                    LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
                    ORDER BY e.nombre, e.apellido
                """)
            else:
                # Si no hay tabla Puestos, usar solo Empleados
                cursor.execute("""
                    SELECT 
                        nombre, 
                        apellido, 
                        CASE 
                            WHEN id_puesto IS NOT NULL THEN 'Puesto ID: ' || CAST(id_puesto AS TEXT)
                            ELSE 'Sin puesto asignado'
                        END as puesto
                    FROM Empleados
                    ORDER BY nombre, apellido
                """)
            
            rows = cursor.fetchall()
            
            if rows:
                print("\n=== EMPLEADOS Y SUS PUESTOS ===\n")
                for row in rows:
                    nombre_completo = f"{row['nombre']} {row['apellido']}".strip()
                    puesto = row['puesto']
                    print(f"{nombre_completo} - {puesto}")
                print(f"\nTotal: {len(rows)} empleado(s)\n")
            else:
                print("\nNo se encontraron empleados en la tabla Empleados\n")
        except sqlite3.OperationalError as e:
            # Si falla, intentar con tabla empleados (minúscula)
            try:
                cursor.execute("""
                    SELECT 
                        nombre, 
                        apellido, 
                        COALESCE(puesto, 'Sin puesto asignado') as puesto
                    FROM empleados
                    WHERE activo = 1
                    ORDER BY nombre, apellido
                """)
                rows = cursor.fetchall()
                
                if rows:
                    print("\n=== EMPLEADOS Y SUS PUESTOS ===\n")
                    for row in rows:
                        nombre_completo = f"{row['nombre']} {row['apellido']}".strip()
                        puesto = row['puesto'] if row['puesto'] else 'Sin puesto asignado'
                        print(f"{nombre_completo} - {puesto}")
                    print(f"\nTotal: {len(rows)} empleado(s)\n")
                else:
                    print("\nNo se encontraron empleados\n")
            except Exception as e2:
                print(f"\nError al consultar empleados: {e2}\n")
        
        conn.close()
    except Exception as e:
        print(f"\nError al conectar con la base de datos: {e}\n")

if __name__ == "__main__":
    consultar_empleados()

