import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, map, of } from 'rxjs';
import { NotificationService } from './notification.service';
import { NotificationType, NotificationModule } from '../models/notification.model';

// Interfaz para historial laboral
export interface WorkHistory {
  id: number;
  empresa: string;
  puesto: string;
  fechaInicio: Date;
  fechaFin?: Date;
  descripcion: string;
  motivoSalida?: string;
}

// Interfaz para historial académico
export interface AcademicHistory {
  id: number;
  institucion: string;
  titulo: string;
  nivel: 'Primaria' | 'Secundaria' | 'Técnico' | 'Universitario' | 'Maestría' | 'Doctorado';
  fechaInicio: Date;
  fechaFin?: Date;
  estado: 'En Curso' | 'Completado' | 'Abandonado';
}

// Interfaz para documentos adjuntos
export interface DocumentFile {
  id: number;
  nombre: string;
  tipo: 'CV' | 'Certificado' | 'Diploma' | 'Contrato' | 'Identificación' | 'Otro';
  descripcion?: string;
  url: string;
  fechaSubida: Date;
  tamano: number; // en bytes
}

// Interfaz principal del empleado
export interface Employee {
  id: number;
  // Datos Personales
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
  direccion?: string;
  cedula?: string;
  fechaNacimiento?: Date;
  genero?: 'Masculino' | 'Femenino' | 'Otro';
  estadoCivil?: 'Soltero' | 'Casado' | 'Divorciado' | 'Viudo';
  nacionalidad?: string;
  
  // Foto de perfil
  foto?: string; // URL de la foto
  
  // Información Laboral
  puesto: string;
  departamento: string;
  salario: number;
  fechaIngreso: Date;
  estado: 'Activo' | 'Suspendido' | 'Retirado';
  motivoSuspension?: string;
  fechaSuspension?: Date;
  fechaRetiro?: Date;
  motivoRetiro?: string;
  
  // Contacto de emergencia
  contactoEmergencia?: {
    nombre: string;
    telefono: string;
    relacion: string;
  };
  
  // Historial laboral y académico
  historialLaboral: WorkHistory[];
  historialAcademico: AcademicHistory[];
  
  // Documentos adjuntos
  documentos: DocumentFile[];
}

@Injectable({
  providedIn: 'root'
})
export class EmployeeService {
  private http = inject(HttpClient);
  private notificationService = inject(NotificationService);
  private apiUrl = 'http://localhost:8000/api';
  
  private employees = signal<Employee[]>([]);
  private loaded = false;

  constructor() {
    this.loadEmployees();
  }

  /**
   * Carga los empleados desde el backend
   */
  private loadEmployees(): void {
    if (this.loaded) return;
    
    this.http.get<{ success: boolean; data: any[] }>(`${this.apiUrl}/empleados`)
      .pipe(
        map(response => {
          if (response.success && response.data) {
            return response.data.map((emp: any): Employee => ({
              id: emp.id,
              nombre: emp.nombre,
              apellido: emp.apellido,
              email: emp.email,
              telefono: emp.telefono || '',
              direccion: undefined,
              cedula: undefined,
              fechaNacimiento: undefined,
              genero: undefined,
              estadoCivil: undefined,
              nacionalidad: undefined,
              foto: `https://ui-avatars.com/api/?name=${encodeURIComponent(emp.nombre + ' ' + emp.apellido)}&background=667eea&color=fff&size=200`,
              puesto: emp.puesto,
              departamento: emp.departamento_nombre || 'Sin departamento',
              salario: emp.salario || 0,
              fechaIngreso: new Date(emp.fecha_ingreso),
              estado: (emp.activo === 1 ? 'Activo' : 'Retirado') as 'Activo' | 'Suspendido' | 'Retirado',
              motivoSuspension: undefined,
              fechaSuspension: undefined,
              fechaRetiro: emp.activo === 0 ? new Date() : undefined,
              motivoRetiro: emp.activo === 0 ? 'Desactivado' : undefined,
              contactoEmergencia: undefined,
              historialLaboral: [],
              historialAcademico: [],
              documentos: []
            }));
          }
          return [];
        }),
        catchError(error => {
          console.error('Error al cargar empleados:', error);
          return [];
        })
      )
      .subscribe(employees => {
        this.employees.set(employees);
        this.loaded = true;
      });
  }

  /**
   * Obtiene todos los empleados
   */
  getEmployees() {
    if (!this.loaded) {
      this.loadEmployees();
    }
    return this.employees.asReadonly();
  }

  /**
   * Obtiene la cantidad total de empleados
   */
  getTotalEmployees(): number {
    return this.employees().length;
  }

  /**
   * Obtiene la cantidad de empleados activos
   */
  getActiveEmployees(): number {
    return this.employees().filter(emp => emp.estado === 'Activo').length;
  }

  /**
   * Obtiene la cantidad de empleados inactivos
   */
  getInactiveEmployees(): number {
    return this.employees().filter(emp => emp.estado !== 'Activo').length;
  }

  /**
   * Obtiene la cantidad de empleados suspendidos
   */
  getSuspendedEmployees(): number {
    return this.employees().filter(emp => emp.estado === 'Suspendido').length;
  }

