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
import { EmployeeService, Employee } from '../../services/employee.service';

@Component({
  selector: 'app-employee-list',
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
    ToastModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './employee-list.html',
  styleUrl: './employee-list.css'
})
export class EmployeeList {
  private employeeService = inject(EmployeeService);
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  employees = this.employeeService.getEmployees();
  searchValue = signal('');

  deleteEmployee(employee: Employee) {
    this.confirmationService.confirm({
      message: `¿Está seguro que desea eliminar a ${employee.nombre} ${employee.apellido}?`,
      header: 'Confirmar Eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí, eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        const success = this.employeeService.deleteEmployee(employee.id);
        if (success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Eliminado',
            detail: 'El empleado ha sido eliminado exitosamente'
          });
        } else {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo eliminar el empleado'
          });
        }
      }
    });
  }

  getSeverity(estado: string): 'success' | 'danger' {
    return estado === 'Activo' ? 'success' : 'danger';
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('es-DO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}

