"""
Script para verificar el contenido de todas las tablas relevantes
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("VERIFICACION COMPLETA DE LA BASE DE DATOS")
    print("=" * 70)
    
    # 1. TABLA EMPLEADOS
    print("\n1. TABLA EMPLEADOS:")
    print("-" * 70)
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
        tabla_emp = cursor.fetchone()
        if tabla_emp:
            table_name = tabla_emp[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_emp = cursor.fetchone()[0]
            print(f"   Tabla: {table_name}")
            print(f"   Total registros: {total_emp}")
            
            # Mostrar rango de IDs
            cursor.execute(f"SELECT MIN(id_empleado), MAX(id_empleado) FROM {table_name}")
            try:
                min_id, max_id = cursor.fetchone()
                print(f"   IDs desde {min_id} hasta {max_id}")
            except:
                cursor.execute(f"SELECT MIN(id), MAX(id) FROM {table_name}")
                try:
                    min_id, max_id = cursor.fetchone()
                    print(f"   IDs desde {min_id} hasta {max_id}")
                except:
                    print("   No se pudo obtener rango de IDs")
            
            # Mostrar algunos ejemplos
            cursor.execute(f"SELECT id_empleado, nombre, apellido, correo FROM {table_name} LIMIT 3")
            empleados = cursor.fetchall()
            if empleados:
                print(f"   Ejemplos:")
                for emp in empleados:
                    print(f"      - ID {emp[0]}: {emp[1]} {emp[2]} ({emp[3]})")
        else:
            print("   [NO EXISTE] No se encontro tabla de empleados")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")
    
    # 2. TABLA USUARIOS
    print("\n2. TABLA USUARIOS (usuarios del sistema):")
    print("-" * 70)
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        tabla_usr = cursor.fetchone()
        if tabla_usr:
            table_name = tabla_usr[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_usr = cursor.fetchone()[0]
            print(f"   Tabla: {table_name}")
            print(f"   Total registros: {total_usr}")
            
            # Mostrar rango de IDs
            cursor.execute(f"SELECT MIN(id), MAX(id) FROM {table_name}")
            min_id, max_id = cursor.fetchone()
            print(f"   IDs desde {min_id} hasta {max_id}")
            
            # Mostrar algunos ejemplos
            cursor.execute(f"SELECT id, nombre, email, rol, activo FROM {table_name} ORDER BY id LIMIT 5")
            usuarios = cursor.fetchall()
            if usuarios:
                print(f"   Primeros 5 usuarios:")
                for usr in usuarios:
                    print(f"      - ID {usr[0]}: {usr[1]} ({usr[2]}) - Rol: {usr[3]} - Activo: {usr[4]}")
            
            # Buscar el usuario con ID 50 si existe
            cursor.execute(f"SELECT id, nombre, email, rol, activo FROM {table_name} WHERE id = 50")
            usuario_50 = cursor.fetchone()
            if usuario_50:
                print(f"\n   [ENCONTRADO] Usuario ID 50:")
                print(f"      - Nombre: {usuario_50[1]}")
                print(f"      - Email: {usuario_50[2]}")
                print(f"      - Rol: {usuario_50[3]}")
                print(f"      - Activo: {usuario_50[4]}")
            else:
                print(f"\n   [NO EXISTE] No hay usuario con ID 50")
        else:
            print("   [NO EXISTE] No se encontro tabla de usuarios")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")
    
    # 3. COMPARACION
    print("\n3. COMPARACION:")
    print("-" * 70)
    try:
        cursor.execute("SELECT COUNT(*) FROM empleados")
        total_emp = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usr = cursor.fetchone()[0]
        print(f"   Empleados: {total_emp}")
        print(f"   Usuarios del sistema: {total_usr}")
        print(f"\n   IMPORTANTE: Son tablas diferentes!")
        print(f"   - EMPLEADOS: Personas que trabajan en la empresa")
        print(f"   - USUARIOS: Cuentas de acceso al sistema (pueden ser mas que empleados)")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")
    
    # 4. LISTAR TODAS LAS TABLAS
    print("\n4. TODAS LAS TABLAS EN LA BASE DE DATOS:")
    print("-" * 70)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas = cursor.fetchall()
    for tabla in tablas:
        table_name = tabla[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   - {table_name}: {count} registros")
    
    print("\n" + "=" * 70)
    
    conn.close()
    
except Exception as e:
    print(f"[ERROR] Error: {str(e)}")
    import traceback
    traceback.print_exc()

