"""
Script para poblar la base de datos con datos empresariales coherentes
Utiliza la estructura actualizada de tablas del sistema
"""
import sqlite3
from datetime import datetime, timedelta
import random
import bcrypt
import json

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def poblar_datos_empresariales():
    print("="*80)
    print("POBLANDO BASE DE DATOS CON DATOS EMPRESARIALES COHERENTES")
    print("="*80)
    
    conn = sqlite3.connect('rrhh.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # ==================================================================
        # 1. DEPARTAMENTOS (8 departamentos principales)
        # ==================================================================
        print("\n[1/11] Creando departamentos...")
        
        departamentos = [
            ('Tecnología', 'Desarrollo de software, sistemas y soporte técnico'),
            ('Recursos Humanos', 'Gestión del talento humano y desarrollo organizacional'),
            ('Finanzas y Contabilidad', 'Gestión financiera, contabilidad y presupuestos'),
            ('Marketing y Comunicación', 'Marketing digital, publicidad y comunicación corporativa'),
            ('Ventas', 'Gestión comercial y desarrollo de negocios'),
            ('Operaciones', 'Gestión operativa y mejora de procesos'),
            ('Atención al Cliente', 'Servicio al cliente y soporte'),
            ('Legal y Cumplimiento', 'Asesoría jurídica y cumplimiento normativo')
        ]
        
        for nombre, desc in departamentos:
            cursor.execute("""
                INSERT OR IGNORE INTO departamentos (nombre, descripcion, activo)
                VALUES (?, ?, 1)
            """, (nombre, desc))
        
        conn.commit()
        print(f"[OK] {len(departamentos)} departamentos creados")
        
        # ==================================================================
        # 2. PUESTOS (15 puestos con niveles y salarios coherentes)
        # ==================================================================
        print("\n[2/11] Creando puestos con estructura salarial...")
        
        puestos = [
            ('Director General', 'Executive', 120000),
            ('Gerente de Departamento', 'Senior', 75000),
            ('Coordinador de Área', 'Mid-Senior', 55000),
            ('Analista Senior', 'Senior', 50000),
            ('Analista', 'Mid', 40000),
            ('Analista Junior', 'Junior', 30000),
            ('Desarrollador Senior', 'Senior', 60000),
            ('Desarrollador', 'Mid', 45000),
            ('Desarrollador Junior', 'Junior', 32000),
            ('Especialista de Marketing', 'Mid', 42000),
            ('Ejecutivo de Ventas', 'Mid', 38000),
            ('Contador', 'Mid', 45000),
            ('Representante de Servicio', 'Junior', 28000),
            ('Asistente Administrativo', 'Junior', 25000),
            ('Asistente de Recursos Humanos', 'Junior', 27000)
        ]
        
        for nombre, nivel, salario in puestos:
            cursor.execute("""
                INSERT OR IGNORE INTO Puestos (nombre_puesto, nivel, salario_base)
                VALUES (?, ?, ?)
            """, (nombre, nivel, salario))
        
        conn.commit()
        print(f"[OK] {len(puestos)} puestos creados")
        
        # ==================================================================
        # 3. EMPLEADOS (35 empleados coherentes con sus departamentos)
        # ==================================================================
        print("\n[3/11] Creando empleados con datos realistas...")
        
        # Obtener IDs de departamentos y puestos
        cursor.execute("SELECT id, nombre FROM departamentos")
        depts = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id_puesto, nombre_puesto, salario_base FROM Puestos")
        puestos_dict = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}
        
        # Empleados por departamento con asignación coherente
        empleados = [
            # Dirección
            ('Juan Carlos', 'Rodríguez', 'jrodriguez@empresa.hn', '+504 9876-5432', 'Legal y Cumplimiento', 'Director General', '2018-01-15'),
            
            # Tecnología
            ('María Fernanda', 'García', 'mgarcia@empresa.hn', '+504 9876-5433', 'Tecnología', 'Gerente de Departamento', '2019-03-10'),
            ('Carlos Eduardo', 'Martínez', 'cmartinez@empresa.hn', '+504 9876-5434', 'Tecnología', 'Desarrollador Senior', '2019-06-15'),
            ('Ana Patricia', 'López', 'alopez@empresa.hn', '+504 9876-5435', 'Tecnología', 'Desarrollador', '2020-02-20'),
            ('Luis Alberto', 'Hernández', 'lhernandez@empresa.hn', '+504 9876-5436', 'Tecnología', 'Desarrollador Junior', '2022-01-10'),
            ('Carmen Rosa', 'Díaz', 'cdiaz@empresa.hn', '+504 9876-5437', 'Tecnología', 'Desarrollador', '2021-04-15'),
            
            # Recursos Humanos
            ('Pedro Antonio', 'González', 'pgonzalez@empresa.hn', '+504 9876-5438', 'Recursos Humanos', 'Gerente de Departamento', '2018-05-20'),
            ('Laura Beatriz', 'Ramírez', 'lramirez@empresa.hn', '+504 9876-5439', 'Recursos Humanos', 'Analista Senior', '2019-08-15'),
            ('José Manuel', 'Torres', 'jtorres@empresa.hn', '+504 9876-5440', 'Recursos Humanos', 'Asistente de Recursos Humanos', '2021-09-01'),
            
            # Finanzas
            ('Patricia Elena', 'Flores', 'pflores@empresa.hn', '+504 9876-5441', 'Finanzas y Contabilidad', 'Gerente de Departamento', '2018-07-12'),
            ('Miguel Ángel', 'Sánchez', 'msanchez@empresa.hn', '+504 9876-5442', 'Finanzas y Contabilidad', 'Contador', '2019-10-05'),
            ('Isabel Cristina', 'Reyes', 'ireyes@empresa.hn', '+504 9876-5443', 'Finanzas y Contabilidad', 'Analista', '2020-05-18'),
            ('Francisco Javier', 'Morales', 'fmorales@empresa.hn', '+504 9876-5444', 'Finanzas y Contabilidad', 'Analista Junior', '2022-03-01'),
            
            # Marketing
            ('Rosa María', 'Cruz', 'rcruz@empresa.hn', '+504 9876-5445', 'Marketing y Comunicación', 'Coordinador de Área', '2019-11-20'),
            ('Antonio José', 'Jiménez', 'ajimenez@empresa.hn', '+504 9876-5446', 'Marketing y Comunicación', 'Especialista de Marketing', '2020-08-10'),
            ('Mercedes Luisa', 'Ortiz', 'mortiz@empresa.hn', '+504 9876-5447', 'Marketing y Comunicación', 'Analista', '2021-06-15'),
            
            # Ventas
            ('Manuel Ernesto', 'Ruiz', 'mruiz@empresa.hn', '+504 9876-5448', 'Ventas', 'Gerente de Departamento', '2018-09-05'),
            ('Elena Victoria', 'Gómez', 'egomez@empresa.hn', '+504 9876-5449', 'Ventas', 'Ejecutivo de Ventas', '2019-12-01'),
            ('Rafael David', 'Pérez', 'rperez@empresa.hn', '+504 9876-5450', 'Ventas', 'Ejecutivo de Ventas', '2020-10-12'),
            ('Cristina Isabel', 'Rivera', 'crivera@empresa.hn', '+504 9876-5451', 'Ventas', 'Ejecutivo de Ventas', '2021-02-20'),
            
            # Operaciones
            ('Fernando Luis', 'Castillo', 'fcastillo@empresa.hn', '+504 9876-5452', 'Operaciones', 'Coordinador de Área', '2019-04-15'),
            ('Beatriz Alejandra', 'Vargas', 'bvargas@empresa.hn', '+504 9876-5453', 'Operaciones', 'Analista', '2020-07-22'),
            ('Jorge Alberto', 'Medina', 'jmedina@empresa.hn', '+504 9876-5454', 'Operaciones', 'Analista Junior', '2022-05-10'),
            
            # Atención al Cliente
            ('Silvia Andrea', 'Campos', 'scampos@empresa.hn', '+504 9876-5455', 'Atención al Cliente', 'Coordinador de Área', '2019-06-08'),
            ('Roberto Carlos', 'Navarro', 'rnavarro@empresa.hn', '+504 9876-5456', 'Atención al Cliente', 'Representante de Servicio', '2020-09-15'),
            ('Monica Patricia', 'Serrano', 'mserrano@empresa.hn', '+504 9876-5457', 'Atención al Cliente', 'Representante de Servicio', '2021-01-20'),
            ('Alberto David', 'Molina', 'amolina@empresa.hn', '+504 9876-5458', 'Atención al Cliente', 'Representante de Servicio', '2021-11-05'),
            
            # Legal
            ('Teresa Gabriela', 'Guerrero', 'tguerrero@empresa.hn', '+504 9876-5459', 'Legal y Cumplimiento', 'Analista Senior', '2019-02-14'),
            ('Raúl Fernando', 'Méndez', 'rmendez@empresa.hn', '+504 9876-5460', 'Legal y Cumplimiento', 'Analista', '2020-11-30'),
            
            # Administrativos
            ('Diana Carolina', 'Aguilar', 'daguilar@empresa.hn', '+504 9876-5461', 'Recursos Humanos', 'Asistente Administrativo', '2021-03-15'),
            ('Rodrigo Andrés', 'Vega', 'rvega@empresa.hn', '+504 9876-5462', 'Finanzas y Contabilidad', 'Asistente Administrativo', '2021-08-22'),
            ('Gabriela María', 'Paredes', 'gparedes@empresa.hn', '+504 9876-5463', 'Operaciones', 'Asistente Administrativo', '2022-02-10'),
            ('Sebastián José', 'Núñez', 'snunez@empresa.hn', '+504 9876-5464', 'Tecnología', 'Analista', '2020-12-05'),
            ('Valeria Sofía', 'Rojas', 'vrojas@empresa.hn', '+504 9876-5465', 'Marketing y Comunicación', 'Analista Junior', '2022-04-18'),
            ('Alejandro Mauricio', 'Mendoza', 'amendoza@empresa.hn', '+504 9876-5466', 'Ventas', 'Analista', '2021-07-12')
        ]
        
        empleados_creados = 0
        empleados_ids = []
        
        for nombre, apellido, email, telefono, dept_nombre, puesto_nombre, fecha_ingreso in empleados:
            dept_id = depts.get(dept_nombre)
            puesto_info = puestos_dict.get(puesto_nombre)
            
            if dept_id and puesto_info:
                puesto_id, salario_base = puesto_info
                
                cursor.execute("""
                    INSERT INTO empleados 
                    (nombre, apellido, email, telefono, fecha_ingreso,
                     departamento_id, puesto, salario, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (nombre, apellido, email, telefono, fecha_ingreso, 
                      dept_id, puesto_nombre, salario_base))
                
                empleados_ids.append(cursor.lastrowid)
                empleados_creados += 1
        
        conn.commit()
        print(f"[OK] {empleados_creados} empleados creados")
        
        # ==================================================================
        # 4. USUARIOS (administradores + algunos empleados)
        # ==================================================================
        print("\n[4/11] Creando usuarios del sistema...")
        
        # Usuarios administrativos
        usuarios_admin = [
            ('Admin Sistema', 'admin@empresa.hn', 'Admin123!', 'administrador'),
            ('RRHH Manager', 'rrhh@empresa.hn', 'RRHH123!', 'rrhh'),
            ('Supervisor General', 'supervisor@empresa.hn', 'Super123!', 'supervisor'),
        ]
        
        usuarios_creados = 0
        usuario_ids = []
        
        for nombre, email, password, rol in usuarios_admin:
            hashed = hash_password(password)
            cursor.execute("""
                INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (nombre, email, hashed, rol))
            if cursor.lastrowid:
                usuario_ids.append(cursor.lastrowid)
                usuarios_creados += 1
        
        # Crear usuarios para los gerentes (empleados)
        cursor.execute("""
            SELECT id, nombre, apellido, email
            FROM empleados 
            WHERE puesto LIKE '%Gerente%' OR puesto LIKE '%Director%'
        """)
        gerentes = cursor.fetchall()
        
        for emp in gerentes:
            email = emp[3]
            nombre_completo = f"{emp[1]} {emp[2]}"
            password_temp = "Temp123!"
            hashed = hash_password(password_temp)
            
            cursor.execute("""
                INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
                VALUES (?, ?, ?, 'supervisor', 1)
            """, (nombre_completo, email, hashed))
            
            if cursor.lastrowid:
                usuario_ids.append(cursor.lastrowid)
                usuarios_creados += 1
        
        conn.commit()
        print(f"[OK] {usuarios_creados} usuarios creados")
        
        # ==================================================================
        # 5. CONTRATOS (todos los empleados)
        # ==================================================================
        print("\n[5/11] Creando contratos laborales...")
        
        cursor.execute("""
            SELECT e.id, e.salario, e.fecha_ingreso, e.puesto, e.nombre, e.apellido
            FROM empleados e
        """)
        empleados_para_contrato = cursor.fetchall()
        
        contratos_creados = 0
        
        for emp in empleados_para_contrato:
            emp_id, salario, fecha_ingreso, puesto_nombre, nombre, apellido = emp
            
            # Mayoría contratos indefinidos, algunos determinados
            if random.random() < 0.8:
                tipo_contrato = 'tiempo_indefinido'
                fecha_fin = None
            else:
                tipo_contrato = 'tiempo_determinado'
                # 1 año desde la fecha de ingreso
                fecha_ingreso_dt = datetime.strptime(fecha_ingreso, '%Y-%m-%d')
                fecha_fin = (fecha_ingreso_dt + timedelta(days=365)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO Contratos 
                (id_empleado, empresa_nombre, trabajador_nombre_completo,
                 nombre_puesto, tipo_contrato, salario_base, salario,
                 fecha_inicio, fecha_fin, estado)
                VALUES (?, 'Empresa Honduras S.A.', ?, ?, ?, ?, ?, ?, ?, 'activo')
            """, (emp_id, f"{nombre} {apellido}", puesto_nombre, tipo_contrato, 
                  salario, salario, fecha_ingreso, fecha_fin))
            
            contratos_creados += 1
        
        conn.commit()
        print(f"[OK] {contratos_creados} contratos creados")
        
        # ==================================================================
        # 6. ASISTENCIAS (último mes - 20 días hábiles)
        # ==================================================================
        print("\n[6/11] Creando registros de asistencia...")
        
        asistencias_creadas = 0
        hoy = datetime.now()
        
        # 20 días hábiles hacia atrás
        for dia in range(20):
            fecha = (hoy - timedelta(days=dia)).strftime('%Y-%m-%d')
            
            # Asistencia para el 90% de empleados (algunos faltan)
            for emp_id in random.sample(empleados_ids, int(len(empleados_ids) * 0.9)):
                # Hora de entrada: mayoría puntual, algunos tarde
                if random.random() < 0.85:  # 85% llega a tiempo
                    hora_entrada = f"08:{random.randint(0, 15):02d}:00"
                else:
                    hora_entrada = f"08:{random.randint(16, 59):02d}:00"
                
                # Hora de salida normal
                hora_salida = f"17:{random.randint(0, 30):02d}:00"
                
                cursor.execute("""
                    INSERT INTO asistencias 
                    (empleado_id, fecha, hora_entrada, hora_salida, estado, observaciones)
                    VALUES (?, ?, ?, ?, 'presente', 'Asistencia normal')
                """, (emp_id, fecha, hora_entrada, hora_salida))
                
                asistencias_creadas += 1
        
        conn.commit()
        print(f"[OK] {asistencias_creadas} registros de asistencia creados")
        
        # ==================================================================
        # 7. NÓMINAS (mes actual)
        # ==================================================================
        print("\n[7/11] Generando nominas del mes actual...")
        
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        
        cursor.execute("SELECT id, salario FROM empleados")
        empleados_nomina = cursor.fetchall()
        
        nominas_creadas = 0
        
        for emp_id, salario_base in empleados_nomina:
            # Bonificaciones: 10% del salario
            bonificaciones = salario_base * 0.10
            
            # Deducciones: IHSS (7%), RAP (1.5%), ISR (variable según salario)
            ihss = salario_base * 0.07
            rap = salario_base * 0.015
            
            # ISR simplificado
            if salario_base > 50000:
                isr = salario_base * 0.15
            elif salario_base > 30000:
                isr = salario_base * 0.10
            else:
                isr = 0
            
            deducciones_total = ihss + rap + isr
            salario_neto = salario_base + bonificaciones - deducciones_total
            
            # JSON de bonificaciones y deducciones
            bonif_json = json.dumps([
                {"concepto": "Bonificación Desempeño", "monto": bonificaciones}
            ])
            
            deduc_json = json.dumps([
                {"concepto": "IHSS", "monto": ihss},
                {"concepto": "RAP", "monto": rap},
                {"concepto": "ISR", "monto": isr}
            ])
            
            cursor.execute("""
                INSERT INTO Nomina 
                (id_empleado, mes, anio, salario_base, bonificaciones, deducciones, 
                 salario_neto, fecha_pago)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (emp_id, mes_actual, anio_actual, salario_base, bonificaciones,
                  deducciones_total, salario_neto, datetime.now().strftime('%Y-%m-%d')))
            
            nominas_creadas += 1
        
        conn.commit()
        print(f"[OK] {nominas_creadas} nominas generadas")
        
        # ==================================================================
        # 8. VACACIONES Y PERMISOS
        # ==================================================================
        print("\n[8/11] Creando solicitudes de vacaciones...")
        
        # 15 solicitudes
        empleados_sample = random.sample(empleados_ids, min(15, len(empleados_ids)))
        vacaciones_creadas = 0
        
        estados = ['pendiente', 'aprobada_jefe', 'aprobada_rrhh', 'rechazada']
        pesos_estados = [0.3, 0.2, 0.4, 0.1]  # Mayoría aprobadas
        
        for emp_id in empleados_sample:
            # Vacaciones futuras
            dias_adelante = random.randint(15, 90)
            dias_duracion = random.randint(5, 15)
            
            fecha_inicio = (hoy + timedelta(days=dias_adelante)).strftime('%Y-%m-%d')
            fecha_fin = (hoy + timedelta(days=dias_adelante + dias_duracion)).strftime('%Y-%m-%d')
            
            estado = random.choices(estados, weights=pesos_estados)[0]
            tipo = random.choice(['vacaciones', 'permiso'])
            
            cursor.execute("""
                INSERT INTO Vacaciones_Permisos 
                (id_empleado, tipo, fecha_inicio, fecha_fin,
                 estado, observaciones, fecha_solicitud)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (emp_id, tipo, fecha_inicio, fecha_fin,
                  estado, 'Vacaciones anuales programadas',
                  (hoy - timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d')))
            
            vacaciones_creadas += 1
        
        conn.commit()
        print(f"[OK] {vacaciones_creadas} solicitudes creadas")
        
        # ==================================================================
        # 9. EVALUACIONES DE DESEMPEÑO
        # ==================================================================
        print("\n[9/11] Creando evaluaciones de desempeno...")
        
        empleados_eval = random.sample(empleados_ids, min(20, len(empleados_ids)))
        evaluaciones_creadas = 0
        
        evaluadores = [
            'Juan Carlos Rodríguez', 'María Fernanda García',
            'Pedro Antonio González', 'Patricia Elena Flores'
        ]
        
        for emp_id in empleados_eval:
            fecha = (hoy - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
            puntaje = random.randint(75, 100)  # Evaluaciones positivas
            evaluador = random.choice(evaluadores)
            
            observaciones = [
                'Excelente desempeño en el trimestre',
                'Cumple con los objetivos establecidos',
                'Muestra iniciativa y compromiso',
                'Buen trabajo en equipo',
                'Liderazgo efectivo en proyectos'
            ]
            
            cursor.execute("""
                INSERT INTO Evaluaciones 
                (id_empleado, fecha, evaluador, puntaje, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (emp_id, fecha, evaluador, puntaje, random.choice(observaciones)))
            
            evaluaciones_creadas += 1
        
        conn.commit()
        print(f"[OK] {evaluaciones_creadas} evaluaciones creadas")
        
        # ==================================================================
        # 10. CAPACITACIONES
        # ==================================================================
        print("\n[10/11] Registrando capacitaciones...")
        
        cursos = [
            ('Liderazgo y Gestión de Equipos', 'Instituto Hondureño de Liderazgo'),
            ('Excel Avanzado para Negocios', 'CEUTEC'),
            ('Programación en Python', 'UNITEC'),
            ('Gestión de Proyectos Ágiles', 'PMI Honduras'),
            ('Inglés Empresarial Nivel Intermedio', 'CATRACHO English Academy'),
            ('Marketing Digital', 'Google Digital Garage'),
            ('Servicio al Cliente de Excelencia', 'COHEP'),
            ('Finanzas para no Financieros', 'INCAE'),
        ]
        
        empleados_cap = random.sample(empleados_ids, min(25, len(empleados_ids)))
        capacitaciones_creadas = 0
        
        for emp_id in empleados_cap:
            curso, institucion = random.choice(cursos)
            dias_inicio = random.randint(60, 180)
            duracion = random.randint(30, 90)
            
            fecha_inicio = (hoy - timedelta(days=dias_inicio)).strftime('%Y-%m-%d')
            fecha_fin = (hoy - timedelta(days=dias_inicio - duracion)).strftime('%Y-%m-%d')
            certificado = random.random() < 0.8  # 80% obtienen certificado
            
            cursor.execute("""
                INSERT INTO Capacitaciones 
                (id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, curso, institucion, fecha_inicio, fecha_fin, 1 if certificado else 0))
            
            capacitaciones_creadas += 1
        
        conn.commit()
        print(f"[OK] {capacitaciones_creadas} capacitaciones registradas")
        
        # ==================================================================
        # 11. NOTIFICACIONES
        # ==================================================================
        print("\n[11/11] Creando notificaciones del sistema...")
        
        if usuario_ids:
            tipos_notif = ['info', 'success', 'warning', 'approval', 'reminder', 'request']
            
            notificaciones = [
                ('info', 'Nuevo empleado incorporado', 'Se ha registrado un nuevo empleado en el sistema'),
                ('approval', 'Solicitud de vacaciones pendiente', 'Hay solicitudes de vacaciones esperando aprobación'),
                ('success', 'Nómina procesada exitosamente', 'La nómina del mes ha sido procesada'),
                ('info', 'Evaluación de desempeño completada', 'Se ha registrado una nueva evaluación'),
                ('reminder', 'Recordatorio de asistencia', 'No olvides registrar tu entrada y salida'),
                ('warning', 'Contrato próximo a vencer', 'Hay contratos que vencen en los próximos 30 días'),
                ('success', 'Capacitación completada', 'Empleado ha finalizado capacitación'),
                ('request', 'Nueva solicitud de permiso', 'Se ha recibido una solicitud de permiso'),
            ]
            
            notif_creadas = 0
            
            for i in range(40):
                usuario_id = random.choice(usuario_ids)
                tipo, titulo, mensaje = random.choice(notificaciones)
                dias_atras = random.randint(0, 15)
                is_read = 1 if dias_atras > 7 else random.choice([0, 1])
                
                cursor.execute("""
                    INSERT INTO Notificaciones 
                    (usuario_id, tipo, titulo, mensaje, modulo, is_read, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (usuario_id, tipo, titulo, mensaje, 'system', is_read,
                      (hoy - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')))
                
                notif_creadas += 1
            
            conn.commit()
            print(f"[OK] {notif_creadas} notificaciones creadas")
        
        # ==================================================================
        # RESUMEN FINAL
        # ==================================================================
        print("\n" + "="*80)
        print("[OK] BASE DE DATOS POBLADA EXITOSAMENTE CON DATOS EMPRESARIALES")
        print("="*80)
        
        # Mostrar conteo
        tablas = [
            'departamentos', 'Puestos', 'empleados', 'usuarios', 'Contratos',
            'asistencias', 'Nomina', 'Vacaciones_Permisos', 'Evaluaciones',
            'Capacitaciones', 'Notificaciones'
        ]
        
        print("\nRESUMEN DE DATOS:")
        print("-" * 50)
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   {tabla:25} {count:5} registros")
            except Exception as e:
                print(f"   {tabla:25} ERROR: {str(e)}")
        
        print("\n" + "="*80)
        print("SISTEMA LISTO PARA PRODUCCION")
        print("="*80)
        print("\nCREDENCIALES DE ACCESO:")
        print("-" * 50)
        print("   Admin:      admin@empresa.hn / Admin123!")
        print("   RRHH:       rrhh@empresa.hn / RRHH123!")
        print("   Supervisor: supervisor@empresa.hn / Super123!")
        print("="*80)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    poblar_datos_empresariales()

