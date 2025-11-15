import { Injectable, signal, computed } from '@angular/core';
import {
  Notification,
  NotificationConfig,
  NotificationType,
  NotificationModule,
  CreateNotificationParams,
  NotificationStats
} from '../models/notification.model';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  // Señales reactivas
  private notifications = signal<Notification[]>([]);
  private configs = signal<NotificationConfig[]>([]);

  // Señales computadas
  public unreadCount = computed(() => 
    this.notifications().filter(n => !n.isRead).length
  );

  public unreadNotifications = computed(() =>
    this.notifications()
      .filter(n => !n.isRead)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  );

  public allNotifications = computed(() =>
    this.notifications()
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  );

  constructor() {
    try {
      this.loadFromStorage();
      this.initializeDefaultConfigs();
    } catch (error) {
      console.error('Error initializing notification service:', error);
      // Inicializar con valores vacíos si hay error
      this.notifications.set([]);
      this.configs.set([]);
      this.initializeDefaultConfigs();
    }
  }

  /**
   * Carga las notificaciones desde localStorage
   */
  private loadFromStorage(): void {
    try {
      const savedNotifications = localStorage.getItem('notifications');
      const savedConfigs = localStorage.getItem('notificationConfigs');

      if (savedNotifications) {
        const parsed = JSON.parse(savedNotifications);
        // Convertir las fechas de string a Date
        const notifications = parsed.map((n: any) => ({
          ...n,
          createdAt: new Date(n.createdAt),
          readAt: n.readAt ? new Date(n.readAt) : undefined
        }));
        this.notifications.set(notifications);
      }

      if (savedConfigs) {
        this.configs.set(JSON.parse(savedConfigs));
      }
    } catch (error) {
      console.error('Error cargando notificaciones:', error);
    }
  }

  /**
   * Guarda las notificaciones en localStorage
   */
  private saveToStorage(): void {
    try {
      localStorage.setItem('notifications', JSON.stringify(this.notifications()));
      localStorage.setItem('notificationConfigs', JSON.stringify(this.configs()));
    } catch (error) {
      console.error('Error guardando notificaciones:', error);
    }
  }

  /**
   * Inicializa configuraciones por defecto para usuarios existentes
   */
  private initializeDefaultConfigs(): void {
    const users = ['admin@rrhh.com', 'usuario@rrhh.com'];
    const existingConfigs = this.configs();

    users.forEach(userId => {
      if (!existingConfigs.find(c => c.userId === userId)) {
        const defaultConfig: NotificationConfig = {
          userId,
          emailNotifications: false,
          enabledTypes: Object.values(NotificationType),
          enabledModules: Object.values(NotificationModule),
          email: userId
        };
        this.configs.update(configs => [...configs, defaultConfig]);
      }
    });

    this.saveToStorage();
  }

  /**
   * Crea una o varias notificaciones
   */
  createNotification(params: CreateNotificationParams): Notification[] {
    const userIds = Array.isArray(params.userId) ? params.userId : [params.userId];
    const createdNotifications: Notification[] = [];

    userIds.forEach(userId => {
      // Verificar si el usuario tiene habilitado este tipo de notificación
      const config = this.getUserConfig(userId);
      if (!this.shouldReceiveNotification(userId, params.type, params.module)) {
        console.log(`Usuario ${userId} no recibirá notificación tipo ${params.type}`);
        return;
      }

      const notification: Notification = {
        id: this.generateId(),
        userId,
        type: params.type,
        title: params.title,
        message: params.message,
        module: params.module,
        moduleId: params.moduleId,
        redirectUrl: params.redirectUrl,
        isRead: false,
        createdAt: new Date(),
        metadata: params.metadata
      };

      createdNotifications.push(notification);
    });

    if (createdNotifications.length > 0) {
      this.notifications.update(notifications => [...notifications, ...createdNotifications]);
      this.saveToStorage();
    }

    return createdNotifications;
  }

  /**
   * Marca una notificación como leída
   */
  markAsRead(notificationId: string): void {
    this.notifications.update(notifications =>
      notifications.map(n =>
        n.id === notificationId
          ? { ...n, isRead: true, readAt: new Date() }
          : n
      )
    );
    this.saveToStorage();
  }

  /**
   * Marca todas las notificaciones como leídas para un usuario
   */
  markAllAsRead(userId: string): void {
    this.notifications.update(notifications =>
      notifications.map(n =>
        n.userId === userId && !n.isRead
          ? { ...n, isRead: true, readAt: new Date() }
          : n
      )
    );
    this.saveToStorage();
  }

  /**
   * Elimina una notificación
   */
  deleteNotification(notificationId: string): void {
    this.notifications.update(notifications =>
      notifications.filter(n => n.id !== notificationId)
    );
    this.saveToStorage();
  }

  /**
   * Elimina todas las notificaciones leídas de un usuario
   */
  deleteAllRead(userId: string): void {
    this.notifications.update(notifications =>
      notifications.filter(n => !(n.userId === userId && n.isRead))
    );
    this.saveToStorage();
  }

  /**
   * Obtiene las notificaciones de un usuario
   */
  getUserNotifications(userId: string): Notification[] {
    return this.notifications()
      .filter(n => n.userId === userId)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  /**
   * Obtiene las notificaciones no leídas de un usuario
   */
  getUserUnreadNotifications(userId: string): Notification[] {
    return this.notifications()
      .filter(n => n.userId === userId && !n.isRead)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  /**
   * Obtiene el conteo de no leídas para un usuario
   */
  getUserUnreadCount(userId: string): number {
    return this.notifications().filter(n => n.userId === userId && !n.isRead).length;
  }

  /**
   * Obtiene estadísticas de notificaciones de un usuario
   */
  getUserStats(userId: string): NotificationStats {
    const userNotifications = this.notifications().filter(n => n.userId === userId);
    const byType: { [key in NotificationType]?: number } = {};

    userNotifications.forEach(n => {
      byType[n.type] = (byType[n.type] || 0) + 1;
    });

    return {
      total: userNotifications.length,
      unread: userNotifications.filter(n => !n.isRead).length,
      byType
    };
  }

  /**
   * Obtiene la configuración de un usuario
   */
  getUserConfig(userId: string): NotificationConfig | undefined {
    return this.configs().find(c => c.userId === userId);
  }

  /**
   * Actualiza la configuración de un usuario
   */
  updateUserConfig(userId: string, config: Partial<NotificationConfig>): void {
    this.configs.update(configs =>
      configs.map(c =>
        c.userId === userId ? { ...c, ...config } : c
      )
    );
    this.saveToStorage();
  }

  /**
   * Verifica si un usuario debe recibir cierto tipo de notificación
   */
  private shouldReceiveNotification(
    userId: string,
    type: NotificationType,
    module?: NotificationModule
  ): boolean {
    const config = this.getUserConfig(userId);
    if (!config) return true; // Por defecto permitir si no hay config

    const typeEnabled = config.enabledTypes.includes(type);
    const moduleEnabled = !module || config.enabledModules.includes(module);

    return typeEnabled && moduleEnabled;
  }

  /**
   * Genera un ID único para notificaciones
   */
  private generateId(): string {
    return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Limpia notificaciones antiguas (más de 30 días)
   */
  cleanOldNotifications(userId?: string): void {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    this.notifications.update(notifications =>
      notifications.filter(n => {
        const shouldDelete = (userId ? n.userId === userId : true) &&
                           n.isRead &&
                           new Date(n.createdAt) < thirtyDaysAgo;
        return !shouldDelete;
      })
    );
    this.saveToStorage();
  }

  /**
   * MÉTODOS DE NOTIFICACIONES AUTOMÁTICAS
   * Estos métodos se pueden llamar desde otros servicios/componentes
   */

  /**
   * Notificación de nuevo empleado
   */
  notifyNewEmployee(employeeName: string, departmentName: string, employeeId?: string): void {
    this.createNotification({
      userId: 'admin@rrhh.com', // Notificar al admin
      type: NotificationType.INFO,
      title: 'Nuevo Empleado Registrado',
      message: `${employeeName} ha sido registrado en el departamento ${departmentName}`,
      module: NotificationModule.EMPLOYEES,
      moduleId: employeeId,
      redirectUrl: employeeId ? `/empleados/editar/${employeeId}` : '/empleados'
    });
  }

  /**
   * Notificación de solicitud de permiso
   */
  notifyPermissionRequest(employeeName: string, permissionType: string, permissionId?: string): void {
    this.createNotification({
      userId: 'admin@rrhh.com',
      type: NotificationType.REQUEST,
      title: 'Nueva Solicitud de Permiso',
      message: `${employeeName} ha solicitado un permiso de tipo: ${permissionType}`,
      module: NotificationModule.PERMISSIONS,
      moduleId: permissionId,
      redirectUrl: permissionId ? `/permisos/${permissionId}` : '/permisos'
    });
  }

  /**
   * Notificación de aprobación
   */
  notifyApproval(userId: string, title: string, message: string, redirectUrl?: string): void {
    this.createNotification({
      userId,
      type: NotificationType.SUCCESS,
      title,
      message,
      redirectUrl
    });
  }

  /**
   * Notificación de rechazo
   */
  notifyRejection(userId: string, title: string, message: string, redirectUrl?: string): void {
    this.createNotification({
      userId,
      type: NotificationType.ERROR,
      title,
      message,
      redirectUrl
    });
  }

  /**
   * Notificación de recordatorio
   */
  notifyReminder(userId: string, title: string, message: string, module?: NotificationModule): void {
    this.createNotification({
      userId,
      type: NotificationType.REMINDER,
      title,
      message,
      module
    });
  }

  /**
   * Notificación de vencimiento
   */
  notifyExpiration(userId: string, title: string, message: string, module?: NotificationModule): void {
    this.createNotification({
      userId,
      type: NotificationType.EXPIRATION,
      title,
      message,
      module
    });
  }

  /**
   * Notificación de alerta/advertencia
   */
  notifyWarning(userId: string, title: string, message: string): void {
    this.createNotification({
      userId,
      type: NotificationType.WARNING,
      title,
      message
    });
  }

  /**
   * Notificación broadcast a todos los usuarios
   */
  notifyAll(title: string, message: string, type: NotificationType = NotificationType.INFO): void {
    const users = ['admin@rrhh.com', 'usuario@rrhh.com']; // En producción, obtener de un servicio
    this.createNotification({
      userId: users,
      type,
      title,
      message
    });
  }

  /**
   * Crea notificaciones de prueba (para testing)
   */
  createSampleNotifications(userId: string): void {
    const samples: CreateNotificationParams[] = [
      {
        userId,
        type: NotificationType.INFO,
        title: 'Bienvenido al Sistema',
        message: 'Esta es una notificación de bienvenida al sistema de RRHH',
        module: NotificationModule.DASHBOARD
      },
      {
        userId,
        type: NotificationType.SUCCESS,
        title: 'Solicitud Aprobada',
        message: 'Tu solicitud de vacaciones ha sido aprobada',
        module: NotificationModule.VACATIONS,
        redirectUrl: '/vacaciones'
      },
      {
        userId,
        type: NotificationType.WARNING,
        title: 'Documentación Pendiente',
        message: 'Tienes documentos pendientes por completar',
        module: NotificationModule.EMPLOYEES
      },
      {
        userId,
        type: NotificationType.REMINDER,
        title: 'Recordatorio de Asistencia',
        message: 'No olvides marcar tu asistencia hoy',
        module: NotificationModule.ATTENDANCE
      }
    ];

    samples.forEach(sample => this.createNotification(sample));
  }
}

