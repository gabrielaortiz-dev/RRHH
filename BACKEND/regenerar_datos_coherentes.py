"""
Script para regenerar datos coherentes en la base de datos
Limpia y crea datos desde cero con integridad referencial
"""
import sqlite3
from datetime import datetime, timedelta
import random
import bcrypt

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def limpiar_datos():
    """Limpia todos los datos existentes manteniendo la estructura"""
    print("\n" + "="*70)
    print("LIMPIANDO DATOS EXISTENTES")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    # Desactivar foreign keys temporalmente
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    tablas_a_limpiar = [
        'Notificaciones',
        'Capacitaciones',
        'Evaluaciones',
        'Vacaciones_Permisos',
        'Nomina_Deducciones',
        'Nomina_Bonificaciones',
        'Nomina',
        'Contratos',
        'asistencias',
        'empleados',
        'Usuarios_Roles',
        'Usuarios_Permisos',
        'Historial_Roles',
        'Roles_Permisos',
        'Roles',
        'usuarios',
        'Puestos',
        'departamentos'
    ]
    
    for tabla in tablas_a_limpiar:
        try:
            cursor.execute(f"DELETE FROM {tabla}")
            # Resetear el autoincrement
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
            print(f"   [OK] {tabla} limpiada")
        except Exception as e:
            print(f"   [SKIP] {tabla}: {str(e)}")
    
    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.close()
    
    print("\n[OK] Datos limpiados exitosamente")

