"""
Verificador Completo del Estado de Roles y Permisos
===================================================

Este script verifica:
1. Roles existentes
2. Permisos por rol
3. Distribución de empleados por rol según puesto
4. Usuarios con roles asignados

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
from datetime import datetime


def verificar_roles():
    """Verifica los roles en el sistema"""
    print("\n" + "="*70)
    print("1. ROLES DEL SISTEMA")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id_rol, nombre, descripcion, nivel_acceso, es_sistema, activo
            FROM Roles
            ORDER BY nivel_acceso DESC
        """)
        
        roles = cursor.fetchall()
        
        if not roles:
            print("\n   ❌ NO HAY ROLES EN EL SISTEMA")
            print("   Ejecuta: python arreglar_roles_definitivo.py")
            return False
        
        print(f"\n   Total de roles: {len(roles)}")
        print("   " + "-"*60)
        
        for rol_id, nombre, descripcion, nivel, es_sistema, activo in roles:
            estado = "✅ Activo" if activo else "❌ Inactivo"
            sistema = "🔒 Sistema" if es_sistema else "📝 Personalizado"
            print(f"\n   ID {rol_id}: {nombre}")
            print(f"      Nivel: {nivel} | {estado} | {sistema}")
            print(f"      {descripcion[:70]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        conn.close()


def verificar_permisos_por_rol():
    """Verifica los permisos asignados a cada rol"""
    print("\n" + "="*70)
    print("2. PERMISOS POR ROL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si hay permisos
        cursor.execute("SELECT COUNT(*) FROM Permisos")
        total_permisos = cursor.fetchone()[0]
        
        if total_permisos == 0:
            print("\n   ⚠️  NO HAY PERMISOS CONFIGURADOS")
            print("   El sistema de permisos aún no se ha implementado completamente")
            return False
        
        print(f"\n   Total de permisos en sistema: {total_permisos}")
        print("   " + "-"*60)
        
        # Obtener permisos por rol
        cursor.execute("""
            SELECT r.nombre, COUNT(rp.id_permiso) as total_permisos
            FROM Roles r
            LEFT JOIN Roles_Permisos rp ON r.id_rol = rp.id_rol
            GROUP BY r.nombre
            ORDER BY r.nivel_acceso DESC
        """)
        
        for rol, permisos in cursor.fetchall():
            print(f"   {rol:.<50} {permisos:>3} permiso(s)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        conn.close()


def verificar_puestos_con_roles():
    """Verifica la distribución de puestos por rol"""
    print("\n" + "="*70)
    print("3. DISTRIBUCIÓN DE PUESTOS POR ROL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.nombre, COUNT(p.id_puesto) as total_puestos
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_rol = p.id_rol
            GROUP BY r.nombre
            ORDER BY r.nivel_acceso DESC
        """)
        
        print("\n   PUESTOS POR ROL:")
        print("   " + "-"*60)
        
        for rol, puestos in cursor.fetchall():
            barra = "█" * puestos if puestos > 0 else ""
            print(f"   {rol:.<40} {puestos:>2} puesto(s) {barra}")
        
        # Detalle de puestos por rol
        print("\n   DETALLE DE PUESTOS:")
        print("   " + "-"*60)
        
        cursor.execute("""
            SELECT r.nombre as rol, p.nombre_puesto, p.nivel, p.salario_base
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_rol = p.id_rol
            ORDER BY r.nivel_acceso DESC, p.nombre_puesto
        """)
        
        rol_actual = None
        for rol, puesto, nivel, salario in cursor.fetchall():
            if rol != rol_actual:
                print(f"\n   📋 {rol}:")
                rol_actual = rol
            
            if puesto:
                print(f"      • {puesto} ({nivel}) - ${salario:,.2f}")
            else:
                if rol == rol_actual:
                    print(f"      (Sin puestos asignados)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        conn.close()


def verificar_empleados_por_rol():
    """Verifica la distribución de empleados por rol"""
    print("\n" + "="*70)
    print("4. DISTRIBUCIÓN DE EMPLEADOS POR ROL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Total de empleados
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE activo = 1")
        total_empleados = cursor.fetchone()[0]
        
        print(f"\n   Total de empleados activos: {total_empleados}")
        
        # Empleados con usuario
        cursor.execute("""
            SELECT COUNT(*) FROM empleados 
            WHERE usuario_id IS NOT NULL AND activo = 1
        """)
        con_usuario = cursor.fetchone()[0]
        
        # Empleados con rol
        cursor.execute("""
            SELECT COUNT(DISTINCT e.id)
            FROM empleados e
            INNER JOIN Usuarios_Roles ur ON e.usuario_id = ur.usuario_id
            WHERE e.activo = 1 AND ur.activo = 1
        """)
        con_rol = cursor.fetchone()[0]
        
        print(f"   Empleados con usuario: {con_usuario}")
        print(f"   Empleados con rol: {con_rol}")
        
        # Distribución por rol
        print("\n   EMPLEADOS POR ROL:")
        print("   " + "-"*60)
        
        cursor.execute("""
            SELECT r.nombre, COUNT(DISTINCT e.id) as cantidad
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_rol = p.id_rol
            LEFT JOIN empleados e ON p.id_puesto = e.puesto AND e.activo = 1
            GROUP BY r.nombre
            ORDER BY r.nivel_acceso DESC
        """)
        
        for rol, cantidad in cursor.fetchall():
            barra = "█" * cantidad if cantidad > 0 else ""
            print(f"   {rol:.<40} {cantidad:>3} empleado(s) {barra}")
        
        # Detalle de empleados por rol (primeros 5 de cada rol)
        print("\n   EJEMPLOS DE EMPLEADOS POR ROL:")
        print("   " + "-"*60)
        
        cursor.execute("""
            SELECT r.nombre as rol, e.nombre, e.apellido, p.nombre_puesto
            FROM Roles r
            INNER JOIN Puestos p ON r.id_rol = p.id_rol
            INNER JOIN empleados e ON p.id_puesto = e.puesto
            WHERE e.activo = 1
            ORDER BY r.nivel_acceso DESC, e.nombre
        """)
        
        rol_actual = None
        contador = 0
        for rol, nombre, apellido, puesto in cursor.fetchall():
            if rol != rol_actual:
                rol_actual = rol
                contador = 0
                print(f"\n   📋 {rol}:")
            
            if contador < 5:  # Mostrar solo primeros 5
                print(f"      • {nombre} {apellido} - {puesto}")
                contador += 1
            elif contador == 5:
                cursor.execute("""
                    SELECT COUNT(*) FROM empleados e
                    INNER JOIN Puestos p ON e.puesto = p.id_puesto
                    INNER JOIN Roles r ON p.id_rol = r.id_rol
                    WHERE r.nombre = ? AND e.activo = 1
                """, (rol,))
                total = cursor.fetchone()[0]
                if total > 5:
                    print(f"      ... y {total - 5} más")
                contador += 1
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        conn.close()


def verificar_usuarios_con_roles():
    """Verifica usuarios con roles asignados"""
    print("\n" + "="*70)
    print("5. USUARIOS CON ROLES")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT u.id, u.nombre, u.email, u.rol, r.nombre as rol_nuevo
            FROM usuarios u
            LEFT JOIN Usuarios_Roles ur ON u.id = ur.usuario_id AND ur.activo = 1
            LEFT JOIN Roles r ON ur.id_rol = r.id_rol
            WHERE u.activo = 1
            ORDER BY u.id
            LIMIT 10
        """)
        
        print("\n   PRIMEROS 10 USUARIOS:")
        print("   " + "-"*60)
        print(f"   {'ID':<4} {'Nombre':<25} {'Rol (campo)':<25} {'Rol (tabla)':<25}")
        print("   " + "-"*60)
        
        for user_id, nombre, email, rol_campo, rol_tabla in cursor.fetchall():
            coincide = "✅" if rol_campo == rol_tabla else "⚠️"
            print(f"   {user_id:<4} {nombre[:24]:<25} {rol_campo[:24]:<25} {(rol_tabla or 'Sin rol')[:24]:<25} {coincide}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        conn.close()


def generar_reporte_final():
    """Genera reporte final con recomendaciones"""
    print("\n" + "="*70)
    print("REPORTE FINAL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si todo está correcto
        cursor.execute("SELECT COUNT(*) FROM Roles WHERE activo = 1")
        roles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Puestos WHERE id_rol IS NOT NULL")
        puestos_con_rol = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Puestos")
        total_puestos = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT e.id)
            FROM empleados e
            WHERE e.usuario_id IS NOT NULL AND e.activo = 1
        """)
        empleados_con_usuario = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT e.id)
            FROM empleados e
            INNER JOIN Usuarios_Roles ur ON e.usuario_id = ur.usuario_id
            WHERE e.activo = 1 AND ur.activo = 1
        """)
        empleados_con_rol = cursor.fetchone()[0]
        
        print("\n   RESUMEN:")
        print("   " + "-"*60)
        print(f"   Roles configurados: {roles}/5")
        print(f"   Puestos con rol: {puestos_con_rol}/{total_puestos}")
        print(f"   Empleados con usuario: {empleados_con_usuario}")
        print(f"   Empleados con rol: {empleados_con_rol}")
        
        print("\n   ESTADO:")
        
        if roles == 5:
            print("   ✅ Los 5 roles están creados")
        else:
            print(f"   ❌ Faltan {5 - roles} roles")
            print("      Ejecuta: python arreglar_roles_definitivo.py")
        
        if puestos_con_rol == total_puestos:
            print("   ✅ Todos los puestos tienen rol asignado")
        else:
            print(f"   ⚠️  {total_puestos - puestos_con_rol} puestos sin rol")
            print("      Ejecuta: python arreglar_roles_definitivo.py")
        
        if empleados_con_usuario > 0 and empleados_con_rol == empleados_con_usuario:
            print("   ✅ Todos los empleados con usuario tienen rol")
        else:
            print(f"   ⚠️  {empleados_con_usuario - empleados_con_rol} empleados sin rol")
            print("      Ejecuta: python vincular_empleados_usuarios_roles.py")
        
    finally:
        conn.close()


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("VERIFICACIÓN COMPLETA DEL SISTEMA DE ROLES")
    print("="*70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Verificaciones en orden
        roles_ok = verificar_roles()
        
        if roles_ok:
            verificar_permisos_por_rol()
            verificar_puestos_con_roles()
            verificar_empleados_por_rol()
            verificar_usuarios_con_roles()
        
        # Reporte final
        generar_reporte_final()
        
        print("\n" + "="*70)
        print("VERIFICACIÓN COMPLETADA")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

