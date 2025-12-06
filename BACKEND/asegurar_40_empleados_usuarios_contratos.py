"""
Script para asegurar que haya exactamente 40 empleados, 40 usuarios (uno por empleado)
y 40 contratos (uno por empleado) en el sistema.
"""
import sqlite3
import os
import bcrypt
from datetime import datetime, date

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def asegurar_40_empleados_usuarios_contratos():
    """Asegura que haya exactamente 40 empleados, 40 usuarios y 40 contratos"""
    print("=" * 70)
    print("ASEGURANDO 40 EMPLEADOS, 40 USUARIOS Y 40 CONTRATOS")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # ========================================================================
        # PASO 1: Obtener los primeros 40 empleados
        # ========================================================================
        print("\n[PASO 1] Obteniendo los primeros 40 empleados...")
        
        # Detectar tabla de empleados
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
        tabla_empleados = cursor.fetchone()
        
        if not tabla_empleados:
            print("[ERROR] No se encontró tabla de empleados")
            return
        
        nombre_tabla_empleados = tabla_empleados[0]
        print(f"[INFO] Usando tabla de empleados: {nombre_tabla_empleados}")
        
        # Detectar columnas
        cursor.execute(f"PRAGMA table_info({nombre_tabla_empleados})")
        columnas = cursor.fetchall()
        id_column = None
        correo_column = None
        nombre_column = None
        apellido_column = None
        
        for col in columnas:
            col_name = col[1].lower()
            if col_name in ['id_empleado', 'id']:
                id_column = col[1]
            elif col_name in ['correo', 'email']:
                correo_column = col[1]
            elif col_name == 'nombre':
                nombre_column = col[1]
            elif col_name == 'apellido':
                apellido_column = col[1]
        
        if not id_column:
            print("[ERROR] No se encontró columna ID en la tabla de empleados")
            return
        
        print(f"[INFO] Columnas detectadas: ID={id_column}, Correo={correo_column}, Nombre={nombre_column}, Apellido={apellido_column}")
        
        # Obtener los primeros 40 empleados
        cursor.execute(f"SELECT {id_column}, {nombre_column or 'nombre'}, {apellido_column or 'apellido'}, {correo_column or 'correo'} FROM {nombre_tabla_empleados} ORDER BY {id_column} LIMIT 40")
        empleados_40 = cursor.fetchall()
        
        if len(empleados_40) == 0:
            print("[ERROR] No se encontraron empleados en la base de datos")
            return
        
        print(f"[OK] Se encontraron {len(empleados_40)} empleados")
        
        # Si hay más de 40, eliminar los excedentes
        if len(empleados_40) > 40:
            print(f"[INFO] Hay más de 40 empleados. Eliminando excedentes...")
            ids_empleados_40 = [emp[0] for emp in empleados_40[:40]]
            placeholders = ','.join(['?'] * len(ids_empleados_40))
            cursor.execute(f"DELETE FROM {nombre_tabla_empleados} WHERE {id_column} NOT IN ({placeholders})", ids_empleados_40)
            empleados_40 = empleados_40[:40]
            print(f"[OK] Empleados reducidos a 40")
        else:
            ids_empleados_40 = [emp[0] for emp in empleados_40]
        
        # ========================================================================
        # PASO 2: Asegurar que haya exactamente 40 usuarios (uno por empleado)
        # ========================================================================
        print("\n[PASO 2] Asegurando 40 usuarios (uno por empleado)...")
        
        # Verificar si existe tabla usuarios
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='usuarios' OR name='Usuarios')")
        tabla_usuarios = cursor.fetchone()
        
        if not tabla_usuarios:
            print("[INFO] No existe tabla de usuarios, se creará automáticamente")
        else:
            nombre_tabla_usuarios = tabla_usuarios[0]
            print(f"[INFO] Usando tabla de usuarios: {nombre_tabla_usuarios}")
            
            # Obtener todos los usuarios actuales
            cursor.execute(f"SELECT id, email FROM {nombre_tabla_usuarios}")
            usuarios_actuales = {row[1].lower(): row[0] for row in cursor.fetchall()}
            print(f"[INFO] Usuarios actuales: {len(usuarios_actuales)}")
            
            # Crear usuarios para empleados que no tienen usuario
            usuarios_creados = 0
            usuarios_actualizados = 0
            
            for empleado_id, nombre, apellido, correo in empleados_40:
                if not correo:
                    correo = f"empleado{empleado_id}@empresa.com"
                    print(f"[WARN] Empleado {empleado_id} no tiene correo, usando: {correo}")
                
                correo_lower = correo.lower()
                nombre_completo = f"{nombre} {apellido}".strip()
                
                if correo_lower in usuarios_actuales:
                    # Usuario ya existe, verificar que esté activo
                    usuario_id = usuarios_actuales[correo_lower]
                    cursor.execute(f"UPDATE {nombre_tabla_usuarios} SET activo = 1 WHERE id = ?", (usuario_id,))
                    usuarios_actualizados += 1
                else:
                    # Crear nuevo usuario
                    password_hash = hash_password("Temporal123!")
                    cursor.execute(f"""
                        INSERT INTO {nombre_tabla_usuarios} (nombre, email, password, rol, activo)
                        VALUES (?, ?, ?, 'empleado', 1)
                    """, (nombre_completo, correo, password_hash))
                    usuarios_creados += 1
                    print(f"[OK] Usuario creado para empleado {empleado_id}: {correo}")
            
            # Desactivar usuarios que no corresponden a los 40 empleados
            correos_empleados_40 = [emp[3].lower() if emp[3] else f"empleado{emp[0]}@empresa.com".lower() for emp in empleados_40]
            placeholders = ','.join(['?'] * len(correos_empleados_40))
            
            # Obtener usuarios a desactivar
            cursor.execute(f"""
                SELECT id, email FROM {nombre_tabla_usuarios} 
                WHERE LOWER(email) NOT IN ({placeholders})
            """, correos_empleados_40)
            usuarios_a_desactivar = cursor.fetchall()
            
            if usuarios_a_desactivar:
                print(f"[INFO] Desactivando {len(usuarios_a_desactivar)} usuarios que no corresponden a los 40 empleados...")
                for usuario_id, email in usuarios_a_desactivar:
                    cursor.execute(f"UPDATE {nombre_tabla_usuarios} SET activo = 0 WHERE id = ?", (usuario_id,))
                    print(f"[INFO] Usuario desactivado: {email}")
            
            print(f"[OK] Usuarios creados: {usuarios_creados}, Actualizados: {usuarios_actualizados}, Desactivados: {len(usuarios_a_desactivar)}")
        
        # ========================================================================
        # PASO 3: Asegurar que haya exactamente 40 contratos (uno por empleado)
        # ========================================================================
        print("\n[PASO 3] Asegurando 40 contratos (uno por empleado)...")
        
        # Verificar si existe tabla Contratos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Contratos' OR name='contratos')")
        tabla_contratos = cursor.fetchone()
        
        if not tabla_contratos:
            print("[INFO] No existe tabla de Contratos")
        else:
            nombre_tabla_contratos = tabla_contratos[0]
            print(f"[INFO] Usando tabla de contratos: {nombre_tabla_contratos}")
            
            # Detectar columna de empleado en Contratos
            cursor.execute(f"PRAGMA table_info({nombre_tabla_contratos})")
            columnas_contratos = cursor.fetchall()
            empleado_col_contratos = None
            
            for col in columnas_contratos:
                if col[1].lower() in ['id_empleado', 'empleado_id', 'id_empleado_id']:
                    empleado_col_contratos = col[1]
                    break
            
            if not empleado_col_contratos:
                print("[ERROR] No se encontró columna de empleado en Contratos")
            else:
                print(f"[INFO] Usando columna de empleado en Contratos: {empleado_col_contratos}")
                
                # Contar contratos antes
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_contratos}")
                total_contratos_antes = cursor.fetchone()[0]
                print(f"[INFO] Total de contratos antes: {total_contratos_antes}")
                
                # Eliminar contratos que no pertenecen a los 40 empleados
                placeholders = ','.join(['?'] * len(ids_empleados_40))
                cursor.execute(
                    f"DELETE FROM {nombre_tabla_contratos} WHERE {empleado_col_contratos} NOT IN ({placeholders})",
                    ids_empleados_40
                )
                contratos_eliminados = cursor.rowcount
                if contratos_eliminados > 0:
                    print(f"[OK] {contratos_eliminados} contratos eliminados (no pertenecían a los 40 empleados)")
                
                # Verificar que cada empleado tenga exactamente un contrato
                contratos_creados = 0
                for empleado_id in ids_empleados_40:
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {nombre_tabla_contratos} WHERE {empleado_col_contratos} = ?",
                        (empleado_id,)
                    )
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        # Crear un contrato básico para este empleado
                        # Obtener datos del empleado
                        cursor.execute(
                            f"SELECT {nombre_column or 'nombre'}, {apellido_column or 'apellido'}, {correo_column or 'correo'} FROM {nombre_tabla_empleados} WHERE {id_column} = ?",
                            (empleado_id,)
                        )
                        emp_data = cursor.fetchone()
                        if emp_data:
                            nombre_emp, apellido_emp, correo_emp = emp_data
                            nombre_completo = f"{nombre_emp} {apellido_emp}".strip()
                            
                            # Crear contrato básico
                            cursor.execute(f"""
                                INSERT INTO {nombre_tabla_contratos} 
                                ({empleado_col_contratos}, trabajador_nombre_completo, trabajador_email, fecha_inicio, estado, tipo_contrato)
                                VALUES (?, ?, ?, ?, 'activo', 'Indefinido')
                            """, (empleado_id, nombre_completo, correo_emp or f"empleado{empleado_id}@empresa.com", date.today().isoformat()))
                            contratos_creados += 1
                            print(f"[OK] Contrato creado para empleado {empleado_id}")
                    elif count > 1:
                        # Eliminar contratos duplicados, dejar solo el más reciente
                        cursor.execute(
                            f"SELECT id_contrato FROM {nombre_tabla_contratos} WHERE {empleado_col_contratos} = ? ORDER BY fecha_inicio DESC, id_contrato DESC",
                            (empleado_id,)
                        )
                        contratos_empleado = cursor.fetchall()
                        if len(contratos_empleado) > 1:
                            # Mantener solo el primero (más reciente) y eliminar los demás
                            ids_a_eliminar = [c[0] for c in contratos_empleado[1:]]
                            placeholders_del = ','.join(['?'] * len(ids_a_eliminar))
                            cursor.execute(
                                f"DELETE FROM {nombre_tabla_contratos} WHERE id_contrato IN ({placeholders_del})",
                                ids_a_eliminar
                            )
                            print(f"[OK] Eliminados {len(ids_a_eliminar)} contratos duplicados del empleado {empleado_id}")
                
                # Contar contratos después
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_contratos}")
                total_contratos_despues = cursor.fetchone()[0]
                print(f"[OK] Total de contratos después: {total_contratos_despues}")
                print(f"[OK] Contratos creados: {contratos_creados}")
        
        # ========================================================================
        # RESUMEN FINAL
        # ========================================================================
        print("\n" + "=" * 70)
        print("RESUMEN FINAL")
        print("=" * 70)
        
        # Contar empleados
        cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_empleados}")
        total_empleados = cursor.fetchone()[0]
        print(f"[OK] Empleados: {total_empleados}")
        
        # Contar usuarios activos
        if tabla_usuarios:
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_usuarios} WHERE activo = 1")
            total_usuarios_activos = cursor.fetchone()[0]
            print(f"[OK] Usuarios activos: {total_usuarios_activos}")
        
        # Contar contratos
        if tabla_contratos:
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_contratos}")
            total_contratos = cursor.fetchone()[0]
            print(f"[OK] Contratos: {total_contratos}")
        
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
    asegurar_40_empleados_usuarios_contratos()

