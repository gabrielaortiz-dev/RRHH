import { Injectable, signal, inject } from '@angular/core';
import { NotificationService } from './notification.service';
import { NotificationType, NotificationModule } from '../models/notification.model';

export interface Department {
  id: number;
  nombre: string;
  descripcion: string;
  gerente: string;
  numeroEmpleados: number;
  presupuesto: number;
  estado: 'Activo' | 'Inactivo';
  fechaCreacion: Date;
}

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {
  private notificationService = inject(NotificationService);
  
  private departments = signal<Department[]>([
    {
      id: 1,
      nombre: 'Tecnología',
      descripcion: 'Departamento encargado del desarrollo y mantenimiento de sistemas',
      gerente: 'Juan Pérez',
      numeroEmpleados: 3,
      presupuesto: 250000,
      estado: 'Activo',
      fechaCreacion: new Date('2020-01-15')
    },
    {
      id: 2,
      nombre: 'Recursos Humanos',
      descripcion: 'Gestión del talento humano y desarrollo organizacional',
      gerente: 'María García',
      numeroEmpleados: 1,
      presupuesto: 150000,
      estado: 'Activo',
      fechaCreacion: new Date('2019-06-20')
    },
    {
      id: 3,
      nombre: 'Finanzas',
      descripcion: 'Administración financiera y contabilidad',
      gerente: 'Carlos Rodríguez',
      numeroEmpleados: 1,
      presupuesto: 180000,
      estado: 'Activo',
      fechaCreacion: new Date('2019-03-10')
    }
  ]);

  private nextId = 4;

  /**
   * Obtiene todos los departamentos
   */
  getDepartments() {
    return this.departments.asReadonly();
  }

  /**
   * Obtiene la cantidad total de departamentos
   */
  getTotalDepartments(): number {
    return this.departments().length;
  }

  /**
   * Obtiene la cantidad de departamentos activos
   */
  getActiveDepartments(): number {
    return this.departments().filter(dept => dept.estado === 'Activo').length;
  }

  /**
   * Obtiene un departamento por ID
   */
  getDepartmentById(id: number): Department | undefined {
    return this.departments().find(dept => dept.id === id);
  }

  /**
   * Agrega un nuevo departamento
   */
  addDepartment(department: Omit<Department, 'id'>): Department {
    const newDepartment: Department = {
      ...department,
      id: this.nextId++
    };
    this.departments.update(depts => [...depts, newDepartment]);
    
    // Notificar al administrador sobre el nuevo departamento
    this.notificationService.createNotification({
      userId: 'admin@rrhh.com',
      type: NotificationType.SUCCESS,
      title: 'Nuevo Departamento Creado',
      message: `El departamento "${newDepartment.nombre}" ha sido creado exitosamente`,
      module: NotificationModule.DEPARTMENTS,
      moduleId: newDepartment.id.toString(),
      redirectUrl: `/departamentos`
    });
    
    return newDepartment;
  }

  /**
   * Actualiza un departamento existente
   */
  updateDepartment(id: number, department: Partial<Department>): boolean {
    const index = this.departments().findIndex(dept => dept.id === id);
    if (index !== -1) {
      const originalDepartment = this.departments()[index];
      this.departments.update(depts => {
        const updated = [...depts];
        updated[index] = { ...updated[index], ...department };
        return updated;
      });
      
      // Notificar si hay cambios importantes
      if (department.estado && department.estado !== originalDepartment.estado) {
        const type = department.estado === 'Activo' ? NotificationType.SUCCESS : NotificationType.WARNING;
        this.notificationService.createNotification({
          userId: 'admin@rrhh.com',
          type,
          title: 'Cambio de Estado de Departamento',
          message: `El departamento "${originalDepartment.nombre}" ha sido ${department.estado === 'Activo' ? 'activado' : 'desactivado'}`,
          module: NotificationModule.DEPARTMENTS,
          moduleId: id.toString(),
          redirectUrl: `/departamentos`
        });
      }
      
      return true;
    }
    return false;
  }

  /**
   * Elimina un departamento
   */
  deleteDepartment(id: number): boolean {
    const department = this.getDepartmentById(id);
    const initialLength = this.departments().length;
    this.departments.update(depts => depts.filter(dept => dept.id !== id));
    
    if (this.departments().length < initialLength && department) {
      // Notificar sobre la eliminación
      this.notificationService.createNotification({
        userId: 'admin@rrhh.com',
        type: NotificationType.WARNING,
        title: 'Departamento Eliminado',
        message: `El departamento "${department.nombre}" ha sido eliminado del sistema`,
        module: NotificationModule.DEPARTMENTS
      });
    }
    
    return this.departments().length < initialLength;
  }

  /**
   * Obtiene el presupuesto total
   */
  getTotalBudget(): number {
    return this.departments().reduce((sum, dept) => sum + dept.presupuesto, 0);
  }

  /**
   * Obtiene el total de empleados en todos los departamentos
   */
  getTotalEmployeesInDepartments(): number {
    return this.departments().reduce((sum, dept) => sum + dept.numeroEmpleados, 0);
  }
}

