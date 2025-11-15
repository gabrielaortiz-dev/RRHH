"""
Modelo para manejar asistencias en la base de datos.
"""
from database import get_db
from typing import Optional, Dict, List


class Asistencia:
    """Clase para manejar operaciones de asistencias."""
    
    @staticmethod
    def create(id_empleado: int, fecha: Optional[str] = None,
               hora_entrada: Optional[str] = None,
               hora_salida: Optional[str] = None,
               observaciones: Optional[str] = None) -> Dict:
        """
        Crea una nueva asistencia.
        
        Args:
            id_empleado: ID del empleado
            fecha: Fecha de la asistencia (YYYY-MM-DD)
            hora_entrada: Hora de entrada (HH:MM:SS)
            hora_salida: Hora de salida (HH:MM:SS)
            observaciones: Observaciones sobre la asistencia
            
        Returns:
            Dict con los datos de la asistencia creada
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar que el empleado existe
            cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
            if not cursor.fetchone():
                raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            # Insertar la nueva asistencia
            cursor.execute("""
                INSERT INTO Asistencias (id_empleado, fecha, hora_entrada, hora_salida, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (id_empleado, fecha, hora_entrada, hora_salida, observaciones))
            
            asistencia_id = cursor.lastrowid
            
            # Obtener la asistencia creada
            cursor.execute("SELECT * FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
            row = cursor.fetchone()
            
            return {
                'id_asistencia': row['id_asistencia'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'hora_entrada': row['hora_entrada'],
                'hora_salida': row['hora_salida'],
                'observaciones': row['observaciones']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Obtiene todas las asistencias."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_asistencia, id_empleado, fecha, hora_entrada, hora_salida, observaciones
                FROM Asistencias 
                ORDER BY fecha DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_asistencia': row['id_asistencia'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'hora_entrada': row['hora_entrada'],
                'hora_salida': row['hora_salida'],
                'observaciones': row['observaciones']
            } for row in rows]
    
    @staticmethod
    def get_by_id(asistencia_id: int) -> Optional[Dict]:
        """Obtiene una asistencia por su ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_asistencia, id_empleado, fecha, hora_entrada, hora_salida, observaciones
                FROM Asistencias 
                WHERE id_asistencia = ?
            """, (asistencia_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_asistencia': row['id_asistencia'],
                    'id_empleado': row['id_empleado'],
                    'fecha': row['fecha'],
                    'hora_entrada': row['hora_entrada'],
                    'hora_salida': row['hora_salida'],
                    'observaciones': row['observaciones']
                }
            return None
    
    @staticmethod
    def get_by_empleado(empleado_id: int) -> List[Dict]:
        """Obtiene todas las asistencias de un empleado."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_asistencia, id_empleado, fecha, hora_entrada, hora_salida, observaciones
                FROM Asistencias 
                WHERE id_empleado = ?
                ORDER BY fecha DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [{
                'id_asistencia': row['id_asistencia'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'hora_entrada': row['hora_entrada'],
                'hora_salida': row['hora_salida'],
                'observaciones': row['observaciones']
            } for row in rows]
    
    @staticmethod
    def update(asistencia_id: int, id_empleado: Optional[int] = None,
               fecha: Optional[str] = None,
               hora_entrada: Optional[str] = None,
               hora_salida: Optional[str] = None,
               observaciones: Optional[str] = None) -> Optional[Dict]:
        """Actualiza una asistencia existente."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
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
            if fecha is not None:
                updates.append("fecha = ?")
                params.append(fecha)
            if hora_entrada is not None:
                updates.append("hora_entrada = ?")
                params.append(hora_entrada)
            if hora_salida is not None:
                updates.append("hora_salida = ?")
                params.append(hora_salida)
            if observaciones is not None:
                updates.append("observaciones = ?")
                params.append(observaciones)
            
            if updates:
                params.append(asistencia_id)
                query = f"UPDATE Asistencias SET {', '.join(updates)} WHERE id_asistencia = ?"
                cursor.execute(query, params)
            
            cursor.execute("""
                SELECT id_asistencia, id_empleado, fecha, hora_entrada, hora_salida, observaciones
                FROM Asistencias 
                WHERE id_asistencia = ?
            """, (asistencia_id,))
            row = cursor.fetchone()
            
            return {
                'id_asistencia': row['id_asistencia'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'hora_entrada': row['hora_entrada'],
                'hora_salida': row['hora_salida'],
                'observaciones': row['observaciones']
            }
    
    @staticmethod
    def delete(asistencia_id: int) -> bool:
        """Elimina una asistencia."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
            return cursor.rowcount > 0

