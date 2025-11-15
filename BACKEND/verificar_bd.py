"""
Script para verificar la conexión y estructura de la base de datos SQLite
Útil para verificar con DB Browser for SQLite
"""
import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def verificar_base_datos():
    """Verificar la conexión y mostrar información de la base de datos"""
    print("=" * 70)
    print("VERIFICACION DE BASE DE DATOS SQLite")
    print("=" * 70)
    print()
    
    # Verificar si el archivo existe
    if not os.path.exists(DATABASE_PATH):
        print(f"[ERROR] El archivo de base de datos no existe: {DATABASE_PATH}")
        print("\nLa base de datos se creará automáticamente al iniciar el servidor.")
        return False
    
    print(f"[OK] Archivo de base de datos encontrado:")
    print(f"     Ruta: {DATABASE_PATH}")
    
    # Obtener tamaño del archivo
    tamaño = os.path.getsize(DATABASE_PATH)
    print(f"     Tamaño: {tamaño:,} bytes ({tamaño / 1024:.2f} KB)")
    print()
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        print("[OK] Conexión exitosa a la base de datos")
        print()
        
        # Obtener versión de SQLite
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"[INFO] Versión de SQLite: {version}")
        print()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        
        print("=" * 70)
        print(f"TABLAS EN LA BASE DE DATOS ({len(tablas)} tablas)")
        print("=" * 70)
        print()
        
        total_registros = 0
        
        for tabla in tablas:
            nombre_tabla = tabla[0]
            
            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas = cursor.fetchall()
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            count = cursor.fetchone()[0]
            total_registros += count
            
            print(f"[TABLA] {nombre_tabla}")
            print(f"   Registros: {count}")
            print(f"   Columnas ({len(columnas)}):")
            
            for col in columnas:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = " [PRIMARY KEY]" if pk else ""
                not_null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"      - {col_name}: {col_type}{not_null_str}{default_str}{pk_str}")
            
            # Mostrar algunos registros de ejemplo (máximo 3)
            if count > 0:
                cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 3")
                registros = cursor.fetchall()
                if len(registros) > 0:
                    print(f"   Ejemplos de registros:")
                    for i, registro in enumerate(registros, 1):
                        # Crear diccionario con nombres de columnas
                        registro_dict = {}
                        for j, col in enumerate(columnas):
                            registro_dict[col[1]] = registro[j]
                        print(f"      [{i}] {registro_dict}")
            
            print()
        
        print("=" * 70)
        print(f"RESUMEN")
        print("=" * 70)
        print(f"Total de tablas: {len(tablas)}")
        print(f"Total de registros: {total_registros}")
        print()
        
        # Verificar integridad de la base de datos
        print("[INFO] Verificando integridad de la base de datos...")
        cursor.execute("PRAGMA integrity_check")
        resultado = cursor.fetchone()[0]
        
        if resultado == "ok":
            print("[OK] Integridad de la base de datos: OK")
        else:
            print(f"[ADVERTENCIA] Problemas de integridad: {resultado}")
        
        print()
        
        # Verificar foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        if fk_errors:
            print(f"[ADVERTENCIA] Se encontraron {len(fk_errors)} errores de foreign keys")
        else:
            print("[OK] Foreign keys: Sin errores")
        
        print()
        print("=" * 70)
        print("VERIFICACION COMPLETADA")
        print("=" * 70)
        print()
        print("Puedes abrir esta base de datos en DB Browser for SQLite:")
        print(f"Archivo: {DATABASE_PATH}")
        print()
        print("Pasos para abrir en DB Browser:")
        print("1. Abre DB Browser for SQLite")
        print("2. Click en 'Abrir Base de Datos'")
        print(f"3. Navega a: {DATABASE_PATH}")
        print("4. Click en 'Abrir'")
        print()
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Error al conectar a la base de datos: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_base_datos()

