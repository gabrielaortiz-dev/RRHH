"""
Modelo para manejar capacitaciones en la base de datos.
"""
from database import get_db
from typing import Optional, Dict, List


class Capacitacion:
    """Clase para manejar operaciones de capacitaciones."""
    
    @staticmethod
    def create(id_empleado: int, nombre_curso: Optional[str] = None,
               institucion: Optional[str] = None,
               fecha_inicio: Optional[str] = None,
               fecha_fin: Optional[str] = None,
               certificado: Optional[bool] = False) -> Dict:
        """
        Crea una nueva capacitación.
        
        Args:
            id_empleado: ID del empleado
            nombre_curso: Nombre del curso
            institucion: Institución que imparte el curso
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            certificado: Si tiene certificado (True/False)
            
        Returns:
            Dict con los datos de la capacitación creada
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
            if not cursor.fetchone():
                raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            certificado_int = 1 if certificado else 0
            
            cursor.execute("""
                INSERT INTO Capacitaciones (id_empleado, nombre_curso, institucion, 
                                          fecha_inicio, fecha_fin, certificado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado_int))
            
            capacitacion_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM Capacitaciones WHERE id_capacitacion = ?", (capacitacion_id,))
            row = cursor.fetchone()
            
            return {
                'id_capacitacion': row['id_capacitacion'],
                'id_empleado': row['id_empleado'],
                'nombre_curso': row['nombre_curso'],
                'institucion': row['institucion'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'certificado': bool(row['certificado'])
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Obtiene todas las capacitaciones."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_capacitacion, id_empleado, nombre_curso, institucion,
                       fecha_inicio, fecha_fin, certificado
                FROM Capacitaciones 
                ORDER BY fecha_inicio DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_capacitacion': row['id_capacitacion'],
                'id_empleado': row['id_empleado'],
                'nombre_curso': row['nombre_curso'],
                'institucion': row['institucion'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'certificado': bool(row['certificado'])
            } for row in rows]
    
    @staticmethod
    def get_by_id(capacitacion_id: int) -> Optional[Dict]:
        """Obtiene una capacitación por su ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_capacitacion, id_empleado, nombre_curso, institucion,
                       fecha_inicio, fecha_fin, certificado
                FROM Capacitaciones 
                WHERE id_capacitacion = ?
            """, (capacitacion_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_capacitacion': row['id_capacitacion'],
                    'id_empleado': row['id_empleado'],
                    'nombre_curso': row['nombre_curso'],
                    'institucion': row['institucion'],
                    'fecha_inicio': row['fecha_inicio'],
                    'fecha_fin': row['fecha_fin'],
                    'certificado': bool(row['certificado'])
                }
            return None
    
    @staticmethod
    def get_by_empleado(empleado_id: int) -> List[Dict]:
        """Obtiene todas las capacitaciones de un empleado."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_capacitacion, id_empleado, nombre_curso, institucion,
                       fecha_inicio, fecha_fin, certificado
                FROM Capacitaciones 
                WHERE id_empleado = ?
                ORDER BY fecha_inicio DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [{
                'id_capacitacion': row['id_capacitacion'],
                'id_empleado': row['id_empleado'],
                'nombre_curso': row['nombre_curso'],
                'institucion': row['institucion'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'certificado': bool(row['certificado'])
            } for row in rows]
    
    @staticmethod
    def update(capacitacion_id: int, id_empleado: Optional[int] = None,
               nombre_curso: Optional[str] = None,
               institucion: Optional[str] = None,
               fecha_inicio: Optional[str] = None,
               fecha_fin: Optional[str] = None,
               certificado: Optional[bool] = None) -> Optional[Dict]:
        """Actualiza una capacitación existente."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Capacitaciones WHERE id_capacitacion = ?", (capacitacion_id,))
            if not cursor.fetchone():
                return None
            
            if id_empleado is not None:
                cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
                if not cursor.fetchone():
                    raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            updates = []
            params = []
            
            if id_empleado is not None:
                updates.append("id_empleado = ?")
                params.append(id_empleado)
            if nombre_curso is not None:
                updates.append("nombre_curso = ?")
                params.append(nombre_curso)
            if institucion is not None:
                updates.append("institucion = ?")
                params.append(institucion)
            if fecha_inicio is not None:
                updates.append("fecha_inicio = ?")
                params.append(fecha_inicio)
            if fecha_fin is not None:
                updates.append("fecha_fin = ?")
                params.append(fecha_fin)
            if certificado is not None:
                updates.append("certificado = ?")
                params.append(1 if certificado else 0)
            
            if updates:
                params.append(capacitacion_id)
                query = f"UPDATE Capacitaciones SET {', '.join(updates)} WHERE id_capacitacion = ?"
                cursor.execute(query, params)
            
            cursor.execute("""
                SELECT id_capacitacion, id_empleado, nombre_curso, institucion,
                       fecha_inicio, fecha_fin, certificado
                FROM Capacitaciones 
                WHERE id_capacitacion = ?
            """, (capacitacion_id,))
            row = cursor.fetchone()
            
            return {
                'id_capacitacion': row['id_capacitacion'],
                'id_empleado': row['id_empleado'],
                'nombre_curso': row['nombre_curso'],
                'institucion': row['institucion'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'certificado': bool(row['certificado'])
            }
    
    @staticmethod
    def delete(capacitacion_id: int) -> bool:
        """Elimina una capacitación."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Capacitaciones WHERE id_capacitacion = ?", (capacitacion_id,))
            return cursor.rowcount > 0

