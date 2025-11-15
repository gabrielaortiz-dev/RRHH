import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { TableModule } from 'primeng/table';
import { EmployeeService } from '../../services/employee.service';
import { DepartmentService } from '../../services/department.service';
import { ExportService } from '../../services/export.service';
import { NotificationService } from '../../services/notification.service';

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
  private exportService = inject(ExportService);
  private notificationService = inject(NotificationService);

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

  async exportPDF() {
    console.log('🔴 Botón PDF clickeado');
    try {
      const departments = this.departments();
      console.log('Departamentos:', departments);
      
      const exportData = departments.map(dept => ({
        nombre: dept.nombre,
        empleados: dept.numeroEmpleados,
        presupuesto: dept.presupuesto,
        estado: dept.estado
      }));
      console.log('Datos preparados:', exportData);

      const columns = [
        { header: 'Departamento', field: 'nombre', width: 40 },
        { header: 'Empleados', field: 'empleados', width: 25 },
        { header: 'Presupuesto', field: 'presupuesto', width: 30 },
        { header: 'Estado', field: 'estado', width: 25 }
      ];

      const options = {
        title: 'Reporte General de Recursos Humanos',
        subtitle: `Total Empleados: ${this.totalEmployees()} | Empleados Activos: ${this.activeEmployees()} | Salario Promedio: ${this.formatCurrency(this.averageSalary())}`,
        filename: `reporte-general-${new Date().getTime()}`,
        orientation: 'portrait' as const,
        includeDate: true
      };

      console.log('Llamando a exportService.exportToPDF...');
      await this.exportService.exportToPDF(exportData, columns, options);
      console.log('✅ PDF exportado exitosamente');
      this.notificationService.success('PDF Generado', 'El reporte se ha exportado correctamente');
    } catch (error) {
      console.error('❌ Error al exportar PDF:', error);
      this.notificationService.error('Error al Exportar', 'No se pudo generar el archivo PDF');
    }
  }

  async exportExcel() {
    console.log('🟢 Botón Excel clickeado');
    try {
      const departments = this.departments();
      
      const exportData = departments.map(dept => ({
        nombre: dept.nombre,
        descripcion: dept.descripcion,
        empleados: dept.numeroEmpleados,
        presupuesto: dept.presupuesto,
        estado: dept.estado,
        gerente: dept.gerente || 'N/A'
      }));

      const columns = [
        { header: 'Departamento', field: 'nombre', width: 25 },
        { header: 'Descripción', field: 'descripcion', width: 35 },
        { header: 'Empleados', field: 'empleados', width: 12 },
        { header: 'Presupuesto', field: 'presupuesto', width: 18 },
        { header: 'Estado', field: 'estado', width: 12 },
        { header: 'Gerente', field: 'gerente', width: 25 }
      ];

      const options = {
        title: 'Reporte General de Recursos Humanos',
        subtitle: `Total Empleados: ${this.totalEmployees()} | Activos: ${this.activeEmployees()} | Inactivos: ${this.inactiveEmployees()}`,
        filename: `reporte-general-${new Date().getTime()}`,
        includeDate: true
      };

      await this.exportService.exportToExcel(exportData, columns, options);
      this.notificationService.success('Excel Generado', 'El reporte se ha exportado correctamente');
    } catch (error) {
      console.error('Error al exportar Excel:', error);
      this.notificationService.error('Error al Exportar', 'No se pudo generar el archivo Excel');
    }
  }

  print() {
    window.print();
  }
}

