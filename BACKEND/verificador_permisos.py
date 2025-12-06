"""
Módulo de Verificación de Permisos
===================================

Este módulo proporciona funciones y decoradores para verificar permisos
de usuarios en el sistema de RRHH.

Uso:
----
```python
from verificador_permisos import verificar_permiso, require_permission

# Verificar permiso manualmente
if verificar_permiso(usuario_id, 'empleados.crear'):
    # Permitir acción
    pass

# Usar decorador en FastAPI
@app.get("/empleados")
@require_permission('empleados.ver')
async def listar_empleados(usuario_id: int):
    # Esta ruta requiere permiso 'empleados.ver'
    pass
```

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
from functools import wraps
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status


class VerificadorPermisos:
    """Clase para verificar y gestionar permisos de usuarios"""
    
    def __init__(self, db_path: str = 'rrhh.db'):
        """
        Inicializa el verificador con la ruta de la BD
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn
        
    def verificar_permiso(self, usuario_id: int, codigo_permiso: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico
        
        Args:
            usuario_id: ID del usuario
            codigo_permiso: Código del permiso (ej: 'empleados.crear')
        
        Returns:
            bool: True si tiene el permiso, False si no
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar permiso a través de roles
            cursor.execute("""
                SELECT COUNT(*) as tiene_permiso
                FROM Permisos p
                INNER JOIN Roles_Permisos rp ON p.id_permiso = rp.id_permiso
                INNER JOIN Usuarios_Roles ur ON rp.id_rol = ur.id_rol
                WHERE ur.usuario_id = ? 
                  AND p.codigo = ? 
                  AND ur.activo = 1
                  AND rp.concedido = 1
                  AND p.activo = 1
            """, (usuario_id, codigo_permiso))
            
            resultado = cursor.fetchone()
            tiene_permiso_rol = resultado['tiene_permiso'] > 0
            
            # Verificar permisos especiales del usuario
            cursor.execute("""
                SELECT concedido
                FROM Usuarios_Permisos up
                INNER JOIN Permisos p ON up.id_permiso = p.id_permiso
                WHERE up.usuario_id = ? 
                  AND p.codigo = ?
                  AND (up.fecha_expiracion IS NULL OR up.fecha_expiracion > datetime('now'))
            """, (usuario_id, codigo_permiso))
            
            permiso_especial = cursor.fetchone()
            
            # Si tiene permiso especial, ese prevalece
            if permiso_especial:
                return permiso_especial['concedido'] == 1
                
            return tiene_permiso_rol
            
        finally:
            conn.close()
            
    def obtener_permisos_usuario(self, usuario_id: int) -> List[Dict]:
        """
        Obtiene todos los permisos de un usuario
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Lista de diccionarios con información de permisos
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT DISTINCT 
                    p.codigo,
                    p.nombre,
                    p.descripcion,
                    p.modulo,
                    p.accion
                FROM Permisos p
                INNER JOIN Roles_Permisos rp ON p.id_permiso = rp.id_permiso
                INNER JOIN Usuarios_Roles ur ON rp.id_rol = ur.id_rol
                WHERE ur.usuario_id = ? 
                  AND ur.activo = 1
                  AND rp.concedido = 1
                  AND p.activo = 1
                ORDER BY p.modulo, p.nombre
            """, (usuario_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
            
    def obtener_rol_usuario(self, usuario_id: int) -> Optional[Dict]:
        """
        Obtiene el rol principal del usuario
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Diccionario con información del rol o None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    r.id_rol,
                    r.nombre,
                    r.descripcion,
                    r.nivel_acceso
                FROM Roles r
                INNER JOIN Usuarios_Roles ur ON r.id_rol = ur.id_rol
                WHERE ur.usuario_id = ? 
                  AND ur.es_principal = 1
                  AND ur.activo = 1
                LIMIT 1
            """, (usuario_id,))
            
            resultado = cursor.fetchone()
            return dict(resultado) if resultado else None
            
        finally:
            conn.close()
            
    def verificar_nivel_acceso(self, usuario_id: int, nivel_minimo: int) -> bool:
        """
        Verifica si el usuario tiene un nivel de acceso mínimo
        
        Args:
            usuario_id: ID del usuario
            nivel_minimo: Nivel de acceso mínimo requerido (10-100)
        
        Returns:
            bool: True si cumple con el nivel mínimo
        """
        rol = self.obtener_rol_usuario(usuario_id)
        if not rol:
            return False
        return rol['nivel_acceso'] >= nivel_minimo
        
    def es_super_admin(self, usuario_id: int) -> bool:
        """
        Verifica si el usuario es Super Admin
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            bool: True si es Super Admin
        """
        return self.verificar_nivel_acceso(usuario_id, 100)
        
    def es_gerente(self, usuario_id: int) -> bool:
        """
        Verifica si el usuario es Gerente o superior
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            bool: True si es Gerente o superior
        """
        return self.verificar_nivel_acceso(usuario_id, 80)
        
    def es_supervisor(self, usuario_id: int) -> bool:
        """
        Verifica si el usuario es Supervisor o superior
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            bool: True si es Supervisor o superior
        """
        return self.verificar_nivel_acceso(usuario_id, 60)
        
    def obtener_permisos_por_modulo(self, usuario_id: int) -> Dict[str, List[str]]:
        """
        Obtiene los permisos del usuario agrupados por módulo
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Diccionario con módulos como clave y lista de permisos como valor
        """
        permisos = self.obtener_permisos_usuario(usuario_id)
        
        permisos_por_modulo = {}
        for permiso in permisos:
            modulo = permiso['modulo']
            if modulo not in permisos_por_modulo:
                permisos_por_modulo[modulo] = []
            permisos_por_modulo[modulo].append(permiso['codigo'])
            
        return permisos_por_modulo
        
    def asignar_rol(self, usuario_id: int, rol_id: int, admin_id: Optional[int] = None, 
                   motivo: str = "Asignación de rol") -> bool:
        """
        Asigna un rol a un usuario
        
        Args:
            usuario_id: ID del usuario
            rol_id: ID del rol a asignar
            admin_id: ID del administrador que realiza la asignación
            motivo: Motivo de la asignación
        
        Returns:
            bool: True si se asignó correctamente
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Desactivar roles principales anteriores
            cursor.execute("""
                UPDATE Usuarios_Roles
                SET activo = 0
                WHERE usuario_id = ? AND es_principal = 1
            """, (usuario_id,))
            
            # Obtener rol anterior para historial
            cursor.execute("""
                SELECT id_rol FROM Usuarios_Roles
                WHERE usuario_id = ? AND es_principal = 1
                ORDER BY fecha_asignacion DESC
                LIMIT 1
            """, (usuario_id,))
            
            rol_anterior = cursor.fetchone()
            rol_anterior_id = rol_anterior['id_rol'] if rol_anterior else None
            
            # Asignar nuevo rol
            cursor.execute("""
                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                VALUES (?, ?, 1, 1)
            """, (usuario_id, rol_id))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO Historial_Roles 
                (usuario_id, id_rol_anterior, id_rol_nuevo, motivo, realizado_por)
                VALUES (?, ?, ?, ?, ?)
            """, (usuario_id, rol_anterior_id, rol_id, motivo, admin_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error al asignar rol: {e}")
            return False
        finally:
            conn.close()
            
    def revocar_rol(self, usuario_id: int, admin_id: Optional[int] = None,
                   motivo: str = "Revocación de rol") -> bool:
        """
        Revoca el rol principal de un usuario
        
        Args:
            usuario_id: ID del usuario
            admin_id: ID del administrador que realiza la revocación
            motivo: Motivo de la revocación
        
        Returns:
            bool: True si se revocó correctamente
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener rol actual
            cursor.execute("""
                SELECT id_rol FROM Usuarios_Roles
                WHERE usuario_id = ? AND es_principal = 1 AND activo = 1
                LIMIT 1
            """, (usuario_id,))
            
            rol_actual = cursor.fetchone()
            
            if not rol_actual:
                return False
                
            rol_actual_id = rol_actual['id_rol']
            
            # Desactivar rol
            cursor.execute("""
                UPDATE Usuarios_Roles
                SET activo = 0
                WHERE usuario_id = ? AND es_principal = 1
            """, (usuario_id,))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO Historial_Roles 
                (usuario_id, id_rol_anterior, id_rol_nuevo, motivo, realizado_por)
                VALUES (?, ?, NULL, ?, ?)
            """, (usuario_id, rol_actual_id, motivo, admin_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error al revocar rol: {e}")
            return False
        finally:
            conn.close()


# Instancia global del verificador
_verificador = VerificadorPermisos()


# Funciones de conveniencia para uso directo
def verificar_permiso(usuario_id: int, codigo_permiso: str) -> bool:
    """Función de conveniencia para verificar un permiso"""
    return _verificador.verificar_permiso(usuario_id, codigo_permiso)


def obtener_permisos_usuario(usuario_id: int) -> List[Dict]:
    """Función de conveniencia para obtener permisos de un usuario"""
    return _verificador.obtener_permisos_usuario(usuario_id)


def obtener_rol_usuario(usuario_id: int) -> Optional[Dict]:
    """Función de conveniencia para obtener el rol de un usuario"""
    return _verificador.obtener_rol_usuario(usuario_id)


def es_super_admin(usuario_id: int) -> bool:
    """Función de conveniencia para verificar si es Super Admin"""
    return _verificador.es_super_admin(usuario_id)


def es_gerente(usuario_id: int) -> bool:
    """Función de conveniencia para verificar si es Gerente"""
    return _verificador.es_gerente(usuario_id)


def es_supervisor(usuario_id: int) -> bool:
    """Función de conveniencia para verificar si es Supervisor"""
    return _verificador.es_supervisor(usuario_id)


# Decoradores para FastAPI
def require_permission(codigo_permiso: str):
    """
    Decorador para requerir un permiso específico en una ruta de FastAPI
    
    Args:
        codigo_permiso: Código del permiso requerido
    
    Usage:
        @app.get("/empleados")
        @require_permission('empleados.ver')
        async def listar_empleados(usuario_id: int):
            # Esta ruta requiere permiso 'empleados.ver'
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener usuario_id de los argumentos
            usuario_id = kwargs.get('usuario_id') or kwargs.get('current_user_id')
            
            if not usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if not verificar_permiso(usuario_id, codigo_permiso):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso denegado. Se requiere: {codigo_permiso}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_level(nivel_minimo: int):
    """
    Decorador para requerir un nivel de acceso mínimo
    
    Args:
        nivel_minimo: Nivel de acceso mínimo requerido (10-100)
    
    Usage:
        @app.delete("/usuarios/{user_id}")
        @require_level(100)  # Solo Super Admin
        async def eliminar_usuario(user_id: int, usuario_id: int):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            usuario_id = kwargs.get('usuario_id') or kwargs.get('current_user_id')
            
            if not usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if not _verificador.verificar_nivel_acceso(usuario_id, nivel_minimo):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Nivel de acceso insuficiente. Se requiere nivel {nivel_minimo}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_super_admin(func):
    """
    Decorador para requerir permisos de Super Admin
    
    Usage:
        @app.post("/configuracion")
        @require_super_admin
        async def configurar_sistema(usuario_id: int):
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        usuario_id = kwargs.get('usuario_id') or kwargs.get('current_user_id')
        
        if not usuario_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        if not es_super_admin(usuario_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de Super Admin"
            )
        
        return await func(*args, **kwargs)
    return wrapper


# Ejemplo de uso
if __name__ == "__main__":
    # Prueba del verificador
    print("="*70)
    print("PRUEBA DEL VERIFICADOR DE PERMISOS")
    print("="*70)
    
    # Ejemplo de verificación (usar un usuario_id real)
    usuario_test = 1
    
    print(f"\nUsuario ID: {usuario_test}")
    
    # Obtener rol
    rol = obtener_rol_usuario(usuario_test)
    if rol:
        print(f"\nRol: {rol['nombre']}")
        print(f"Nivel de Acceso: {rol['nivel_acceso']}")
    else:
        print("\nNo tiene rol asignado")
    
    # Obtener permisos
    permisos = obtener_permisos_usuario(usuario_test)
    print(f"\nPermisos totales: {len(permisos)}")
    
    # Agrupar por módulo
    permisos_por_modulo = _verificador.obtener_permisos_por_modulo(usuario_test)
    print("\nPermisos por módulo:")
    for modulo, permisos in permisos_por_modulo.items():
        print(f"  • {modulo}: {len(permisos)} permiso(s)")
    
    # Verificar permisos específicos
    print("\nVerificación de permisos específicos:")
    permisos_a_verificar = [
        'empleados.ver',
        'empleados.crear',
        'usuarios.crear',
        'sistema.configurar'
    ]
    
    for permiso in permisos_a_verificar:
        tiene = verificar_permiso(usuario_test, permiso)
        simbolo = "✅" if tiene else "❌"
        print(f"  {simbolo} {permiso}")
    
    print("\n" + "="*70)

