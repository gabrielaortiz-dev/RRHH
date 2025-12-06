"""
Script para reducir empleados a 40 y poblar todas las listas faltantes:
- Evaluaciones (40, una por empleado)
- Capacitaciones (varias por empleado)
- Vacaciones (varias por empleado)
- Nóminas (varias por empleado)
"""
import sqlite3
import os
from datetime import datetime, date, timedelta
import random
import bcrypt

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def reducir_empleados_a_40():
    """Reduce los empleados a 40 y elimina datos relacionados"""
    print("=" * 70)
    print("REDUCIENDO EMPLEADOS A 40 Y LIMPIANDO DATOS RELACIONADOS")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    # Desactivar foreign keys para evitar conflictos de nombres de tablas
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Detectar qué tabla de empleados existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
        tabla_empleados = cursor.fetchone()
        
        if not tabla_empleados:
            print("[ERROR] No se encontró tabla de empleados")
            return []
        
        nombre_tabla = tabla_empleados[0]
        print(f"[INFO] Usando tabla: {nombre_tabla}")
        
        # Detectar el nombre de la columna ID
        cursor.execute(f"PRAGMA table_info({nombre_tabla})")
        columnas = cursor.fetchall()
        id_column = None
        for col in columnas:
            if col[1] in ['id_empleado', 'id']:
                id_column = col[1]
                break
        
        if not id_column:
            print("[ERROR] No se encontró columna ID en la tabla de empleados")
            return []
        
        print(f"[INFO] Usando columna ID: {id_column}")
        
        # Obtener todos los empleados
        cursor.execute(f"SELECT {id_column} FROM {nombre_tabla} ORDER BY {id_column}")
        todos_empleados = cursor.fetchall()
        
        if len(todos_empleados) <= 40:
            print(f"[INFO] Ya hay {len(todos_empleados)} empleados o menos. No se necesita reducir.")
            empleados_a_mantener = [emp[0] for emp in todos_empleados]
        else:
            # Mantener los primeros 40
            empleados_a_mantener = [emp[0] for emp in todos_empleados[:40]]
            empleados_a_eliminar = [emp[0] for emp in todos_empleados[40:]]
            
            print(f"[INFO] Empleados totales: {len(todos_empleados)}")
            print(f"[INFO] Empleados a mantener: {len(empleados_a_mantener)}")
            print(f"[INFO] Empleados a eliminar: {len(empleados_a_eliminar)}")
            
            # Eliminar datos relacionados primero
            print("\n[INFO] Eliminando datos relacionados...")
            
            # Determinar nombre de columna de empleado en tablas relacionadas
            empleado_col = 'id_empleado' if id_column == 'id_empleado' else 'empleado_id'
            placeholders = ','.join(['?'] * len(empleados_a_eliminar))
            
            # Eliminar contratos
            try:
                cursor.execute(f"DELETE FROM Contratos WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                contratos_eliminados = cursor.rowcount
                print(f"[OK] {contratos_eliminados} contratos eliminados")
            except sqlite3.OperationalError:
                print("[INFO] Tabla Contratos no existe o tiene otro nombre")
            
            # Eliminar asistencias
            try:
                cursor.execute(f"DELETE FROM Asistencias WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                asistencias_eliminadas = cursor.rowcount
                print(f"[OK] {asistencias_eliminadas} asistencias eliminadas")
            except sqlite3.OperationalError:
                try:
                    cursor.execute(f"DELETE FROM asistencias WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                    asistencias_eliminadas = cursor.rowcount
                    print(f"[OK] {asistencias_eliminadas} asistencias eliminadas")
                except sqlite3.OperationalError:
                    print("[INFO] Tabla Asistencias no existe")
            
            # Eliminar capacitaciones
            try:
                cursor.execute(f"DELETE FROM Capacitaciones WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                capacitaciones_eliminadas = cursor.rowcount
                print(f"[OK] {capacitaciones_eliminadas} capacitaciones eliminadas")
            except sqlite3.OperationalError:
                print("[INFO] Tabla Capacitaciones no existe")
            
            # Eliminar evaluaciones
            try:
                cursor.execute(f"DELETE FROM Evaluaciones WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                evaluaciones_eliminadas = cursor.rowcount
                print(f"[OK] {evaluaciones_eliminadas} evaluaciones eliminadas")
            except sqlite3.OperationalError:
                print("[INFO] Tabla Evaluaciones no existe")
            
            # Eliminar vacaciones/permisos
            try:
                cursor.execute(f"DELETE FROM Vacaciones_Permisos WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                vacaciones_eliminadas = cursor.rowcount
                print(f"[OK] {vacaciones_eliminadas} vacaciones/permisos eliminados")
            except sqlite3.OperationalError:
                print("[INFO] Tabla Vacaciones_Permisos no existe o tiene otro nombre")
            
            # Eliminar nóminas
            try:
                cursor.execute(f"DELETE FROM Nomina WHERE {empleado_col} IN ({placeholders})", empleados_a_eliminar)
                nominas_eliminadas = cursor.rowcount
                print(f"[OK] {nominas_eliminadas} nóminas eliminadas")
            except sqlite3.OperationalError:
                print("[INFO] Tabla Nomina no existe o tiene otro nombre")
            
            # Eliminar documentos (puede referenciar a Empleados con mayúsculas)
            # Primero verificar si existe la tabla Documentos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Documentos'")
            if cursor.fetchone():
                try:
                    # Intentar eliminar con diferentes nombres de columna
                    for col_name in [empleado_col, 'id_empleado', 'empleado_id', 'id']:
                        try:
                            cursor.execute(f"DELETE FROM Documentos WHERE {col_name} IN ({placeholders})", empleados_a_eliminar)
                            documentos_eliminados = cursor.rowcount
                            if documentos_eliminados > 0:
                                print(f"[OK] {documentos_eliminados} documentos eliminados")
                                break
                        except sqlite3.OperationalError:
                            continue
                except Exception as e:
                    print(f"[INFO] Error al eliminar documentos: {e}")
            else:
                print("[INFO] Tabla Documentos no existe")
            
            # Eliminar usuarios relacionados (si tienen relación con empleados)
            try:
                # Obtener correos de empleados a eliminar
                correo_col = 'correo' if id_column == 'id_empleado' else 'email'
                cursor.execute(f"SELECT {correo_col} FROM {nombre_tabla} WHERE {id_column} IN ({placeholders})", empleados_a_eliminar)
                correos = [row[0] for row in cursor.fetchall() if row[0]]
                
                if correos:
                    correos_placeholders = ','.join(['?'] * len(correos))
                    cursor.execute(f"""
                        SELECT DISTINCT u.id_usuario 
                        FROM usuarios u
                        WHERE u.email IN ({correos_placeholders})
                    """, correos)
                    usuarios_a_eliminar = [row[0] for row in cursor.fetchall()]
                    
                    if usuarios_a_eliminar:
                        usuarios_placeholders = ','.join(['?'] * len(usuarios_a_eliminar))
                        # Eliminar notificaciones de usuarios
                        try:
                            cursor.execute(f"DELETE FROM Notificaciones WHERE usuario_id IN ({usuarios_placeholders})", usuarios_a_eliminar)
                        except:
                            pass
                        # Eliminar usuarios
                        cursor.execute(f"DELETE FROM usuarios WHERE id_usuario IN ({usuarios_placeholders})", usuarios_a_eliminar)
                        print(f"[OK] {len(usuarios_a_eliminar)} usuarios eliminados")
            except sqlite3.OperationalError as e:
                print(f"[INFO] No se pudieron eliminar usuarios relacionados: {e}")
            
            # Finalmente, eliminar los empleados
            cursor.execute(f"DELETE FROM {nombre_tabla} WHERE {id_column} IN ({placeholders})", empleados_a_eliminar)
            empleados_eliminados = cursor.rowcount
            print(f"[OK] {empleados_eliminados} empleados eliminados")
        
        conn.commit()
        # Reactivar foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        print(f"\n[OK] Proceso completado. Empleados restantes: {len(empleados_a_mantener)}")
        return empleados_a_mantener
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al reducir empleados: {e}")
        raise
    finally:
        # Asegurar que foreign keys se reactiven
        try:
            conn.execute("PRAGMA foreign_keys = ON")
        except:
            pass
        conn.close()

def crear_evaluaciones(empleados_ids):
    """Crea una evaluación por cada empleado"""
    print("\n" + "=" * 70)
    print("CREANDO EVALUACIONES (UNA POR EMPLEADO)")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    # Desactivar foreign keys para evitar conflictos de nombres de tablas
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Evaluaciones'")
        if not cursor.fetchone():
            print("[ERROR] La tabla Evaluaciones no existe. Creándola...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Evaluaciones (
                    id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    fecha DATE,
                    evaluador VARCHAR(100),
                    puntaje INTEGER,
                    observaciones TEXT,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
                )
            """)
            conn.commit()
        
        # Limpiar evaluaciones existentes
        cursor.execute("DELETE FROM Evaluaciones")
        print(f"[INFO] Evaluaciones existentes eliminadas")
        
        evaluadores = [
            "María González", "Carlos Rodríguez", "Ana Martínez", 
            "Luis Pérez", "Sofía López", "Pedro Sánchez", "Laura Fernández"
        ]
        
        observaciones_templates = [
            "Excelente desempeño en todas las áreas evaluadas",
            "Buen desempeño general con áreas de mejora en comunicación",
            "Desempeño satisfactorio, cumpliendo con las expectativas",
            "Destacado en trabajo en equipo y colaboración",
            "Alto rendimiento en proyectos asignados",
            "Cumplimiento adecuado de objetivos, con potencial de crecimiento",
            "Buen desempeño técnico, necesita mejorar habilidades blandas"
        ]
        
        evaluaciones_creadas = 0
        fecha_base = date.today() - timedelta(days=30)
        
        for emp_id in empleados_ids:
            # Fecha aleatoria en los últimos 30 días
            dias_aleatorios = random.randint(0, 30)
            fecha_evaluacion = fecha_base + timedelta(days=dias_aleatorios)
            
            evaluador = random.choice(evaluadores)
            puntaje = random.randint(70, 95)  # Puntajes entre 70 y 95
            observaciones = random.choice(observaciones_templates)
            
            cursor.execute("""
                INSERT INTO Evaluaciones (id_empleado, fecha, evaluador, puntaje, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (emp_id, fecha_evaluacion.isoformat(), evaluador, puntaje, observaciones))
            
            evaluaciones_creadas += 1
        
        conn.commit()
        print(f"[OK] {evaluaciones_creadas} evaluaciones creadas")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear evaluaciones: {e}")
        raise
    finally:
        conn.close()

def crear_capacitaciones(empleados_ids):
    """Crea capacitaciones para los empleados"""
    print("\n" + "=" * 70)
    print("CREANDO CAPACITACIONES")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    # Desactivar foreign keys para evitar conflictos de nombres de tablas
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Capacitaciones'")
        if not cursor.fetchone():
            print("[ERROR] La tabla Capacitaciones no existe. Creándola...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Capacitaciones (
                    id_capacitacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    nombre_curso VARCHAR(100),
                    institucion VARCHAR(100),
                    fecha_inicio DATE,
                    fecha_fin DATE,
                    certificado BOOLEAN,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
                )
            """)
            conn.commit()
        
        # Limpiar capacitaciones existentes
        cursor.execute("DELETE FROM Capacitaciones")
        print(f"[INFO] Capacitaciones existentes eliminadas")
        
        cursos = [
            ("Liderazgo y Gestión de Equipos", "Instituto de Desarrollo Profesional"),
            ("Comunicación Efectiva", "Centro de Capacitación Empresarial"),
            ("Gestión del Tiempo", "Academia de Habilidades"),
            ("Excel Avanzado", "Instituto Tecnológico"),
            ("Python para Principiantes", "Plataforma Online"),
            ("Scrum y Metodologías Ágiles", "Instituto de Proyectos"),
            ("Atención al Cliente", "Centro de Servicio"),
            ("Marketing Digital", "Academia Digital"),
            ("Finanzas Personales", "Instituto Financiero"),
            ("Seguridad Informática", "Centro de Ciberseguridad"),
            ("Diseño Gráfico", "Escuela de Diseño"),
            ("Inglés Empresarial", "Instituto de Idiomas"),
            ("Ventas y Negociación", "Academia Comercial"),
            ("Recursos Humanos", "Instituto de RRHH"),
            ("Análisis de Datos", "Centro de Analytics")
        ]
        
        instituciones = [
            "Instituto de Desarrollo Profesional",
            "Centro de Capacitación Empresarial",
            "Academia de Habilidades",
            "Instituto Tecnológico",
            "Plataforma Online",
            "Instituto de Proyectos",
            "Centro de Servicio",
            "Academia Digital"
        ]
        
        capacitaciones_creadas = 0
        
        for emp_id in empleados_ids:
            # Cada empleado tiene entre 1 y 3 capacitaciones
            num_capacitaciones = random.randint(1, 3)
            
            for _ in range(num_capacitaciones):
                curso_nombre, institucion = random.choice(cursos)
                
                # Fecha de inicio aleatoria en los últimos 6 meses
                dias_aleatorios = random.randint(0, 180)
                fecha_inicio = date.today() - timedelta(days=dias_aleatorios)
                
                # Duración entre 1 semana y 3 meses
                duracion_dias = random.randint(7, 90)
                fecha_fin = fecha_inicio + timedelta(days=duracion_dias)
                
                # 70% de probabilidad de tener certificado
                certificado = random.random() < 0.7
                
                cursor.execute("""
                    INSERT INTO Capacitaciones (id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (emp_id, curso_nombre, institucion, fecha_inicio.isoformat(), fecha_fin.isoformat(), 1 if certificado else 0))
                
                capacitaciones_creadas += 1
        
        conn.commit()
        print(f"[OK] {capacitaciones_creadas} capacitaciones creadas")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear capacitaciones: {e}")
        raise
    finally:
        conn.close()

def crear_vacaciones(empleados_ids):
    """Crea vacaciones/permisos para los empleados"""
    print("\n" + "=" * 70)
    print("CREANDO VACACIONES Y PERMISOS")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    # Desactivar foreign keys para evitar conflictos de nombres de tablas
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla existe (puede tener diferentes nombres)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Vacaciones_Permisos' OR name='vacaciones' OR name='Vacaciones')")
        tabla_vacaciones = cursor.fetchone()
        
        if not tabla_vacaciones:
            print("[INFO] La tabla de vacaciones no existe. Creándola...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Vacaciones_Permisos (
                    id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    tipo VARCHAR(50),
                    fecha_solicitud DATE,
                    fecha_inicio DATE,
                    fecha_fin DATE,
                    dias_solicitados INTEGER,
                    motivo TEXT,
                    estado VARCHAR(50),
                    aprobado_por_jefe INTEGER,
                    aprobado_por_rrhh INTEGER,
                    fecha_aprobacion_jefe DATE,
                    fecha_aprobacion_rrhh DATE,
                    motivo_rechazo TEXT,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
                )
            """)
            conn.commit()
            nombre_tabla = "Vacaciones_Permisos"
        else:
            nombre_tabla = tabla_vacaciones[0]
        
        # Limpiar vacaciones existentes
        cursor.execute(f"DELETE FROM {nombre_tabla}")
        print(f"[INFO] Vacaciones/permisos existentes eliminados")
        
        tipos = ["vacaciones", "permiso_personal", "permiso_medico", "permiso_familiar"]
        estados = ["aprobado", "pendiente", "rechazado"]
        
        vacaciones_creadas = 0
        
        for emp_id in empleados_ids:
            # Cada empleado tiene entre 1 y 2 solicitudes de vacaciones/permisos
            num_solicitudes = random.randint(1, 2)
            
            for _ in range(num_solicitudes):
                tipo = random.choice(tipos)
                estado = random.choice(estados)
                
                # Fecha de solicitud en los últimos 3 meses
                dias_aleatorios = random.randint(0, 90)
                fecha_solicitud = date.today() - timedelta(days=dias_aleatorios)
                
                # Fecha de inicio futura o pasada
                dias_futuro = random.randint(-30, 60)
                fecha_inicio = date.today() + timedelta(days=dias_futuro)
                
                # Duración entre 1 y 10 días
                dias_solicitados = random.randint(1, 10)
                fecha_fin = fecha_inicio + timedelta(days=dias_solicitados - 1)
                
                motivos = [
                    "Vacaciones planificadas",
                    "Asuntos personales",
                    "Consulta médica",
                    "Emergencia familiar",
                    "Descanso y recreación",
                    "Trámites personales",
                    "Evento familiar"
                ]
                motivo = random.choice(motivos)
                
                # Si está aprobado, agregar fechas de aprobación
                aprobado_por_jefe = None
                aprobado_por_rrhh = None
                fecha_aprobacion_jefe = None
                fecha_aprobacion_rrhh = None
                motivo_rechazo = None
                
                if estado == "aprobado":
                    aprobado_por_jefe = random.randint(1, 5)
                    aprobado_por_rrhh = random.randint(1, 3)
                    fecha_aprobacion_jefe = fecha_solicitud + timedelta(days=random.randint(1, 3))
                    fecha_aprobacion_rrhh = fecha_aprobacion_jefe + timedelta(days=random.randint(1, 2))
                elif estado == "rechazo":
                    motivo_rechazo = "No hay disponibilidad en el período solicitado"
                
                # Verificar qué columnas tiene la tabla
                cursor.execute(f"PRAGMA table_info({nombre_tabla})")
                columnas_tabla = [col[1] for col in cursor.fetchall()]
                
                # Construir INSERT dinámico según las columnas disponibles
                columnas_disponibles = []
                valores = []
                
                if 'id_empleado' in columnas_tabla:
                    columnas_disponibles.append('id_empleado')
                    valores.append(emp_id)
                if 'tipo' in columnas_tabla:
                    columnas_disponibles.append('tipo')
                    valores.append(tipo)
                if 'fecha_solicitud' in columnas_tabla:
                    columnas_disponibles.append('fecha_solicitud')
                    valores.append(fecha_solicitud.isoformat())
                if 'fecha_inicio' in columnas_tabla:
                    columnas_disponibles.append('fecha_inicio')
                    valores.append(fecha_inicio.isoformat())
                if 'fecha_fin' in columnas_tabla:
                    columnas_disponibles.append('fecha_fin')
                    valores.append(fecha_fin.isoformat())
                if 'dias_solicitados' in columnas_tabla:
                    columnas_disponibles.append('dias_solicitados')
                    valores.append(dias_solicitados)
                if 'motivo' in columnas_tabla:
                    columnas_disponibles.append('motivo')
                    valores.append(motivo)
                if 'observaciones' in columnas_tabla:
                    columnas_disponibles.append('observaciones')
                    valores.append(motivo)  # Usar motivo como observaciones
                if 'estado' in columnas_tabla:
                    columnas_disponibles.append('estado')
                    valores.append(estado)
                if 'aprobado_por_jefe' in columnas_tabla:
                    columnas_disponibles.append('aprobado_por_jefe')
                    valores.append(aprobado_por_jefe)
                if 'aprobado_por_rrhh' in columnas_tabla:
                    columnas_disponibles.append('aprobado_por_rrhh')
                    valores.append(aprobado_por_rrhh)
                if 'fecha_aprobacion_jefe' in columnas_tabla:
                    columnas_disponibles.append('fecha_aprobacion_jefe')
                    valores.append(fecha_aprobacion_jefe.isoformat() if fecha_aprobacion_jefe else None)
                if 'fecha_aprobacion_rrhh' in columnas_tabla:
                    columnas_disponibles.append('fecha_aprobacion_rrhh')
                    valores.append(fecha_aprobacion_rrhh.isoformat() if fecha_aprobacion_rrhh else None)
                if 'motivo_rechazo' in columnas_tabla:
                    columnas_disponibles.append('motivo_rechazo')
                    valores.append(motivo_rechazo)
                
                placeholders = ','.join(['?'] * len(valores))
                columnas_str = ','.join(columnas_disponibles)
                
                cursor.execute(f"""
                    INSERT INTO {nombre_tabla} ({columnas_str})
                    VALUES ({placeholders})
                """, tuple(valores))
                
                vacaciones_creadas += 1
        
        conn.commit()
        print(f"[OK] {vacaciones_creadas} vacaciones/permisos creados")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear vacaciones: {e}")
        raise
    finally:
        conn.close()

def crear_nominas(empleados_ids):
    """Crea nóminas para los empleados"""
    print("\n" + "=" * 70)
    print("CREANDO NÓMINAS")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    # Desactivar foreign keys para evitar conflictos de nombres de tablas
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Nomina' OR name='nomina')")
        tabla_nomina = cursor.fetchone()
        
        if not tabla_nomina:
            print("[INFO] La tabla Nomina no existe. Creándola...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Nomina (
                    id_nomina INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    mes INTEGER,
                    anio INTEGER,
                    salario_base DECIMAL(10,2),
                    bonificaciones DECIMAL(10,2),
                    deducciones DECIMAL(10,2),
                    salario_neto DECIMAL(10,2),
                    fecha_pago DATE,
                    estado VARCHAR(50),
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
                )
            """)
            conn.commit()
            nombre_tabla = "Nomina"
        else:
            nombre_tabla = tabla_nomina[0]
        
        # Limpiar nóminas existentes
        cursor.execute(f"DELETE FROM {nombre_tabla}")
        print(f"[INFO] Nóminas existentes eliminadas")
        
        # Detectar tabla de empleados y columna ID
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
        tabla_emp = cursor.fetchone()
        if tabla_emp:
            nombre_tabla_emp = tabla_emp[0]
            cursor.execute(f"PRAGMA table_info({nombre_tabla_emp})")
            columnas_emp = cursor.fetchall()
            id_col_emp = None
            salario_col = None
            for col in columnas_emp:
                if col[1] in ['id_empleado', 'id']:
                    id_col_emp = col[1]
                if col[1] in ['salario', 'salario_base']:
                    salario_col = col[1]
            
            if not id_col_emp:
                id_col_emp = 'id'
            if not salario_col:
                salario_col = 'salario'
            
            # Obtener salarios de los empleados
            placeholders_emp = ','.join(['?'] * len(empleados_ids))
            cursor.execute(f"SELECT {id_col_emp}, {salario_col} FROM {nombre_tabla_emp} WHERE {id_col_emp} IN ({placeholders_emp})", empleados_ids)
            salarios_empleados = {row[0]: row[1] or 30000.0 for row in cursor.fetchall()}
        else:
            # Si no se encuentra la tabla, usar valores por defecto
            salarios_empleados = {emp_id: 30000.0 for emp_id in empleados_ids}
        
        nominas_creadas = 0
        anio_actual = date.today().year
        mes_actual = date.today().month
        
        for emp_id in empleados_ids:
            salario_base = salarios_empleados.get(emp_id, 30000.0)
            
            # Crear nóminas para los últimos 3 meses
            for i in range(3):
                mes = mes_actual - i
                anio = anio_actual
                
                if mes <= 0:
                    mes += 12
                    anio -= 1
                
                # Bonificaciones aleatorias (0-10% del salario)
                bonificaciones = round(salario_base * random.uniform(0, 0.10), 2)
                
                # Deducciones (IHSS, RAP, ISR aproximado - 5-15% del salario)
                deducciones = round(salario_base * random.uniform(0.05, 0.15), 2)
                
                # Salario neto
                salario_neto = round(salario_base + bonificaciones - deducciones, 2)
                
                # Fecha de pago (último día del mes o primeros días del siguiente)
                if mes == mes_actual:
                    fecha_pago = date.today() - timedelta(days=random.randint(0, 5))
                else:
                    # Último día del mes
                    if mes == 12:
                        ultimo_dia = date(anio, 12, 31)
                    else:
                        ultimo_dia = date(anio, mes + 1, 1) - timedelta(days=1)
                    fecha_pago = ultimo_dia + timedelta(days=random.randint(0, 3))
                
                estado = "pagado" if fecha_pago < date.today() else "pendiente"
                
                # Verificar qué columnas tiene la tabla
                cursor.execute(f"PRAGMA table_info({nombre_tabla})")
                columnas_tabla = [col[1] for col in cursor.fetchall()]
                
                # Construir INSERT dinámico según las columnas disponibles
                columnas_disponibles = []
                valores = []
                
                empleado_col_nomina = 'id_empleado' if 'id_empleado' in columnas_tabla else 'empleado_id'
                
                if empleado_col_nomina in columnas_tabla:
                    columnas_disponibles.append(empleado_col_nomina)
                    valores.append(emp_id)
                if 'mes' in columnas_tabla:
                    columnas_disponibles.append('mes')
                    valores.append(mes)
                if 'anio' in columnas_tabla:
                    columnas_disponibles.append('anio')
                    valores.append(anio)
                if 'salario_base' in columnas_tabla:
                    columnas_disponibles.append('salario_base')
                    valores.append(salario_base)
                if 'bonificaciones' in columnas_tabla:
                    columnas_disponibles.append('bonificaciones')
                    valores.append(bonificaciones)
                if 'deducciones' in columnas_tabla:
                    columnas_disponibles.append('deducciones')
                    valores.append(deducciones)
                if 'salario_neto' in columnas_tabla:
                    columnas_disponibles.append('salario_neto')
                    valores.append(salario_neto)
                if 'fecha_pago' in columnas_tabla:
                    columnas_disponibles.append('fecha_pago')
                    valores.append(fecha_pago.isoformat())
                if 'estado' in columnas_tabla:
                    columnas_disponibles.append('estado')
                    valores.append(estado)
                
                placeholders_nomina = ','.join(['?'] * len(valores))
                columnas_str_nomina = ','.join(columnas_disponibles)
                
                cursor.execute(f"""
                    INSERT INTO {nombre_tabla} ({columnas_str_nomina})
                    VALUES ({placeholders_nomina})
                """, tuple(valores))
                
                nominas_creadas += 1
        
        conn.commit()
        print(f"[OK] {nominas_creadas} nóminas creadas")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al crear nóminas: {e}")
        raise
    finally:
        conn.close()

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("SCRIPT DE REDUCCIÓN Y POBLADO DE DATOS")
    print("=" * 70)
    print()
    
    try:
        # 1. Reducir empleados a 40
        empleados_ids = reducir_empleados_a_40()
        
        if not empleados_ids:
            print("[ERROR] No hay empleados disponibles")
            return
        
        # 2. Crear evaluaciones
        crear_evaluaciones(empleados_ids)
        
        # 3. Crear capacitaciones
        crear_capacitaciones(empleados_ids)
        
        # 4. Crear vacaciones
        crear_vacaciones(empleados_ids)
        
        # 5. Crear nóminas
        crear_nominas(empleados_ids)
        
        print("\n" + "=" * 70)
        print("[OK] PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print(f"\nResumen:")
        print(f"  - Empleados: {len(empleados_ids)}")
        print(f"  - Evaluaciones: {len(empleados_ids)} (una por empleado)")
        print(f"  - Capacitaciones: Varias por empleado")
        print(f"  - Vacaciones/Permisos: Varias por empleado")
        print(f"  - Nóminas: 3 meses por empleado")
        print()
        
    except Exception as e:
        print(f"\n[ERROR] Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()

