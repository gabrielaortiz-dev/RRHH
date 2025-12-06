"""
Script para Verificar y Corregir Roles del Sistema
==================================================

Este script:
1. Verifica el estado actual de los roles
2. Limpia roles antiguos
3. Crea los nuevos roles correctos
4. Reasigna roles a usuarios existentes

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
from datetime import datetime


def verificar_estado_actual():
    """Verifica qué roles existen actualmente"""
    print("\n" + "="*70)
    print("VERIFICANDO ESTADO ACTUAL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Ver roles actuales
        cursor.execute("SELECT id_rol, nombre, nivel_acceso FROM Roles ORDER BY nivel_acceso DESC")
        roles = cursor.fetchall()
        
        if roles:
            print(f"\n[INFO] Se encontraron {len(roles)} roles:")
            for rol_id, nombre, nivel in roles:
                print(f"   • ID {rol_id}: {nombre} (Nivel {nivel})")
        else:
            print("\n[INFO] No hay roles en el sistema")
        
        # Ver cuántos usuarios tienen roles asignados
        cursor.execute("""
            SELECT COUNT(DISTINCT usuario_id) 
            FROM Usuarios_Roles 
            WHERE activo = 1
        """)
        usuarios_con_rol = cursor.fetchone()[0]
        print(f"\n[INFO] Usuarios con rol asignado: {usuarios_con_rol}")
        
        return roles
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return []
    finally:
        conn.close()


def limpiar_roles_antiguos():
    """Limpia todos los roles y asignaciones antiguas"""
    print("\n" + "="*70)
    print("LIMPIANDO ROLES ANTIGUOS")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Desactivar foreign keys temporalmente
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("\n[INFO] Eliminando datos antiguos...")
        
        # Limpiar tablas en orden
        tablas = [
            'Usuarios_Roles',
            'Historial_Roles',
            'Roles_Permisos',
            'Roles'
        ]
        
        for tabla in tablas:
            try:
                cursor.execute(f"DELETE FROM {tabla}")
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
                print(f"   ✓ {tabla} limpiada")
            except Exception as e:
                print(f"   ⚠️  {tabla}: {e}")
        
        conn.commit()
        cursor.execute("PRAGMA foreign_keys = ON")
        print("\n[OK] Roles antiguos eliminados")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()


def crear_roles_correctos():
    """Crea los 5 roles nuevos correctos"""
    print("\n" + "="*70)
    print("CREANDO ROLES CORRECTOS")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    roles_correctos = [
        {
            'nombre': 'Super Admin',
            'descripcion': 'Control total del sistema, configuraciones, seguridad y creación de usuarios. Puede gestionar todo el sistema sin restricciones.',
            'nivel_acceso': 100,
            'es_sistema': 1
        },
        {
            'nombre': 'Gerente / Alta Gerencia',
            'descripcion': 'Decisiones estratégicas, aprobación de solicitudes y acceso a reportes completos. Supervisa operaciones sin acceso a configuraciones técnicas.',
            'nivel_acceso': 80,
            'es_sistema': 1
        },
        {
            'nombre': 'Supervisor / Jefe de Área',
            'descripcion': 'Gestión de equipos y departamentos. Puede crear, editar y aprobar solo dentro de su área de responsabilidad.',
            'nivel_acceso': 60,
            'es_sistema': 1
        },
        {
            'nombre': 'Operativo',
            'descripcion': 'Trabajo diario en el sistema. Puede registrar información, subir documentos y modificar su propia información.',
            'nivel_acceso': 30,
            'es_sistema': 1
        },
        {
            'nombre': 'Consulta / Solo Visualización',
            'descripcion': 'Acceso de solo lectura. Puede visualizar información del sistema sin poder modificar, crear, eliminar o aprobar.',
            'nivel_acceso': 10,
            'es_sistema': 1
        }
    ]
    
    try:
        roles_ids = {}
        
        for rol in roles_correctos:
            cursor.execute("""
                INSERT INTO Roles (nombre, descripcion, nivel_acceso, es_sistema, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (rol['nombre'], rol['descripcion'], rol['nivel_acceso'], rol['es_sistema']))
            
            rol_id = cursor.lastrowid
            roles_ids[rol['nombre']] = rol_id
            
            print(f"\n   ✓ {rol['nombre']}")
            print(f"     ID: {rol_id}, Nivel: {rol['nivel_acceso']}")
        
        conn.commit()
        print(f"\n[OK] {len(roles_correctos)} roles creados correctamente")
        return roles_ids
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
        return {}
    finally:
        conn.close()


