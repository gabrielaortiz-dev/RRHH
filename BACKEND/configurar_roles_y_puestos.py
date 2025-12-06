"""
Sistema de Gestión de Roles y Puestos - RRHH
==============================================

Este script configura el sistema de roles y permisos basado en puestos de trabajo.
Los usuarios no tienen permisos por puesto, sino por el rol asignado.

Estructura de Roles:
--------------------
1. Super Admin - Control total del sistema
2. Gerente / Alta Gerencia - Decisiones estratégicas y aprobaciones
3. Supervisor / Jefe de Área - Gestión departamental
4. Operativo - Trabajo diario sin aprobaciones
5. Consulta / Solo Visualización - Solo lectura

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
import os
from typing import List, Tuple, Dict
from datetime import datetime


class GestorRolesYPuestos:
    """Clase para gestionar la configuración de roles y puestos en el sistema"""
    
    def __init__(self, db_path: str = 'rrhh.db'):
        """
        Inicializa el gestor con la ruta de la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.conn = None
        self.cursor = None
        
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path, timeout=10.0)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
            print("[OK] Conexión establecida con la base de datos")
        except Exception as e:
            print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
            raise
            
    def desconectar(self):
        """Cierra la conexión con la base de datos"""
        if self.conn:
            self.conn.close()
            print("[OK] Conexión cerrada")
            
    def obtener_roles_sistema(self) -> List[Dict]:
        """
        Define los 5 roles del sistema según especificaciones
        
        Returns:
            Lista de diccionarios con información de cada rol
        """
        return [
            {
                'nombre': 'Super Admin',
                'descripcion': 'Control total del sistema, configuraciones, seguridad y creación de usuarios. '
                              'Puede gestionar todo el sistema sin restricciones.',
                'nivel_acceso': 100,
                'es_sistema': 1,
                'permisos': [
                    'Control total',
                    'Gestionar usuarios y roles',
                    'Configurar sistema',
                    'Ver todos los reportes',
                    'Aprobar todo',
                    'Eliminar registros',
                    'Auditar sistema'
                ]
            },
            {
                'nombre': 'Gerente / Alta Gerencia',
                'descripcion': 'Decisiones estratégicas, aprobación de solicitudes y acceso a reportes completos. '
                              'Supervisa operaciones sin acceso a configuraciones técnicas.',
                'nivel_acceso': 80,
                'es_sistema': 1,
                'permisos': [
                    'Aprobar solicitudes (vacaciones, permisos, nóminas)',
                    'Ver reportes completos',
                    'Crear y editar información',
                    'Ver datos de toda la empresa',
                    'Descargar documentos corporativos',
                    'Supervisar departamentos'
                ]
            },
            {
                'nombre': 'Supervisor / Jefe de Área',
                'descripcion': 'Gestión de equipos y departamentos. Puede crear, editar y aprobar '
                              'solo dentro de su área de responsabilidad.',
                'nivel_acceso': 60,
                'es_sistema': 1,
                'permisos': [
                    'Crear y editar dentro de su área',
                    'Aprobar procesos departamentales',
                    'Ver reportes de su departamento',
                    'Supervisar su equipo',
                    'Gestionar asistencias de su área'
                ]
            },
            {
                'nombre': 'Operativo',
                'descripcion': 'Trabajo diario en el sistema. Puede registrar información, '
                              'subir documentos y modificar su propia información.',
                'nivel_acceso': 30,
                'es_sistema': 1,
                'permisos': [
                    'Registrar información',
                    'Subir documentos',
                    'Modificar información propia',
                    'Descargar recibos propios',
                    'Ver reportes personales',
                    'Solicitar vacaciones/permisos'
                ]
            },
            {
                'nombre': 'Consulta / Solo Visualización',
                'descripcion': 'Acceso de solo lectura. Puede visualizar información del sistema '
                              'sin poder modificar, crear, eliminar o aprobar.',
                'nivel_acceso': 10,
                'es_sistema': 1,
                'permisos': [
                    'Ver información (solo lectura)',
                    'Consultar reportes asignados',
                    'Ver datos generales',
                    'Auditar información'
                ]
            }
        ]
        
    def obtener_puestos_por_rol(self) -> Dict[str, List[Tuple]]:
        """
        Define el mapeo de puestos a roles según especificaciones
        
        Returns:
            Diccionario con rol como clave y lista de puestos como valor
            Cada puesto es una tupla: (nombre, nivel, salario_base)
        """
        return {
            'Super Admin': [
                ('Gerente General', 'Executive', 95000),
                ('Director de Tecnología (CTO)', 'Executive', 90000),
                ('Gerente de Proyectos', 'Executive', 85000)
            ],
            'Gerente / Alta Gerencia': [
                ('Gerente de RRHH', 'Senior', 75000),
                ('Gerente de Ventas', 'Senior', 75000)
            ],
            'Supervisor / Jefe de Área': [
                ('Analista de RRHH', 'Mid', 50000),
                ('Contador', 'Senior', 55000),
                ('Analista Financiero', 'Mid', 50000),
                ('Especialista en Marketing', 'Mid', 48000),
                ('Supervisor de Atención', 'Mid', 45000),
                ('Coordinador de Operaciones', 'Mid', 47000),
                ('Coordinador Logístico', 'Mid', 46000),
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
        
    def limpiar_roles_y_puestos_existentes(self):
        """Limpia los datos existentes de roles y puestos para regenerarlos"""
        print("\n" + "="*70)
        print("LIMPIANDO ROLES Y PUESTOS EXISTENTES")
        print("="*70)
        
        try:
            # Desactivar foreign keys temporalmente
            self.cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Limpiar tablas relacionadas
            tablas = [
                'Usuarios_Roles',
                'Usuarios_Permisos', 
                'Historial_Roles',
                'Roles_Permisos',
                'Roles',
                'Puestos'
            ]
            
            for tabla in tablas:
                try:
                    self.cursor.execute(f"DELETE FROM {tabla}")
                    self.cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
                    print(f"   [OK] {tabla} limpiada")
                except Exception as e:
                    print(f"   [SKIP] {tabla}: {str(e)}")
                    
            self.conn.commit()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print("\n[OK] Limpieza completada")
            
        except Exception as e:
            print(f"[ERROR] Error en limpieza: {e}")
            self.conn.rollback()
            raise
            
    def crear_roles(self) -> Dict[str, int]:
        """
        Crea los roles del sistema en la base de datos
        
        Returns:
            Diccionario con nombre de rol como clave y ID como valor
        """
        print("\n" + "="*70)
        print("CREANDO ROLES DEL SISTEMA")
        print("="*70)
        
        roles_sistema = self.obtener_roles_sistema()
        roles_ids = {}
        
        for rol in roles_sistema:
            try:
                self.cursor.execute("""
                    INSERT INTO Roles (nombre, descripcion, nivel_acceso, es_sistema, activo)
                    VALUES (?, ?, ?, ?, 1)
                """, (rol['nombre'], rol['descripcion'], rol['nivel_acceso'], rol['es_sistema']))
                
                rol_id = self.cursor.lastrowid
                roles_ids[rol['nombre']] = rol_id
                
                print(f"\n   [OK] Rol: {rol['nombre']}")
                print(f"        Nivel de acceso: {rol['nivel_acceso']}")
                print(f"        Permisos:")
                for permiso in rol['permisos']:
                    print(f"          • {permiso}")
                    
            except Exception as e:
                print(f"   [ERROR] No se pudo crear rol {rol['nombre']}: {e}")
                
        self.conn.commit()
        print(f"\n[OK] {len(roles_ids)} roles creados exitosamente")
        return roles_ids
        
    def crear_puestos(self, roles_ids: Dict[str, int]):
        """
        Crea los puestos y los vincula con sus roles correspondientes
        
        Args:
            roles_ids: Diccionario con nombre de rol y su ID en la BD
        """
        print("\n" + "="*70)
        print("CREANDO PUESTOS Y VINCULÁNDOLOS CON ROLES")
        print("="*70)
        
        puestos_por_rol = self.obtener_puestos_por_rol()
        total_puestos = 0
        
        for rol_nombre, puestos in puestos_por_rol.items():
            if rol_nombre not in roles_ids:
                print(f"   [WARNING] Rol {rol_nombre} no encontrado en la BD")
                continue
                
            rol_id = roles_ids[rol_nombre]
            print(f"\n   ROL: {rol_nombre} (ID: {rol_id})")
            print(f"   {'-'*60}")
            
            for nombre_puesto, nivel, salario in puestos:
                try:
                    # Crear puesto vinculado al rol
                    self.cursor.execute("""
                        INSERT INTO Puestos (nombre_puesto, nivel, salario_base, id_rol)
                        VALUES (?, ?, ?, ?)
                    """, (nombre_puesto, nivel, salario, rol_id))
                    
                    total_puestos += 1
                    print(f"      ✓ {nombre_puesto:.<40} {nivel:.<10} ${salario:,.2f}")
                    
                except Exception as e:
                    print(f"      ✗ {nombre_puesto}: {str(e)}")
                    
        self.conn.commit()
        print(f"\n[OK] {total_puestos} puestos creados y vinculados a roles")
        
    def verificar_tabla_puestos(self):
        """Verifica si la tabla Puestos tiene la columna id_rol, si no, la agrega"""
        print("\n[INFO] Verificando estructura de tabla Puestos...")
        
        try:
            # Verificar si existe la columna id_rol
            self.cursor.execute("PRAGMA table_info(Puestos)")
            columnas = self.cursor.fetchall()
            columnas_nombres = [col[1] for col in columnas]
            
            if 'id_rol' not in columnas_nombres:
                print("   [INFO] Columna id_rol no existe. Agregándola...")
                
                # Crear nueva tabla con la columna id_rol
                self.cursor.execute("""
                    CREATE TABLE Puestos_Nueva (
                        id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_puesto VARCHAR(100) NOT NULL,
                        nivel VARCHAR(50),
                        salario_base DECIMAL(10,2),
                        id_rol INTEGER,
                        FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
                    )
                """)
                
                # Copiar datos existentes
                self.cursor.execute("""
                    INSERT INTO Puestos_Nueva (id_puesto, nombre_puesto, nivel, salario_base)
                    SELECT id_puesto, nombre_puesto, nivel, salario_base FROM Puestos
                """)
                
                # Eliminar tabla antigua y renombrar
                self.cursor.execute("DROP TABLE Puestos")
                self.cursor.execute("ALTER TABLE Puestos_Nueva RENAME TO Puestos")
                
                self.conn.commit()
                print("   [OK] Columna id_rol agregada exitosamente")
            else:
                print("   [OK] Columna id_rol ya existe")
                
        except Exception as e:
            print(f"   [ERROR] Error al verificar tabla: {e}")
            raise
            
    def generar_reporte(self):
        """Genera un reporte completo de la configuración de roles y puestos"""
        print("\n" + "="*70)
        print("REPORTE DE CONFIGURACIÓN DE ROLES Y PUESTOS")
        print("="*70)
        
        # Contar roles
        self.cursor.execute("SELECT COUNT(*) FROM Roles WHERE activo = 1")
        total_roles = self.cursor.fetchone()[0]
        
        # Contar puestos
        self.cursor.execute("SELECT COUNT(*) FROM Puestos")
        total_puestos = self.cursor.fetchone()[0]
        
        print(f"\n   Total de Roles: {total_roles}")
        print(f"   Total de Puestos: {total_puestos}")
        
        # Mostrar distribución por rol
        print("\n   DISTRIBUCIÓN DE PUESTOS POR ROL:")
        print("   " + "-"*66)
        
        self.cursor.execute("""
            SELECT r.nombre, COUNT(p.id_puesto) as cantidad
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_rol = p.id_rol
            WHERE r.activo = 1
            GROUP BY r.nombre
            ORDER BY r.nivel_acceso DESC
        """)
        
        for rol, cantidad in self.cursor.fetchall():
            print(f"   {rol:.<50} {cantidad:>2} puesto(s)")
            
        print("\n   DETALLE COMPLETO:")
        print("   " + "-"*66)
        
        self.cursor.execute("""
            SELECT r.nombre as rol, r.nivel_acceso, p.nombre_puesto, p.nivel, p.salario_base
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_rol = p.id_rol
            WHERE r.activo = 1
            ORDER BY r.nivel_acceso DESC, p.nombre_puesto
        """)
        
        rol_actual = None
        for rol, nivel_acceso, puesto, nivel, salario in self.cursor.fetchall():
            if rol != rol_actual:
                print(f"\n   📋 {rol} (Nivel de Acceso: {nivel_acceso})")
                rol_actual = rol
                
            if puesto:
                print(f"      • {puesto} ({nivel}) - ${salario:,.2f}")
            else:
                print(f"      (Sin puestos asignados)")
                
        print("\n" + "="*70)
        print("CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        
        print("\n📌 NOTAS IMPORTANTES:")
        print("   • Los usuarios obtienen permisos según su ROL, no según su puesto")
        print("   • Un puesto está vinculado a UN rol específico")
        print("   • Los niveles de acceso van de 10 (menor) a 100 (máximo)")
        print("   • Los roles son aplicados al asignar un puesto a un empleado")
        print("\n" + "="*70)
        
    def ejecutar_configuracion_completa(self, limpiar_datos: bool = True):
        """
        Ejecuta el proceso completo de configuración de roles y puestos
        
        Args:
            limpiar_datos: Si es True, limpia los datos existentes antes de crear nuevos
        """
        try:
            self.conectar()
            
            print("\n" + "="*70)
            print("SISTEMA DE GESTIÓN DE ROLES Y PUESTOS - RRHH")
            print("Configuración Completa del Sistema")
            print("="*70)
            print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Base de datos: {self.db_path}")
            
            # Verificar estructura
            self.verificar_tabla_puestos()
            
            # Limpiar datos si se solicita
            if limpiar_datos:
                respuesta = input("\n¿Desea limpiar roles y puestos existentes? (s/n): ")
                if respuesta.lower() == 's':
                    self.limpiar_roles_y_puestos_existentes()
            
            # Crear roles
            roles_ids = self.crear_roles()
            
            # Crear puestos
            self.crear_puestos(roles_ids)
            
            # Generar reporte
            self.generar_reporte()
            
        except Exception as e:
            print(f"\n[ERROR CRÍTICO] {str(e)}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.conn.rollback()
        finally:
            self.desconectar()


def main():
    """Función principal para ejecutar el configurador"""
    gestor = GestorRolesYPuestos()
    gestor.ejecutar_configuracion_completa(limpiar_datos=True)


if __name__ == "__main__":
    main()

