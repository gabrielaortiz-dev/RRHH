"""
Ejemplo de Uso Completo del Sistema de Roles y Permisos
========================================================

Este script demuestra cómo usar el sistema de roles y permisos
en un caso de uso real completo.

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
from verificador_permisos import (
    VerificadorPermisos,
    verificar_permiso,
    obtener_rol_usuario,
    obtener_permisos_usuario,
    es_super_admin,
    es_gerente,
    es_supervisor
)


def ejemplo_1_verificar_permisos_basico():
    """Ejemplo 1: Verificación básica de permisos"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Verificación Básica de Permisos")
    print("="*70)
    
    usuario_id = 1  # Usuario de prueba
    
    # Obtener rol del usuario
    rol = obtener_rol_usuario(usuario_id)
    if rol:
        print(f"\n👤 Usuario ID: {usuario_id}")
        print(f"   Rol: {rol['nombre']}")
        print(f"   Nivel de Acceso: {rol['nivel_acceso']}")
        
        # Verificar diferentes permisos
        print("\n🔍 Verificando permisos:")
        permisos_a_verificar = [
            ('empleados.ver', 'Ver empleados'),
            ('empleados.crear', 'Crear empleados'),
            ('usuarios.crear', 'Crear usuarios'),
            ('nomina.aprobar', 'Aprobar nóminas'),
            ('sistema.configurar', 'Configurar sistema')
        ]
        
        for codigo, nombre in permisos_a_verificar:
            tiene = verificar_permiso(usuario_id, codigo)
            simbolo = "✅" if tiene else "❌"
            print(f"   {simbolo} {nombre} ({codigo})")
    else:
        print(f"❌ Usuario {usuario_id} no tiene rol asignado")


def ejemplo_2_comparar_roles():
    """Ejemplo 2: Comparar permisos entre diferentes roles"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Comparación de Permisos entre Roles")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Obtener todos los roles
    cursor.execute("""
        SELECT id_rol, nombre, nivel_acceso 
        FROM Roles 
        WHERE activo = 1 
        ORDER BY nivel_acceso DESC
    """)
    
    roles = cursor.fetchall()
    
    # Permiso de prueba
    permiso_prueba = 'empleados.crear'
    
    print(f"\n🔍 ¿Quién puede '{permiso_prueba}'?")
    print("-" * 60)
    
    for rol_id, nombre, nivel in roles:
        # Crear usuario temporal para probar
        cursor.execute("SELECT id FROM usuarios LIMIT 1")
        usuario_temp = cursor.fetchone()
        
        if usuario_temp:
            # Verificar si el rol tiene el permiso
            cursor.execute("""
                SELECT COUNT(*) FROM Roles_Permisos rp
                INNER JOIN Permisos p ON rp.id_permiso = p.id_permiso
                WHERE rp.id_rol = ? AND p.codigo = ?
            """, (rol_id, permiso_prueba))
            
            tiene = cursor.fetchone()[0] > 0
            simbolo = "✅" if tiene else "❌"
            print(f"   {simbolo} {nombre:.<40} Nivel: {nivel}")
    
    conn.close()


def ejemplo_3_gestionar_roles():
    """Ejemplo 3: Asignar y cambiar roles de usuarios"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Gestión de Roles de Usuarios")
    print("="*70)
    
    verificador = VerificadorPermisos()
    
    # Simular datos (ajustar IDs según tu BD)
    usuario_id = 5
    nuevo_rol_id = 4  # Operativo
    admin_id = 1
    
    print(f"\n📋 Asignando rol a usuario {usuario_id}")
    
    # Verificar rol actual
    rol_actual = obtener_rol_usuario(usuario_id)
    if rol_actual:
        print(f"   Rol actual: {rol_actual['nombre']}")
    else:
        print("   Sin rol asignado")
    
    # Asignar nuevo rol
    print(f"\n🔄 Asignando nuevo rol...")
    exito = verificador.asignar_rol(
        usuario_id=usuario_id,
        rol_id=nuevo_rol_id,
        admin_id=admin_id,
        motivo="Ejemplo de asignación de rol"
    )
    
    if exito:
        print("   ✅ Rol asignado exitosamente")
        
        # Verificar nuevo rol
        rol_nuevo = obtener_rol_usuario(usuario_id)
        if rol_nuevo:
            print(f"   Nuevo rol: {rol_nuevo['nombre']}")
    else:
        print("   ❌ Error al asignar rol")


