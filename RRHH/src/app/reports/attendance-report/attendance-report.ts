import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { EmployeeService } from '../../services/employee.service';
import { ExportService } from '../../services/export.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-attendance-report',
  standalone: true,
  imports: [CommonModule, FormsModule, CardModule, ButtonModule, DatePickerModule, TableModule, TagModule],
  templateUrl: './attendance-report.html',
  styleUrl: './attendance-report.css'
})
export class AttendanceReport {
  private employeeService = inject(EmployeeService);
  private exportService = inject(ExportService);
  private notificationService = inject(NotificationService);

  startDate: Date = new Date();
  endDate: Date = new Date();
  
  employees = this.employeeService.getEmployees();

  attendanceData = this.employees().map(emp => ({
    employee: `${emp.nombre} ${emp.apellido}`,
    department: emp.departamento,
    present: Math.floor(Math.random() * 20) + 5,
    absent: Math.floor(Math.random() * 3),
    late: Math.floor(Math.random() * 2),
    percentage: Math.floor(Math.random() * 15) + 85
  }));

  getAttendanceStatus(percentage: number): 'success' | 'warn' | 'danger' {
    if (percentage >= 95) return 'success';
    if (percentage >= 85) return 'warn';
    return 'danger';
  }

  generateReport() {
    this.attendanceData = this.employees().map(emp => ({
      employee: `${emp.nombre} ${emp.apellido}`,
      department: emp.departamento,
      present: Math.floor(Math.random() * 20) + 5,
      absent: Math.floor(Math.random() * 3),
      late: Math.floor(Math.random() * 2),
      percentage: Math.floor(Math.random() * 15) + 85
    }));
    this.notificationService.info('Reporte Actualizado', 'El reporte de asistencias se ha regenerado');
  }

  async exportPDF() {
    alert('¡Botón PDF clickeado! Iniciando exportación...');
    console.log('🔴 Botón PDF Asistencias clickeado');
    try {
      const columns = [
        { header: 'Empleado', field: 'employee', width: 40 },
        { header: 'Departamento', field: 'department', width: 30 },
        { header: 'Presentes', field: 'present', width: 20 },
        { header: 'Ausentes', field: 'absent', width: 20 },
        { header: 'Tarde', field: 'late', width: 20 },
        { header: 'Asistencia %', field: 'percentage', width: 25 }
      ];

      const dateRange = `${this.startDate.toLocaleDateString('es-HN')} - ${this.endDate.toLocaleDateString('es-HN')}`;

      const options = {
        title: 'Reporte de Asistencias',
        subtitle: `Período: ${dateRange}`,
        filename: `reporte-asistencias-${new Date().getTime()}`,
        orientation: 'landscape' as const,
        includeDate: true
      };

      await this.exportService.exportToPDF(this.attendanceData, columns, options);
      alert('✅ PDF generado exitosamente. Revisa tus descargas.');
      this.notificationService.success('PDF Generado', 'El reporte de asistencias se ha exportado correctamente');
    } catch (error) {
      console.error('Error al exportar PDF:', error);
      alert('❌ Error al generar PDF: ' + error);
      this.notificationService.error('Error al Exportar', 'No se pudo generar el archivo PDF');
    }
  }

  async exportExcel() {
    alert('¡Botón Excel clickeado! Iniciando exportación...');
    console.log('🟢 Botón Excel Asistencias clickeado');
    try {
      const columns = [
        { header: 'Empleado', field: 'employee', width: 30 },
        { header: 'Departamento', field: 'department', width: 25 },
        { header: 'Días Presentes', field: 'present', width: 15 },
        { header: 'Días Ausentes', field: 'absent', width: 15 },
        { header: 'Llegadas Tarde', field: 'late', width: 15 },
        { header: 'Porcentaje Asistencia', field: 'percentage', width: 20 }
      ];

      const dateRange = `${this.startDate.toLocaleDateString('es-HN')} - ${this.endDate.toLocaleDateString('es-HN')}`;

      const options = {
        title: 'Reporte de Asistencias',
        subtitle: `Período: ${dateRange}`,
        filename: `reporte-asistencias-${new Date().getTime()}`,
        includeDate: true
      };

      await this.exportService.exportToExcel(this.attendanceData, columns, options);
      alert('✅ Excel generado exitosamente. Revisa tus descargas.');
      this.notificationService.success('Excel Generado', 'El reporte de asistencias se ha exportado correctamente');
    } catch (error) {
      console.error('Error al exportar Excel:', error);
      alert('❌ Error al generar Excel: ' + error);
      this.notificationService.error('Error al Exportar', 'No se pudo generar el archivo Excel');
    }
  }
}

