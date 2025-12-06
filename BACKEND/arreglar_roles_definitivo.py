"""
Script Definitivo para Arreglar Roles
=====================================

Este script arregla DEFINITIVAMENTE el problema de los roles.
NO hace preguntas, simplemente ejecuta todo.

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
from datetime import datetime


print("\n" + "="*70)
print("ARREGLANDO ROLES DEFINITIVAMENTE")
print("="*70)
print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

try:
    # PASO 1: Limpiar roles antiguos
    print("[1/5] Limpiando roles antiguos...")
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    cursor.execute("DELETE FROM Usuarios_Roles")
    cursor.execute("DELETE FROM Historial_Roles")
    cursor.execute("DELETE FROM Roles_Permisos")
    cursor.execute("DELETE FROM Roles")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('Roles', 'Usuarios_Roles', 'Historial_Roles', 'Roles_Permisos')")
    
    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON")
    print("   ✓ Roles antiguos eliminados")
    
    # PASO 2: Crear roles nuevos
    print("\n[2/5] Creando roles nuevos...")
    
    roles = [
        ('Super Admin', 'Control total del sistema', 100, 1),
        ('Gerente / Alta Gerencia', 'Decisiones estratégicas', 80, 1),
        ('Supervisor / Jefe de Área', 'Gestión departamental', 60, 1),
        ('Operativo', 'Trabajo diario', 30, 1),
        ('Consulta / Solo Visualización', 'Solo lectura', 10, 1)
    ]
    
    roles_ids = {}
    for nombre, desc, nivel, es_sistema in roles:
        cursor.execute("""
            INSERT INTO Roles (nombre, descripcion, nivel_acceso, es_sistema, activo)
            VALUES (?, ?, ?, ?, 1)
        """, (nombre, desc, nivel, es_sistema))
        roles_ids[nombre] = cursor.lastrowid
        print(f"   ✓ {nombre} (ID: {cursor.lastrowid})")
    
    conn.commit()
    
    # PASO 3: Actualizar puestos con roles
    print("\n[3/5] Actualizando puestos...")
    
    mapeo = {
        'Super Admin': ['Gerente General', 'Director de Tecnología (CTO)', 'Director de Tecnologia (CTO)', 'Gerente de Proyectos'],
        'Gerente / Alta Gerencia': ['Gerente de RRHH', 'Gerente de Ventas'],
        'Supervisor / Jefe de Área': ['Analista de RRHH', 'Contador', 'Contador Senior', 'Analista Financiero', 
                                      'Especialista en Marketing', 'Supervisor de Atención', 'Supervisor de Atencion',
                                      'Coordinador de Operaciones', 'Coordinador Logístico', 'Coordinador Logistico',
                                      'Abogado Corporativo'],
        'Operativo': ['Desarrollador Senior', 'Desarrollador Junior', 'Desarrollador Mid', 'Community Manager',
                     'Ejecutivo de Ventas', 'Representante de Servicio', 'Asistente Legal', 
                     'Asistente Administrativo', 'Reclutador']
    }
    
    actualizados = 0
    for rol_nombre, puestos in mapeo.items():
        rol_id = roles_ids[rol_nombre]
        for puesto in puestos:
            cursor.execute("UPDATE Puestos SET id_rol = ? WHERE nombre_puesto = ?", (rol_id, puesto))
            if cursor.rowcount > 0:
                actualizados += 1
    
    conn.commit()
    print(f"   ✓ {actualizados} puestos actualizados")
    
    # PASO 4: Actualizar campo 'rol' en tabla usuarios
    print("\n[4/5] Actualizando campo 'rol' en usuarios...")
    
    # Mapeo de roles antiguos a nuevos
    mapeo_roles = {
        'admin': 'Super Admin',
        'administrador': 'Super Admin',
        'rrhh': 'Gerente / Alta Gerencia',
        'supervisor': 'Supervisor / Jefe de Área',
        'empleado': 'Operativo',
        'invitado': 'Consulta / Solo Visualización'
    }
    
    actualizados_usuarios = 0
    for rol_antiguo, rol_nuevo in mapeo_roles.items():
        cursor.execute("""
            UPDATE usuarios 
            SET rol = ? 
            WHERE LOWER(rol) = ?
        """, (rol_nuevo, rol_antiguo.lower()))
        actualizados_usuarios += cursor.rowcount
    
    conn.commit()
    print(f"   ✓ {actualizados_usuarios} usuarios actualizados")
    
    # PASO 5: Asignar roles en Usuarios_Roles
    print("\n[5/5] Asignando roles a usuarios...")
    
    cursor.execute("""
        SELECT id, nombre, rol
        FROM usuarios
        WHERE activo = 1
    """)
    
    usuarios = cursor.fetchall()
    asignados = 0
    
    for usuario_id, nombre, rol_usuario in usuarios:
        # Buscar el ID del rol
        cursor.execute("SELECT id_rol FROM Roles WHERE nombre = ?", (rol_usuario,))
        resultado = cursor.fetchone()
        
        if resultado:
            rol_id = resultado[0]
            
            # Asignar rol
            cursor.execute("""
                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                VALUES (?, ?, 1, 1)
            """, (usuario_id, rol_id))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
                VALUES (?, ?, 'Migración automática a nuevo sistema de roles')
            """, (usuario_id, rol_id))
            
            asignados += 1
    
    conn.commit()
    print(f"   ✓ {asignados} roles asignados")
    
    # REPORTE FINAL
    print("\n" + "="*70)
    print("REPORTE FINAL")
    print("="*70)
    
    cursor.execute("""
        SELECT r.nombre, COUNT(u.id) as cantidad
        FROM Roles r
        LEFT JOIN usuarios u ON r.nombre = u.rol AND u.activo = 1
        GROUP BY r.nombre
        ORDER BY r.nivel_acceso DESC
    """)
    
    print("\n   DISTRIBUCIÓN DE USUARIOS POR ROL:")
    print("   " + "-"*60)
    for rol, cantidad in cursor.fetchall():
        barra = "█" * cantidad if cantidad > 0 else ""
        print(f"   {rol:.<40} {cantidad:>2} {barra}")
    
    print("\n" + "="*70)
    print("✅ ROLES ARREGLADOS EXITOSAMENTE")
    print("="*70)
    
    print("\n📌 AHORA HAZ ESTO:")
    print("   1. Ve a tu navegador")
    print("   2. Presiona Ctrl+Shift+R (recarga forzada)")
    print("   3. Deberías ver los nuevos roles:")
    print("      • Super Admin")
    print("      • Gerente / Alta Gerencia")
    print("      • Supervisor / Jefe de Área")
    print("      • Operativo")
    print("      • Consulta / Solo Visualización")
    print("\n" + "="*70)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()

