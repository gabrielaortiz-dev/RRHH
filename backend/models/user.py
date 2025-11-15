"""
Modelo para manejar usuarios en la base de datos.
"""
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, List
from datetime import datetime


class User:
    """Clase para manejar operaciones de usuarios."""
    
    @staticmethod
    def create(username: str, email: str, password: str) -> Dict:
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            username: Nombre de usuario único
            email: Email único del usuario
            password: Contraseña en texto plano (se hasheará)
            
        Returns:
            Dict con los datos del usuario creado
            
        Raises:
            ValueError: Si el username o email ya existen
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar si el username ya existe
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise ValueError(f"El usuario '{username}' ya existe")
            
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise ValueError(f"El email '{email}' ya está registrado")
            
            # Hashear la contraseña
            password_hash = generate_password_hash(password)
            
            # Insertar el nuevo usuario
            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            
            user_id = cursor.lastrowid
            
            # Obtener el usuario creado
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            return {
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'created_at': row['created_at']
            }
    
    @staticmethod
    def get_all() -> List[Dict]:
        """
        Obtiene todos los usuarios de la base de datos.
        
        Returns:
            Lista de diccionarios con los datos de los usuarios
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'created_at': row['created_at']
            } for row in rows]
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con los datos del usuario o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'created_at': row['created_at']
                }
            return None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Dict]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Dict con los datos del usuario (incluyendo password hash) o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'password': row['password'],
                    'created_at': row['created_at']
                }
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Dict con los datos del usuario o None si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'created_at': row['created_at']
                }
            return None
    
    @staticmethod
    def update(user_id: int, username: Optional[str] = None, 
               email: Optional[str] = None, password: Optional[str] = None) -> Optional[Dict]:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar
            username: Nuevo nombre de usuario (opcional)
            email: Nuevo email (opcional)
            password: Nueva contraseña en texto plano (opcional, se hasheará)
            
        Returns:
            Dict con los datos actualizados del usuario o None si no existe
            
        Raises:
            ValueError: Si el username o email ya existen en otro usuario
        """
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar que el usuario existe
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                return None
            
            # Verificar duplicados si se está actualizando username
            if username and username != user['username']:
                cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
                if cursor.fetchone():
                    raise ValueError(f"El usuario '{username}' ya existe")
            
            # Verificar duplicados si se está actualizando email
            if email and email != user['email']:
                cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
                if cursor.fetchone():
                    raise ValueError(f"El email '{email}' ya está registrado")
            
            # Construir la query de actualización dinámicamente
            updates = []
            params = []
            
            if username:
                updates.append("username = ?")
                params.append(username)
            
            if email:
                updates.append("email = ?")
                params.append(email)
            
            if password:
                updates.append("password = ?")
                params.append(generate_password_hash(password))
            
            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            # Obtener el usuario actualizado
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            return {
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'created_at': row['created_at']
            }
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """
        Elimina un usuario de la base de datos.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            return cursor.rowcount > 0
    
    @staticmethod
    def verify_password(user: Dict, password: str) -> bool:
        """
        Verifica si una contraseña es correcta para un usuario.
        
        Args:
            user: Dict con los datos del usuario (debe incluir 'password')
            password: Contraseña en texto plano a verificar
            
        Returns:
            True si la contraseña es correcta, False en caso contrario
        """
        return check_password_hash(user['password'], password)

