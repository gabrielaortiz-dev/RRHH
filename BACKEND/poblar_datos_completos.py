"""
Script para poblar la base de datos con datos de prueba completos
Crea datos realistas en todos los módulos del sistema
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

def poblar_base_datos():
    print("="*70)
    print("🚀 POBLANDO BASE DE DATOS CON DATOS COMPLETOS")
    print("="*70)
    
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # ==================================================================
        # 1. DEPARTAMENTOS (10)
        # ==================================================================
        print("\n📁 Creando departamentos...")
        
        departamentos = [
            ('Tecnología', 'Desarrollo de software y sistemas'),
            ('Recursos Humanos', 'Gestión del talento humano'),
            ('Finanzas', 'Contabilidad y gestión financiera'),
            ('Marketing', 'Publicidad y comunicación'),
            ('Ventas', 'Gestión comercial y ventas'),
            ('Operaciones', 'Gestión operativa'),
            ('Atención al Cliente', 'Servicio y soporte al cliente'),
            ('Logística', 'Distribución y cadena de suministro'),
            ('Legal', 'Asesoría jurídica'),
            ('Administración', 'Gestión administrativa')
        ]
        
        for nombre, desc in departamentos:
            cursor.execute("""
                INSERT OR IGNORE INTO departamentos (nombre, descripcion, activo)
                VALUES (?, ?, 1)
            """, (nombre, desc))
        
        conn.commit()
        print(f"✅ {len(departamentos)} departamentos creados")
        
        # ==================================================================
        # 2. PUESTOS (20)
        # ==================================================================
        print("\n💼 Creando puestos...")
        
        puestos = [
            ('Desarrollador Senior', 'Senior', 55000),
            ('Desarrollador Junior', 'Junior', 30000),
            ('Analista de RRHH', 'Mid', 38000),
            ('Gerente de RRHH', 'Senior', 60000),
            ('Contador', 'Mid', 42000),
            ('Analista Financiero', 'Junior', 35000),
            ('Especialista en Marketing', 'Mid', 40000),
            ('Community Manager', 'Junior', 28000),
            ('Ejecutivo de Ventas', 'Mid', 35000),
            ('Gerente de Ventas', 'Senior', 65000),
            ('Coordinador de Operaciones', 'Mid', 38000),
            ('Representante de Servicio', 'Junior', 25000),
            ('Supervisor de Atención', 'Mid', 35000),
            ('Coordinador Logístico', 'Mid', 36000),
            ('Asistente Legal', 'Junior', 32000),
            ('Abogado Corporativo', 'Senior', 70000),
            ('Asistente Administrativo', 'Junior', 24000),
            ('Gerente General', 'Executive', 90000),
            ('Director de Tecnología', 'Executive', 85000),
            ('Gerente de Proyectos', 'Senior', 58000)
        ]
        
        for nombre, nivel, salario in puestos:
            cursor.execute("""
                INSERT OR IGNORE INTO Puestos (nombre_puesto, nivel, salario_base)
                VALUES (?, ?, ?)
            """, (nombre, nivel, salario))
        
        conn.commit()
        print(f"✅ {len(puestos)} puestos creados")
        
        # ==================================================================
        # 3. EMPLEADOS (50)
        # ==================================================================
        print("\n👥 Creando empleados...")
        
        nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura', 
                   'José', 'Patricia', 'Miguel', 'Isabel', 'Francisco', 'Rosa', 'Antonio',
                   'Mercedes', 'Manuel', 'Elena', 'Rafael', 'Cristina', 'Fernando', 'Beatriz',
                   'Jorge', 'Silvia', 'Roberto', 'Monica', 'Alberto', 'Teresa', 'Raul', 'Diana']
        
        apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 
                     'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez', 'Díaz',
                     'Cruz', 'Morales', 'Reyes', 'Jiménez', 'Hernández', 'Ruiz', 'Ortiz']
        
        # Obtener IDs de departamentos y puestos
        cursor.execute("SELECT id FROM departamentos")
        dept_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id_puesto FROM Puestos")
        puesto_ids = [row[0] for row in cursor.fetchall()]
        
        empleados_creados = 0
        for i in range(50):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            email = f"{nombre.lower()}.{apellido.lower()}{i}@empresa.com"
            telefono = f"+504 {random.randint(2000, 9999)}-{random.randint(1000, 9999)}"
            
            # Fecha de ingreso entre 1 y 5 años atrás
            dias_atras = random.randint(365, 1825)
            fecha_ingreso = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            # Salario entre 24000 y 90000
            salario = random.randint(24000, 90000)
            
            dept_id = random.choice(dept_ids)
            puesto_id = random.choice(puesto_ids)
            
            cursor.execute("""
                INSERT INTO empleados 
                (nombre, apellido, email, telefono, departamento_id, puesto, fecha_ingreso, salario, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (nombre, apellido, email, telefono, dept_id, puesto_id, fecha_ingreso, salario))
            
            empleados_creados += 1
        
        conn.commit()
        print(f"✅ {empleados_creados} empleados creados")
        
        # ==================================================================
        # 4. USUARIOS (5 + empleados como usuarios)
        # ==================================================================
        print("\n👤 Creando usuarios...")
        
        # Usuarios administrativos
        usuarios_admin = [
            ('Admin Sistema', 'admin@rrhh.com', 'admin123', 'admin'),
            ('RRHH Manager', 'rrhh@rrhh.com', 'rrhh123', 'rrhh'),
            ('Supervisor', 'supervisor@empresa.com', 'super123', 'supervisor'),
        ]
        
        for nombre, email, password, rol in usuarios_admin:
            hashed = hash_password(password)
            cursor.execute("""
                INSERT OR IGNORE INTO usuarios (nombre, email, password, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (nombre, email, hashed, rol))
        
        conn.commit()
        print(f"✅ {len(usuarios_admin)} usuarios administrativos creados")
        
        # ==================================================================
        # 5. CONTRATOS (30)
        # ==================================================================
        print("\n📄 Creando contratos...")
        
        cursor.execute("SELECT id FROM empleados LIMIT 30")
        empleados_para_contrato = [row[0] for row in cursor.fetchall()]
        
        tipos_contrato = ['tiempo_indefinido', 'tiempo_determinado', 'por_horas']
        contratos_creados = 0
        
        for emp_id in empleados_para_contrato:
            tipo = random.choice(tipos_contrato)
            fecha_inicio = (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d')
            
            # Fecha fin solo para contratos determinados
            fecha_fin = None
            if tipo == 'tiempo_determinado':
                fecha_fin = (datetime.now() + timedelta(days=random.randint(180, 720))).strftime('%Y-%m-%d')
            
            salario = random.randint(25000, 80000)
            
            cursor.execute("""
                INSERT INTO Contratos 
                (id_empleado, tipo_contrato, salario_base, fecha_inicio, fecha_fin, estado)
                VALUES (?, ?, ?, ?, ?, 'activo')
            """, (emp_id, tipo, salario, fecha_inicio, fecha_fin))
            
            contratos_creados += 1
        
        conn.commit()
        print(f"✅ {contratos_creados} contratos creados")
        
        # ==================================================================
        # 6. ASISTENCIAS (100 registros del último mes)
        # ==================================================================
        print("\n📅 Creando registros de asistencia...")
        
        cursor.execute("SELECT id FROM empleados LIMIT 20")
        empleados_asistencia = [row[0] for row in cursor.fetchall()]
        
        asistencias_creadas = 0
        for i in range(100):
            emp_id = random.choice(empleados_asistencia)
            dias_atras = random.randint(1, 30)
            fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            # Hora de entrada entre 7:30 y 9:00
            hora_entrada = f"{random.randint(7, 8)}:{random.randint(0, 59):02d}:00"
            
            # Hora de salida entre 16:00 y 18:00
            hora_salida = f"{random.randint(16, 17)}:{random.randint(0, 59):02d}:00"
            
            cursor.execute("""
                INSERT INTO asistencias 
                (empleado_id, fecha, hora_entrada, hora_salida, observaciones)
                VALUES (?, ?, ?, ?, 'Registro manual')
            """, (emp_id, fecha, hora_entrada, hora_salida))
            
            asistencias_creadas += 1
        
        conn.commit()
        print(f"✅ {asistencias_creadas} registros de asistencia creados")
        
        # ==================================================================
        # 7. NÓMINAS (20)
        # ==================================================================
        print("\n💰 Creando nóminas...")
        
        cursor.execute("SELECT id, salario FROM empleados LIMIT 20")
        empleados_nomina = cursor.fetchall()
        
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        
        nominas_creadas = 0
        for emp_id, salario in empleados_nomina:
            # Crear nómina del mes actual
            bonificaciones = salario * 0.10  # 10% de bonificación
            deducciones = salario * 0.15  # 15% de deducciones
            total = salario + bonificaciones - deducciones
            
            cursor.execute("""
                INSERT INTO Nomina 
                (id_empleado, mes, anio, salario_base, bonificaciones, deducciones, 
                 salario_neto, fecha_pago)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (emp_id, mes_actual, anio_actual, salario, bonificaciones, 
                  deducciones, total, datetime.now().strftime('%Y-%m-%d')))
            
            nominas_creadas += 1
        
        conn.commit()
        print(f"✅ {nominas_creadas} nóminas creadas")
        
        # ==================================================================
        # 8. VACACIONES (15)
        # ==================================================================
        print("\n🏖️ Creando solicitudes de vacaciones...")
        
        cursor.execute("SELECT id FROM empleados LIMIT 15")
        empleados_vacaciones = [row[0] for row in cursor.fetchall()]
        
        estados = ['pendiente', 'aprobada_jefe', 'aprobada_rrhh', 'rechazada']
        vacaciones_creadas = 0
        
        for emp_id in empleados_vacaciones:
            # Vacaciones en el futuro
            dias_adelante = random.randint(10, 90)
            fecha_inicio = (datetime.now() + timedelta(days=dias_adelante)).strftime('%Y-%m-%d')
            fecha_fin = (datetime.now() + timedelta(days=dias_adelante + random.randint(5, 14))).strftime('%Y-%m-%d')
            
            estado = random.choice(estados)
            
            cursor.execute("""
                INSERT INTO Vacaciones_Permisos 
                (id_empleado, tipo, fecha_inicio, fecha_fin, estado, observaciones)
                VALUES (?, 'vacaciones', ?, ?, ?, 'Vacaciones anuales')
            """, (emp_id, fecha_inicio, fecha_fin, estado))
            
            vacaciones_creadas += 1
        
        conn.commit()
        print(f"✅ {vacaciones_creadas} solicitudes de vacaciones creadas")
        
        # ==================================================================
        # 9. EVALUACIONES (10)
        # ==================================================================
        print("\n⭐ Creando evaluaciones de desempeño...")
        
        cursor.execute("SELECT id FROM empleados LIMIT 10")
        empleados_eval = [row[0] for row in cursor.fetchall()]
        
        evaluadores = ['Carlos Gómez', 'Ana Martínez', 'Luis Torres', 'María Flores']
        evaluaciones_creadas = 0
        
        for emp_id in empleados_eval:
            fecha = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
            puntaje = random.randint(70, 100)
            evaluador = random.choice(evaluadores)
            
            cursor.execute("""
                INSERT INTO Evaluaciones 
                (id_empleado, fecha, evaluador, puntaje, observaciones)
                VALUES (?, ?, ?, ?, 'Evaluación de desempeño trimestral')
            """, (emp_id, fecha, evaluador, puntaje))
            
            evaluaciones_creadas += 1
        
        conn.commit()
        print(f"✅ {evaluaciones_creadas} evaluaciones creadas")
        
        # ==================================================================
        # 10. CAPACITACIONES (10)
        # ==================================================================
        print("\n📚 Creando capacitaciones...")
        
        cursor.execute("SELECT id FROM empleados LIMIT 10")
        empleados_cap = [row[0] for row in cursor.fetchall()]
        
        cursos = [
            ('Liderazgo Efectivo', 'Instituto de Liderazgo'),
            ('Excel Avanzado', 'Platzi'),
            ('Programación en Python', 'Udemy'),
            ('Gestión de Proyectos', 'PMI'),
            ('Inglés Empresarial', 'English Academy'),
        ]
        
        capacitaciones_creadas = 0
        for emp_id in empleados_cap:
            curso, institucion = random.choice(cursos)
            fecha_inicio = (datetime.now() - timedelta(days=random.randint(60, 180))).strftime('%Y-%m-%d')
            fecha_fin = (datetime.now() - timedelta(days=random.randint(1, 59))).strftime('%Y-%m-%d')
            certificado = random.choice([True, False])
            
            cursor.execute("""
                INSERT INTO Capacitaciones 
                (id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, curso, institucion, fecha_inicio, fecha_fin, 1 if certificado else 0))
            
            capacitaciones_creadas += 1
        
        conn.commit()
        print(f"✅ {capacitaciones_creadas} capacitaciones creadas")
        
        # ==================================================================
        # 11. NOTIFICACIONES (50)
        # ==================================================================
        print("\n🔔 Creando notificaciones de ejemplo...")
        
        cursor.execute("SELECT id FROM usuarios LIMIT 5")
        usuarios = [row[0] for row in cursor.fetchall()]
        
        if usuarios:
            tipos = ['info', 'success', 'warning', 'approval', 'reminder']
            titulos = [
                'Nuevo empleado registrado',
                'Solicitud de vacaciones pendiente',
                'Nómina procesada',
                'Evaluación completada',
                'Contrato próximo a vencer',
                'Asistencia registrada',
                'Documento subido',
                'Capacitación programada',
            ]
            
            notif_creadas = 0
            for i in range(50):
                usuario_id = random.choice(usuarios)
                tipo = random.choice(tipos)
                titulo = random.choice(titulos)
                dias_atras = random.randint(1, 30)
                
                cursor.execute("""
                    INSERT INTO Notificaciones 
                    (usuario_id, tipo, titulo, mensaje, is_read, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (usuario_id, tipo, titulo, 
                      f"Esta es una notificación de ejemplo para {titulo}",
                      random.choice([0, 1]),
                      (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')))
                
                notif_creadas += 1
            
            conn.commit()
            print(f"✅ {notif_creadas} notificaciones creadas")
        
        # ==================================================================
        # RESUMEN
        # ==================================================================
        print("\n" + "="*70)
        print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print("="*70)
        
        # Mostrar conteo final
        tablas = [
            'departamentos', 'Puestos', 'empleados', 'usuarios', 'Contratos',
            'asistencias', 'Nomina', 'Vacaciones_Permisos', 'Evaluaciones',
            'Capacitaciones', 'Notificaciones'
        ]
        
        print("\n📊 RESUMEN:")
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   {tabla}: {count} registros")
            except:
                pass
        
        print("\n🎉 ¡Sistema listo para usar con datos realistas!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    poblar_base_datos()