def generar_datos_coherentes():
    """Genera datos coherentes con integridad referencial"""
    print("\n" + "="*70)
    print("GENERANDO DATOS COHERENTES")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # ================================================================
        # 1. DEPARTAMENTOS (10 departamentos desde ID 1)
        # ================================================================
        print("\n[1/10] Creando departamentos...")
        
        departamentos = [
            ('Recursos Humanos', 'Gestion de personal, reclutamiento y desarrollo organizacional'),
            ('Tecnologia', 'Desarrollo de software, infraestructura y sistemas'),
            ('Finanzas', 'Contabilidad, presupuestos y gestion financiera'),
            ('Marketing', 'Publicidad, comunicacion y marca'),
            ('Ventas', 'Gestion comercial y atencion a clientes'),
            ('Operaciones', 'Gestion operativa y procesos'),
            ('Legal', 'Asesoria juridica y cumplimiento'),
            ('Administracion', 'Gestion administrativa general'),
            ('Logistica', 'Distribucion y cadena de suministro'),
            ('Atencion al Cliente', 'Servicio y soporte al cliente')
        ]
        
        for nombre, desc in departamentos:
            cursor.execute("""
                INSERT INTO departamentos (nombre, descripcion, activo)
                VALUES (?, ?, 1)
            """, (nombre, desc))
        
        conn.commit()
        print(f"   [OK] {len(departamentos)} departamentos creados (ID 1-{len(departamentos)})")
        
        # ================================================================
        # 2. PUESTOS (20 puestos desde ID 1)
        # ================================================================
        print("\n[2/10] Creando puestos...")
        
        puestos = [
            ('Director de RRHH', 'Executive', 75000),
            ('Gerente de RRHH', 'Senior', 55000),
            ('Analista de RRHH', 'Mid', 38000),
            ('Reclutador', 'Junior', 30000),
            ('Director de Tecnologia', 'Executive', 85000),
            ('Desarrollador Senior', 'Senior', 60000),
            ('Desarrollador Mid', 'Mid', 45000),
            ('Desarrollador Junior', 'Junior', 32000),
            ('Director Financiero', 'Executive', 80000),
            ('Contador Senior', 'Senior', 50000),
            ('Analista Financiero', 'Mid', 40000),
            ('Gerente de Marketing', 'Senior', 58000),
            ('Especialista en Marketing', 'Mid', 42000),
            ('Community Manager', 'Junior', 30000),
            ('Gerente de Ventas', 'Senior', 62000),
            ('Ejecutivo de Ventas', 'Mid', 38000),
            ('Gerente de Operaciones', 'Senior', 60000),
            ('Coordinador de Logistica', 'Mid', 40000),
            ('Abogado Corporativo', 'Senior', 65000),
            ('Asistente Administrativo', 'Junior', 28000)
        ]
        
        for nombre, nivel, salario in puestos:
            cursor.execute("""
                INSERT INTO Puestos (nombre_puesto, nivel, salario_base)
                VALUES (?, ?, ?)
            """, (nombre, nivel, salario))
        
        conn.commit()
        print(f"   [OK] {len(puestos)} puestos creados (ID 1-{len(puestos)})")
        
        # ================================================================
        # 3. EMPLEADOS (100 empleados desde ID 1)
        # ================================================================
        print("\n[3/10] Creando empleados...")
        
        nombres = [
            'Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura',
            'Jose', 'Patricia', 'Miguel', 'Isabel', 'Francisco', 'Rosa', 'Antonio',
            'Mercedes', 'Manuel', 'Elena', 'Rafael', 'Cristina', 'Fernando', 'Beatriz',
            'Jorge', 'Silvia', 'Roberto', 'Monica', 'Alberto', 'Teresa', 'Raul', 'Diana',
            'Sergio', 'Lucia', 'Javier', 'Marta', 'Diego', 'Pilar', 'Andres', 'Natalia',
            'Oscar', 'Veronica', 'Ricardo', 'Sandra', 'Guillermo', 'Adriana', 'Pablo', 'Claudia'
        ]
        
        apellidos = [
            'Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Perez',
            'Sanchez', 'Ramirez', 'Torres', 'Flores', 'Rivera', 'Gomez', 'Diaz',
            'Cruz', 'Morales', 'Reyes', 'Jimenez', 'Hernandez', 'Ruiz', 'Ortiz',
            'Castillo', 'Romero', 'Silva', 'Moreno', 'Alvarez', 'Castro', 'Vargas'
        ]
        
        empleados_creados = 0
        for i in range(1, 101):  # 100 empleados
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            email = f"{nombre.lower()}.{apellido.lower()}{i}@empresa.com"
            telefono = f"+504 {random.randint(2000, 9999)}-{random.randint(1000, 9999)}"
            
            # Departamento entre 1 y 10
            dept_id = random.randint(1, 10)
            
            # Puesto entre 1 y 20
            puesto_id = random.randint(1, 20)
            
            # Obtener salario base del puesto
            cursor.execute("SELECT salario_base FROM Puestos WHERE id_puesto = ?", (puesto_id,))
            salario_base = cursor.fetchone()[0]
            salario = salario_base + random.randint(-5000, 10000)  # Variacion
            
            # Fecha de ingreso entre 1 y 5 años atras
            dias_atras = random.randint(365, 1825)
            fecha_ingreso = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO empleados 
                (nombre, apellido, email, telefono, departamento_id, puesto, fecha_ingreso, salario, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (nombre, apellido, email, telefono, dept_id, puesto_id, fecha_ingreso, salario))
            
            empleados_creados += 1
        
        conn.commit()
        print(f"   [OK] {empleados_creados} empleados creados (ID 1-{empleados_creados})")
        
        # ================================================================
        # 4. USUARIOS (10 usuarios administrativos)
        # ================================================================
        print("\n[4/10] Creando usuarios...")
        
        usuarios = [
            ('Admin Sistema', 'admin@rrhh.com', 'admin123', 'admin'),
            ('RRHH Manager', 'rrhh@rrhh.com', 'rrhh123', 'rrhh'),
            ('Supervisor General', 'supervisor@empresa.com', 'super123', 'supervisor'),
            ('Gerente TI', 'ti@empresa.com', 'ti123', 'empleado'),
            ('Gerente Finanzas', 'finanzas@empresa.com', 'fin123', 'empleado'),
            ('Gerente Ventas', 'ventas@empresa.com', 'ventas123', 'empleado'),
        ]
        
        for nombre, email, password, rol in usuarios:
            hashed = hash_password(password)
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (nombre, email, hashed, rol))
        
        conn.commit()
        print(f"   [OK] {len(usuarios)} usuarios creados")
        
        # ================================================================
        # 5. ROLES (5 roles del sistema)
        # ================================================================
        print("\n[5/10] Creando roles...")
        
        roles = [
            ('Administrador', 'Control total del sistema', None, 10, 1),
            ('RRHH', 'Gestion de recursos humanos', 1, 8, 1),
            ('Supervisor', 'Supervision de equipos', None, 6, 1),
            ('Empleado', 'Usuario estandar', None, 3, 1),
            ('Invitado', 'Acceso limitado', None, 1, 1)
        ]
        
        for nombre, desc, puesto, nivel, es_sistema in roles:
            cursor.execute("""
                INSERT INTO Roles (nombre, descripcion, id_puesto, nivel_acceso, es_sistema, activo)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (nombre, desc, puesto, nivel, es_sistema))
        
        conn.commit()
        print(f"   [OK] {len(roles)} roles creados")
        
        # ================================================================
        # 6. CONTRATOS (100 contratos, uno por empleado)
        # ================================================================
        print("\n[6/10] Creando contratos...")
        
        tipos_contrato = ['tiempo_indefinido', 'tiempo_determinado', 'por_proyecto']
        contratos_creados = 0
        
        for emp_id in range(1, 101):  # Un contrato por cada empleado
            tipo = random.choice(tipos_contrato)
            
            # Obtener fecha de ingreso del empleado
            cursor.execute("SELECT fecha_ingreso, salario FROM empleados WHERE id = ?", (emp_id,))
            emp_data = cursor.fetchone()
            fecha_inicio = emp_data[0]
            salario = emp_data[1]
            
            # Fecha fin solo para contratos determinados
            fecha_fin = None
            if tipo == 'tiempo_determinado':
                fecha_fin = (datetime.strptime(fecha_inicio, '%Y-%m-%d') + 
                           timedelta(days=random.randint(365, 730))).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO Contratos 
                (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, salario, estado)
                VALUES (?, ?, ?, ?, ?, 'activo')
            """, (emp_id, tipo, fecha_inicio, fecha_fin, salario))
            
            contratos_creados += 1
        
        conn.commit()
        print(f"   [OK] {contratos_creados} contratos creados (1 por empleado)")
        
        # ================================================================
        # 7. EVALUACIONES (100 evaluaciones, una por empleado)
        # ================================================================
        print("\n[7/10] Creando evaluaciones...")
        
        evaluadores = [
            'Carlos Gomez - Director RRHH',
            'Ana Martinez - Gerente RRHH',
            'Luis Torres - Supervisor General',
            'Maria Flores - Gerente de Area',
            'Pedro Sanchez - Director de Operaciones'
        ]
        
        evaluaciones_creadas = 0
        for emp_id in range(1, 101):  # Una evaluacion por empleado
            fecha = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
            puntaje = random.randint(65, 100)
            evaluador = random.choice(evaluadores)
            
            observaciones = [
                'Excelente desempeño en el periodo evaluado',
                'Cumple con los objetivos establecidos',
                'Muestra compromiso y dedicacion',
                'Requiere mejorar en algunas areas',
                'Destacado en trabajo en equipo'
            ]
            
            cursor.execute("""
                INSERT INTO Evaluaciones 
                (id_empleado, fecha, evaluador, puntaje, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (emp_id, fecha, evaluador, puntaje, random.choice(observaciones)))
            
            evaluaciones_creadas += 1
        
        conn.commit()
        print(f"   [OK] {evaluaciones_creadas} evaluaciones creadas (1 por empleado)")
        
        # ================================================================
        # 8. ASISTENCIAS (200 registros del ultimo mes)
        # ================================================================
        print("\n[8/10] Creando registros de asistencia...")
        
        asistencias_creadas = 0
        for i in range(200):
            emp_id = random.randint(1, 100)
            dias_atras = random.randint(1, 30)
            fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            # Hora de entrada entre 7:00 y 9:00
            hora_entrada = f"{random.randint(7, 8)}:{random.randint(0, 59):02d}:00"
            
            # Hora de salida entre 16:00 y 18:00
            hora_salida = f"{random.randint(16, 17)}:{random.randint(0, 59):02d}:00"
            
            cursor.execute("""
                INSERT INTO asistencias 
                (empleado_id, fecha, hora_entrada, hora_salida)
                VALUES (?, ?, ?, ?)
            """, (emp_id, fecha, hora_entrada, hora_salida))
            
            asistencias_creadas += 1
        
        conn.commit()
        print(f"   [OK] {asistencias_creadas} registros de asistencia creados")
        
        # ================================================================
        # 9. VACACIONES (50 solicitudes)
        # ================================================================
        print("\n[9/10] Creando solicitudes de vacaciones...")
        
        estados = ['pendiente', 'aprobada_jefe', 'aprobada_rrhh', 'rechazada']
        vacaciones_creadas = 0
        
        for i in range(50):
            emp_id = random.randint(1, 100)
            dias_adelante = random.randint(10, 180)
            fecha_inicio = (datetime.now() + timedelta(days=dias_adelante)).strftime('%Y-%m-%d')
            fecha_fin = (datetime.now() + timedelta(days=dias_adelante + random.randint(5, 15))).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO Vacaciones_Permisos 
                (id_empleado, tipo, fecha_inicio, fecha_fin, estado, observaciones)
                VALUES (?, 'vacaciones', ?, ?, ?, 'Vacaciones anuales')
            """, (emp_id, fecha_inicio, fecha_fin, random.choice(estados)))
            
            vacaciones_creadas += 1
        
        conn.commit()
        print(f"   [OK] {vacaciones_creadas} solicitudes de vacaciones creadas")
        
        # ================================================================
        # 10. CAPACITACIONES (30 registros)
        # ================================================================
        print("\n[10/10] Creando capacitaciones...")
        
        cursos = [
            ('Liderazgo Efectivo', 'Instituto de Liderazgo'),
            ('Excel Avanzado', 'Platzi'),
            ('Programacion en Python', 'Udemy'),
            ('Gestion de Proyectos', 'PMI'),
            ('Ingles Empresarial', 'English Academy'),
            ('Marketing Digital', 'Google Activate'),
            ('Finanzas para no Financieros', 'Coursera'),
            ('Atencion al Cliente', 'LinkedIn Learning')
        ]
        
        capacitaciones_creadas = 0
        for i in range(30):
            emp_id = random.randint(1, 100)
            curso, institucion = random.choice(cursos)
            fecha_inicio = (datetime.now() - timedelta(days=random.randint(60, 365))).strftime('%Y-%m-%d')
            fecha_fin = (datetime.now() - timedelta(days=random.randint(1, 59))).strftime('%Y-%m-%d')
            certificado = random.choice([0, 1])
            
            cursor.execute("""
                INSERT INTO Capacitaciones 
                (id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, curso, institucion, fecha_inicio, fecha_fin, certificado))
            
            capacitaciones_creadas += 1
        
        conn.commit()
        print(f"   [OK] {capacitaciones_creadas} capacitaciones creadas")
        
        # ================================================================
        # RESUMEN FINAL
        # ================================================================
        print("\n" + "="*70)
        print("RESUMEN DE DATOS GENERADOS")
        print("="*70)
        
        tablas_resumen = [
            ('departamentos', 'Departamentos'),
            ('Puestos', 'Puestos'),
            ('empleados', 'Empleados'),
            ('usuarios', 'Usuarios'),
            ('Roles', 'Roles'),
            ('Contratos', 'Contratos'),
            ('Evaluaciones', 'Evaluaciones'),
            ('asistencias', 'Asistencias'),
            ('Vacaciones_Permisos', 'Vacaciones'),
            ('Capacitaciones', 'Capacitaciones')
        ]
        
        for tabla, nombre in tablas_resumen:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"   {nombre:.<30} {count:>3} registros")
        
        print("\n" + "="*70)
        print("DATOS COHERENTES GENERADOS EXITOSAMENTE")
        print("="*70)
        print("\nCaracteristicas:")
        print("  - Departamentos: ID 1-10")
        print("  - Puestos: ID 1-20")
        print("  - Empleados: ID 1-100")
        print("  - Contratos: 1 por empleado (100 total)")
        print("  - Evaluaciones: 1 por empleado (100 total)")
        print("  - Integridad referencial: 100% correcta")
        print("  - Usuarios admin: 6 usuarios de prueba")
        print("\nCredenciales de prueba:")
        print("  Email: admin@rrhh.com")
        print("  Password: admin123")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("REGENERACION DE DATOS COHERENTES")
    print("Sistema RRHH - Base de Datos SQLite")
    print("="*70)
    print("\nEste script va a:")
    print("  1. Limpiar todos los datos existentes")
    print("  2. Generar datos nuevos coherentes")
    print("  3. Mantener integridad referencial")
    print("\n" + "="*70)
    
    respuesta = input("\nDesea continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        limpiar_datos()
        generar_datos_coherentes()
    else:
        print("\nOperacion cancelada.")

