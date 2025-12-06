import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

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

// Interfaz principal del empleado (compatible con backend)
export interface Employee {
  id?: number;
  id_empleado?: number;
  // Datos Personales
  nombre: string;
  apellido?: string;
  email?: string;
  correo?: string;
  telefono?: string;
  direccion?: string;
  cedula?: string;
  fecha_nacimiento?: string;
  fechaNacimiento?: Date;
  genero?: 'Masculino' | 'Femenino' | 'Otro';
  estado_civil?: string;
  estadoCivil?: 'Soltero' | 'Casado' | 'Divorciado' | 'Viudo';
  nacionalidad?: string;
  
  // Información Laboral
  puesto?: string;
  departamento?: string;
  id_departamento?: number;
  id_puesto?: number; // ID del puesto (compatible con backend)
  salario?: number;
  fecha_ingreso?: string;
  fechaIngreso?: Date;
  estado?: 'Activo' | 'Suspendido' | 'Retirado';
  motivoSuspension?: string;
  fechaSuspension?: Date;
  fechaRetiro?: Date;
  motivoRetiro?: string;
  
  // Campos adicionales del frontend
  foto?: string;
  contactoEmergencia?: {
    nombre: string;
    telefono: string;
    relacion: string;
  };
  historialLaboral?: WorkHistory[];
  historialAcademico?: AcademicHistory[];
  documentos?: DocumentFile[];
}

interface ApiResponse<T> {
  status: string;
  data?: T | T[];
  message?: string;
  count?: number;
}

