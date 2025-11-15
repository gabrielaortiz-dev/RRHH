import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { SharedModule } from 'primeng/api';
import { EmployeeService } from '../services/employee.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, CardModule, ButtonModule, ChartModule, SharedModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard {
  private employeeService = inject(EmployeeService);
  private authService = inject(AuthService);

  currentUser = this.authService.getCurrentUser();

  // Estadísticas calculadas
  totalEmployees = computed(() => this.employeeService.getTotalEmployees());
  activeEmployees = computed(() => this.employeeService.getActiveEmployees());
  inactiveEmployees = computed(() => this.employeeService.getInactiveEmployees());
  averageSalary = computed(() => {
    const avg = this.employeeService.getAverageSalary();
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(avg);
  });

  // Datos para gráfico de empleados por departamento
  departmentChartData = computed(() => {
    const deptData = this.employeeService.getEmployeesByDepartment();
    return {
      labels: Object.keys(deptData),
      datasets: [
        {
          label: 'Empleados por Departamento',
          data: Object.values(deptData),
          backgroundColor: [
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#4facfe',
            '#43e97b',
            '#fa709a'
          ],
          borderColor: '#ffffff',
          borderWidth: 2
        }
      ]
    };
  });

  departmentChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      }
    }
  };

  // Datos para gráfico de estado de empleados
  statusChartData = computed(() => {
    return {
      labels: ['Activos', 'Inactivos'],
      datasets: [
        {
          data: [this.activeEmployees(), this.inactiveEmployees()],
          backgroundColor: ['#43e97b', '#fa709a'],
          borderColor: '#ffffff',
          borderWidth: 2
        }
      ]
    };
  });

  statusChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      }
    }
  };
}

