import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { EmployeeService } from '../../services/employee.service';

@Component({
  selector: 'app-attendance-report',
  standalone: true,
  imports: [CommonModule, FormsModule, CardModule, ButtonModule, DatePickerModule, TableModule, TagModule],
  templateUrl: './attendance-report.html',
  styleUrl: './attendance-report.css'
})
export class AttendanceReport {
  private employeeService = inject(EmployeeService);

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
    alert('Generando reporte de asistencias...');
  }

  exportPDF() {
    alert('Exportando a PDF...');
  }
}

