"""
Script para actualizar la estructura de la tabla Nomina
Agrega las columnas faltantes si la tabla tiene la estructura antigua
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("ACTUALIZANDO ESTRUCTURA DE TABLA NOMINA")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Obtener las columnas actuales de la tabla Nomina
    cursor.execute("PRAGMA table_info(Nomina)")
    columnas_actuales = {row[1] for row in cursor.fetchall()}
    
    print(f"Columnas actuales en Nomina: {sorted(columnas_actuales)}")
    print()
    
    # Columnas requeridas según la nueva estructura
    columnas_requeridas = {
        'id_nomina': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'id_empleado': 'INTEGER',
        'nombre_empleado': 'VARCHAR(200)',
        'mes': 'INTEGER NOT NULL',
        'anio': 'INTEGER NOT NULL',
        'periodo': 'TEXT NOT NULL',
        'salario_base': 'DECIMAL(10,2) NOT NULL',
        'total_bonificaciones': 'DECIMAL(10,2) DEFAULT 0',
        'total_deducciones': 'DECIMAL(10,2) DEFAULT 0',
        'salario_neto': 'DECIMAL(10,2) NOT NULL',
        'fecha_pago': 'DATE',
        'estado': 'VARCHAR(20) DEFAULT \'pendiente\'',
        'fecha_creacion': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'fecha_modificacion': 'DATETIME',
        'creado_por': 'INTEGER',
        'modificado_por': 'INTEGER',
        'observaciones': 'TEXT'
    }
    
    # Verificar y agregar columnas faltantes
    columnas_agregadas = []
    columnas_faltantes = []
    
    for columna, tipo in columnas_requeridas.items():
        if columna == 'id_nomina':
            continue  # Skip primary key
        if columna not in columnas_actuales:
            columnas_faltantes.append(columna)
            try:
                # SQLite solo permite agregar columnas sin NOT NULL directamente
                # Simplificamos el tipo para ALTER TABLE
                tipo_simple = tipo
                # Remover restricciones que SQLite no soporta en ALTER TABLE
                tipo_simple = tipo_simple.replace(' NOT NULL', '')
                tipo_simple = tipo_simple.replace(' DEFAULT 0', '')
                tipo_simple = tipo_simple.replace(' DEFAULT \'pendiente\'', '')
                tipo_simple = tipo_simple.replace(' DEFAULT CURRENT_TIMESTAMP', '')
                tipo_simple = tipo_simple.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'INTEGER')
                
                cursor.execute(f"ALTER TABLE Nomina ADD COLUMN {columna} {tipo_simple}")
                
                # Actualizar valores por defecto después de agregar la columna
                if 'DEFAULT 0' in tipo:
                    cursor.execute(f"UPDATE Nomina SET {columna} = 0 WHERE {columna} IS NULL")
                elif 'DEFAULT \'pendiente\'' in tipo:
                    cursor.execute(f"UPDATE Nomina SET {columna} = 'pendiente' WHERE {columna} IS NULL")
                elif 'DEFAULT CURRENT_TIMESTAMP' in tipo:
                    cursor.execute(f"UPDATE Nomina SET {columna} = CURRENT_TIMESTAMP WHERE {columna} IS NULL")
                
                # Actualizar valores calculados
                if columna == 'periodo':
                    cursor.execute("UPDATE Nomina SET periodo = printf('%02d/%d', mes, anio) WHERE periodo IS NULL OR periodo = ''")
                elif columna == 'nombre_empleado':
                    try:
                        cursor.execute("""
                            UPDATE Nomina 
                            SET nombre_empleado = (
                                SELECT nombre || ' ' || apellido 
                                FROM Empleados 
                                WHERE Empleados.id_empleado = Nomina.id_empleado
                            )
                            WHERE nombre_empleado IS NULL OR nombre_empleado = ''
                        """)
                    except:
                        pass  # Si falla, no es crítico
                
                columnas_agregadas.append(columna)
                print(f"[OK] Columna '{columna}' agregada exitosamente")
            except Exception as e:
                print(f"[ERROR] Error al agregar columna '{columna}': {e}")
    
    if columnas_agregadas:
        conn.commit()
        print()
        print(f"[OK] Se agregaron {len(columnas_agregadas)} columnas:")
        for col in columnas_agregadas:
            print(f"   - {col}")
    else:
        print("[OK] La tabla Nomina ya tiene todas las columnas necesarias")
    
    if columnas_faltantes:
        print()
        print(f"[INFO] Columnas que faltaban: {columnas_faltantes}")
    
    # Verificar estructura final
    print()
    print("=" * 70)
    print("ESTRUCTURA FINAL DE LA TABLA NOMINA:")
    print("=" * 70)
    cursor.execute("PRAGMA table_info(Nomina)")
    for row in cursor.fetchall():
        print(f"  {row[1]} ({row[2]})")
    
    # Crear índices si no existen
    print()
    print("=" * 70)
    print("CREANDO ÍNDICES:")
    print("=" * 70)
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_nomina_id_empleado ON Nomina(id_empleado)",
        "CREATE INDEX IF NOT EXISTS idx_nomina_mes_anio ON Nomina(mes, anio)",
        "CREATE INDEX IF NOT EXISTS idx_nomina_fecha_creacion ON Nomina(fecha_creacion DESC)",
        "CREATE INDEX IF NOT EXISTS idx_nomina_estado ON Nomina(estado)"
    ]
    
    for idx_sql in indices:
        try:
            cursor.execute(idx_sql)
            print(f"[OK] Indice creado: {idx_sql.split('ON')[1].strip()}")
        except Exception as e:
            print(f"[WARNING] Error al crear indice: {e}")
    
    conn.commit()
    
    print()
    print("=" * 70)
    print("[OK] ACTUALIZACION COMPLETADA")
    print("=" * 70)
    
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] ERROR: {e}")
    import traceback
    print(traceback.format_exc())
    if 'conn' in locals():
        conn.close()

