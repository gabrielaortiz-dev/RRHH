"""
Script para Vincular Empleados con Usuarios y Roles
====================================================

Este script:
1. Agrega columna usuario_id a la tabla empleados
2. Crea usuarios para cada empleado que no tenga uno
3. Asigna roles automáticamente según el puesto del empleado

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
import os
import bcrypt
from datetime import datetime


def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def agregar_columna_usuario_id():
    """Agrega columna usuario_id a la tabla empleados"""
    print("\n" + "="*70)
    print("PASO 1: Agregar columna usuario_id a empleados")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(empleados)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'usuario_id' in columnas:
            print("   [OK] La columna usuario_id ya existe")
            conn.close()
            return
        
        print("   [INFO] Agregando columna usuario_id...")
        
        # Agregar columna
        cursor.execute("""
            ALTER TABLE empleados 
            ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)
        """)
        
        conn.commit()
        print("   [OK] Columna usuario_id agregada exitosamente")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()


def crear_usuarios_para_empleados():
    """Crea usuarios para empleados que no tienen uno"""
    print("\n" + "="*70)
    print("PASO 2: Crear usuarios para empleados")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Obtener empleados sin usuario
        cursor.execute("""
            SELECT id, nombre, apellido, email
            FROM empleados
            WHERE usuario_id IS NULL AND activo = 1
        """)
        
        empleados_sin_usuario = cursor.fetchall()
        
        if not empleados_sin_usuario:
            print("\n   [INFO] Todos los empleados ya tienen usuario asignado")
            conn.close()
            return
        
        print(f"\n   [INFO] Se encontraron {len(empleados_sin_usuario)} empleados sin usuario")
        print("   [INFO] Creando usuarios...")
        
        creados = 0
        
        for emp_id, nombre, apellido, email in empleados_sin_usuario:
            try:
                # Verificar si ya existe un usuario con ese email
                cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
                usuario_existente = cursor.fetchone()
                
                if usuario_existente:
                    # Ya existe el usuario, solo vincularlo
                    usuario_id = usuario_existente[0]
                    cursor.execute("""
                        UPDATE empleados SET usuario_id = ? WHERE id = ?
                    """, (usuario_id, emp_id))
                    print(f"      ✓ Vinculado: {nombre} {apellido} → Usuario existente")
                else:
                    # Crear nuevo usuario
                    nombre_completo = f"{nombre} {apellido}"
                    password_default = "Empleado123"  # Contraseña por defecto
                    password_hash = hash_password(password_default)
                    
                    cursor.execute("""
                        INSERT INTO usuarios (nombre, email, password, activo)
                        VALUES (?, ?, ?, 1)
                    """, (nombre_completo, email, password_hash))
                    
                    usuario_id = cursor.lastrowid
                    
                    # Vincular empleado con usuario
                    cursor.execute("""
                        UPDATE empleados SET usuario_id = ? WHERE id = ?
                    """, (usuario_id, emp_id))
                    
                    print(f"      ✓ Creado: {nombre} {apellido} → Usuario ID {usuario_id}")
                    creados += 1
                    
            except Exception as e:
                print(f"      ✗ Error con {nombre} {apellido}: {e}")
                continue
        
        conn.commit()
        print(f"\n   [OK] {creados} usuarios nuevos creados")
        print(f"   [OK] Total de empleados vinculados: {len(empleados_sin_usuario)}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()


def asignar_roles_segun_puesto():
    """Asigna roles a usuarios según el puesto del empleado"""
    print("\n" + "="*70)
    print("PASO 3: Asignar roles según puestos")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Obtener empleados con usuario pero sin rol asignado
        cursor.execute("""
            SELECT 
                e.id as emp_id,
                e.nombre,
                e.apellido,
                e.usuario_id,
                e.puesto as puesto_id,
                p.nombre_puesto,
                p.id_rol
            FROM empleados e
            LEFT JOIN Puestos p ON e.puesto = p.id_puesto
            WHERE e.usuario_id IS NOT NULL 
              AND e.activo = 1
              AND e.usuario_id NOT IN (
                  SELECT usuario_id FROM Usuarios_Roles WHERE activo = 1
              )
        """)
        
        empleados_sin_rol = cursor.fetchall()
        
        if not empleados_sin_rol:
            print("\n   [INFO] Todos los empleados con usuario ya tienen rol asignado")
            conn.close()
            return
        
        print(f"\n   [INFO] Se encontraron {len(empleados_sin_rol)} empleados sin rol")
        print("   [INFO] Asignando roles...")
        
        asignados = 0
        sin_puesto = 0
        
        for emp_id, nombre, apellido, usuario_id, puesto_id, puesto_nombre, rol_id in empleados_sin_rol:
            try:
                if not rol_id:
                    print(f"      ⚠️  {nombre} {apellido} - Puesto sin rol asignado")
                    sin_puesto += 1
                    continue
                
                # Asignar rol al usuario
                cursor.execute("""
                    INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                    VALUES (?, ?, 1, 1)
                """, (usuario_id, rol_id))
                
                # Registrar en historial
                cursor.execute("""
                    INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
                    VALUES (?, ?, 'Asignación automática según puesto')
                """, (usuario_id, rol_id))
                
                # Obtener nombre del rol
                cursor.execute("SELECT nombre FROM Roles WHERE id_rol = ?", (rol_id,))
                rol_nombre = cursor.fetchone()[0]
                
                print(f"      ✓ {nombre} {apellido} → {puesto_nombre} → {rol_nombre}")
                asignados += 1
                
            except Exception as e:
                print(f"      ✗ Error con {nombre} {apellido}: {e}")
                continue
        
        conn.commit()
        print(f"\n   [OK] {asignados} roles asignados exitosamente")
        
        if sin_puesto > 0:
            print(f"   [INFO] {sin_puesto} empleados sin puesto/rol definido")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def generar_reporte_final():
    """Genera un reporte del estado actual"""
    print("\n" + "="*70)
    print("REPORTE FINAL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Total de empleados
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE activo = 1")
        total_empleados = cursor.fetchone()[0]
        
        # Empleados con usuario
        cursor.execute("""
            SELECT COUNT(*) FROM empleados 
            WHERE usuario_id IS NOT NULL AND activo = 1
        """)
        empleados_con_usuario = cursor.fetchone()[0]
        
        # Empleados con rol
        cursor.execute("""
            SELECT COUNT(DISTINCT e.id)
            FROM empleados e
            INNER JOIN Usuarios_Roles ur ON e.usuario_id = ur.usuario_id
            WHERE e.activo = 1 AND ur.activo = 1
        """)
        empleados_con_rol = cursor.fetchone()[0]
        
        print(f"\n   Total de empleados activos: {total_empleados}")
        print(f"   Empleados con usuario: {empleados_con_usuario}")
        print(f"   Empleados con rol: {empleados_con_rol}")
        
        # Distribución por rol
        print("\n   DISTRIBUCIÓN POR ROL:")
        print("   " + "-"*60)
        
        cursor.execute("""
            SELECT r.nombre, COUNT(DISTINCT e.id) as cantidad
            FROM Roles r
            LEFT JOIN Usuarios_Roles ur ON r.id_rol = ur.id_rol AND ur.activo = 1
            LEFT JOIN empleados e ON ur.usuario_id = e.usuario_id AND e.activo = 1
            GROUP BY r.nombre
            ORDER BY r.nivel_acceso DESC
        """)
        
        for rol, cantidad in cursor.fetchall():
            barra = "█" * cantidad if cantidad > 0 else ""
            print(f"   {rol:.<40} {cantidad:>3} {barra}")
        
        # Empleados sin usuario o rol
        if empleados_con_usuario < total_empleados:
            print("\n   ⚠️  EMPLEADOS SIN USUARIO:")
            cursor.execute("""
                SELECT nombre, apellido, email
                FROM empleados
                WHERE usuario_id IS NULL AND activo = 1
                LIMIT 10
            """)
            for nombre, apellido, email in cursor.fetchall():
                print(f"      • {nombre} {apellido} ({email})")
        
        if empleados_con_rol < empleados_con_usuario:
            print("\n   ⚠️  EMPLEADOS SIN ROL:")
            cursor.execute("""
                SELECT e.nombre, e.apellido, p.nombre_puesto
                FROM empleados e
                LEFT JOIN Puestos p ON e.puesto = p.id_puesto
                WHERE e.usuario_id IS NOT NULL 
                  AND e.activo = 1
                  AND e.usuario_id NOT IN (
                      SELECT usuario_id FROM Usuarios_Roles WHERE activo = 1
                  )
                LIMIT 10
            """)
            for nombre, apellido, puesto in cursor.fetchall():
                print(f"      • {nombre} {apellido} - Puesto: {puesto or 'Sin puesto'}")
        
        print("\n" + "="*70)
        
        if empleados_con_rol == total_empleados:
            print("✅ TODOS LOS EMPLEADOS TIENEN USUARIO Y ROL ASIGNADO")
        else:
            print("⚠️  HAY EMPLEADOS SIN USUARIO O ROL")
            print("   Ejecuta este script de nuevo después de asignar puestos")
        
        print("="*70)
        
    except Exception as e:
        print(f"   [ERROR] {e}")
    finally:
        conn.close()


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("VINCULACIÓN DE EMPLEADOS CON USUARIOS Y ROLES")
    print("Sistema RRHH")
    print("="*70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nEste script va a:")
    print("  1. Agregar columna usuario_id a empleados (si no existe)")
    print("  2. Crear usuarios para empleados que no tengan uno")
    print("  3. Asignar roles automáticamente según el puesto")
    print("\n" + "="*70)
    
    try:
        # Paso 1: Agregar columna usuario_id
        agregar_columna_usuario_id()
        
        # Paso 2: Crear usuarios para empleados
        crear_usuarios_para_empleados()
        
        # Paso 3: Asignar roles según puesto
        asignar_roles_segun_puesto()
        
        # Reporte final
        generar_reporte_final()
        
        print("\n📌 NOTAS IMPORTANTES:")
        print("   • La contraseña por defecto es: Empleado123")
        print("   • Los usuarios deben cambiarla en el primer login")
        print("   • Los roles se asignaron según el puesto del empleado")
        print("\n" + "="*70)
        print("PROCESO COMPLETADO")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

