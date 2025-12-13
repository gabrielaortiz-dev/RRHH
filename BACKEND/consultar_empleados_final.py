"""Script para consultar empleados y sus puestos con mapeo correcto"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def consultar_empleados():
    """Consulta empleados y sus puestos desde la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Primero obtener todos los puestos para crear un diccionario
        puestos_dict = {}
        try:
            cursor.execute("SELECT id_puesto, nombre_puesto FROM Puestos")
            for row in cursor.fetchall():
                puestos_dict[row['id_puesto']] = row['nombre_puesto']
        except:
            pass
        
        # Intentar con tabla Empleados (mayúscula)
        try:
            # Verificar columnas disponibles
            cursor.execute("PRAGMA table_info(Empleados)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            # Construir query según columnas disponibles
            if 'id_puesto' in columnas:
                query = """
                    SELECT 
                        nombre, 
                        apellido, 
                        id_puesto
                    FROM Empleados
                    ORDER BY nombre, apellido
                """
            elif 'puesto' in columnas:
                query = """
                    SELECT 
                        nombre, 
                        apellido, 
                        puesto as id_puesto
                    FROM Empleados
                    ORDER BY nombre, apellido
                """
            else:
                query = """
                    SELECT 
                        nombre, 
                        apellido, 
                        NULL as id_puesto
                    FROM Empleados
                    ORDER BY nombre, apellido
                """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if rows:
                print("\n=== EMPLEADOS Y SUS PUESTOS ===\n")
                for row in rows:
                    nombre_completo = f"{row['nombre']} {row['apellido']}".strip()
                    id_puesto = row['id_puesto']
                    
                    # Intentar convertir a int para el lookup
                    puesto = "Sin puesto asignado"
                    if id_puesto is not None:
                        try:
                            id_int = int(id_puesto)
                            if id_int in puestos_dict:
                                puesto = puestos_dict[id_int]
                            else:
                                puesto = f"Puesto ID: {id_int}"
                        except (ValueError, TypeError):
                            puesto = f"Puesto: {id_puesto}" if id_puesto else "Sin puesto asignado"
                    
                    print(f"{nombre_completo} - {puesto}")
                print(f"\nTotal: {len(rows)} empleado(s)\n")
            else:
                print("\nNo se encontraron empleados\n")
                
        except Exception as e:
            print(f"Error: {e}\n")
            # Intentar con tabla empleados (minúscula)
            try:
                cursor.execute("""
                    SELECT 
                        nombre, 
                        apellido, 
                        puesto
                    FROM empleados
                    WHERE activo = 1
                    ORDER BY nombre, apellido
                """)
                rows = cursor.fetchall()
                
                if rows:
                    print("\n=== EMPLEADOS Y SUS PUESTOS ===\n")
                    for row in rows:
                        nombre_completo = f"{row['nombre']} {row['apellido']}".strip()
                        puesto_val = row['puesto']
                        
                        # Intentar convertir a int si es posible
                        try:
                            if puesto_val and int(puesto_val) in puestos_dict:
                                puesto = puestos_dict[int(puesto_val)]
                            else:
                                puesto = puesto_val if puesto_val else "Sin puesto asignado"
                        except:
                            puesto = puesto_val if puesto_val else "Sin puesto asignado"
                        
                        print(f"{nombre_completo} - {puesto}")
                    print(f"\nTotal: {len(rows)} empleado(s)\n")
            except Exception as e2:
                print(f"Error al consultar: {e2}\n")
        
        conn.close()
    except Exception as e:
        print(f"Error al conectar: {e}\n")

if __name__ == "__main__":
    consultar_empleados()

