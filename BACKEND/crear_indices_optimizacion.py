"""
Script para crear índices que mejoran el rendimiento de las consultas
Ejecuta este script para optimizar la base de datos existente
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("CREANDO ÍNDICES PARA OPTIMIZACIÓN")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=20.0)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    indices = [
        # Índices para tabla Nomina
        ("idx_nomina_id_empleado", "CREATE INDEX IF NOT EXISTS idx_nomina_id_empleado ON Nomina(id_empleado)"),
        ("idx_nomina_mes_anio", "CREATE INDEX IF NOT EXISTS idx_nomina_mes_anio ON Nomina(mes, anio)"),
        ("idx_nomina_fecha_creacion", "CREATE INDEX IF NOT EXISTS idx_nomina_fecha_creacion ON Nomina(fecha_creacion DESC)"),
        ("idx_nomina_estado", "CREATE INDEX IF NOT EXISTS idx_nomina_estado ON Nomina(estado)"),
        
        # Índices para tabla Nomina_Bonificaciones
        ("idx_bonificaciones_id_nomina", "CREATE INDEX IF NOT EXISTS idx_bonificaciones_id_nomina ON Nomina_Bonificaciones(id_nomina)"),
        
        # Índices para tabla Nomina_Deducciones
        ("idx_deducciones_id_nomina", "CREATE INDEX IF NOT EXISTS idx_deducciones_id_nomina ON Nomina_Deducciones(id_nomina)"),
        
        # Índices para tabla Empleados (mejora consultas de JOIN)
        ("idx_empleados_id_empleado", "CREATE INDEX IF NOT EXISTS idx_empleados_id_empleado ON Empleados(id_empleado)"),
        ("idx_empleados_departamento", "CREATE INDEX IF NOT EXISTS idx_empleados_departamento ON Empleados(id_departamento)"),
        
        # Índices para tabla Asistencias
        ("idx_asistencias_id_empleado", "CREATE INDEX IF NOT EXISTS idx_asistencias_id_empleado ON Asistencias(id_empleado)"),
        ("idx_asistencias_fecha", "CREATE INDEX IF NOT EXISTS idx_asistencias_fecha ON Asistencias(fecha)"),
        
        # Índices para tabla Contratos
        ("idx_contratos_id_empleado", "CREATE INDEX IF NOT EXISTS idx_contratos_id_empleado ON Contratos(id_empleado)"),
    ]
    
    indices_creados = []
    indices_ya_existentes = []
    errores = []
    
    for nombre_indice, sql in indices:
        try:
            cursor.execute(sql)
            # Verificar si se creó
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name=?
            """, (nombre_indice,))
            if cursor.fetchone():
                indices_creados.append(nombre_indice)
                print(f"[OK] Índice creado: {nombre_indice}")
            else:
                indices_ya_existentes.append(nombre_indice)
                print(f"[INFO] Índice ya existe: {nombre_indice}")
        except Exception as e:
            errores.append((nombre_indice, str(e)))
            print(f"[ERROR] Error al crear índice {nombre_indice}: {e}")
    
    conn.commit()
    
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Índices creados: {len(indices_creados)}")
    print(f"Índices ya existentes: {len(indices_ya_existentes)}")
    print(f"Errores: {len(errores)}")
    
    if errores:
        print("\nErrores encontrados:")
        for nombre, error in errores:
            print(f"  - {nombre}: {error}")
    
    print()
    print("[OK] Proceso completado!")
    print()
    print("NOTA: Los índices mejorarán significativamente el rendimiento")
    print("de las consultas, especialmente con grandes volúmenes de datos.")
    
    conn.close()
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("\n[ERROR] Base de datos bloqueada")
        print("Cierra DB Browser for SQLite y cualquier otra aplicación")
        print("que esté usando la base de datos, luego ejecuta este script nuevamente.")
    else:
        print(f"\n[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"\n[ERROR] Error inesperado: {e}")
    import traceback
    traceback.print_exc()

