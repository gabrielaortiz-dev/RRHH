"""
Script para insertar datos de prueba en el sistema RRHH
Ejecutar: python insertar_datos_prueba.py
"""
import sqlite3
import bcrypt
from datetime import datetime, date

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def insertar_datos_prueba():
    """Inserta datos de prueba en la base de datos"""
    
    # Conectar a la base de datos
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    print("🚀 Iniciando inserción de datos de prueba...\n")
    
    # ============================================================================
    # 1. DEPARTAMENTOS
    # ============================================================================
    print("📁 Insertando Departamentos...")
    departamentos = [
        ('Tecnología', 'Departamento de Desarrollo y Sistemas'),
        ('Recursos Humanos', 'Gestión de personal y talento'),
        ('Finanzas', 'Control financiero y contabilidad'),
        ('Ventas', 'Departamento comercial y ventas'),
        ('Marketing', 'Publicidad y comunicación'),
        ('Operaciones', 'Logística y operaciones'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Departamentos (nombre_departamento, descripcion)
        VALUES (?, ?)
    ''', departamentos)
    
    print(f"   ✅ {len(departamentos)} departamentos insertados\n")
    
    # ============================================================================
    # 2. PUESTOS
    # ============================================================================
    print("💼 Insertando Puestos...")
    puestos = [
        # Tecnología
        ('Desarrollador Junior', 'Junior', 25000.00),
        ('Desarrollador Senior', 'Senior', 45000.00),
        ('Tech Lead', 'Lead', 60000.00),
        ('Arquitecto de Software', 'Senior', 70000.00),
        
        # RRHH
        ('Analista de RRHH', 'Junior', 22000.00),
        ('Especialista de RRHH', 'Semi-Senior', 32000.00),
        ('Gerente de RRHH', 'Gerente', 55000.00),
        
        # Finanzas
        ('Contador Junior', 'Junior', 23000.00),
        ('Contador Senior', 'Senior', 40000.00),
        ('Gerente Financiero', 'Gerente', 60000.00),
        
        # Ventas
        ('Ejecutivo de Ventas', 'Junior', 20000.00),
        ('Supervisor de Ventas', 'Semi-Senior', 35000.00),
        ('Gerente de Ventas', 'Gerente', 50000.00),
        
        # Marketing
        ('Analista de Marketing', 'Junior', 22000.00),
        ('Especialista en Marketing Digital', 'Semi-Senior', 33000.00),
        ('Gerente de Marketing', 'Gerente', 52000.00),
        
        # Operaciones
        ('Asistente de Operaciones', 'Junior', 18000.00),
        ('Coordinador de Logística', 'Semi-Senior', 30000.00),
        ('Gerente de Operaciones', 'Gerente', 55000.00),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Puestos (nombre_puesto, nivel, salario_base)
        VALUES (?, ?, ?)
    ''', puestos)
    
    print(f"   ✅ {len(puestos)} puestos insertados\n")
    
    # ============================================================================
    # 3. EMPLEADOS
    # ============================================================================
    print("👥 Insertando Empleados...")
    empleados = [
        # Tecnología (depto 1)
        ('Carlos', 'Méndez', '1990-05-15', 'Masculino', 'Soltero', 'Col. Palmira, Tegucigalpa', '9988-7766', 'carlos.mendez@empresa.com', '2023-01-15', 'Activo', 1, 2),
        ('Ana', 'Torres', '1988-08-22', 'Femenino', 'Casada', 'Col. Kennedy, Tegucigalpa', '9977-6655', 'ana.torres@empresa.com', '2022-06-10', 'Activo', 1, 3),
        ('Luis', 'Ramírez', '1992-03-10', 'Masculino', 'Soltero', 'Res. El Trapiche, SPS', '9966-5544', 'luis.ramirez@empresa.com', '2024-02-01', 'Activo', 1, 1),
        
        # RRHH (depto 2)
        ('María', 'González', '1989-11-05', 'Femenino', 'Casada', 'Col. Lomas del Guijarro, Teg', '9955-4433', 'maria.gonzalez@empresa.com', '2021-03-15', 'Activo', 2, 7),
        ('Roberto', 'Sánchez', '1991-07-18', 'Masculino', 'Soltero', 'Col. Rubén Darío, Teg', '9944-3322', 'roberto.sanchez@empresa.com', '2023-09-01', 'Activo', 2, 6),
        
        # Finanzas (depto 3)
        ('Patricia', 'Flores', '1987-12-30', 'Femenino', 'Casada', 'Col. Miraflores, Teg', '9933-2211', 'patricia.flores@empresa.com', '2020-05-20', 'Activo', 3, 10),
        ('Jorge', 'Martínez', '1993-04-25', 'Masculino', 'Soltero', 'Col. Ayala, Teg', '9922-1100', 'jorge.martinez@empresa.com', '2023-11-10', 'Activo', 3, 9),
        
        # Ventas (depto 4)
        ('Sofía', 'López', '1994-09-08', 'Femenino', 'Soltera', 'Col. Las Colinas, Teg', '9911-0099', 'sofia.lopez@empresa.com', '2024-01-05', 'Activo', 4, 11),
        ('Diego', 'Hernández', '1990-02-14', 'Masculino', 'Casado', 'Col. Tepeyac, Teg', '9900-9988', 'diego.hernandez@empresa.com', '2022-08-15', 'Activo', 4, 12),
        
        # Marketing (depto 5)
        ('Valentina', 'Cruz', '1992-06-20', 'Femenino', 'Soltera', 'Col. La Granja, Teg', '9899-8877', 'valentina.cruz@empresa.com', '2023-04-01', 'Activo', 5, 14),
        
        # Operaciones (depto 6)
        ('Fernando', 'Reyes', '1991-10-12', 'Masculino', 'Casado', 'Col. Jardines del Valle, SPS', '9888-7766', 'fernando.reyes@empresa.com', '2022-12-01', 'Activo', 6, 18),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Empleados (
            nombre, apellido, fecha_nacimiento, genero, estado_civil, 
            direccion, telefono, correo, fecha_ingreso, estado, 
            id_departamento, id_puesto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', empleados)
    
    print(f"   ✅ {len(empleados)} empleados insertados\n")
    
    # ============================================================================
    # 4. USUARIOS
    # ============================================================================
    print("🔐 Insertando Usuarios...")
    
    # Usuario administrador
    admin_password = hash_password("admin123")
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Administrador del Sistema', 'admin@empresa.com', admin_password, 'administrador', 1))
    
    # Usuario RRHH
    rrhh_password = hash_password("rrhh123")
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
        VALUES (?, ?, ?, ?, ?)
    ''', ('María González', 'maria.gonzalez@empresa.com', rrhh_password, 'rrhh', 1))
    
    # Usuario Supervisor
    supervisor_password = hash_password("supervisor123")
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Ana Torres', 'ana.torres@empresa.com', supervisor_password, 'supervisor', 1))
    
    # Usuario Empleado
    empleado_password = hash_password("empleado123")
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Carlos Méndez', 'carlos.mendez@empresa.com', empleado_password, 'empleado', 1))
    
    print(f"   ✅ 4 usuarios insertados (admin, rrhh, supervisor, empleado)\n")
    
    # ============================================================================
    # 5. ASIGNAR ROLES A USUARIOS
    # ============================================================================
    print("🎯 Asignando roles a usuarios...")
    
    # Obtener IDs de usuarios y roles
    cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@empresa.com'")
    admin_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM usuarios WHERE email = 'maria.gonzalez@empresa.com'")
    rrhh_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM usuarios WHERE email = 'ana.torres@empresa.com'")
    supervisor_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM usuarios WHERE email = 'carlos.mendez@empresa.com'")
    empleado_id = cursor.fetchone()[0]
    
    # Obtener IDs de roles
    cursor.execute("SELECT id_rol FROM Roles WHERE nombre = 'administrador'")
    rol_admin_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id_rol FROM Roles WHERE nombre = 'rrhh'")
    rol_rrhh_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id_rol FROM Roles WHERE nombre = 'supervisor'")
    rol_supervisor_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id_rol FROM Roles WHERE nombre = 'empleado'")
    rol_empleado_id = cursor.fetchone()[0]
    
    # Asignar roles
    roles_usuarios = [
        (admin_id, rol_admin_id, 1),
        (rrhh_id, rol_rrhh_id, 1),
        (supervisor_id, rol_supervisor_id, 1),
        (empleado_id, rol_empleado_id, 1),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
        VALUES (?, ?, ?, 1)
    ''', roles_usuarios)
    
    print(f"   ✅ Roles asignados a usuarios\n")
    
    # ============================================================================
    # 6. CAPACITACIONES
    # ============================================================================
    print("📚 Insertando Capacitaciones...")
    capacitaciones = [
        (1, 'Python Avanzado', 'Platzi', '2024-01-15', '2024-03-15', 1),
        (2, 'Arquitectura de Software', 'Udemy', '2024-02-01', '2024-04-01', 1),
        (3, 'Git y GitHub', 'Coursera', '2024-03-10', '2024-04-10', 1),
        (4, 'Gestión de Talento Humano', 'INFOP', '2023-06-01', '2023-08-01', 1),
        (5, 'Excel Avanzado para RRHH', 'LinkedIn Learning', '2024-01-10', '2024-02-10', 1),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Capacitaciones (
            id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', capacitaciones)
    
    print(f"   ✅ {len(capacitaciones)} capacitaciones insertadas\n")
    
    # ============================================================================
    # 7. EVALUACIONES
    # ============================================================================
    print("⭐ Insertando Evaluaciones...")
    evaluaciones = [
        (1, '2024-06-15', 'Ana Torres', 85, 'Excelente desempeño en desarrollo de APIs'),
        (2, '2024-06-15', 'Gerente TI', 92, 'Liderazgo excepcional en proyectos'),
        (3, '2024-06-20', 'Ana Torres', 78, 'Buen progreso, necesita mejorar testing'),
        (4, '2024-06-18', 'Gerente RRHH', 88, 'Excelente gestión de procesos de reclutamiento'),
        (5, '2024-06-19', 'María González', 80, 'Cumple con objetivos, buen trabajo en equipo'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Evaluaciones (
            id_empleado, fecha, evaluador, puntaje, observaciones
        ) VALUES (?, ?, ?, ?, ?)
    ''', evaluaciones)
    
    print(f"   ✅ {len(evaluaciones)} evaluaciones insertadas\n")
    
    # ============================================================================
    # 8. VINCULAR ROLES A PUESTOS (Ejemplos)
    # ============================================================================
    print("🔗 Vinculando roles a puestos...")
    
    # Gerente de RRHH → rol RRHH
    cursor.execute('''
        UPDATE Roles SET id_puesto = 7 WHERE nombre = 'rrhh'
    ''')
    
    # Tech Lead → rol supervisor
    cursor.execute('''
        UPDATE Roles SET id_puesto = 3 WHERE nombre = 'supervisor'
    ''')
    
    print(f"   ✅ Roles vinculados a puestos específicos\n")
    
    # ============================================================================
    # COMMIT Y RESUMEN
    # ============================================================================
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("✅ DATOS DE PRUEBA INSERTADOS EXITOSAMENTE")
    print("=" * 60)
    print("\n📊 RESUMEN:")
    print(f"   • {len(departamentos)} Departamentos")
    print(f"   • {len(puestos)} Puestos")
    print(f"   • {len(empleados)} Empleados")
    print(f"   • 4 Usuarios con roles asignados")
    print(f"   • {len(capacitaciones)} Capacitaciones")
    print(f"   • {len(evaluaciones)} Evaluaciones")
    print(f"   • Roles del sistema: 5 (admin, rrhh, supervisor, empleado, invitado)")
    print(f"   • Permisos del sistema: 42 en 13 módulos")
    
    print("\n🔐 CREDENCIALES DE PRUEBA:")
    print("-" * 60)
    print("1. ADMINISTRADOR:")
    print("   Email: admin@empresa.com")
    print("   Password: admin123")
    print("   Permisos: TODOS (42)")
    print()
    print("2. RRHH:")
    print("   Email: maria.gonzalez@empresa.com")
    print("   Password: rrhh123")
    print("   Permisos: ~35 permisos de gestión de RRHH")
    print()
    print("3. SUPERVISOR:")
    print("   Email: ana.torres@empresa.com")
    print("   Password: supervisor123")
    print("   Permisos: ~15 permisos de gestión de equipo")
    print()
    print("4. EMPLEADO:")
    print("   Email: carlos.mendez@empresa.com")
    print("   Password: empleado123")
    print("   Permisos: ~8 permisos básicos")
    print("-" * 60)
    
    print("\n🚀 ENDPOINTS PARA PROBAR:")
    print("-" * 60)
    print("   GET  http://localhost:8000/api/puestos")
    print("   GET  http://localhost:8000/api/empleados")
    print("   GET  http://localhost:8000/api/roles")
    print("   GET  http://localhost:8000/api/permisos")
    print("   GET  http://localhost:8000/api/usuarios/1/permisos")
    print("   POST http://localhost:8000/api/usuarios/login")
    print("-" * 60)
    
    print("\n✨ ¡LISTO! Ahora puedes probar el sistema completo.")
    print("   Abre: http://localhost:8000/docs para ver Swagger UI\n")

if __name__ == "__main__":
    try:
        insertar_datos_prueba()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nAsegúrate de que:")
        print("1. El servidor FastAPI esté corriendo")
        print("2. La base de datos rrhh.db exista")
        print("3. Las tablas estén creadas (se crean al iniciar el servidor)")