  /**
   * Obtiene la cantidad de empleados retirados
   */
  getRetiredEmployees(): number {
    return this.employees().filter(emp => emp.estado === 'Retirado').length;
  }

  /**
   * Obtiene un empleado por ID
   */
  getEmployeeById(id: number): Employee | undefined {
    return this.employees().find(emp => emp.id === id);
  }

  /**
   * Agrega un nuevo empleado
   */
  addEmployee(employee: Omit<Employee, 'id'>): Employee {
    // Obtener departamento_id del nombre del departamento
    // Por ahora usaremos 1 como default, deberías tener un servicio de departamentos
    const departamentoId = 1; // TODO: Obtener del servicio de departamentos
    
    const newEmployeeData = {
      nombre: employee.nombre,
      apellido: employee.apellido,
      email: employee.email,
      telefono: employee.telefono || '',
      departamento_id: departamentoId,
      puesto: employee.puesto,
      fecha_ingreso: employee.fechaIngreso.toISOString().split('T')[0],
      salario: employee.salario
    };

    this.http.post<{ success: boolean; data: any }>(
      `${this.apiUrl}/empleados`,
      newEmployeeData
    ).pipe(
      map(response => {
        if (response.success && response.data) {
          const newEmployee: Employee = {
            id: response.data.id,
            nombre: response.data.nombre,
            apellido: response.data.apellido,
            email: response.data.email,
            telefono: response.data.telefono || '',
            direccion: employee.direccion,
            cedula: employee.cedula,
            fechaNacimiento: employee.fechaNacimiento,
            genero: employee.genero,
            estadoCivil: employee.estadoCivil,
            nacionalidad: employee.nacionalidad,
            foto: employee.foto || `https://ui-avatars.com/api/?name=${encodeURIComponent(response.data.nombre + ' ' + response.data.apellido)}&background=667eea&color=fff&size=200`,
            puesto: response.data.puesto,
            departamento: response.data.departamento_nombre || employee.departamento,
            salario: response.data.salario,
            fechaIngreso: new Date(response.data.fecha_ingreso),
            estado: 'Activo',
            contactoEmergencia: employee.contactoEmergencia,
            historialLaboral: employee.historialLaboral || [],
            historialAcademico: employee.historialAcademico || [],
            documentos: employee.documentos || []
          };
          
          this.employees.update(emps => [...emps, newEmployee]);
          
          // Notificar al administrador sobre el nuevo empleado
          this.notificationService.createNotification({
            userId: 'admin@rrhh.com',
            type: NotificationType.SUCCESS,
            title: 'Nuevo Empleado Registrado',
            message: `${newEmployee.nombre} ${newEmployee.apellido} ha sido registrado exitosamente en ${newEmployee.departamento}`,
            module: NotificationModule.EMPLOYEES,
            moduleId: newEmployee.id.toString(),
            redirectUrl: `/empleados`
          });
          
          return newEmployee;
        }
        throw new Error('Error al crear empleado');
      }),
      catchError(error => {
        console.error('Error al crear empleado:', error);
        throw error;
      })
    ).subscribe();

    // Retornar un objeto temporal mientras se procesa
    return {
      id: 0,
      ...employee,
      historialLaboral: employee.historialLaboral || [],
      historialAcademico: employee.historialAcademico || [],
      documentos: employee.documentos || []
    } as Employee;
  }

  /**
   * Actualiza un empleado existente
   */
  updateEmployee(id: number, employee: Partial<Employee>): boolean {
    const updateData: any = {};
    
    if (employee.nombre !== undefined) updateData.nombre = employee.nombre;
    if (employee.apellido !== undefined) updateData.apellido = employee.apellido;
    if (employee.email !== undefined) updateData.email = employee.email;
    if (employee.telefono !== undefined) updateData.telefono = employee.telefono;
    if (employee.puesto !== undefined) updateData.puesto = employee.puesto;
    if (employee.salario !== undefined) updateData.salario = employee.salario;
    if (employee.fechaIngreso !== undefined) {
      updateData.fecha_ingreso = employee.fechaIngreso.toISOString().split('T')[0];
    }
    if (employee.estado !== undefined) {
      updateData.activo = employee.estado === 'Activo' ? 1 : 0;
    }

    this.http.put<{ success: boolean; data: any }>(
      `${this.apiUrl}/empleados/${id}`,
      updateData
    ).pipe(
      map(response => {
        if (response.success) {
          const originalEmployee = this.getEmployeeById(id);
          this.loadEmployees(); // Recargar desde backend
          
          // Notificar si hay cambios importantes
          if (employee.estado && employee.estado !== originalEmployee?.estado) {
            let message = '';
            let type = NotificationType.INFO;
            
            if (employee.estado === 'Suspendido') {
              message = `${originalEmployee?.nombre} ${originalEmployee?.apellido} ha sido suspendido`;
              type = NotificationType.WARNING;
            } else if (employee.estado === 'Retirado') {
              message = `${originalEmployee?.nombre} ${originalEmployee?.apellido} ha sido retirado de la empresa`;
              type = NotificationType.INFO;
            } else if (employee.estado === 'Activo') {
              message = `${originalEmployee?.nombre} ${originalEmployee?.apellido} ha sido reactivado`;
              type = NotificationType.SUCCESS;
            }
            
            if (message) {
              this.notificationService.createNotification({
                userId: 'admin@rrhh.com',
                type,
                title: 'Cambio de Estado de Empleado',
                message,
                module: NotificationModule.EMPLOYEES,
                moduleId: id.toString(),
                redirectUrl: `/empleados`
              });
            }
          }
          
          return true;
        }
        return false;
      }),
      catchError(error => {
        console.error('Error al actualizar empleado:', error);
        return of(false);
      })
    ).subscribe();

    return true;
  }

