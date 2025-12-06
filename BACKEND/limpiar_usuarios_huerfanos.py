"""
Script para limpiar usuarios huérfanos (usuarios sin empleados asociados)
y asegurar que solo existan usuarios relacionados con empleados.
"""
import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def limpiar_usuarios_huerfanos():
    """Desactiva usuarios que no tienen un empleado asociado"""
    print("=" * 70)
    print("LIMPIEZA DE USUARIOS HUÉRFANOS")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Verificar si existe tabla Empleados
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
        tabla_empleados = cursor.fetchone()
        
        if not tabla_empleados:
            print("[ERROR] No se encontró tabla de empleados")
            return
        
        nombre_tabla_empleados = tabla_empleados[0]
        print(f"[INFO] Usando tabla de empleados: {nombre_tabla_empleados}")
        
        # Detectar columna de correo en Empleados
        cursor.execute(f"PRAGMA table_info({nombre_tabla_empleados})")
        columnas = cursor.fetchall()
        correo_column = None
        
        for col in columnas:
            col_name = col[1].lower()
            if col_name in ['correo', 'email']:
                correo_column = col[1]
                break
        
        if not correo_column:
            print("[ERROR] No se encontró columna de correo/email en la tabla de empleados")
            return
        
        print(f"[INFO] Usando columna de correo: {correo_column}")
        
        # Obtener todos los correos de empleados activos
        cursor.execute(f"SELECT DISTINCT LOWER({correo_column}) FROM {nombre_tabla_empleados} WHERE {correo_column} IS NOT NULL AND {correo_column} != ''")
        correos_empleados = {row[0] for row in cursor.fetchall()}
        print(f"[INFO] Empleados con correo: {len(correos_empleados)}")
        
        # Obtener todos los usuarios activos
        cursor.execute("SELECT id, email, nombre, activo FROM usuarios")
        todos_usuarios = cursor.fetchall()
        print(f"[INFO] Total de usuarios en la base de datos: {len(todos_usuarios)}")
        
        # Identificar usuarios huérfanos (sin empleado asociado)
        usuarios_huerfanos = []
        usuarios_con_empleado = []
        
        for usuario_id, email, nombre, activo in todos_usuarios:
            if email and email.lower() in correos_empleados:
                usuarios_con_empleado.append((usuario_id, email, nombre))
            else:
                usuarios_huerfanos.append((usuario_id, email, nombre, activo))
        
        print(f"\n[INFO] Usuarios con empleado asociado: {len(usuarios_con_empleado)}")
        print(f"[INFO] Usuarios huérfanos (sin empleado): {len(usuarios_huerfanos)}")
        
        # Desactivar usuarios huérfanos que están activos
        usuarios_desactivados = 0
        usuarios_ya_inactivos = 0
        
        for usuario_id, email, nombre, activo in usuarios_huerfanos:
            if activo == 1:
                cursor.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
                usuarios_desactivados += 1
                print(f"[INFO] Usuario desactivado: {nombre} ({email})")
            else:
                usuarios_ya_inactivos += 1
        
        print(f"\n[OK] Usuarios desactivados: {usuarios_desactivados}")
        print(f"[INFO] Usuarios ya inactivos: {usuarios_ya_inactivos}")
        
        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
        total_activos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 0")
        total_inactivos = cursor.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("RESUMEN FINAL")
        print("=" * 70)
        print(f"[OK] Usuarios activos (con empleado): {total_activos}")
        print(f"[INFO] Usuarios inactivos (huérfanos): {total_inactivos}")
        print(f"[INFO] Total de usuarios: {total_activos + total_inactivos}")
        
        conn.commit()
        print("\n" + "=" * 70)
        print("[OK] PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

if __name__ == "__main__":
    limpiar_usuarios_huerfanos()

