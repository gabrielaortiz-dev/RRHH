"""
Modelo para manejar evaluaciones en la base de datos.
"""
from database import get_db
from typing import Optional, Dict, List


class Evaluacion:
    """Clase para manejar operaciones de evaluaciones."""
    
    @staticmethod
    def create(id_empleado: int, fecha: Optional[str] = None,
               evaluador: Optional[str] = None,
               puntaje: Optional[int] = None,
               observaciones: Optional[str] = None) -> Dict:
        """
        Crea una nueva evaluación.
        
        Args:
            id_empleado: ID del empleado
            fecha: Fecha de la evaluación (YYYY-MM-DD)
            evaluador: Nombre del evaluador
            puntaje: Puntaje de la evaluación
            observaciones: Observaciones sobre la evaluación
            
        Returns:
            Dict con los datos de la evaluación creada
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
            if not cursor.fetchone():
                raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            cursor.execute("""
                INSERT INTO Evaluaciones (id_empleado, fecha, evaluador, puntaje, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (id_empleado, fecha, evaluador, puntaje, observaciones))
            
            evaluacion_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM Evaluaciones WHERE id_evaluacion = ?", (evaluacion_id,))
            row = cursor.fetchone()
            
            return {
                'id_evaluacion': row['id_evaluacion'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'evaluador': row['evaluador'],
                'puntaje': row['puntaje'],
                'observaciones': row['observaciones']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Obtiene todas las evaluaciones."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_evaluacion, id_empleado, fecha, evaluador, puntaje, observaciones
                FROM Evaluaciones 
                ORDER BY fecha DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_evaluacion': row['id_evaluacion'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'evaluador': row['evaluador'],
                'puntaje': row['puntaje'],
                'observaciones': row['observaciones']
            } for row in rows]
    
    @staticmethod
    def get_by_id(evaluacion_id: int) -> Optional[Dict]:
        """Obtiene una evaluación por su ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_evaluacion, id_empleado, fecha, evaluador, puntaje, observaciones
                FROM Evaluaciones 
                WHERE id_evaluacion = ?
            """, (evaluacion_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_evaluacion': row['id_evaluacion'],
                    'id_empleado': row['id_empleado'],
                    'fecha': row['fecha'],
                    'evaluador': row['evaluador'],
                    'puntaje': row['puntaje'],
                    'observaciones': row['observaciones']
                }
            return None
    
    @staticmethod
    def get_by_empleado(empleado_id: int) -> List[Dict]:
        """Obtiene todas las evaluaciones de un empleado."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_evaluacion, id_empleado, fecha, evaluador, puntaje, observaciones
                FROM Evaluaciones 
                WHERE id_empleado = ?
                ORDER BY fecha DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [{
                'id_evaluacion': row['id_evaluacion'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'evaluador': row['evaluador'],
                'puntaje': row['puntaje'],
                'observaciones': row['observaciones']
            } for row in rows]
    
    @staticmethod
    def update(evaluacion_id: int, id_empleado: Optional[int] = None,
               fecha: Optional[str] = None,
               evaluador: Optional[str] = None,
               puntaje: Optional[int] = None,
               observaciones: Optional[str] = None) -> Optional[Dict]:
        """Actualiza una evaluación existente."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Evaluaciones WHERE id_evaluacion = ?", (evaluacion_id,))
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
            if evaluador is not None:
                updates.append("evaluador = ?")
                params.append(evaluador)
            if puntaje is not None:
                updates.append("puntaje = ?")
                params.append(puntaje)
            if observaciones is not None:
                updates.append("observaciones = ?")
                params.append(observaciones)
            
            if updates:
                params.append(evaluacion_id)
                query = f"UPDATE Evaluaciones SET {', '.join(updates)} WHERE id_evaluacion = ?"
                cursor.execute(query, params)
            
            cursor.execute("""
                SELECT id_evaluacion, id_empleado, fecha, evaluador, puntaje, observaciones
                FROM Evaluaciones 
                WHERE id_evaluacion = ?
            """, (evaluacion_id,))
            row = cursor.fetchone()
            
            return {
                'id_evaluacion': row['id_evaluacion'],
                'id_empleado': row['id_empleado'],
                'fecha': row['fecha'],
                'evaluador': row['evaluador'],
                'puntaje': row['puntaje'],
                'observaciones': row['observaciones']
            }
    
    @staticmethod
    def delete(evaluacion_id: int) -> bool:
        """Elimina una evaluación."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Evaluaciones WHERE id_evaluacion = ?", (evaluacion_id,))
            return cursor.rowcount > 0

