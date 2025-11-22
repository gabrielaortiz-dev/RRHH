import { Component, inject, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { TableModule } from 'primeng/table';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';
import { EmployeeService } from '../../services/employee.service';
import { DepartmentService } from '../../services/department.service';

@Component({
  selector: 'app-general-report',
  standalone: true,
  imports: [CommonModule, FormsModule, CardModule, ButtonModule, ChartModule, TableModule, SelectModule, DatePickerModule],
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

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  // Filtros
  selectedDepartment = signal<string>('');
  selectedContractType = signal<string>('');
  startDate = signal<Date | null>(null);
  endDate = signal<Date | null>(null);

  departments = computed(() => {
    const depts = this.departmentService.getDepartments();
    return [{ label: 'Todos', value: '' }, ...depts().map(d => ({ label: d.nombre, value: d.nombre }))];
  });

  contractTypes = [
    { label: 'Todos', value: '' },
    { label: 'Tiempo Completo', value: 'Tiempo Completo' },
    { label: 'Medio Tiempo', value: 'Medio Tiempo' },
    { label: 'Por Proyecto', value: 'Por Proyecto' },
    { label: 'Temporal', value: 'Temporal' }
  ];

  // Indicadores clave
  turnoverRate = computed(() => {
    const total = this.totalEmployees();
    const inactive = this.inactiveEmployees();
    return total > 0 ? ((inactive / total) * 100).toFixed(2) : '0.00';
  });

  attendanceRate = computed(() => {
    // Simulación de tasa de asistencia
    return '92.5';
  });

  trainingRate = computed(() => {
    // Simulación de tasa de capacitación
    return '75.0';
  });

  exportPDF() {
    const reportData = {
      fecha: new Date().toLocaleDateString('es-DO'),
      totalEmpleados: this.totalEmployees(),
      empleadosActivos: this.activeEmployees(),
      salarioPromedio: this.averageSalary(),
      rotacion: this.turnoverRate(),
      asistencia: this.attendanceRate(),
      capacitacion: this.trainingRate()
    };

    const content = `
      REPORTE GENERAL DE RRHH
      ========================
      Fecha: ${reportData.fecha}
      
      INDICADORES CLAVE:
      - Total Empleados: ${reportData.totalEmpleados}
      - Empleados Activos: ${reportData.empleadosActivos}
      - Salario Promedio: ${this.formatCurrency(reportData.salarioPromedio)}
      - Tasa de Rotación: ${reportData.rotacion}%
      - Tasa de Asistencia: ${reportData.asistencia}%
      - Tasa de Capacitación: ${reportData.capacitacion}%
    `;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Reporte_General_${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  exportExcel() {
    // Simulación de exportación a Excel
    const csvContent = `Empleado,Departamento,Salario,Estado\n` +
      this.employeeService.getEmployees()().map(emp => 
        `${emp.nombre} ${emp.apellido},${emp.departamento},${emp.salario},${emp.estado}`
      ).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Reporte_General_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  print() {
    window.print();
  }

  applyFilters() {
    // Aplicar filtros (implementación básica)
    console.log('Aplicando filtros:', {
      department: this.selectedDepartment(),
      contractType: this.selectedContractType(),
      startDate: this.startDate(),
      endDate: this.endDate()
    });
  }

  clearFilters() {
    this.selectedDepartment.set('');
    this.selectedContractType.set('');
    this.startDate.set(null);
    this.endDate.set(null);
  }
}

