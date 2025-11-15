"""
Modelo para manejar empleados en la base de datos (tabla Empleados).
"""
from database import get_db
from typing import Optional, Dict, List


class Empleado:
    """Clase para manejar operaciones de empleados (tabla Empleados)."""
    
    @staticmethod
    def create(nombre: str, apellido: str, 
               fecha_nacimiento: Optional[str] = None,
               genero: Optional[str] = None,
               estado_civil: Optional[str] = None,
               direccion: Optional[str] = None,
               telefono: Optional[str] = None,
               correo: Optional[str] = None,
               fecha_ingreso: Optional[str] = None,
               estado: Optional[str] = None,
               id_departamento: Optional[int] = None,
               id_puesto: Optional[int] = None) -> Dict:
        """
        Crea un nuevo empleado en la base de datos.
        
        Args:
            nombre: Nombre del empleado
            apellido: Apellido del empleado
            fecha_nacimiento: Fecha de nacimiento (YYYY-MM-DD)
            genero: Género del empleado
            estado_civil: Estado civil
            direccion: Dirección del empleado
            telefono: Teléfono
            correo: Correo electrónico
            fecha_ingreso: Fecha de ingreso (YYYY-MM-DD)
            estado: Estado del empleado (Activo, Suspendido, Retirado)
            id_departamento: ID del departamento
            id_puesto: ID del puesto
            
        Returns:
            Dict con los datos del empleado creado
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Insertar el nuevo empleado
            cursor.execute("""
                INSERT INTO Empleados (nombre, apellido, fecha_nacimiento, genero,
                                     estado_civil, direccion, telefono, correo,
                                     fecha_ingreso, estado, id_departamento, id_puesto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, apellido, fecha_nacimiento, genero, estado_civil,
                  direccion, telefono, correo, fecha_ingreso, estado,
                  id_departamento, id_puesto))
            
            empleado_id = cursor.lastrowid
            
            # Obtener el empleado creado
            cursor.execute("SELECT * FROM Empleados WHERE id_empleado = ?", (empleado_id,))
            row = cursor.fetchone()
            
            return {
                'id_empleado': row['id_empleado'],
                'nombre': row['nombre'],
                'apellido': row['apellido'],
                'fecha_nacimiento': row['fecha_nacimiento'],
                'genero': row['genero'],
                'estado_civil': row['estado_civil'],
                'direccion': row['direccion'],
                'telefono': row['telefono'],
                'correo': row['correo'],
                'fecha_ingreso': row['fecha_ingreso'],
                'estado': row['estado'],
                'id_departamento': row['id_departamento'],
                'id_puesto': row['id_puesto']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """
        Obtiene todos los empleados de la base de datos.
        
        Returns:
            Lista de diccionarios con los datos de los empleados
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_empleado, nombre, apellido, fecha_nacimiento, genero,
                       estado_civil, direccion, telefono, correo, fecha_ingreso,
                       estado, id_departamento, id_puesto
                FROM Empleados 
                ORDER BY fecha_ingreso DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id_empleado': row['id_empleado'],
                'nombre': row['nombre'],
                'apellido': row['apellido'],
                'fecha_nacimiento': row['fecha_nacimiento'],
                'genero': row['genero'],
                'estado_civil': row['estado_civil'],
                'direccion': row['direccion'],
                'telefono': row['telefono'],
                'correo': row['correo'],
                'fecha_ingreso': row['fecha_ingreso'],
                'estado': row['estado'],
                'id_departamento': row['id_departamento'],
                'id_puesto': row['id_puesto']
            } for row in rows]
    
    @staticmethod
    def get_by_id(empleado_id: int) -> Optional[Dict]:
        """
        Obtiene un empleado por su ID.
        
        Args:
            empleado_id: ID del empleado
            
        Returns:
            Dict con los datos del empleado o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_empleado, nombre, apellido, fecha_nacimiento, genero,
                       estado_civil, direccion, telefono, correo, fecha_ingreso,
                       estado, id_departamento, id_puesto
                FROM Empleados 
                WHERE id_empleado = ?
            """, (empleado_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_empleado': row['id_empleado'],
                    'nombre': row['nombre'],
                    'apellido': row['apellido'],
                    'fecha_nacimiento': row['fecha_nacimiento'],
                    'genero': row['genero'],
                    'estado_civil': row['estado_civil'],
                    'direccion': row['direccion'],
                    'telefono': row['telefono'],
                    'correo': row['correo'],
                    'fecha_ingreso': row['fecha_ingreso'],
                    'estado': row['estado'],
                    'id_departamento': row['id_departamento'],
                    'id_puesto': row['id_puesto']
                }
            return None
    
    @staticmethod
    def update(empleado_id: int, nombre: Optional[str] = None,
               apellido: Optional[str] = None,
               fecha_nacimiento: Optional[str] = None,
               genero: Optional[str] = None,
               estado_civil: Optional[str] = None,
               direccion: Optional[str] = None,
               telefono: Optional[str] = None,
               correo: Optional[str] = None,
               fecha_ingreso: Optional[str] = None,
               estado: Optional[str] = None,
               id_departamento: Optional[int] = None,
               id_puesto: Optional[int] = None) -> Optional[Dict]:
        """
        Actualiza un empleado existente.
        
        Args:
            empleado_id: ID del empleado a actualizar
            nombre: Nuevo nombre (opcional)
            apellido: Nuevo apellido (opcional)
            fecha_nacimiento: Nueva fecha de nacimiento (opcional)
            genero: Nuevo género (opcional)
            estado_civil: Nuevo estado civil (opcional)
            direccion: Nueva dirección (opcional)
            telefono: Nuevo teléfono (opcional)
            correo: Nuevo correo (opcional)
            fecha_ingreso: Nueva fecha de ingreso (opcional)
            estado: Nuevo estado (opcional)
            id_departamento: Nuevo ID de departamento (opcional)
            id_puesto: Nuevo ID de puesto (opcional)
            
        Returns:
            Dict con los datos actualizados del empleado o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar que el empleado existe
            cursor.execute("SELECT * FROM Empleados WHERE id_empleado = ?", (empleado_id,))
            empleado = cursor.fetchone()
            if not empleado:
                return None
            
            # Construir la query de actualización dinámicamente
            updates = []
            params = []
            
            if nombre is not None:
                updates.append("nombre = ?")
                params.append(nombre)
            
            if apellido is not None:
                updates.append("apellido = ?")
                params.append(apellido)
            
            if fecha_nacimiento is not None:
                updates.append("fecha_nacimiento = ?")
                params.append(fecha_nacimiento)
            
            if genero is not None:
                updates.append("genero = ?")
                params.append(genero)
            
            if estado_civil is not None:
                updates.append("estado_civil = ?")
                params.append(estado_civil)
            
            if direccion is not None:
                updates.append("direccion = ?")
                params.append(direccion)
            
            if telefono is not None:
                updates.append("telefono = ?")
                params.append(telefono)
            
            if correo is not None:
                updates.append("correo = ?")
                params.append(correo)
            
            if fecha_ingreso is not None:
                updates.append("fecha_ingreso = ?")
                params.append(fecha_ingreso)
            
            if estado is not None:
                updates.append("estado = ?")
                params.append(estado)
            
            if id_departamento is not None:
                updates.append("id_departamento = ?")
                params.append(id_departamento)
            
            if id_puesto is not None:
                updates.append("id_puesto = ?")
                params.append(id_puesto)
            
            if updates:
                params.append(empleado_id)
                query = f"UPDATE Empleados SET {', '.join(updates)} WHERE id_empleado = ?"
                cursor.execute(query, params)
            
            # Obtener el empleado actualizado
            cursor.execute("""
                SELECT id_empleado, nombre, apellido, fecha_nacimiento, genero,
                       estado_civil, direccion, telefono, correo, fecha_ingreso,
                       estado, id_departamento, id_puesto
                FROM Empleados 
                WHERE id_empleado = ?
            """, (empleado_id,))
            row = cursor.fetchone()
            
            return {
                'id_empleado': row['id_empleado'],
                'nombre': row['nombre'],
                'apellido': row['apellido'],
                'fecha_nacimiento': row['fecha_nacimiento'],
                'genero': row['genero'],
                'estado_civil': row['estado_civil'],
                'direccion': row['direccion'],
                'telefono': row['telefono'],
                'correo': row['correo'],
                'fecha_ingreso': row['fecha_ingreso'],
                'estado': row['estado'],
                'id_departamento': row['id_departamento'],
                'id_puesto': row['id_puesto']
            }
    
    @staticmethod
    def delete(empleado_id: int) -> bool:
        """
        Elimina un empleado de la base de datos.
        
        Args:
            empleado_id: ID del empleado a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Empleados WHERE id_empleado = ?", (empleado_id,))
            
            return cursor.rowcount > 0

