"""
Script para verificar la conexión y estructura de la base de datos SQLite.
Útil para verificar antes de abrir en DB Browser for SQLite.
"""
from database import get_db, init_db, DB_PATH
import os
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def verificar_base_datos():
    """Verifica la conexión y muestra la estructura de la base de datos."""
    
    print("=" * 60)
    print("VERIFICACION DE BASE DE DATOS SQLite")
    print("=" * 60)
    print()
    
    # Verificar que el archivo existe
    if os.path.exists(DB_PATH):
        file_size = os.path.getsize(DB_PATH)
        print(f"[OK] Base de datos encontrada: {DB_PATH}")
        print(f"     Tamaño: {file_size} bytes")
    else:
        print(f"[!] Base de datos no encontrada. Inicializando...")
        init_db()
        print(f"[OK] Base de datos creada: {DB_PATH}")
    
    print()
    
    # Conectar y verificar tablas
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            print(f"[OK] Conexion exitosa a la base de datos")
            print(f"[OK] Tablas encontradas: {len(tables)}")
            print()
            
            # Mostrar información de cada tabla
            for table_row in tables:
                table_name = table_row[0]
                print(f"Tabla: {table_name}")
                print("-" * 60)
                
                # Obtener información de columnas
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"  Columnas ({len(columns)}):")
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    null_text = "NOT NULL" if not_null else "NULL"
                    pk_text = " (PRIMARY KEY)" if pk else ""
                    default_text = f" DEFAULT {default_val}" if default_val else ""
                    print(f"    - {col_name:20} {col_type:15} {null_text}{default_text}{pk_text}")
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Registros: {count}")
                
                print()
            
            print("=" * 60)
            print("[OK] Verificacion completada exitosamente")
            print()
            print(f"Puedes abrir la base de datos en DB Browser for SQLite:")
            print(f"  Ruta: {DB_PATH}")
            print("=" * 60)
            
    except Exception as e:
        print(f"[ERROR] Error al conectar con la base de datos: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    verificar_base_datos()

