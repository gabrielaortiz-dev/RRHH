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
import { SelectModule } from 'primeng/select';
import { ConfirmationService, MessageService } from 'primeng/api';
import { AttendanceService, Asistencia } from '../../services/attendance.service';
import { EmployeeService } from '../../services/employee.service';

@Component({
  selector: 'app-attendance-list',
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
    SelectModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './attendance-list.html',
  styleUrl: './attendance-list.css'
})
export class AttendanceList implements OnInit {
  private attendanceService = inject(AttendanceService);
  private employeeService = inject(EmployeeService);
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  asistencias = signal<Asistencia[]>([]);
  empleados = signal<any[]>([]);
  loading = signal(false);
  fechaInicio = signal<Date | null>(null);
  fechaFin = signal<Date | null>(null);
  empleadoFiltro = signal<number | null>(null);

  ngOnInit() {
    this.cargarEmpleados();
    this.cargarAsistencias();
  }

  cargarEmpleados() {
    const employeesSignal = this.employeeService.getEmployees();
    this.empleados.set(employeesSignal());
  }

  cargarAsistencias() {
    this.loading.set(true);
    const filters: any = {};
    
    if (this.fechaInicio()) {
      filters.fecha_inicio = this.fechaInicio()!.toISOString().split('T')[0];
    }
    if (this.fechaFin()) {
      filters.fecha_fin = this.fechaFin()!.toISOString().split('T')[0];
    }
    if (this.empleadoFiltro()) {
      filters.id_empleado = this.empleadoFiltro()!;
    }

    this.attendanceService.getAsistencias(filters).subscribe({
      next: (response) => {
        if (response.success && Array.isArray(response.data)) {
          this.asistencias.set(response.data);
        }
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudieron cargar las asistencias'
        });
      }
    });
  }

  aplicarFiltros() {
    this.cargarAsistencias();
  }

  limpiarFiltros() {
    this.fechaInicio.set(null);
    this.fechaFin.set(null);
    this.empleadoFiltro.set(null);
    this.cargarAsistencias();
  }

  deleteAsistencia(asistencia: Asistencia) {
    this.confirmationService.confirm({
      message: `¿Está seguro que desea eliminar este registro de asistencia?`,
      header: 'Confirmar Eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí, eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.attendanceService.deleteAsistencia(asistencia.id_asistencia).subscribe({
          next: (response) => {
            if (response.success) {
              this.messageService.add({
                severity: 'success',
                summary: 'Eliminado',
                detail: 'El registro de asistencia ha sido eliminado exitosamente'
              });
              this.cargarAsistencias();
            } else {
              this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: response.message || 'No se pudo eliminar el registro'
              });
            }
          },
          error: () => {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Error al eliminar el registro'
            });
          }
        });
      }
    });
  }

  getSeverityEstado(estado?: string): 'success' | 'warn' | 'danger' {
    switch(estado) {
      case 'Completa': return 'success';
      case 'Incompleta': return 'warn';
      case 'Falta': return 'danger';
      default: return 'success';
    }
  }

  formatDate(date: string): string {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('es-HN');
  }

  formatTime(time: string): string {
    if (!time) return 'N/A';
    return time.substring(0, 5);
  }

  generarReporte() {
    if (!this.fechaInicio() || !this.fechaFin()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Advertencia',
        detail: 'Por favor seleccione un rango de fechas para generar el reporte'
      });
      return;
    }

    this.loading.set(true);
    const reporte = {
      fecha_inicio: this.fechaInicio()!.toISOString().split('T')[0],
      fecha_fin: this.fechaFin()!.toISOString().split('T')[0],
      id_empleado: this.empleadoFiltro() || undefined
    };

    this.attendanceService.generarReporte(reporte).subscribe({
      next: (response) => {
        if (response.success) {
          this.messageService.add({
            severity: 'success',
            summary: 'Reporte Generado',
            detail: `Total: ${response.estadisticas?.total_registros || 0} registros. Completas: ${response.estadisticas?.completas || 0}, Incompletas: ${response.estadisticas?.incompletas || 0}, Faltas: ${response.estadisticas?.faltas || 0}`
          });
          if (Array.isArray(response.data)) {
            this.asistencias.set(response.data);
          }
        }
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Error al generar el reporte'
        });
      }
    });
  }
}