  /**
   * Elimina un empleado
   */
  deleteEmployee(id: number): boolean {
    const employee = this.getEmployeeById(id);
    
    this.http.delete<{ success: boolean }>(`${this.apiUrl}/empleados/${id}`)
      .pipe(
        map(response => {
          if (response.success) {
            this.employees.update(emps => emps.filter(emp => emp.id !== id));
            
            if (employee) {
              // Notificar sobre la eliminación
              this.notificationService.createNotification({
                userId: 'admin@rrhh.com',
                type: NotificationType.WARNING,
                title: 'Empleado Eliminado',
                message: `El registro de ${employee.nombre} ${employee.apellido} ha sido eliminado del sistema`,
                module: NotificationModule.EMPLOYEES
              });
            }
            
            return true;
          }
          return false;
        }),
        catchError(error => {
          console.error('Error al eliminar empleado:', error);
          return of(false);
        })
      ).subscribe();

    return true;
  }

  /**
   * Agrega historial laboral a un empleado
   */
  addWorkHistory(employeeId: number, workHistory: Omit<WorkHistory, 'id'>): boolean {
    const index = this.employees().findIndex(emp => emp.id === employeeId);
    if (index !== -1) {
      const newWorkHistory: WorkHistory = {
        ...workHistory,
        id: Date.now() // ID temporal
      };
      this.employees.update(emps => {
        const updated = [...emps];
        updated[index].historialLaboral = [...updated[index].historialLaboral, newWorkHistory];
        return updated;
      });
      return true;
    }
    return false;
  }

  /**
   * Agrega historial académico a un empleado
   */
  addAcademicHistory(employeeId: number, academicHistory: Omit<AcademicHistory, 'id'>): boolean {
    const index = this.employees().findIndex(emp => emp.id === employeeId);
    if (index !== -1) {
      const newAcademicHistory: AcademicHistory = {
        ...academicHistory,
        id: Date.now() // ID temporal
      };
      this.employees.update(emps => {
        const updated = [...emps];
        updated[index].historialAcademico = [...updated[index].historialAcademico, newAcademicHistory];
        return updated;
      });
      return true;
    }
    return false;
  }

  /**
   * Agrega documento a un empleado
   */
  addDocument(employeeId: number, document: Omit<DocumentFile, 'id'>): boolean {
    const index = this.employees().findIndex(emp => emp.id === employeeId);
    if (index !== -1) {
      const newDocument: DocumentFile = {
        ...document,
        id: Date.now() // ID temporal
      };
      this.employees.update(emps => {
        const updated = [...emps];
        updated[index].documentos = [...updated[index].documentos, newDocument];
        return updated;
      });
      return true;
    }
    return false;
  }

  /**
   * Elimina un documento
   */
  removeDocument(employeeId: number, documentId: number): boolean {
    const index = this.employees().findIndex(emp => emp.id === employeeId);
    if (index !== -1) {
      this.employees.update(emps => {
        const updated = [...emps];
        updated[index].documentos = updated[index].documentos.filter(doc => doc.id !== documentId);
        return updated;
      });
      return true;
    }
    return false;
  }

  /**
   * Obtiene estadísticas de empleados por departamento
   */
  getEmployeesByDepartment(): { [key: string]: number } {
    const departments: { [key: string]: number } = {};
    this.employees().forEach(emp => {
      departments[emp.departamento] = (departments[emp.departamento] || 0) + 1;
    });
    return departments;
  }

  /**
   * Obtiene el salario promedio
   */
  getAverageSalary(): number {
    const employees = this.employees();
    if (employees.length === 0) return 0;
    const total = employees.reduce((sum, emp) => sum + emp.salario, 0);
    return total / employees.length;
  }

  /**
   * Cambia el estado de un empleado
   */
  changeEmployeeStatus(
    employeeId: number, 
    status: 'Activo' | 'Suspendido' | 'Retirado',
    reason?: string,
    date?: Date
  ): boolean {
    return this.updateEmployee(employeeId, {
      estado: status,
      motivoSuspension: status === 'Suspendido' ? reason : undefined,
      fechaSuspension: status === 'Suspendido' ? (date || new Date()) : undefined,
      motivoRetiro: status === 'Retirado' ? reason : undefined,
      fechaRetiro: status === 'Retirado' ? (date || new Date()) : undefined
    });
  }
}
