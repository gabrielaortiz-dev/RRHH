"""Verificador Simple del Estado de Roles"""
import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

print("\n" + "="*70)
print("ESTADO ACTUAL DEL SISTEMA DE ROLES")
print("="*70)

# 1. ROLES
print("\n1. ROLES EN EL SISTEMA:")
print("-" * 60)
cursor.execute("SELECT nombre, nivel_acceso FROM Roles ORDER BY nivel_acceso DESC")
for nombre, nivel in cursor.fetchall():
    print(f"   - {nombre} (Nivel {nivel})")

# 2. PUESTOS POR ROL
print("\n2. PUESTOS POR ROL:")
print("-" * 60)
cursor.execute("""
    SELECT r.nombre, COUNT(p.id_puesto) as total
    FROM Roles r
    LEFT JOIN Puestos p ON r.id_rol = p.id_rol
    GROUP BY r.nombre
    ORDER BY r.nivel_acceso DESC
""")
for rol, total in cursor.fetchall():
    print(f"   {rol:.<45} {total} puesto(s)")

# 3. DETALLE DE PUESTOS
print("\n3. DETALLE DE PUESTOS POR ROL:")
print("-" * 60)
cursor.execute("""
    SELECT r.nombre as rol, p.nombre_puesto, p.salario_base
    FROM Roles r
    INNER JOIN Puestos p ON r.id_rol = p.id_rol
    ORDER BY r.nivel_acceso DESC, p.nombre_puesto
""")
rol_actual = None
for rol, puesto, salario in cursor.fetchall():
    if rol != rol_actual:
        print(f"\n   {rol}:")
        rol_actual = rol
    print(f"      - {puesto} (${salario:,.2f})")

# 4. EMPLEADOS POR ROL
print("\n4. EMPLEADOS POR ROL:")
print("-" * 60)
cursor.execute("""
    SELECT r.nombre, COUNT(DISTINCT e.id) as total
    FROM Roles r
    LEFT JOIN Puestos p ON r.id_rol = p.id_rol
    LEFT JOIN empleados e ON p.id_puesto = e.puesto AND e.activo = 1
    GROUP BY r.nombre
    ORDER BY r.nivel_acceso DESC
""")
for rol, total in cursor.fetchall():
    barra = "*" * total if total > 0 else ""
    print(f"   {rol:.<45} {total:>3} empleado(s) {barra}")

# 5. USUARIOS CON ROLES
print("\n5. USUARIOS CON ROLES (primeros 10):")
print("-" * 60)
cursor.execute("""
    SELECT u.nombre, r.nombre as rol
    FROM usuarios u
    LEFT JOIN Usuarios_Roles ur ON u.id = ur.usuario_id AND ur.activo = 1
    LEFT JOIN Roles r ON ur.id_rol = r.id_rol
    WHERE u.activo = 1
    LIMIT 10
""")
for nombre, rol in cursor.fetchall():
    print(f"   - {nombre:.<40} {rol or 'Sin rol'}")

# 6. RESUMEN
print("\n6. RESUMEN:")
print("-" * 60)
cursor.execute("SELECT COUNT(*) FROM Roles WHERE activo = 1")
total_roles = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM Puestos WHERE id_rol IS NOT NULL")
puestos_con_rol = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM empleados WHERE activo = 1")
total_empleados = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT e.id)
    FROM empleados e
    INNER JOIN Usuarios_Roles ur ON e.usuario_id = ur.usuario_id
    WHERE e.activo = 1 AND ur.activo = 1
""")
empleados_con_rol = cursor.fetchone()[0]

print(f"   Roles configurados: {total_roles}/5")
print(f"   Puestos con rol: {puestos_con_rol}")
print(f"   Total empleados: {total_empleados}")
print(f"   Empleados con rol: {empleados_con_rol}")

if total_roles == 5 and puestos_con_rol > 0 and empleados_con_rol > 0:
    print("\n   ESTADO: OK - Sistema configurado correctamente")
else:
    print("\n   ESTADO: REVISAR - Faltan configuraciones")

print("\n" + "="*70)
print("VERIFICACION COMPLETADA")
print("="*70)

conn.close()

