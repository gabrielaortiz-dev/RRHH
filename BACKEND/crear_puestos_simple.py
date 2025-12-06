"""Crear Puestos y Vincular con Roles - Version Simple"""
import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

# Mapeo de puestos a roles
puestos_por_rol = {
    'Super Admin': [
        ('Gerente General', 'Executive', 95000),
        ('Director de Tecnologia (CTO)', 'Executive', 90000),
        ('Gerente de Proyectos', 'Executive', 85000)
    ],
    'Gerente / Alta Gerencia': [
        ('Gerente de RRHH', 'Senior', 75000),
        ('Gerente de Ventas', 'Senior', 75000)
    ],
    'Supervisor / Jefe de Area': [
        ('Analista de RRHH', 'Mid', 50000),
        ('Contador', 'Senior', 55000),
        ('Analista Financiero', 'Mid', 50000),
        ('Especialista en Marketing', 'Mid', 48000),
        ('Supervisor de Atencion', 'Mid', 45000),
        ('Coordinador de Operaciones', 'Mid', 47000),
        ('Coordinador Logistico', 'Mid', 46000),
        ('Abogado Corporativo', 'Senior', 65000)
    ],
    'Operativo': [
        ('Desarrollador Senior', 'Senior', 60000),
        ('Desarrollador Junior', 'Junior', 35000),
        ('Community Manager', 'Junior', 32000),
        ('Ejecutivo de Ventas', 'Mid', 38000),
        ('Representante de Servicio', 'Junior', 30000),
        ('Asistente Legal', 'Junior', 33000),
        ('Asistente Administrativo', 'Junior', 28000)
    ]
}

print("\n" + "="*70)
print("CREANDO PUESTOS Y VINCULANDOLOS CON ROLES")
print("="*70)

total = 0
for rol_nombre, puestos in puestos_por_rol.items():
    # Obtener ID del rol
    cursor.execute("SELECT id_rol FROM Roles WHERE nombre = ?", (rol_nombre,))
    resultado = cursor.fetchone()
    
    if not resultado:
        print(f"\nERROR: No se encontro el rol {rol_nombre}")
        continue
    
    rol_id = resultado[0]
    print(f"\nRol: {rol_nombre} (ID: {rol_id})")
    
    for nombre_puesto, nivel, salario in puestos:
        try:
            cursor.execute("""
                INSERT INTO Puestos (nombre_puesto, nivel, salario_base, id_rol)
                VALUES (?, ?, ?, ?)
            """, (nombre_puesto, nivel, salario, rol_id))
            
            print(f"  + {nombre_puesto} - ${salario:,.2f}")
            total += 1
        except Exception as e:
            print(f"  ERROR con {nombre_puesto}: {e}")

conn.commit()

print(f"\n{total} puestos creados exitosamente")
print("="*70)

# Ahora asignar roles a empleados
print("\nASIGNANDO ROLES A EMPLEADOS...")
print("="*70)

cursor.execute("""
    SELECT e.id, e.nombre, e.apellido, e.usuario_id, e.puesto, p.nombre_puesto, p.id_rol
    FROM empleados e
    LEFT JOIN Puestos p ON e.puesto = p.id_puesto
    WHERE e.activo = 1 AND e.usuario_id IS NOT NULL
""")

empleados = cursor.fetchall()
asignados = 0

for emp_id, nombre, apellido, usuario_id, puesto_id, puesto_nombre, rol_id in empleados:
    if not rol_id:
        continue
    
    try:
        # Verificar si ya tiene rol
        cursor.execute("""
            SELECT COUNT(*) FROM Usuarios_Roles
            WHERE usuario_id = ? AND id_rol = ? AND activo = 1
        """, (usuario_id, rol_id))
        
        if cursor.fetchone()[0] == 0:
            # Asignar rol
            cursor.execute("""
                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                VALUES (?, ?, 1, 1)
            """, (usuario_id, rol_id))
            
            asignados += 1
    except Exception as e:
        pass

conn.commit()
print(f"{asignados} roles asignados a empleados")
print("="*70)

conn.close()

print("\nCOMPLETADO - Ahora ejecuta: python ver_estado_simple.py")

