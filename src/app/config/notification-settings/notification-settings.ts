import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { InputTextModule } from 'primeng/inputtext';
import { DividerModule } from 'primeng/divider';
import { MessageModule } from 'primeng/message';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { NotificationService } from '../../services/notification.service';
import { AuthService } from '../../services/auth.service';
import { NotificationType, NotificationModule, NotificationConfig } from '../../models/notification.model';

interface NotificationTypeOption {
  type: NotificationType;
  label: string;
  description: string;
  icon: string;
}

interface NotificationModuleOption {
  module: NotificationModule;
  label: string;
  description: string;
  icon: string;
}

@Component({
  selector: 'app-notification-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CardModule,
    ButtonModule,
    CheckboxModule,
    InputTextModule,
    DividerModule,
    MessageModule,
    ToastModule
  ],
  templateUrl: './notification-settings.html',
  styleUrl: './notification-settings.css',
  providers: [MessageService]
})
export class NotificationSettings implements OnInit {
  private notificationService = inject(NotificationService);
  private authService = inject(AuthService);
  private messageService = inject(MessageService);

  currentUser = this.authService.getCurrentUser();
  config = signal<NotificationConfig | null>(null);
  
  // Opciones de tipos de notificaciones
  typeOptions: NotificationTypeOption[] = [
    {
      type: NotificationType.INFO,
      label: 'Información',
      description: 'Notificaciones informativas generales',
      icon: 'pi-info-circle'
    },
    {
      type: NotificationType.SUCCESS,
      label: 'Éxito',
      description: 'Confirmaciones de acciones exitosas',
      icon: 'pi-check-circle'
    },
    {
      type: NotificationType.WARNING,
      label: 'Advertencias',
      description: 'Alertas y advertencias importantes',
      icon: 'pi-exclamation-triangle'
    },
    {
      type: NotificationType.ERROR,
      label: 'Errores',
      description: 'Notificaciones de errores críticos',
      icon: 'pi-times-circle'
    },
    {
      type: NotificationType.APPROVAL,
      label: 'Aprobaciones',
      description: 'Notificaciones de aprobaciones',
      icon: 'pi-thumbs-up'
    },
    {
      type: NotificationType.REQUEST,
      label: 'Solicitudes',
      description: 'Nuevas solicitudes pendientes',
      icon: 'pi-inbox'
    },
    {
      type: NotificationType.REMINDER,
      label: 'Recordatorios',
      description: 'Recordatorios de tareas pendientes',
      icon: 'pi-clock'
    },
    {
      type: NotificationType.EXPIRATION,
      label: 'Vencimientos',
      description: 'Alertas de vencimientos próximos',
      icon: 'pi-calendar-times'
    }
  ];

  // Opciones de módulos
  moduleOptions: NotificationModuleOption[] = [
    {
      module: NotificationModule.DASHBOARD,
      label: 'Dashboard',
      description: 'Notificaciones del panel principal',
      icon: 'pi-home'
    },
    {
      module: NotificationModule.EMPLOYEES,
      label: 'Empleados',
      description: 'Notificaciones relacionadas con empleados',
      icon: 'pi-users'
    },
    {
      module: NotificationModule.DEPARTMENTS,
      label: 'Departamentos',
      description: 'Notificaciones de departamentos',
      icon: 'pi-building'
    },
    {
      module: NotificationModule.REPORTS,
      label: 'Reportes',
      description: 'Notificaciones de reportes generados',
      icon: 'pi-chart-bar'
    },
    {
      module: NotificationModule.CONFIG,
      label: 'Configuración',
      description: 'Notificaciones del sistema',
      icon: 'pi-cog'
    },
    {
      module: NotificationModule.PERMISSIONS,
      label: 'Permisos',
      description: 'Solicitudes y aprobaciones de permisos',
      icon: 'pi-lock'
    },
    {
      module: NotificationModule.VACATIONS,
      label: 'Vacaciones',
      description: 'Solicitudes y aprobaciones de vacaciones',
      icon: 'pi-calendar'
    },
    {
      module: NotificationModule.ATTENDANCE,
      label: 'Asistencias',
      description: 'Notificaciones de asistencias',
      icon: 'pi-clock'
    }
  ];

