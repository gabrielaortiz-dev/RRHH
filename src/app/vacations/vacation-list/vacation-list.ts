import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
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

interface Vacation {
  id: number;
  employeeId: number;
  employeeName: string;
  startDate: Date;
  endDate: Date;
  days: number;
  type: string;
  status: string;
  reason: string;
  availableDays: number;
  requestedDate: Date;
}

@Component({
  selector: 'app-vacation-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    TableModule,
    ButtonModule,
    InputTextModule,
    TagModule,
    TooltipModule,
    ConfirmDialogModule,
    ToastModule,
    DialogModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './vacation-list.html',
  styleUrl: './vacation-list.css'
})
export class VacationList {
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  vacations = signal<Vacation[]>([
    {
      id: 1,
      employeeId: 1,
      employeeName: 'Juan Pérez',
      startDate: new Date('2024-02-01'),
      endDate: new Date('2024-02-05'),
      days: 5,
      type: 'Vacaciones',
      status: 'Pendiente',
      reason: 'Vacaciones familiares',
      availableDays: 15,
      requestedDate: new Date('2024-01-15')
    }
  ]);

  selectedVacation = signal<Vacation | null>(null);
  showDetailsDialog = signal(false);

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('es-DO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  getSeverity(status: string): 'success' | 'warn' | 'danger' | 'info' {
    switch (status) {
      case 'Aprobado':
        return 'success';
      case 'Pendiente':
        return 'warn';
      case 'Rechazado':
        return 'danger';
      case 'En Proceso':
        return 'info';
      default:
        return 'warn';
    }
  }

  approveVacation(vacation: Vacation) {
    this.confirmationService.confirm({
      message: `¿Aprobar la solicitud de vacaciones de ${vacation.employeeName}?`,
      header: 'Confirmar Aprobación',
      icon: 'pi pi-check-circle',
      acceptLabel: 'Sí, aprobar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-success',
      accept: () => {
        this.vacations.update(list => 
          list.map(v => v.id === vacation.id ? { ...v, status: 'Aprobado' } : v)
        );
        this.messageService.add({
          severity: 'success',
          summary: 'Aprobado',
          detail: 'La solicitud de vacaciones ha sido aprobada'
        });
      }
    });
  }

  rejectVacation(vacation: Vacation) {
    this.confirmationService.confirm({
      message: `¿Rechazar la solicitud de vacaciones de ${vacation.employeeName}?`,
      header: 'Confirmar Rechazo',
      icon: 'pi pi-times-circle',
      acceptLabel: 'Sí, rechazar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.vacations.update(list => 
          list.map(v => v.id === vacation.id ? { ...v, status: 'Rechazado' } : v)
        );
        this.messageService.add({
          severity: 'info',
          summary: 'Rechazado',
          detail: 'La solicitud de vacaciones ha sido rechazada'
        });
      }
    });
  }

  viewDetails(vacation: Vacation) {
    this.selectedVacation.set(vacation);
    this.showDetailsDialog.set(true);
  }

  // Sistema de alertas y seguimiento
  getAlerts(vacation: Vacation): string[] {
    const alerts: string[] = [];
    
    // Alerta si los días solicitados exceden los disponibles
    if (vacation.days > vacation.availableDays) {
      alerts.push('⚠️ Los días solicitados exceden los días disponibles');
    }
    
    // Alerta si la solicitud está pendiente por más de 5 días
    const daysPending = Math.floor((new Date().getTime() - vacation.requestedDate.getTime()) / (1000 * 60 * 60 * 24));
    if (vacation.status === 'Pendiente' && daysPending > 5) {
      alerts.push(`⏰ Solicitud pendiente por ${daysPending} días`);
    }
    
    // Alerta si la fecha de inicio es próxima
    const daysUntilStart = Math.floor((vacation.startDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    if (daysUntilStart <= 7 && daysUntilStart > 0 && vacation.status === 'Aprobado') {
      alerts.push(`📅 Las vacaciones inician en ${daysUntilStart} días`);
    }
    
    return alerts;
  }

  // Verificar si hay alertas para mostrar
  hasAlerts(vacation: Vacation): boolean {
    return this.getAlerts(vacation).length > 0;
  }
}

