import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { TableModule } from 'primeng/table';
import { EmployeeService } from '../../services/employee.service';
import { DepartmentService } from '../../services/department.service';

@Component({
  selector: 'app-general-report',
  standalone: true,
  imports: [CommonModule, CardModule, ButtonModule, ChartModule, TableModule],
  templateUrl: './general-report.html',
  styleUrl: './general-report.css'
})
export class GeneralReport {
  private employeeService = inject(EmployeeService);
  private departmentService = inject(DepartmentService);

  // Estadísticas de empleados
  totalEmployees = computed(() => this.employeeService.getTotalEmployees());
  activeEmployees = computed(() => this.employeeService.getActiveEmployees());
  inactiveEmployees = computed(() => this.employeeService.getInactiveEmployees());
  averageSalary = computed(() => this.employeeService.getAverageSalary());

  // Estadísticas de departamentos
  totalDepartments = computed(() => this.departmentService.getTotalDepartments());
  activeDepartments = computed(() => this.departmentService.getActiveDepartments());
  totalBudget = computed(() => this.departmentService.getTotalBudget());

  // Datos para gráficos
  employeesByDepartment = computed(() => {
    const data = this.employeeService.getEmployeesByDepartment();
    return {
      labels: Object.keys(data),
      datasets: [{
        label: 'Empleados',
        data: Object.values(data),
        backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']
      }]
    };
  });

  chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  };

  departments = this.departmentService.getDepartments();

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  exportPDF() {
    alert('Función de exportación a PDF en desarrollo');
  }

  exportExcel() {
    alert('Función de exportación a Excel en desarrollo');
  }

  print() {
    window.print();
  }
}