def ejemplo_4_permisos_por_modulo():
    """Ejemplo 4: Obtener permisos agrupados por módulo"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Permisos Agrupados por Módulo")
    print("="*70)
    
    verificador = VerificadorPermisos()
    usuario_id = 1
    
    # Obtener permisos agrupados
    permisos_por_modulo = verificador.obtener_permisos_por_modulo(usuario_id)
    
    print(f"\n👤 Usuario ID: {usuario_id}")
    print(f"   Módulos con permisos: {len(permisos_por_modulo)}")
    
    print("\n📦 Permisos por módulo:")
    for modulo, permisos in sorted(permisos_por_modulo.items()):
        print(f"\n   📂 {modulo.upper()}")
        for permiso in sorted(permisos):
            print(f"      • {permiso}")


def ejemplo_5_verificar_niveles():
    """Ejemplo 5: Verificar niveles de acceso"""
    print("\n" + "="*70)
    print("EJEMPLO 5: Verificación de Niveles de Acceso")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Obtener algunos usuarios con roles
    cursor.execute("""
        SELECT DISTINCT u.id, u.nombre, r.nombre as rol, r.nivel_acceso
        FROM usuarios u
        INNER JOIN Usuarios_Roles ur ON u.id = ur.usuario_id
        INNER JOIN Roles r ON ur.id_rol = r.id_rol
        WHERE ur.activo = 1
        LIMIT 5
    """)
    
    usuarios = cursor.fetchall()
    
    print("\n👥 Verificando niveles de acceso:")
    print("-" * 60)
    
    for user_id, nombre, rol, nivel in usuarios:
        print(f"\n   📌 {nombre} ({rol} - Nivel {nivel})")
        
        # Verificar diferentes niveles
        checks = [
            ('Super Admin', es_super_admin(user_id), "👑"),
            ('Gerente', es_gerente(user_id), "🏢"),
            ('Supervisor', es_supervisor(user_id), "🧑‍💼")
        ]
        
        for titulo, resultado, emoji in checks:
            simbolo = "✅" if resultado else "❌"
            print(f"      {simbolo} Es {titulo} o superior: {emoji if resultado else ''}")
    
    conn.close()


def ejemplo_6_historial_roles():
    """Ejemplo 6: Ver historial de cambios de roles"""
    print("\n" + "="*70)
    print("EJEMPLO 6: Historial de Cambios de Roles")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Obtener historial reciente
    cursor.execute("""
        SELECT 
            u.nombre as usuario,
            r_anterior.nombre as rol_anterior,
            r_nuevo.nombre as rol_nuevo,
            hr.motivo,
            hr.fecha_cambio
        FROM Historial_Roles hr
        INNER JOIN usuarios u ON hr.usuario_id = u.id
        LEFT JOIN Roles r_anterior ON hr.id_rol_anterior = r_anterior.id_rol
        LEFT JOIN Roles r_nuevo ON hr.id_rol_nuevo = r_nuevo.id_rol
        ORDER BY hr.fecha_cambio DESC
        LIMIT 10
    """)
    
    historial = cursor.fetchall()
    
    if historial:
        print("\n📜 Últimos cambios de roles:")
        print("-" * 60)
        
        for usuario, rol_ant, rol_nue, motivo, fecha in historial:
            cambio = f"{rol_ant or 'Sin rol'} → {rol_nue or 'Sin rol'}"
            print(f"\n   👤 {usuario}")
            print(f"      {cambio}")
            print(f"      📝 {motivo}")
            print(f"      📅 {fecha}")
    else:
        print("\n   ℹ️  No hay historial de cambios disponible")
    
    conn.close()


def ejemplo_7_estadisticas_sistema():
    """Ejemplo 7: Estadísticas del sistema de roles"""
    print("\n" + "="*70)
    print("EJEMPLO 7: Estadísticas del Sistema")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Estadísticas generales
    print("\n📊 Estadísticas Generales:")
    print("-" * 60)
    
    # Total de roles
    cursor.execute("SELECT COUNT(*) FROM Roles WHERE activo = 1")
    total_roles = cursor.fetchone()[0]
    print(f"   Roles activos: {total_roles}")
    
    # Total de permisos
    cursor.execute("SELECT COUNT(*) FROM Permisos WHERE activo = 1")
    total_permisos = cursor.fetchone()[0]
    print(f"   Permisos disponibles: {total_permisos}")
    
    # Total de puestos
    cursor.execute("SELECT COUNT(*) FROM Puestos")
    total_puestos = cursor.fetchone()[0]
    print(f"   Puestos configurados: {total_puestos}")
    
    # Total de usuarios con rol
    cursor.execute("""
        SELECT COUNT(DISTINCT usuario_id) 
        FROM Usuarios_Roles 
        WHERE activo = 1
    """)
    total_usuarios_con_rol = cursor.fetchone()[0]
    print(f"   Usuarios con rol asignado: {total_usuarios_con_rol}")
    
    # Distribución de usuarios por rol
    print("\n👥 Distribución de Usuarios por Rol:")
    print("-" * 60)
    
    cursor.execute("""
        SELECT r.nombre, r.nivel_acceso, COUNT(ur.usuario_id) as cantidad
        FROM Roles r
        LEFT JOIN Usuarios_Roles ur ON r.id_rol = ur.id_rol AND ur.activo = 1
        WHERE r.activo = 1
        GROUP BY r.nombre, r.nivel_acceso
        ORDER BY r.nivel_acceso DESC
    """)
    
    for rol, nivel, cantidad in cursor.fetchall():
        barra = "█" * cantidad if cantidad > 0 else ""
        print(f"   {rol:.<40} {cantidad:>2} {barra}")
    
    # Permisos más comunes
    print("\n🔑 Permisos Más Asignados:")
    print("-" * 60)
    
    cursor.execute("""
        SELECT p.codigo, p.nombre, COUNT(rp.id_rol) as roles
        FROM Permisos p
        INNER JOIN Roles_Permisos rp ON p.id_permiso = rp.id_permiso
        WHERE p.activo = 1
        GROUP BY p.codigo, p.nombre
        ORDER BY roles DESC
        LIMIT 5
    """)
    
    for codigo, nombre, roles in cursor.fetchall():
        print(f"   • {nombre}")
        print(f"     {codigo} - Asignado a {roles} rol(es)")
    
    conn.close()


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*70)
    print("SISTEMA DE ROLES Y PERMISOS - EJEMPLOS DE USO")
    print("="*70)
    print("\nEste script demuestra cómo usar el sistema de roles y permisos")
    print("en diferentes casos de uso reales.")
    
    try:
        # Verificar que existe la base de datos
        conn = sqlite3.connect('rrhh.db')
        cursor = conn.cursor()
        
        # Verificar que existen las tablas necesarias
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Roles'
        """)
        
        if not cursor.fetchone():
            print("\n❌ ERROR: Las tablas del sistema de roles no existen.")
            print("   Por favor ejecuta primero:")
            print("   1. python actualizar_estructura_roles.py")
            print("   2. python configurar_roles_y_puestos.py")
            conn.close()
            return
        
        conn.close()
        
        # Ejecutar ejemplos
        ejemplo_1_verificar_permisos_basico()
        ejemplo_2_comparar_roles()
        ejemplo_3_gestionar_roles()
        ejemplo_4_permisos_por_modulo()
        ejemplo_5_verificar_niveles()
        ejemplo_6_historial_roles()
        ejemplo_7_estadisticas_sistema()
        
        print("\n" + "="*70)
        print("EJEMPLOS COMPLETADOS")
        print("="*70)
        print("\n✅ Todos los ejemplos se ejecutaron correctamente")
        print("\n📚 Para más información, consulta:")
        print("   • DOCUMENTACION_SISTEMA_ROLES.md")
        print("   • README_SISTEMA_ROLES.md")
        print("   • REFERENCIA_RAPIDA_ROLES.md")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

