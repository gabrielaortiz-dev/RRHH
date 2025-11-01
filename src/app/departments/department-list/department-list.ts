import { Component, inject } from '@angular/core';
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
import { DepartmentService, Department } from '../../services/department.service';

@Component({
  selector: 'app-department-list',
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
  templateUrl: './department-list.html',
  styleUrl: './department-list.css'
})
export class DepartmentList {
  private departmentService = inject(DepartmentService);
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  departments = this.departmentService.getDepartments();

  deleteDepartment(department: Department) {
    this.confirmationService.confirm({
      message: `¿Está seguro que desea eliminar el departamento "${department.nombre}"?`,
      header: 'Confirmar Eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí, eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        const success = this.departmentService.deleteDepartment(department.id);
        if (success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Eliminado',
            detail: 'El departamento ha sido eliminado exitosamente'
          });
        } else {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo eliminar el departamento'
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

