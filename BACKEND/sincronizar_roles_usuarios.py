"""
Script para Sincronizar Roles en Tabla Usuarios
===============================================

Este script actualiza el campo 'rol' en la tabla usuarios
para que coincida con el sistema nuevo de roles.

El problema es que hay DOS lugares donde están los roles:
1. Campo 'rol' en tabla usuarios (ANTIGUO - es lo que se muestra)
2. Tabla Usuarios_Roles (NUEVO - lo que creamos)

Este script sincroniza ambos.

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
from datetime import datetime


def verificar_estructura():
    """Verifica la estructura actual"""
    print("\n" + "="*70)
    print("VERIFICANDO ESTRUCTURA ACTUAL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Ver estructura de tabla usuarios
        print("\n[INFO] Estructura de tabla usuarios:")
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"   • {col[1]} ({col[2]})")
        
        # Ver usuarios actuales con sus roles
        print("\n[INFO] Usuarios actuales con roles:")
        cursor.execute("""
            SELECT id, nombre, email, rol 
            FROM usuarios 
            ORDER BY id
        """)
        
        for user_id, nombre, email, rol in cursor.fetchall():
            print(f"   • ID {user_id}: {nombre} - Rol: {rol}")
        
        # Ver roles nuevos
        print("\n[INFO] Roles en tabla Roles:")
        cursor.execute("SELECT id_rol, nombre FROM Roles ORDER BY nivel_acceso DESC")
        roles_nuevos = cursor.fetchall()
        
        if roles_nuevos:
            for rol_id, nombre in roles_nuevos:
                print(f"   • ID {rol_id}: {nombre}")
        else:
            print("   ⚠️  No hay roles en la tabla Roles")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    finally:
        conn.close()


def mapear_rol_antiguo_a_nuevo(rol_antiguo):
    """Mapea los roles antiguos a los nuevos"""
    mapeo = {
        'admin': 'Super Admin',
        'administrador': 'Super Admin',
        'rrhh': 'Gerente / Alta Gerencia',
        'supervisor': 'Supervisor / Jefe de Área',
        'empleado': 'Operativo',
        'invitado': 'Consulta / Solo Visualización'
    }
    
    return mapeo.get(rol_antiguo.lower(), 'Operativo')


def sincronizar_roles():
    """Sincroniza los roles antiguos con los nuevos"""
    print("\n" + "="*70)
    print("SINCRONIZANDO ROLES")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Obtener todos los usuarios
        cursor.execute("""
            SELECT id, nombre, rol
            FROM usuarios
            WHERE activo = 1
        """)
        
        usuarios = cursor.fetchall()
        actualizados = 0
        
        for usuario_id, nombre, rol_antiguo in usuarios:
            # Obtener el rol nuevo del usuario desde Usuarios_Roles
            cursor.execute("""
                SELECT r.id_rol, r.nombre
                FROM Usuarios_Roles ur
                INNER JOIN Roles r ON ur.id_rol = r.id_rol
                WHERE ur.usuario_id = ? AND ur.activo = 1 AND ur.es_principal = 1
                LIMIT 1
            """, (usuario_id,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                # El usuario ya tiene rol nuevo asignado
                rol_id, rol_nuevo = resultado
                
                # Actualizar el campo 'rol' en la tabla usuarios
                # Usamos un nombre más corto para que se vea bien en la UI
                rol_para_ui = rol_nuevo
                
                cursor.execute("""
                    UPDATE usuarios
                    SET rol = ?
                    WHERE id = ?
                """, (rol_para_ui, usuario_id))
                
                print(f"   ✓ {nombre}: {rol_antiguo} → {rol_nuevo}")
                actualizados += 1
            else:
                # No tiene rol nuevo, asignar basándose en el rol antiguo
                rol_nuevo_nombre = mapear_rol_antiguo_a_nuevo(rol_antiguo)
                
                # Buscar el ID del rol nuevo
                cursor.execute("""
                    SELECT id_rol FROM Roles WHERE nombre = ?
                """, (rol_nuevo_nombre,))
                
                rol_nuevo_id = cursor.fetchone()
                
                if rol_nuevo_id:
                    # Asignar en Usuarios_Roles
                    cursor.execute("""
                        INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                        VALUES (?, ?, 1, 1)
                    """, (usuario_id, rol_nuevo_id[0]))
                    
                    # Actualizar campo rol en usuarios
                    cursor.execute("""
                        UPDATE usuarios
                        SET rol = ?
                        WHERE id = ?
                    """, (rol_nuevo_nombre, usuario_id))
                    
                    print(f"   ✓ {nombre}: {rol_antiguo} → {rol_nuevo_nombre} (creado)")
                    actualizados += 1
        
        conn.commit()
        print(f"\n[OK] {actualizados} usuarios actualizados")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def verificar_resultado():
    """Verifica el resultado final"""
    print("\n" + "="*70)
    print("VERIFICANDO RESULTADO")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        print("\n[INFO] Usuarios con roles actualizados:")
        cursor.execute("""
            SELECT 
                u.id,
                u.nombre,
                u.email,
                u.rol as rol_campo,
                r.nombre as rol_tabla
            FROM usuarios u
            LEFT JOIN Usuarios_Roles ur ON u.id = ur.usuario_id AND ur.activo = 1
            LEFT JOIN Roles r ON ur.id_rol = r.id_rol
            WHERE u.activo = 1
            ORDER BY u.id
        """)
        
        print("\n   ID | Nombre              | Rol (campo) | Rol (tabla)")
        print("   " + "-"*70)
        
        for user_id, nombre, email, rol_campo, rol_tabla in cursor.fetchall():
            print(f"   {user_id:2d} | {nombre:20s} | {rol_campo:20s} | {rol_tabla or 'Sin rol':20s}")
        
        # Contar por rol
        print("\n[INFO] Distribución de usuarios por rol:")
        cursor.execute("""
            SELECT rol, COUNT(*) as cantidad
            FROM usuarios
            WHERE activo = 1
            GROUP BY rol
            ORDER BY cantidad DESC
        """)
        
        for rol, cantidad in cursor.fetchall():
            barra = "█" * cantidad
            print(f"   {rol:.<40} {cantidad:>2} {barra}")
        
    finally:
        conn.close()


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("SINCRONIZACIÓN DE ROLES - TABLA USUARIOS")
    print("="*70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nEste script va a:")
    print("  1. Verificar la estructura actual")
    print("  2. Sincronizar roles antiguos con nuevos")
    print("  3. Actualizar el campo 'rol' en tabla usuarios")
    print("  4. Generar reporte de resultados")
    
    print("\n" + "="*70)
    
    try:
        # 1. Verificar estructura
        if not verificar_estructura():
            print("\n[ERROR] No se puede continuar sin roles en la tabla Roles")
            print("Ejecuta primero: python verificar_y_corregir_roles.py")
            return
        
        # 2. Sincronizar roles
        sincronizar_roles()
        
        # 3. Verificar resultado
        verificar_resultado()
        
        print("\n" + "="*70)
        print("✅ SINCRONIZACIÓN COMPLETADA")
        print("="*70)
        
        print("\n📌 PRÓXIMOS PASOS:")
        print("   1. Recarga la página en el navegador (Ctrl+F5)")
        print("   2. Los roles deberían mostrarse actualizados")
        print("   3. Si aún no se ven, verifica el código del frontend")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

