import { Component, inject, signal, OnInit } from '@angular/core';
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
import { BadgeModule } from 'primeng/badge';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ContractService, Contrato } from '../../services/contract.service';
import { EmployeeService } from '../../services/employee.service';

@Component({
  selector: 'app-contract-list',
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
    BadgeModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './contract-list.html',
  styleUrl: './contract-list.css'
})
export class ContractList implements OnInit {
  private contractService = inject(ContractService);
  private employeeService = inject(EmployeeService);
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  contratos = signal<Contrato[]>([]);
  alertasVencimiento = signal<Contrato[]>([]);
  loading = signal(false);
  mostrarAlertas = signal(false);
  empleados: any[] = [];

  ngOnInit() {
    this.cargarContratos();
    this.cargarAlertas();
    this.cargarEmpleados();
  }

  cargarContratos() {
    this.loading.set(true);
    this.contractService.getContratos().subscribe({
      next: (response) => {
        if (response.success && Array.isArray(response.data)) {
          this.contratos.set(response.data);
        }
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudieron cargar los contratos'
        });
      }
    });
  }

  cargarAlertas() {
    this.contractService.getAlertasVencimiento(30).subscribe({
      next: (response) => {
        if (response.success && Array.isArray(response.data)) {
          this.alertasVencimiento.set(response.data);
        }
      }
    });
  }

  cargarEmpleados() {
    const employeesSignal = this.employeeService.getEmployees();
    this.empleados = employeesSignal();
  }

  deleteContrato(contrato: Contrato) {
    this.confirmationService.confirm({
      message: `¿Está seguro que desea eliminar este contrato?`,
      header: 'Confirmar Eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí, eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.contractService.deleteContrato(contrato.id_contrato).subscribe({
          next: (response) => {
            if (response.success) {
              this.messageService.add({
                severity: 'success',
                summary: 'Eliminado',
                detail: 'El contrato ha sido eliminado exitosamente'
              });
              this.cargarContratos();
            } else {
              this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: response.message || 'No se pudo eliminar el contrato'
              });
            }
          },
          error: () => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Error al eliminar el contrato'
            });
          }
        });
      }
    });
  }

  getSeverityTipo(tipo: string): 'success' | 'warn' | 'info' {
    switch(tipo) {
      case 'permanente': return 'success';
      case 'temporal': return 'warn';
      case 'honorarios': return 'info';
      default: return 'info';
    }
  }

  getSeverityVencimiento(estado?: string): 'success' | 'warn' | 'danger' {
    switch(estado) {
      case 'vencido': return 'danger';
      case 'por_vencer': return 'warn';
      case 'vigente': return 'success';
      default: return 'success';
    }
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  formatDate(date: string): string {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('es-HN');
  }

  getNombreEmpleado(idEmpleado: number): string {
    const empleado = this.empleados.find(e => e.id === idEmpleado);
    return empleado ? `${empleado.nombre} ${empleado.apellido}` : `ID: ${idEmpleado}`;
  }

  toggleAlertas() {
    this.mostrarAlertas.set(!this.mostrarAlertas());
  }
}

