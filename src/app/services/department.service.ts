import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, map, of } from 'rxjs';
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
  private http = inject(HttpClient);
  private notificationService = inject(NotificationService);
  private apiUrl = 'http://localhost:8000/api';
  
  private departments = signal<Department[]>([]);
  private loaded = false;

  constructor() {
    this.loadDepartments();
  }

  /**
   * Carga los departamentos desde el backend
   */
  private loadDepartments(): void {
    if (this.loaded) return;
    
    this.http.get<{ success: boolean; data: any[] }>(`${this.apiUrl}/departamentos`)
      .pipe(
        map(response => {
          if (response.success && response.data) {
            return response.data.map((dept: any): Department => ({
              id: dept.id,
              nombre: dept.nombre,
              descripcion: dept.descripcion || '',
              gerente: 'Sin asignar', // Campo no disponible en backend
              numeroEmpleados: 0, // Se calculará después
              presupuesto: 0, // Campo no disponible en backend
              estado: (dept.activo === 1 ? 'Activo' : 'Inactivo') as 'Activo' | 'Inactivo',
              fechaCreacion: new Date(dept.fecha_creacion || Date.now())
            }));
          }
          return [];
        }),
        catchError(error => {
          console.error('Error al cargar departamentos:', error);
          return [];
        })
      )
      .subscribe(departments => {
        this.departments.set(departments);
        this.loaded = true;
      });
  }

  /**
   * Obtiene todos los departamentos
   */
  getDepartments() {
    if (!this.loaded) {
      this.loadDepartments();
    }
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
    const newDepartmentData = {
      nombre: department.nombre,
      descripcion: department.descripcion
    };

    this.http.post<{ success: boolean; data: any }>(
      `${this.apiUrl}/departamentos`,
      newDepartmentData
    ).pipe(
      map(response => {
        if (response.success && response.data) {
          const newDepartment: Department = {
            id: response.data.id,
            nombre: response.data.nombre,
            descripcion: response.data.descripcion || '',
            gerente: department.gerente || 'Sin asignar',
            numeroEmpleados: department.numeroEmpleados || 0,
            presupuesto: department.presupuesto || 0,
            estado: response.data.activo === 1 ? 'Activo' : 'Inactivo',
            fechaCreacion: new Date(response.data.fecha_creacion || Date.now())
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
        throw new Error('Error al crear departamento');
      }),
      catchError(error => {
        console.error('Error al crear departamento:', error);
        throw error;
      })
    ).subscribe();

    // Retornar un objeto temporal mientras se procesa
    return {
      id: 0,
      ...department
    } as Department;
  }

  /**
   * Actualiza un departamento existente
   */
  updateDepartment(id: number, department: Partial<Department>): boolean {
    const updateData: any = {};
    
    if (department.nombre !== undefined) updateData.nombre = department.nombre;
    if (department.descripcion !== undefined) updateData.descripcion = department.descripcion;
    if (department.estado !== undefined) updateData.activo = department.estado === 'Activo';

    this.http.put<{ success: boolean; data: any }>(
      `${this.apiUrl}/departamentos/${id}`,
      updateData
    ).pipe(
      map(response => {
        if (response.success) {
          const originalDepartment = this.getDepartmentById(id);
          this.loadDepartments(); // Recargar desde backend
          
          // Notificar si hay cambios importantes
          if (department.estado && department.estado !== originalDepartment?.estado) {
            const type = department.estado === 'Activo' ? NotificationType.SUCCESS : NotificationType.WARNING;
            this.notificationService.createNotification({
              userId: 'admin@rrhh.com',
              type,
              title: 'Cambio de Estado de Departamento',
              message: `El departamento "${originalDepartment?.nombre}" ha sido ${department.estado === 'Activo' ? 'activado' : 'desactivado'}`,
              module: NotificationModule.DEPARTMENTS,
              moduleId: id.toString(),
              redirectUrl: `/departamentos`
            });
          }
          
          return true;
        }
        return false;
      }),
      catchError(error => {
        console.error('Error al actualizar departamento:', error);
        return of(false);
      })
    ).subscribe();

    return true;
  }

  /**
   * Elimina un departamento
   */
  deleteDepartment(id: number): boolean {
    const department = this.getDepartmentById(id);
    
    this.http.delete<{ success: boolean }>(`${this.apiUrl}/departamentos/${id}`)
      .pipe(
        map(response => {
          if (response.success) {
            this.departments.update(depts => depts.filter(dept => dept.id !== id));
            
            if (department) {
              // Notificar sobre la eliminación
              this.notificationService.createNotification({
                userId: 'admin@rrhh.com',
                type: NotificationType.WARNING,
                title: 'Departamento Eliminado',
                message: `El departamento "${department.nombre}" ha sido eliminado del sistema`,
                module: NotificationModule.DEPARTMENTS
              });
            }
            
            return true;
          }
          return false;
        }),
        catchError(error => {
          console.error('Error al eliminar departamento:', error);
          return of(false);
        })
      ).subscribe();

    return true;
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
