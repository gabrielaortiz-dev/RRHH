import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmationService, MessageService } from 'primeng/api';
import { DialogModule } from 'primeng/dialog';
import { CheckboxModule } from 'primeng/checkbox';

interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: string;
  status: string;
  lastLogin: Date;
  permissions: string[];
}

interface AuditLog {
  id: number;
  userId: number;
  userName: string;
  action: string;
  module: string;
  timestamp: Date;
  ipAddress?: string;
  details?: string;
}

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    TableModule,
    ButtonModule,
    InputTextModule,
    TagModule,
    TooltipModule,
    ConfirmDialogModule,
    ToastModule,
    DialogModule,
    CheckboxModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './user-list.html',
  styleUrl: './user-list.css'
})
export class UserList {
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  users = signal<User[]>([
    {
      id: 1,
      username: 'admin',
      name: 'Administrador',
      email: 'admin@rrhh.com',
      role: 'Admin',
      status: 'Activo',
      lastLogin: new Date('2024-01-30'),
      permissions: ['all']
    },
    {
      id: 2,
      username: 'rrhh_user',
      name: 'Usuario RRHH',
      email: 'rrhh@rrhh.com',
      role: 'RRHH',
      status: 'Activo',
      lastLogin: new Date('2024-01-29'),
      permissions: ['employees', 'payroll', 'vacations']
    }
  ]);

  selectedUser = signal<User | null>(null);
  showPermissionsDialog = signal(false);
  showUserDialog = signal(false);
  showAuditDialog = signal(false);
  
  auditLogs = signal<AuditLog[]>([
    {
      id: 1,
      userId: 1,
      userName: 'admin',
      action: 'Login',
      module: 'Sistema',
      timestamp: new Date('2024-01-30T10:30:00'),
      ipAddress: '192.168.1.100',
      details: 'Inicio de sesión exitoso'
    },
    {
      id: 2,
      userId: 1,
      userName: 'admin',
      action: 'Modificar',
      module: 'Usuarios',
      timestamp: new Date('2024-01-30T11:15:00'),
      ipAddress: '192.168.1.100',
      details: 'Permisos actualizados para usuario rrhh_user'
    }
  ]);

  roles = [
    { label: 'Administrador', value: 'Admin' },
    { label: 'RRHH', value: 'RRHH' },
    { label: 'Empleado', value: 'Employee' }
  ];

  modules = [
    { label: 'Empleados', value: 'employees' },
    { label: 'Nómina', value: 'payroll' },
    { label: 'Vacaciones', value: 'vacations' },
    { label: 'Documentos', value: 'documents' },
    { label: 'Reportes', value: 'reports' },
    { label: 'Configuración', value: 'config' }
  ];

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('es-DO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getSeverity(status: string): 'success' | 'danger' {
    return status === 'Activo' ? 'success' : 'danger';
  }

  getRoleSeverity(role: string): 'success' | 'warn' | 'info' {
    switch (role) {
      case 'Admin':
        return 'success';
      case 'RRHH':
        return 'warn';
      case 'Employee':
        return 'info';
      default:
        return 'info';
    }
  }

  managePermissions(user: User) {
    this.selectedUser.set(user);
    this.showPermissionsDialog.set(true);
  }

  editUser(user: User) {
    this.selectedUser.set(user);
    this.showUserDialog.set(true);
  }

  deleteUser(user: User) {
    this.confirmationService.confirm({
      message: `¿Está seguro que desea eliminar al usuario "${user.name}"?`,
      header: 'Confirmar Eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí, eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.users.update(list => list.filter(u => u.id !== user.id));
        this.messageService.add({
          severity: 'success',
          summary: 'Eliminado',
          detail: 'El usuario ha sido eliminado exitosamente'
        });
      }
    });
  }

  toggleUserStatus(user: User) {
    const newStatus = user.status === 'Activo' ? 'Inactivo' : 'Activo';
    this.users.update(list => 
      list.map(u => u.id === user.id ? { ...u, status: newStatus } : u)
    );
    
    // Registrar en auditoría
    this.addAuditLog({
      userId: user.id,
      userName: user.username,
      action: 'Cambiar Estado',
      module: 'Usuarios',
      details: `Estado cambiado a ${newStatus}`
    });
    
    this.messageService.add({
      severity: 'success',
      summary: 'Actualizado',
      detail: `Usuario ${newStatus.toLowerCase()}`
    });
  }

  viewAuditLogs() {
    this.showAuditDialog.set(true);
  }

  addAuditLog(log: Omit<AuditLog, 'id' | 'timestamp'>) {
    const newLog: AuditLog = {
      id: this.auditLogs().length + 1,
      ...log,
      timestamp: new Date(),
      ipAddress: log.ipAddress || 'N/A'
    };
    this.auditLogs.update(logs => [newLog, ...logs]);
  }
}