@Injectable({
  providedIn: 'root'
})
export class EmployeeService {
  private employees = signal<Employee[]>([]);
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  /**
   * Carga todos los empleados desde el backend
   */
  loadEmployees(): Observable<Employee[]> {
    return this.http.get<ApiResponse<Employee[]>>(`${this.apiUrl}/empleados`).pipe(
      map(response => {
        if (response.status === 'success' && response.data) {
          const employees = Array.isArray(response.data) ? response.data : [response.data];
          // Normalizar datos del backend al formato del frontend
          const normalizedEmployees = employees.map(emp => this.normalizeEmployee(emp));
          this.employees.set(normalizedEmployees);
          return normalizedEmployees;
        }
        return [];
      }),
      catchError(error => {
        console.error('Error al cargar empleados:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Normaliza un empleado del formato del backend al formato del frontend
   */
  private normalizeEmployee(emp: any): Employee {
    return {
      id: emp.id_empleado || emp.id,
      id_empleado: emp.id_empleado || emp.id,
      nombre: emp.nombre || '',
      apellido: emp.apellido || '',
      email: emp.correo || emp.email || '',
      correo: emp.correo || emp.email || '',
      telefono: emp.telefono || '',
      direccion: emp.direccion || '',
      cedula: emp.cedula || '',
      fechaNacimiento: emp.fecha_nacimiento ? new Date(emp.fecha_nacimiento) : undefined,
      fecha_nacimiento: emp.fecha_nacimiento,
      genero: emp.genero,
      estadoCivil: emp.estado_civil as any,
      estado_civil: emp.estado_civil,
      fechaIngreso: emp.fecha_ingreso ? new Date(emp.fecha_ingreso) : undefined,
      fecha_ingreso: emp.fecha_ingreso,
      estado: emp.estado,
      id_departamento: emp.id_departamento,
      id_puesto: emp.id_puesto, // Agregado para compatibilidad completa
      historialLaboral: emp.historialLaboral || [],
      historialAcademico: emp.historialAcademico || [],
      documentos: emp.documentos || []
    };
  }

  /**
   * Obtiene todos los empleados
   */
  getEmployees(): Observable<Employee[]> {
    if (this.employees().length === 0) {
      return this.loadEmployees();
    }
    return new Observable(observer => {
      observer.next(this.employees());
      observer.complete();
    });
  }

  /**
   * Obtiene un empleado por ID
   */
  getEmployeeById(id: number): Observable<Employee | null> {
    return this.http.get<ApiResponse<Employee>>(`${this.apiUrl}/empleados/${id}`).pipe(
      map(response => {
        if (response.status === 'success' && response.data) {
          return this.normalizeEmployee(response.data);
        }
        return null;
      }),
      catchError(error => {
        console.error(`Error al obtener empleado ${id}:`, error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Crea un nuevo empleado
   */
  addEmployee(employee: Partial<Employee>): Observable<Employee> {
    // Convertir del formato frontend al formato backend
    const employeeData: any = {
      nombre: employee.nombre || '',
      apellido: employee.apellido || '',
      correo: employee.email || employee.correo || '',
      telefono: employee.telefono || '',
      direccion: employee.direccion || '',
      fecha_nacimiento: employee.fechaNacimiento?.toISOString().split('T')[0] || employee.fecha_nacimiento,
      genero: employee.genero,
      estado_civil: employee.estadoCivil || employee.estado_civil,
      fecha_ingreso: employee.fechaIngreso?.toISOString().split('T')[0] || employee.fecha_ingreso,
      estado: employee.estado || 'Activo',
      id_departamento: employee.id_departamento
    };
    
    // Agregar id_puesto si está disponible (el backend lo acepta como opcional)
    if (employee.id_puesto !== undefined) {
      employeeData.id_puesto = employee.id_puesto;
    }

    return this.http.post<ApiResponse<Employee>>(`${this.apiUrl}/empleados`, employeeData).pipe(
      map(response => {
        if (response.status === 'success' && response.data) {
          const newEmployee = this.normalizeEmployee(response.data);
          this.employees.update(emps => [...emps, newEmployee]);
          return newEmployee;
        }
        throw new Error(response.message || 'Error al crear empleado');
      }),
      catchError(error => {
        console.error('Error al crear empleado:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Actualiza un empleado existente
   */
  updateEmployee(id: number, employee: Partial<Employee>): Observable<Employee> {
    const employeeData: any = {};
    
    if (employee.nombre) employeeData.nombre = employee.nombre;
    if (employee.apellido) employeeData.apellido = employee.apellido;
    if (employee.email || employee.correo) employeeData.correo = employee.email || employee.correo;
    if (employee.telefono) employeeData.telefono = employee.telefono;
    if (employee.direccion) employeeData.direccion = employee.direccion;
    if (employee.fechaNacimiento) employeeData.fecha_nacimiento = employee.fechaNacimiento.toISOString().split('T')[0];
    if (employee.fecha_nacimiento) employeeData.fecha_nacimiento = employee.fecha_nacimiento;
    if (employee.genero) employeeData.genero = employee.genero;
    if (employee.estadoCivil) employeeData.estado_civil = employee.estadoCivil;
    if (employee.estado_civil) employeeData.estado_civil = employee.estado_civil;
    if (employee.fechaIngreso) employeeData.fecha_ingreso = employee.fechaIngreso.toISOString().split('T')[0];
    if (employee.fecha_ingreso) employeeData.fecha_ingreso = employee.fecha_ingreso;
    if (employee.estado) employeeData.estado = employee.estado;
    if (employee.id_departamento !== undefined) employeeData.id_departamento = employee.id_departamento;
    if (employee.id_puesto !== undefined) employeeData.id_puesto = employee.id_puesto;

    return this.http.put<ApiResponse<Employee>>(`${this.apiUrl}/empleados/${id}`, employeeData).pipe(
      map(response => {
        if (response.status === 'success' && response.data) {
          const updatedEmployee = this.normalizeEmployee(response.data);
          this.employees.update(emps => 
            emps.map(emp => emp.id === id ? updatedEmployee : emp)
          );
          return updatedEmployee;
        }
        throw new Error(response.message || 'Error al actualizar empleado');
      }),
      catchError(error => {
        console.error(`Error al actualizar empleado ${id}:`, error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Elimina un empleado
   */
  deleteEmployee(id: number): Observable<boolean> {
    return this.http.delete<ApiResponse<any>>(`${this.apiUrl}/empleados/${id}`).pipe(
      map(response => {
        if (response.status === 'success') {
          this.employees.update(emps => emps.filter(emp => emp.id !== id));
          return true;
        }
        return false;
      }),
      catchError(error => {
        console.error(`Error al eliminar empleado ${id}:`, error);
        return throwError(() => error);
      })
    );
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
   * Obtiene el salario promedio de todos los empleados activos
   */
  getAverageSalary(): number {
    const activeEmployees = this.employees().filter(emp => emp.estado === 'Activo' && emp.salario);
    if (activeEmployees.length === 0) return 0;

    const totalSalary = activeEmployees.reduce((sum, emp) => sum + (emp.salario || 0), 0);
    return totalSalary / activeEmployees.length;
  }

  /**
   * Obtiene empleados agrupados por departamento
   */
  getEmployeesByDepartment(): { [key: string]: number } {
    const departmentCounts: { [key: string]: number } = {};
    this.employees().forEach(emp => {
      const dept = emp.departamento || 'Sin Departamento';
      departmentCounts[dept] = (departmentCounts[dept] || 0) + 1;
    });
    return departmentCounts;
  }
}
