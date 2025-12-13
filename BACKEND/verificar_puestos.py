"""Script para verificar puestos en la base de datos"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def verificar_puestos():
    """Verifica qué puestos hay en la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si existe tabla Puestos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        print(f"Tablas encontradas: {tablas}\n")
        
        if 'Puestos' in tablas:
            cursor.execute("SELECT * FROM Puestos ORDER BY id_puesto")
            puestos = cursor.fetchall()
            print("=== PUESTOS EN LA BASE DE DATOS ===\n")
            for puesto in puestos:
                nombre = puesto['nombre_puesto'] if 'nombre_puesto' in puesto.keys() else 'N/A'
                print(f"ID: {puesto['id_puesto']} - {nombre}")
            print(f"\nTotal: {len(puestos)} puesto(s)\n")
        else:
            print("No se encontró la tabla Puestos\n")
        
        # Verificar algunos empleados para ver sus id_puesto
        print("=== EJEMPLO DE EMPLEADOS Y SUS ID_PUESTO ===\n")
        cursor.execute("SELECT nombre, apellido, id_puesto FROM Empleados LIMIT 5")
        empleados = cursor.fetchall()
        for emp in empleados:
            print(f"{emp['nombre']} {emp['apellido']} - id_puesto: {emp['id_puesto']}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == "__main__":
    verificar_puestos()

