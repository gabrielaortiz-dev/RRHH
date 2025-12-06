"""
Helper para crear notificaciones automáticas desde el backend
"""
from typing import Optional
from database import Database

class NotificationHelper:
    """
    Clase helper para crear notificaciones automáticas
    Centraliza la lógica de creación de notificaciones
    """
    
    @staticmethod
    def crear_notificacion(
        db: Database,
        usuario_id: int,
        tipo: str,
        titulo: str,
        mensaje: str,
        modulo: Optional[str] = None,
        modulo_id: Optional[str] = None,
        redirect_url: Optional[str] = None
    ) -> dict:
        """
        Crea una notificación en la base de datos
        
        Args:
            db: Instancia de Database
            usuario_id: ID del usuario destinatario
            tipo: Tipo de notificación (info, success, warning, error, etc.)
            titulo: Título de la notificación
            mensaje: Mensaje descriptivo
            modulo: Módulo relacionado (opcional)
            modulo_id: ID del elemento del módulo (opcional)
            redirect_url: URL de redirección (opcional)
        
        Returns:
            dict con los datos de la notificación creada
        """
        try:
            db.execute_query(
                """INSERT INTO Notificaciones 
                   (usuario_id, tipo, titulo, mensaje, modulo, modulo_id, redirect_url, is_read)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
                (usuario_id, tipo, titulo, mensaje, modulo, modulo_id, redirect_url)
            )
            
            # Obtener la notificación creada
            notificacion = db.fetch_one(
                "SELECT * FROM Notificaciones WHERE id = last_insert_rowid()"
            )
            
            return dict(notificacion) if notificacion else {}
        except Exception as e:
            print(f"Error al crear notificación: {str(e)}")
            return {}
    
    @staticmethod
    def notificar_empleado_creado(db: Database, usuario_id: int, nombre_empleado: str, empleado_id: int):
        """Notifica cuando se crea un nuevo empleado"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='success',
            titulo='Nuevo Empleado Registrado',
            mensaje=f'Se ha registrado exitosamente a {nombre_empleado} en el sistema',
            modulo='employees',
            modulo_id=str(empleado_id),
            redirect_url=f'/empleados/{empleado_id}'
        )
    
    @staticmethod
    def notificar_empleado_actualizado(db: Database, usuario_id: int, nombre_empleado: str, empleado_id: int):
        """Notifica cuando se actualiza un empleado"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='info',
            titulo='Empleado Actualizado',
            mensaje=f'Los datos de {nombre_empleado} han sido actualizados',
            modulo='employees',
            modulo_id=str(empleado_id),
            redirect_url=f'/empleados/{empleado_id}'
        )
    
    @staticmethod
    def notificar_contrato_creado(db: Database, usuario_id: int, nombre_empleado: str, contrato_id: int):
        """Notifica cuando se crea un contrato"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='success',
            titulo='Nuevo Contrato Generado',
            mensaje=f'Se ha generado un contrato para {nombre_empleado}',
            modulo='contracts',
            modulo_id=str(contrato_id),
            redirect_url=f'/contratos/{contrato_id}'
        )
    
    @staticmethod
    def notificar_vacaciones_solicitadas(db: Database, usuario_id: int, nombre_empleado: str, permiso_id: int):
        """Notifica cuando se solicitan vacaciones"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='approval',
            titulo='Nueva Solicitud de Vacaciones',
            mensaje=f'{nombre_empleado} ha solicitado vacaciones. Requiere aprobación.',
            modulo='vacations',
            modulo_id=str(permiso_id),
            redirect_url=f'/vacaciones'
        )
    
    @staticmethod
    def notificar_vacaciones_aprobadas(db: Database, usuario_id: int, fecha_inicio: str, fecha_fin: str):
        """Notifica cuando se aprueban vacaciones"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='success',
            titulo='Vacaciones Aprobadas',
            mensaje=f'Tu solicitud de vacaciones del {fecha_inicio} al {fecha_fin} ha sido aprobada',
            modulo='vacations',
            redirect_url='/vacaciones'
        )
    
    @staticmethod
    def notificar_vacaciones_rechazadas(db: Database, usuario_id: int, motivo: str):
        """Notifica cuando se rechazan vacaciones"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='warning',
            titulo='Solicitud de Vacaciones Rechazada',
            mensaje=f'Tu solicitud ha sido rechazada. Motivo: {motivo}',
            modulo='vacations',
            redirect_url='/vacaciones'
        )
    
    @staticmethod
    def notificar_nomina_generada(db: Database, usuario_id: int, mes: int, anio: int, total: float):
        """Notifica cuando se genera una nómina"""
        meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='success',
            titulo='Nómina Procesada',
            mensaje=f'Tu nómina de {meses[mes]} {anio} ha sido procesada. Total: L. {total:,.2f}',
            modulo='payroll',
            redirect_url='/nomina'
        )
    
    @staticmethod
    def notificar_evaluacion_creada(db: Database, usuario_id: int, puntaje: int):
        """Notifica cuando se crea una evaluación"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='info',
            titulo='Nueva Evaluación de Desempeño',
            mensaje=f'Has recibido una evaluación de desempeño. Puntaje: {puntaje}/100',
            modulo='evaluations',
            redirect_url='/evaluaciones'
        )
    
    @staticmethod
    def notificar_documento_subido(db: Database, usuario_id: int, nombre_documento: str):
        """Notifica cuando se sube un documento"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='success',
            titulo='Documento Subido',
            mensaje=f'Se ha subido el documento: {nombre_documento}',
            modulo='documents',
            redirect_url='/documentos'
        )
    
    @staticmethod
    def notificar_asistencia_registrada(db: Database, usuario_id: int, fecha: str, hora: str):
        """Notifica cuando se registra asistencia"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='info',
            titulo='Asistencia Registrada',
            mensaje=f'Tu asistencia del {fecha} a las {hora} ha sido registrada',
            modulo='attendance',
            redirect_url='/asistencias'
        )
    
    @staticmethod
    def notificar_contrato_por_vencer(db: Database, usuario_id: int, nombre_empleado: str, fecha_fin: str):
        """Notifica cuando un contrato está por vencer"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='warning',
            titulo='Contrato Próximo a Vencer',
            mensaje=f'El contrato de {nombre_empleado} vence el {fecha_fin}. Se requiere acción.',
            modulo='contracts',
            redirect_url='/contratos'
        )
    
    @staticmethod
    def notificar_departamento_creado(db: Database, usuario_id: int, nombre_dept: str):
        """Notifica cuando se crea un departamento"""
        return NotificationHelper.crear_notificacion(
            db=db,
            usuario_id=usuario_id,
            tipo='info',
            titulo='Nuevo Departamento Creado',
            mensaje=f'Se ha creado el departamento: {nombre_dept}',
            modulo='departments',
            redirect_url='/departments'
        )