  ngOnInit(): void {
    this.loadConfig();
  }

  /**
   * Carga la configuración del usuario
   */
  loadConfig(): void {
    const user = this.currentUser();
    if (user?.email) {
      const userConfig = this.notificationService.getUserConfig(user.email);
      if (userConfig) {
        this.config.set(userConfig);
      }
    }
  }

  /**
   * Verifica si un tipo está habilitado
   */
  isTypeEnabled(type: NotificationType): boolean {
    const cfg = this.config();
    return cfg ? cfg.enabledTypes.includes(type) : false;
  }

  /**
   * Alterna la habilitación de un tipo
   */
  toggleType(type: NotificationType): void {
    const cfg = this.config();
    if (!cfg) return;

    const enabledTypes = cfg.enabledTypes.includes(type)
      ? cfg.enabledTypes.filter(t => t !== type)
      : [...cfg.enabledTypes, type];

    this.config.set({ ...cfg, enabledTypes });
  }

  /**
   * Verifica si un módulo está habilitado
   */
  isModuleEnabled(module: NotificationModule): boolean {
    const cfg = this.config();
    return cfg ? cfg.enabledModules.includes(module) : false;
  }

  /**
   * Alterna la habilitación de un módulo
   */
  toggleModule(module: NotificationModule): void {
    const cfg = this.config();
    if (!cfg) return;

    const enabledModules = cfg.enabledModules.includes(module)
      ? cfg.enabledModules.filter(m => m !== module)
      : [...cfg.enabledModules, module];

    this.config.set({ ...cfg, enabledModules });
  }

  /**
   * Alterna las notificaciones por email
   */
  toggleEmailNotifications(): void {
    const cfg = this.config();
    if (!cfg) return;

    this.config.set({
      ...cfg,
      emailNotifications: !cfg.emailNotifications
    });
  }

  /**
   * Actualiza el email
   */
  updateEmail(email: string): void {
    const cfg = this.config();
    if (!cfg) return;

    this.config.set({ ...cfg, email });
  }

  /**
   * Guarda la configuración
   */
  saveConfig(): void {
    const user = this.currentUser();
    const cfg = this.config();

    if (!user?.email || !cfg) return;

    this.notificationService.updateUserConfig(user.email, cfg);

    this.messageService.add({
      severity: 'success',
      summary: 'Configuración guardada',
      detail: 'Tus preferencias de notificaciones han sido actualizadas',
      life: 3000
    });
  }

  /**
   * Restaura configuración por defecto
   */
  resetConfig(): void {
    const user = this.currentUser();
    if (!user?.email) return;

    const defaultConfig: NotificationConfig = {
      userId: user.email,
      emailNotifications: false,
      enabledTypes: Object.values(NotificationType),
      enabledModules: Object.values(NotificationModule),
      email: user.email
    };

    this.config.set(defaultConfig);
    this.notificationService.updateUserConfig(user.email, defaultConfig);

    this.messageService.add({
      severity: 'info',
      summary: 'Configuración restaurada',
      detail: 'Se han restaurado las preferencias por defecto',
      life: 3000
    });
  }

  /**
   * Habilitar todo
   */
  enableAll(): void {
    const cfg = this.config();
    if (!cfg) return;

    this.config.set({
      ...cfg,
      enabledTypes: Object.values(NotificationType),
      enabledModules: Object.values(NotificationModule)
    });
  }

  /**
   * Deshabilitar todo
   */
  disableAll(): void {
    const cfg = this.config();
    if (!cfg) return;

    this.config.set({
      ...cfg,
      enabledTypes: [],
      enabledModules: []
    });
  }

  /**
   * Crear notificaciones de prueba
   */
  createTestNotifications(): void {
    const user = this.currentUser();
    if (!user?.email) return;

    this.notificationService.createSampleNotifications(user.email);

    this.messageService.add({
      severity: 'success',
      summary: 'Notificaciones de prueba creadas',
      detail: 'Se han generado notificaciones de ejemplo',
      life: 3000
    });
  }
}

