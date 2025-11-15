"""
Modelo para manejar nómina en la base de datos.
"""
from database import get_db
from typing import Optional, Dict, List


class Nomina:
    """Clase para manejar operaciones de nómina."""
    
    @staticmethod
    def create(id_empleado: int, mes: Optional[int] = None,
               anio: Optional[int] = None,
               salario_base: Optional[float] = None,
               bonificaciones: Optional[float] = None,
               deducciones: Optional[float] = None,
               salario_neto: Optional[float] = None,
               fecha_pago: Optional[str] = None) -> Dict:
        """
        Crea un nuevo registro de nómina.
        
        Args:
            id_empleado: ID del empleado
            mes: Mes del pago (1-12)
            anio: Año del pago
            salario_base: Salario base
            bonificaciones: Bonificaciones
            deducciones: Deducciones
            salario_neto: Salario neto
            fecha_pago: Fecha de pago (YYYY-MM-DD)
            
        Returns:
            Dict con los datos del registro de nómina creado
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (id_empleado,))
            if not cursor.fetchone():
                raise ValueError(f"El empleado con ID {id_empleado} no existe")
            
            cursor.execute("""
                INSERT INTO Nomina (id_empleado, mes, anio, salario_base, bonificaciones,
                                  deducciones, salario_neto, fecha_pago)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_empleado, mes, anio, salario_base, bonificaciones, 
                  deducciones, salario_neto, fecha_pago))
            
            nomina_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM Nomina WHERE id_nomina = ?", (nomina_id,))
            row = cursor.fetchone()
            
            return {
                'id_nomina': row['id_nomina'],
                'id_empleado': row['id_empleado'],
                'mes': row['mes'],
                'anio': row['anio'],
                'salario_base': row['salario_base'],
                'bonificaciones': row['bonificaciones'],
                'deducciones': row['deducciones'],
                'salario_neto': row['salario_neto'],
                'fecha_pago': row['fecha_pago']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Obtiene todos los registros de nómina."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_nomina, id_empleado, mes, anio, salario_base, bonificaciones,
                       deducciones, salario_neto, fecha_pago
                FROM Nomina 
                ORDER BY anio DESC, mes DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_nomina': row['id_nomina'],
                'id_empleado': row['id_empleado'],
                'mes': row['mes'],
                'anio': row['anio'],
                'salario_base': row['salario_base'],
                'bonificaciones': row['bonificaciones'],
                'deducciones': row['deducciones'],
                'salario_neto': row['salario_neto'],
                'fecha_pago': row['fecha_pago']
            } for row in rows]
    
    @staticmethod
    def get_by_id(nomina_id: int) -> Optional[Dict]:
        """Obtiene un registro de nómina por su ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_nomina, id_empleado, mes, anio, salario_base, bonificaciones,
                       deducciones, salario_neto, fecha_pago
                FROM Nomina 
                WHERE id_nomina = ?
            """, (nomina_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_nomina': row['id_nomina'],
                    'id_empleado': row['id_empleado'],
                    'mes': row['mes'],
                    'anio': row['anio'],
                    'salario_base': row['salario_base'],
                    'bonificaciones': row['bonificaciones'],
                    'deducciones': row['deducciones'],
                    'salario_neto': row['salario_neto'],
                    'fecha_pago': row['fecha_pago']
                }
            return None
    
    @staticmethod
    def get_by_empleado(empleado_id: int) -> List[Dict]:
        """Obtiene todos los registros de nómina de un empleado."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_nomina, id_empleado, mes, anio, salario_base, bonificaciones,
                       deducciones, salario_neto, fecha_pago
                FROM Nomina 
                WHERE id_empleado = ?
                ORDER BY anio DESC, mes DESC
            """, (empleado_id,))
            rows = cursor.fetchall()
            
            return [{
                'id_nomina': row['id_nomina'],
                'id_empleado': row['id_empleado'],
                'mes': row['mes'],
                'anio': row['anio'],
                'salario_base': row['salario_base'],
                'bonificaciones': row['bonificaciones'],
                'deducciones': row['deducciones'],
                'salario_neto': row['salario_neto'],
                'fecha_pago': row['fecha_pago']
            } for row in rows]
    
    @staticmethod
    def update(nomina_id: int, id_empleado: Optional[int] = None,
               mes: Optional[int] = None,
               anio: Optional[int] = None,
               salario_base: Optional[float] = None,
               bonificaciones: Optional[float] = None,
               deducciones: Optional[float] = None,
               salario_neto: Optional[float] = None,
               fecha_pago: Optional[str] = None) -> Optional[Dict]:
        """Actualiza un registro de nómina existente."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM Nomina WHERE id_nomina = ?", (nomina_id,))
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
            if mes is not None:
                updates.append("mes = ?")
                params.append(mes)
            if anio is not None:
                updates.append("anio = ?")
                params.append(anio)
            if salario_base is not None:
                updates.append("salario_base = ?")
                params.append(salario_base)
            if bonificaciones is not None:
                updates.append("bonificaciones = ?")
                params.append(bonificaciones)
            if deducciones is not None:
                updates.append("deducciones = ?")
                params.append(deducciones)
            if salario_neto is not None:
                updates.append("salario_neto = ?")
                params.append(salario_neto)
            if fecha_pago is not None:
                updates.append("fecha_pago = ?")
                params.append(fecha_pago)
            
            if updates:
                params.append(nomina_id)
                query = f"UPDATE Nomina SET {', '.join(updates)} WHERE id_nomina = ?"
                cursor.execute(query, params)
            
            cursor.execute("""
                SELECT id_nomina, id_empleado, mes, anio, salario_base, bonificaciones,
                       deducciones, salario_neto, fecha_pago
                FROM Nomina 
                WHERE id_nomina = ?
            """, (nomina_id,))
            row = cursor.fetchone()
            
            return {
                'id_nomina': row['id_nomina'],
                'id_empleado': row['id_empleado'],
                'mes': row['mes'],
                'anio': row['anio'],
                'salario_base': row['salario_base'],
                'bonificaciones': row['bonificaciones'],
                'deducciones': row['deducciones'],
                'salario_neto': row['salario_neto'],
                'fecha_pago': row['fecha_pago']
            }
    
    @staticmethod
    def delete(nomina_id: int) -> bool:
        """Elimina un registro de nómina."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Nomina WHERE id_nomina = ?", (nomina_id,))
            return cursor.rowcount > 0

