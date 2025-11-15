"""
Modelo para manejar vacaciones y permisos en la base de datos.
"""
from database import get_db
from typing import Optional, Dict, List


class VacacionPermiso:
    """Clase para manejar operaciones de vacaciones y permisos."""
    
    @staticmethod
    def create(id_empleado: int, tipo: Optional[str] = None,
               fecha_solicitud: Optional[str] = None,
               fecha_inicio: Optional[str] = None,
               fecha_fin: Optional[str] = None,
               estado: Optional[str] = None,
               observaciones: Optional[str] = None) -> Dict:
        """
        Crea un nuevo registro de vacación o permiso.
        
        Args:
            id_empleado: ID del empleado
            tipo: Tipo de permiso (Vacación, Permiso, Licencia)
            fecha_solicitud: Fecha de solicitud (YYYY-MM-DD)
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            estado: Estado (Aprobado, Pendiente, Rechazado)
            observaciones: Observaciones
            
        Returns:
            Dict con los datos del registro creado
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
            if not cursor.fetchone():
                raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            cursor.execute("""
                INSERT INTO Vacaciones_Permisos (id_empleado, tipo, fecha_solicitud,
                                                fecha_inicio, fecha_fin, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_empleado, tipo, fecha_solicitud, fecha_inicio, fecha_fin, estado, observaciones))
            
            permiso_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM Vacaciones_Permisos WHERE id_permiso = ?", (permiso_id,))
            row = cursor.fetchone()
            
            return {
                'id_permiso': row['id_permiso'],
                'id_empleado': row['id_empleado'],
                'tipo': row['tipo'],
                'fecha_solicitud': row['fecha_solicitud'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'estado': row['estado'],
                'observaciones': row['observaciones']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Obtiene todos los registros de vacaciones y permisos."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_permiso, id_empleado, tipo, fecha_solicitud, fecha_inicio,
                       fecha_fin, estado, observaciones
                FROM Vacaciones_Permisos 
                ORDER BY fecha_solicitud DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_permiso': row['id_permiso'],
                'id_empleado': row['id_empleado'],
                'tipo': row['tipo'],
                'fecha_solicitud': row['fecha_solicitud'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'estado': row['estado'],
                'observaciones': row['observaciones']
            } for row in rows]
    
    @staticmethod
    def get_by_id(permiso_id: int) -> Optional[Dict]:
        """Obtiene un registro por su ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_permiso, id_empleado, tipo, fecha_solicitud, fecha_inicio,
                       fecha_fin, estado, observaciones
                FROM Vacaciones_Permisos 
                WHERE id_permiso = ?
            """, (permiso_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_permiso': row['id_permiso'],
                    'id_empleado': row['id_empleado'],
                    'tipo': row['tipo'],
                    'fecha_solicitud': row['fecha_solicitud'],
                    'fecha_inicio': row['fecha_inicio'],
                    'fecha_fin': row['fecha_fin'],
                    'estado': row['estado'],
                    'observaciones': row['observaciones']
                }
            return None
    
    @staticmethod
    def get_by_empleado(empleado_id: int) -> List[Dict]:
        """Obtiene todos los registros de un empleado."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_permiso, id_empleado, tipo, fecha_solicitud, fecha_inicio,
                       fecha_fin, estado, observaciones
                FROM Vacaciones_Permisos 
                WHERE id_empleado = ?
                ORDER BY fecha_solicitud DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [{
                'id_permiso': row['id_permiso'],
                'id_empleado': row['id_empleado'],
                'tipo': row['tipo'],
                'fecha_solicitud': row['fecha_solicitud'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'estado': row['estado'],
                'observaciones': row['observaciones']
            } for row in rows]
    
    @staticmethod
    def update(permiso_id: int, id_empleado: Optional[int] = None,
               tipo: Optional[str] = None,
               fecha_solicitud: Optional[str] = None,
               fecha_inicio: Optional[str] = None,
               fecha_fin: Optional[str] = None,
               estado: Optional[str] = None,
               observaciones: Optional[str] = None) -> Optional[Dict]:
        """Actualiza un registro existente."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Vacaciones_Permisos WHERE id_permiso = ?", (permiso_id,))
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
            if tipo is not None:
                updates.append("tipo = ?")
                params.append(tipo)
            if fecha_solicitud is not None:
                updates.append("fecha_solicitud = ?")
                params.append(fecha_solicitud)
            if fecha_inicio is not None:
                updates.append("fecha_inicio = ?")
                params.append(fecha_inicio)
            if fecha_fin is not None:
                updates.append("fecha_fin = ?")
                params.append(fecha_fin)
            if estado is not None:
                updates.append("estado = ?")
                params.append(estado)
            if observaciones is not None:
                updates.append("observaciones = ?")
                params.append(observaciones)
            
            if updates:
                params.append(permiso_id)
                query = f"UPDATE Vacaciones_Permisos SET {', '.join(updates)} WHERE id_permiso = ?"
                cursor.execute(query, params)
            
            cursor.execute("""
                SELECT id_permiso, id_empleado, tipo, fecha_solicitud, fecha_inicio,
                       fecha_fin, estado, observaciones
                FROM Vacaciones_Permisos 
                WHERE id_permiso = ?
            """, (permiso_id,))
            row = cursor.fetchone()
            
            return {
                'id_permiso': row['id_permiso'],
                'id_empleado': row['id_empleado'],
                'tipo': row['tipo'],
                'fecha_solicitud': row['fecha_solicitud'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'estado': row['estado'],
                'observaciones': row['observaciones']
            }
    
    @staticmethod
    def delete(permiso_id: int) -> bool:
        """Elimina un registro."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Vacaciones_Permisos WHERE id_permiso = ?", (permiso_id,))
            return cursor.rowcount > 0

