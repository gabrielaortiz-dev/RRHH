"""
Script para actualizar la estructura de la base de datos y migrar al nuevo sistema de roles

Este script:
1. Agrega las columnas necesarias a las tablas existentes
2. Migra los datos actuales al nuevo sistema de roles
3. Asigna roles automáticamente basándose en puestos
4. Mantiene la integridad de los datos existentes

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
import os
from datetime import datetime


class ActualizadorEstructuraRoles:
    """Actualiza la estructura de la BD para soportar el nuevo sistema de roles"""
    
    def __init__(self, db_path: str = 'rrhh.db'):
        """Inicializa el actualizador con la ruta de la BD"""
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.conn = None
        self.cursor = None
        
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path, timeout=10.0)
            self.conn.execute("PRAGMA foreign_keys = OFF")  # Desactivar temporalmente
            self.cursor = self.conn.cursor()
            print("[OK] Conexión establecida")
        except Exception as e:
            print(f"[ERROR] No se pudo conectar: {e}")
            raise
            
    def desconectar(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print("[OK] Conexión cerrada")
            
    def verificar_y_crear_tablas(self):
        """Verifica que existan todas las tablas necesarias y las crea si faltan"""
        print("\n" + "="*70)
        print("VERIFICANDO ESTRUCTURA DE TABLAS")
        print("="*70)
        
        # Tabla Roles
        print("\n[INFO] Verificando tabla Roles...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Roles (
                id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(50) UNIQUE NOT NULL,
                descripcion TEXT,
                id_puesto INTEGER,
                nivel_acceso INTEGER DEFAULT 1,
                es_sistema BOOLEAN DEFAULT 0,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion DATETIME,
                FOREIGN KEY (id_puesto) REFERENCES Puestos(id_puesto)
            )
        """)
        print("   [OK] Tabla Roles verificada")
        
        # Tabla Permisos
        print("\n[INFO] Verificando tabla Permisos...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Permisos (
                id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) UNIQUE NOT NULL,
                descripcion TEXT,
                modulo VARCHAR(50) NOT NULL,
                accion VARCHAR(50) NOT NULL,
                codigo VARCHAR(100) UNIQUE NOT NULL,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   [OK] Tabla Permisos verificada")
        
        # Tabla Roles_Permisos
        print("\n[INFO] Verificando tabla Roles_Permisos...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Roles_Permisos (
                id_rol_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                id_rol INTEGER NOT NULL,
                id_permiso INTEGER NOT NULL,
                concedido BOOLEAN DEFAULT 1,
                fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE,
                FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso) ON DELETE CASCADE,
                UNIQUE(id_rol, id_permiso)
            )
        """)
        print("   [OK] Tabla Roles_Permisos verificada")
        
        # Tabla Usuarios_Roles
        print("\n[INFO] Verificando tabla Usuarios_Roles...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios_Roles (
                id_usuario_rol INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                id_rol INTEGER NOT NULL,
                es_principal BOOLEAN DEFAULT 0,
                fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion DATETIME,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE,
                UNIQUE(usuario_id, id_rol)
            )
        """)
        print("   [OK] Tabla Usuarios_Roles verificada")
        
        # Tabla Usuarios_Permisos
        print("\n[INFO] Verificando tabla Usuarios_Permisos...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios_Permisos (
                id_usuario_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                id_permiso INTEGER NOT NULL,
                concedido BOOLEAN DEFAULT 1,
                razon TEXT,
                fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion DATETIME,
                asignado_por INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso) ON DELETE CASCADE,
                FOREIGN KEY (asignado_por) REFERENCES usuarios(id),
                UNIQUE(usuario_id, id_permiso)
            )
        """)
        print("   [OK] Tabla Usuarios_Permisos verificada")
        
        # Tabla Historial_Roles
        print("\n[INFO] Verificando tabla Historial_Roles...")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Historial_Roles (
                id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                id_rol_anterior INTEGER,
                id_rol_nuevo INTEGER,
                motivo TEXT,
                realizado_por INTEGER,
                fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (id_rol_anterior) REFERENCES Roles(id_rol),
                FOREIGN KEY (id_rol_nuevo) REFERENCES Roles(id_rol),
                FOREIGN KEY (realizado_por) REFERENCES usuarios(id)
            )
        """)
        print("   [OK] Tabla Historial_Roles verificada")
        
        self.conn.commit()
        print("\n[OK] Todas las tablas verificadas y creadas")
        
    def agregar_columna_id_rol_a_puestos(self):
        """Agrega la columna id_rol a la tabla Puestos si no existe"""
        print("\n" + "="*70)
        print("ACTUALIZANDO ESTRUCTURA DE TABLA PUESTOS")
        print("="*70)
        
        try:
            # Verificar si la columna ya existe
            self.cursor.execute("PRAGMA table_info(Puestos)")
            columnas = [col[1] for col in self.cursor.fetchall()]
            
            if 'id_rol' in columnas:
                print("\n[OK] La columna id_rol ya existe en Puestos")
                return
                
            print("\n[INFO] Agregando columna id_rol a tabla Puestos...")
            
            # Obtener datos actuales
            self.cursor.execute("SELECT * FROM Puestos")
            puestos_actuales = self.cursor.fetchall()
            
            # Obtener estructura de columnas
            self.cursor.execute("PRAGMA table_info(Puestos)")
            estructura_actual = self.cursor.fetchall()
            
            # Crear tabla temporal con nueva estructura
            self.cursor.execute("""
                CREATE TABLE Puestos_Temp (
                    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_puesto VARCHAR(100) NOT NULL,
                    nivel VARCHAR(50),
                    salario_base DECIMAL(10,2),
                    id_rol INTEGER,
                    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
                )
            """)
            
            # Copiar datos existentes
            if puestos_actuales:
                print(f"   [INFO] Copiando {len(puestos_actuales)} puestos existentes...")
                for puesto in puestos_actuales:
                    self.cursor.execute("""
                        INSERT INTO Puestos_Temp (id_puesto, nombre_puesto, nivel, salario_base)
                        VALUES (?, ?, ?, ?)
                    """, (puesto[0], puesto[1], puesto[2], puesto[3]))
            
            # Eliminar tabla antigua
            self.cursor.execute("DROP TABLE Puestos")
            
            # Renombrar tabla temporal
            self.cursor.execute("ALTER TABLE Puestos_Temp RENAME TO Puestos")
            
            self.conn.commit()
            print("   [OK] Estructura actualizada exitosamente")
            
        except Exception as e:
            print(f"   [ERROR] Error al actualizar estructura: {e}")
            self.conn.rollback()
            raise
            
    def asignar_roles_a_empleados(self):
        """Asigna roles a empleados existentes basándose en sus puestos"""
        print("\n" + "="*70)
        print("ASIGNANDO ROLES A EMPLEADOS EXISTENTES")
        print("="*70)
        
        try:
            # Verificar si hay empleados
            self.cursor.execute("SELECT COUNT(*) FROM empleados")
            total_empleados = self.cursor.fetchone()[0]
            
            if total_empleados == 0:
                print("\n[INFO] No hay empleados en la base de datos")
                return
                
            print(f"\n[INFO] Se encontraron {total_empleados} empleados")
            print("[INFO] Asignando roles basándose en puestos...")
            
            # Obtener empleados con sus puestos
            self.cursor.execute("""
                SELECT e.id, e.nombre, e.apellido, p.nombre_puesto, p.id_rol
                FROM empleados e
                LEFT JOIN Puestos p ON e.puesto = p.id_puesto
                WHERE e.activo = 1
            """)
            
            empleados = self.cursor.fetchall()
            asignados = 0
            sin_rol = 0
            
            for emp_id, nombre, apellido, puesto, id_rol in empleados:
                if id_rol:
                    # Verificar si el empleado tiene un usuario asociado
                    self.cursor.execute("""
                        SELECT id FROM usuarios 
                        WHERE email = (SELECT email FROM empleados WHERE id = ?)
                    """, (emp_id,))
                    
                    usuario = self.cursor.fetchone()
                    
                    if usuario:
                        usuario_id = usuario[0]
                        
                        # Verificar si ya tiene este rol asignado
                        self.cursor.execute("""
                            SELECT id_usuario_rol FROM Usuarios_Roles
                            WHERE usuario_id = ? AND id_rol = ?
                        """, (usuario_id, id_rol))
                        
                        if not self.cursor.fetchone():
                            # Asignar rol al usuario
                            self.cursor.execute("""
                                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                                VALUES (?, ?, 1, 1)
                            """, (usuario_id, id_rol))
                            
                            # Registrar en historial
                            self.cursor.execute("""
                                INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
                                VALUES (?, ?, 'Asignación automática basada en puesto')
                            """, (usuario_id, id_rol))
                            
                            asignados += 1
                            print(f"   ✓ {nombre} {apellido} - Puesto: {puesto}")
                else:
                    sin_rol += 1
                    
            self.conn.commit()
            
            print(f"\n[OK] Roles asignados: {asignados}")
            if sin_rol > 0:
                print(f"[INFO] Empleados sin rol asignado: {sin_rol}")
                print("        (No tienen puesto asignado o el puesto no tiene rol)")
                
        except Exception as e:
            print(f"[ERROR] Error al asignar roles: {e}")
            self.conn.rollback()
            raise
            
    def generar_reporte_migracion(self):
        """Genera un reporte de la migración realizada"""
        print("\n" + "="*70)
        print("REPORTE DE MIGRACIÓN")
        print("="*70)
        
        # Contar registros
        self.cursor.execute("SELECT COUNT(*) FROM Roles WHERE activo = 1")
        total_roles = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM Puestos")
        total_puestos = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM Usuarios_Roles WHERE activo = 1")
        total_asignaciones = self.cursor.fetchone()[0]
        
        print(f"\n   Roles activos: {total_roles}")
        print(f"   Puestos totales: {total_puestos}")
        print(f"   Asignaciones de roles a usuarios: {total_asignaciones}")
        
        # Mostrar distribución de usuarios por rol
        print("\n   DISTRIBUCIÓN DE USUARIOS POR ROL:")
        print("   " + "-"*66)
        
        self.cursor.execute("""
            SELECT r.nombre, COUNT(ur.usuario_id) as usuarios
            FROM Roles r
            LEFT JOIN Usuarios_Roles ur ON r.id_rol = ur.id_rol AND ur.activo = 1
            WHERE r.activo = 1
            GROUP BY r.nombre
            ORDER BY r.nivel_acceso DESC
        """)
        
        for rol, cantidad in self.cursor.fetchall():
            print(f"   {rol:.<50} {cantidad:>2} usuario(s)")
            
        print("\n" + "="*70)
        
    def ejecutar_actualizacion_completa(self):
        """Ejecuta todo el proceso de actualización"""
        try:
            self.conectar()
            
            print("\n" + "="*70)
            print("ACTUALIZACIÓN DE ESTRUCTURA DE ROLES")
            print("Sistema de Gestión de RRHH")
            print("="*70)
            print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 1. Verificar y crear tablas necesarias
            self.verificar_y_crear_tablas()
            
            # 2. Actualizar estructura de Puestos
            self.agregar_columna_id_rol_a_puestos()
            
            # 3. Asignar roles a empleados existentes
            self.asignar_roles_a_empleados()
            
            # 4. Generar reporte
            self.generar_reporte_migracion()
            
            print("\n" + "="*70)
            print("ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            
            print("\n📌 PRÓXIMOS PASOS:")
            print("   1. Ejecutar: python configurar_roles_y_puestos.py")
            print("   2. Esto creará los 5 roles del sistema y asignará puestos")
            print("   3. Los empleados heredarán los roles de sus puestos")
            print("\n" + "="*70)
            
        except Exception as e:
            print(f"\n[ERROR CRÍTICO] {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.desconectar()


def main():
    """Función principal"""
    actualizador = ActualizadorEstructuraRoles()
    actualizador.ejecutar_actualizacion_completa()


if __name__ == "__main__":
    main()