def actualizar_puestos_con_roles(roles_ids):
    """Actualiza los puestos con los nuevos IDs de roles"""
    print("\n" + "="*70)
    print("ACTUALIZANDO PUESTOS CON ROLES CORRECTOS")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Mapeo de puestos a roles
    mapeo_puestos_roles = {
        'Super Admin': [
            'Gerente General',
            'Director de Tecnología (CTO)',
            'Director de Tecnologia (CTO)',
            'Gerente de Proyectos'
        ],
        'Gerente / Alta Gerencia': [
            'Gerente de RRHH',
            'Gerente de Ventas'
        ],
        'Supervisor / Jefe de Área': [
            'Analista de RRHH',
            'Contador',
            'Contador Senior',
            'Analista Financiero',
            'Especialista en Marketing',
            'Supervisor de Atención',
            'Supervisor de Atencion',
            'Coordinador de Operaciones',
            'Coordinador Logístico',
            'Coordinador Logistico',
            'Abogado Corporativo'
        ],
        'Operativo': [
            'Desarrollador Senior',
            'Desarrollador Junior',
            'Desarrollador Mid',
            'Community Manager',
            'Ejecutivo de Ventas',
            'Representante de Servicio',
            'Asistente Legal',
            'Asistente Administrativo',
            'Reclutador'
        ]
    }
    
    try:
        actualizados = 0
        
        for rol_nombre, puestos in mapeo_puestos_roles.items():
            if rol_nombre not in roles_ids:
                continue
            
            rol_id = roles_ids[rol_nombre]
            
            for puesto in puestos:
                cursor.execute("""
                    UPDATE Puestos 
                    SET id_rol = ? 
                    WHERE nombre_puesto = ?
                """, (rol_id, puesto))
                
                if cursor.rowcount > 0:
                    print(f"   ✓ {puesto} → {rol_nombre}")
                    actualizados += 1
        
        conn.commit()
        print(f"\n[OK] {actualizados} puestos actualizados")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()


def reasignar_roles_usuarios():
    """Reasigna roles a usuarios según sus puestos"""
    print("\n" + "="*70)
    print("REASIGNANDO ROLES A USUARIOS")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Obtener usuarios con puestos
        cursor.execute("""
            SELECT 
                u.id as usuario_id,
                u.nombre,
                e.puesto as puesto_id,
                p.nombre_puesto,
                p.id_rol
            FROM usuarios u
            LEFT JOIN empleados e ON u.id = e.usuario_id
            LEFT JOIN Puestos p ON e.puesto = p.id_puesto
            WHERE u.activo = 1
        """)
        
        usuarios = cursor.fetchall()
        asignados = 0
        sin_puesto = 0
        
        for usuario_id, nombre, puesto_id, puesto_nombre, rol_id in usuarios:
            if not rol_id:
                sin_puesto += 1
                continue
            
            try:
                # Asignar rol
                cursor.execute("""
                    INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                    VALUES (?, ?, 1, 1)
                """, (usuario_id, rol_id))
                
                # Registrar en historial
                cursor.execute("""
                    INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
                    VALUES (?, ?, 'Reasignación automática de roles')
                """, (usuario_id, rol_id))
                
                # Obtener nombre del rol
                cursor.execute("SELECT nombre FROM Roles WHERE id_rol = ?", (rol_id,))
                rol_nombre = cursor.fetchone()[0]
                
                print(f"   ✓ {nombre} → {puesto_nombre} → {rol_nombre}")
                asignados += 1
                
            except Exception as e:
                print(f"   ⚠️  Error con {nombre}: {e}")
        
        conn.commit()
        print(f"\n[OK] {asignados} roles asignados")
        
        if sin_puesto > 0:
            print(f"[INFO] {sin_puesto} usuarios sin puesto/rol")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()


def generar_reporte():
    """Genera reporte final"""
    print("\n" + "="*70)
    print("REPORTE FINAL")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Roles creados
        cursor.execute("""
            SELECT nombre, nivel_acceso, 
                   (SELECT COUNT(*) FROM Usuarios_Roles ur 
                    WHERE ur.id_rol = r.id_rol AND ur.activo = 1) as usuarios
            FROM Roles r
            ORDER BY nivel_acceso DESC
        """)
        
        print("\n   ROLES EN EL SISTEMA:")
        print("   " + "-"*60)
        for nombre, nivel, usuarios in cursor.fetchall():
            print(f"   {nombre:.<40} Nivel {nivel:>3} - {usuarios} usuario(s)")
        
        print("\n" + "="*70)
        print("✅ SISTEMA CORREGIDO EXITOSAMENTE")
        print("="*70)
        
        print("\n📌 PRÓXIMOS PASOS:")
        print("   1. Recarga la página en el navegador (F5)")
        print("   2. Deberías ver los nuevos roles:")
        print("      • Super Admin")
        print("      • Gerente / Alta Gerencia")
        print("      • Supervisor / Jefe de Área")
        print("      • Operativo")
        print("      • Consulta / Solo Visualización")
        print("\n" + "="*70)
        
    finally:
        conn.close()


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("CORRECCIÓN COMPLETA DEL SISTEMA DE ROLES")
    print("="*70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nEste script va a:")
    print("  1. Verificar roles actuales")
    print("  2. Eliminar roles antiguos")
    print("  3. Crear los 5 roles correctos")
    print("  4. Actualizar puestos con roles")
    print("  5. Reasignar roles a usuarios")
    print("\n" + "="*70)
    
    respuesta = input("\n¿Desea continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("\nOperación cancelada.")
        return
    
    try:
        # 1. Verificar estado actual
        verificar_estado_actual()
        
        # 2. Limpiar roles antiguos
        limpiar_roles_antiguos()
        
        # 3. Crear roles correctos
        roles_ids = crear_roles_correctos()
        
        if not roles_ids:
            print("\n[ERROR] No se pudieron crear los roles")
            return
        
        # 4. Actualizar puestos
        actualizar_puestos_con_roles(roles_ids)
        
        # 5. Reasignar roles a usuarios
        reasignar_roles_usuarios()
        
        # 6. Generar reporte
        generar_reporte()
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

