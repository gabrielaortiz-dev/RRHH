/**
 * Tipos de notificaciones disponibles en el sistema
 */
export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  APPROVAL = 'approval',
  REQUEST = 'request',
  REMINDER = 'reminder',
  EXPIRATION = 'expiration'
}

/**
 * Módulos del sistema para redirección
 */
export enum NotificationModule {
  DASHBOARD = 'dashboard',
  EMPLOYEES = 'employees',
  DEPARTMENTS = 'departments',
  REPORTS = 'reports',
  CONFIG = 'config',
  PERMISSIONS = 'permissions',
  VACATIONS = 'vacations',
  ATTENDANCE = 'attendance'
}

/**
 * Interfaz principal de Notificación
 */
export interface Notification {
  id: string;
  userId: string;                    // Usuario destinatario
  type: NotificationType;            // Tipo de notificación
  title: string;                     // Título de la notificación
  message: string;                   // Mensaje descriptivo
  module?: NotificationModule;       // Módulo relacionado
  moduleId?: string;                 // ID del elemento del módulo (ej: ID del empleado)
  redirectUrl?: string;              // URL de redirección
  isRead: boolean;                   // Estado leída/no leída
  createdAt: Date;                   // Fecha de creación
  readAt?: Date;                     // Fecha de lectura
  metadata?: any;                    // Datos adicionales
}

/**
 * Configuración de notificaciones por usuario
 */
export interface NotificationConfig {
  userId: string;
  emailNotifications: boolean;       // Recibir por email
  enabledTypes: NotificationType[];  // Tipos de notificaciones habilitadas
  enabledModules: NotificationModule[]; // Módulos habilitados
  email?: string;                    // Email para envío
}

/**
 * Parámetros para crear una notificación
 */
export interface CreateNotificationParams {
  userId: string | string[];         // Puede ser uno o varios usuarios
  type: NotificationType;
  title: string;
  message: string;
  module?: NotificationModule;
  moduleId?: string;
  redirectUrl?: string;
  metadata?: any;
}

/**
 * Estadísticas de notificaciones
 */
export interface NotificationStats {
  total: number;
  unread: number;
  byType: { [key in NotificationType]?: number };
}

