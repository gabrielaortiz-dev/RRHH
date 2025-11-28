"""
Script para insertar datos de ejemplo en la base de datos
"""
from database import get_db
from datetime import datetime, date
import bcrypt

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    # Asegurar que la contraseña no exceda 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def insert_sample_data():
    """Insertar datos de ejemplo en la base de datos"""
    print("=" * 60)
    print("INSERTANDO DATOS DE EJEMPLO")
    print("=" * 60)
    
    try:
        db = get_db()
        
        # Insertar usuarios de ejemplo
        print("\n[INFO] Insertando usuarios...")
        usuarios = [
            ('Admin Sistema', 'admin@rrhh.com', 'admin123', 'administrador'),
            ('Juan Perez', 'juan.perez@rrhh.com', 'pass123', 'empleado'),
            ('Maria Garcia', 'maria.garcia@rrhh.com', 'pass123', 'supervisor'),
        ]
        
        for usuario in usuarios:
            nombre, email, password, rol = usuario
            password_hash = hash_password(password)
            db.execute_query(
                "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
                (nombre, email, password_hash, rol)
            )
        print(f"[OK] {len(usuarios)} usuarios insertados")
        
        # Insertar departamentos
        print("\n[INFO] Insertando departamentos...")
        departamentos = [
            ('Recursos Humanos', 'Departamento encargado de la gestión del personal'),
            ('Tecnología', 'Departamento de desarrollo y sistemas'),
            ('Ventas', 'Departamento comercial y ventas'),
            ('Marketing', 'Departamento de marketing y comunicaciones'),
            ('Finanzas', 'Departamento de contabilidad y finanzas'),
        ]
        
        for depto in departamentos:
            db.execute_query(
                "INSERT INTO departamentos (nombre, descripcion) VALUES (?, ?)",
                depto
            )
        print(f"[OK] {len(departamentos)} departamentos insertados")
        
        # Insertar empleados
        print("\n[INFO] Insertando empleados...")
        empleados = [
            ('Carlos', 'Rodriguez', 'carlos.rodriguez@empresa.com', '555-0101', 1, 'Gerente de RRHH', '2020-01-15', 50000),
            ('Ana', 'Martinez', 'ana.martinez@empresa.com', '555-0102', 2, 'Desarrollador Senior', '2019-03-20', 45000),
            ('Luis', 'Gonzalez', 'luis.gonzalez@empresa.com', '555-0103', 3, 'Ejecutivo de Ventas', '2021-06-10', 35000),
            ('Sofia', 'Lopez', 'sofia.lopez@empresa.com', '555-0104', 4, 'Especialista en Marketing', '2020-09-01', 38000),
            ('Pedro', 'Sanchez', 'pedro.sanchez@empresa.com', '555-0105', 5, 'Contador', '2018-11-12', 42000),
            ('Laura', 'Fernandez', 'laura.fernandez@empresa.com', '555-0106', 2, 'Desarrollador Junior', '2022-02-14', 30000),
            ('Miguel', 'Torres', 'miguel.torres@empresa.com', '555-0107', 3, 'Gerente de Ventas', '2017-05-08', 55000),
            ('Carmen', 'Ramirez', 'carmen.ramirez@empresa.com', '555-0108', 1, 'Asistente de RRHH', '2021-08-22', 28000),
        ]
        
        for emp in empleados:
            db.execute_query(
                """INSERT INTO empleados 
                (nombre, apellido, email, telefono, departamento_id, puesto, fecha_ingreso, salario) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                emp
            )
        print(f"[OK] {len(empleados)} empleados insertados")
        
        # Insertar algunas asistencias
        print("\n[INFO] Insertando registros de asistencia...")
        hoy = date.today()
        asistencias = [
            (1, hoy, '08:00', '17:00', 'presente', None),
            (2, hoy, '08:15', '17:30', 'presente', None),
            (3, hoy, '09:00', '18:00', 'presente', 'Llegó tarde'),
            (4, hoy, '08:00', '17:00', 'presente', None),
            (5, hoy, None, None, 'ausente', 'Permiso médico'),
        ]
        
        for asist in asistencias:
            db.execute_query(
                """INSERT INTO asistencias 
                (empleado_id, fecha, hora_entrada, hora_salida, estado, observaciones) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                asist
            )
        print(f"[OK] {len(asistencias)} registros de asistencia insertados")
        
        # Insertar notificaciones
        print("\n[INFO] Insertando notificaciones...")
        notificaciones = [
            (1, 'Bienvenido al Sistema', 'Bienvenido al sistema de gestión de RRHH', 'info'),
            (2, 'Recordatorio', 'No olvides marcar tu asistencia diaria', 'warning'),
            (3, 'Nueva tarea', 'Tienes una nueva tarea asignada', 'info'),
        ]
        
        for notif in notificaciones:
            db.execute_query(
                "INSERT INTO notificaciones (usuario_id, titulo, mensaje, tipo) VALUES (?, ?, ?, ?)",
                notif
            )
        print(f"[OK] {len(notificaciones)} notificaciones insertadas")
        
        print("\n" + "=" * 60)
        print("[OK] DATOS DE EJEMPLO INSERTADOS EXITOSAMENTE")
        print("=" * 60)
        print("\nCredenciales de prueba:")
        print("  Email: admin@rrhh.com")
        print("  Password: admin123")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al insertar datos: {e}\n")
        return False

if __name__ == "__main__":
    insert_sample_data()

