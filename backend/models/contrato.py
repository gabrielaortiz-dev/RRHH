"""
Modelo para manejar contratos en la base de datos.
"""
from database import get_db
from typing import Optional, Dict, List


class Contrato:
    """Clase para manejar operaciones de contratos."""
    
    @staticmethod
    def create(id_empleado: int, tipo_contrato: Optional[str] = None,
               fecha_inicio: Optional[str] = None,
               fecha_fin: Optional[str] = None,
               salario: Optional[float] = None,
               condiciones: Optional[str] = None) -> Dict:
        """
        Crea un nuevo contrato en la base de datos.
        
        Args:
            id_empleado: ID del empleado
            tipo_contrato: Tipo de contrato (Permanente, Temporal, Honorarios)
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            salario: Salario del contrato
            condiciones: Condiciones del contrato
            
        Returns:
            Dict con los datos del contrato creado
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar que el empleado existe
            cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
            if not cursor.fetchone():
                raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            # Insertar el nuevo contrato
            cursor.execute("""
                INSERT INTO Contratos (id_empleado, tipo_contrato, fecha_inicio,
                                     fecha_fin, salario, condiciones)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, salario, condiciones))
            
            contrato_id = cursor.lastrowid
            
            # Obtener el contrato creado
            cursor.execute("SELECT * FROM Contratos WHERE id_contrato = ?", (contrato_id,))
            row = cursor.fetchone()
            
            return {
                'id_contrato': row['id_contrato'],
                'id_empleado': row['id_empleado'],
                'tipo_contrato': row['tipo_contrato'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'salario': row['salario'],
                'condiciones': row['condiciones']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """
        Obtiene todos los contratos de la base de datos.
        
        Returns:
            Lista de diccionarios con los datos de los contratos
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_contrato, id_empleado, tipo_contrato, fecha_inicio,
                       fecha_fin, salario, condiciones
                FROM Contratos 
                ORDER BY fecha_inicio DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_contrato': row['id_contrato'],
                'id_empleado': row['id_empleado'],
                'tipo_contrato': row['tipo_contrato'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'salario': row['salario'],
                'condiciones': row['condiciones']
            } for row in rows]
    
    @staticmethod
    def get_by_id(contrato_id: int) -> Optional[Dict]:
        """
        Obtiene un contrato por su ID.
        
        Args:
            contrato_id: ID del contrato
            
        Returns:
            Dict con los datos del contrato o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_contrato, id_empleado, tipo_contrato, fecha_inicio,
                       fecha_fin, salario, condiciones
                FROM Contratos 
                WHERE id_contrato = ?
            """, (contrato_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_contrato': row['id_contrato'],
                    'id_empleado': row['id_empleado'],
                    'tipo_contrato': row['tipo_contrato'],
                    'fecha_inicio': row['fecha_inicio'],
                    'fecha_fin': row['fecha_fin'],
                    'salario': row['salario'],
                    'condiciones': row['condiciones']
                }
            return None
    
    @staticmethod
    def get_by_empleado(empleado_id: int) -> List[Dict]:
        """
        Obtiene todos los contratos de un empleado.
        
        Args:
            empleado_id: ID del empleado
            
        Returns:
            Lista de diccionarios con los datos de los contratos
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_contrato, id_empleado, tipo_contrato, fecha_inicio,
                       fecha_fin, salario, condiciones
                FROM Contratos 
                WHERE id_empleado = ?
                ORDER BY fecha_inicio DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [{
                'id_contrato': row['id_contrato'],
                'id_empleado': row['id_empleado'],
                'tipo_contrato': row['tipo_contrato'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'salario': row['salario'],
                'condiciones': row['condiciones']
            } for row in rows]
    
    @staticmethod
    def update(contrato_id: int, id_empleado: Optional[int] = None,
               tipo_contrato: Optional[str] = None,
               fecha_inicio: Optional[str] = None,
               fecha_fin: Optional[str] = None,
               salario: Optional[float] = None,
               condiciones: Optional[str] = None) -> Optional[Dict]:
        """
        Actualiza un contrato existente.
        
        Args:
            contrato_id: ID del contrato a actualizar
            id_empleado: Nuevo ID de empleado (opcional)
            tipo_contrato: Nuevo tipo de contrato (opcional)
            fecha_inicio: Nueva fecha de inicio (opcional)
            fecha_fin: Nueva fecha de fin (opcional)
            salario: Nuevo salario (opcional)
            condiciones: Nuevas condiciones (opcional)
            
        Returns:
            Dict con los datos actualizados del contrato o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar que el contrato existe
            cursor.execute("SELECT * FROM Contratos WHERE id_contrato = ?", (contrato_id,))
            contrato = cursor.fetchone()
            if not contrato:
                return None
            
            # Si se actualiza el id_empleado, verificar que existe
            if id_empleado is not None:
                cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
                if not cursor.fetchone():
                    raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            # Construir la query de actualización dinámicamente
            updates = []
            params = []
            
            if id_empleado is not None:
                updates.append("id_empleado = ?")
                params.append(id_empleado)
            
            if tipo_contrato is not None:
                updates.append("tipo_contrato = ?")
                params.append(tipo_contrato)
            
            if fecha_inicio is not None:
                updates.append("fecha_inicio = ?")
                params.append(fecha_inicio)
            
            if fecha_fin is not None:
                updates.append("fecha_fin = ?")
                params.append(fecha_fin)
            
            if salario is not None:
                updates.append("salario = ?")
                params.append(salario)
            
            if condiciones is not None:
                updates.append("condiciones = ?")
                params.append(condiciones)
            
            if updates:
                params.append(contrato_id)
                query = f"UPDATE Contratos SET {', '.join(updates)} WHERE id_contrato = ?"
                cursor.execute(query, params)
            
            # Obtener el contrato actualizado
            cursor.execute("""
                SELECT id_contrato, id_empleado, tipo_contrato, fecha_inicio,
                       fecha_fin, salario, condiciones
                FROM Contratos 
                WHERE id_contrato = ?
            """, (contrato_id,))
            row = cursor.fetchone()
            
            return {
                'id_contrato': row['id_contrato'],
                'id_empleado': row['id_empleado'],
                'tipo_contrato': row['tipo_contrato'],
                'fecha_inicio': row['fecha_inicio'],
                'fecha_fin': row['fecha_fin'],
                'salario': row['salario'],
                'condiciones': row['condiciones']
            }
    
    @staticmethod
    def delete(contrato_id: int) -> bool:
        """
        Elimina un contrato de la base de datos.
        
        Args:
            contrato_id: ID del contrato a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Contratos WHERE id_contrato = ?", (contrato_id,))
            
            return cursor.rowcount > 0

