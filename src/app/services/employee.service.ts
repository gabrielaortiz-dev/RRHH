import { Injectable, signal } from '@angular/core';

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
  private employees = signal<Employee[]>([
    {
      id: 1,
      nombre: 'Juan',
      apellido: 'Pérez',
      email: 'juan.perez@empresa.com',
      telefono: '809-555-1234',
      puesto: 'Desarrollador Senior',
      departamento: 'Tecnología',
      salario: 75000,
      fechaIngreso: new Date('2020-01-15'),
      estado: 'Activo',
      direccion: 'Calle Principal #123, Santo Domingo',
      cedula: '001-1234567-8',
      fechaNacimiento: new Date('1990-05-15'),
      genero: 'Masculino',
      estadoCivil: 'Casado',
      nacionalidad: 'Hondureña',
      foto: 'https://ui-avatars.com/api/?name=Juan+Perez&background=667eea&color=fff&size=200',
      contactoEmergencia: {
        nombre: 'María Pérez',
        telefono: '809-555-9999',
        relacion: 'Esposa'
      },
      historialLaboral: [
        {
          id: 1,
          empresa: 'Tech Solutions',
          puesto: 'Desarrollador Junior',
          fechaInicio: new Date('2018-01-01'),
          fechaFin: new Date('2019-12-31'),
          descripcion: 'Desarrollo de aplicaciones web con React y Node.js',
          motivoSalida: 'Mejor oportunidad laboral'
        }
      ],
      historialAcademico: [
        {
          id: 1,
          institucion: 'Universidad Nacional',
          titulo: 'Ingeniería en Sistemas',
          nivel: 'Universitario',
          fechaInicio: new Date('2012-01-01'),
          fechaFin: new Date('2017-12-31'),
          estado: 'Completado'
        }
      ],
      documentos: [
        {
          id: 1,
          nombre: 'CV_Juan_Perez.pdf',
          tipo: 'CV',
          url: '#',
          fechaSubida: new Date('2023-01-15'),
          tamano: 245000
        }
      ]
    },
    {
      id: 2,
      nombre: 'María',
      apellido: 'García',
      email: 'maria.garcia@empresa.com',
      telefono: '809-555-5678',
      puesto: 'Gerente de RRHH',
      departamento: 'Recursos Humanos',
      salario: 85000,
      fechaIngreso: new Date('2019-06-20'),
      estado: 'Activo',
      direccion: 'Av. 27 de Febrero #456, Santo Domingo',
      cedula: '001-2345678-9',
      fechaNacimiento: new Date('1985-08-22'),
      genero: 'Femenino',
      estadoCivil: 'Soltero',
      nacionalidad: 'Hondureña',
      foto: 'https://ui-avatars.com/api/?name=Maria+Garcia&background=764ba2&color=fff&size=200',
      contactoEmergencia: {
        nombre: 'Pedro García',
        telefono: '809-555-8888',
        relacion: 'Padre'
      },
      historialLaboral: [],
      historialAcademico: [
        {
          id: 1,
          institucion: 'Universidad Autónoma',
          titulo: 'Licenciatura en Psicología',
          nivel: 'Universitario',
          fechaInicio: new Date('2007-01-01'),
          fechaFin: new Date('2012-12-31'),
          estado: 'Completado'
        },
        {
          id: 2,
          institucion: 'Instituto de Especialización',
          titulo: 'Maestría en Recursos Humanos',
          nivel: 'Maestría',
          fechaInicio: new Date('2015-01-01'),
          fechaFin: new Date('2017-06-30'),
          estado: 'Completado'
        }
      ],
      documentos: []
    },
    {
      id: 3,
      nombre: 'Carlos',
      apellido: 'Rodríguez',
      email: 'carlos.rodriguez@empresa.com',
      telefono: '809-555-9012',
      puesto: 'Contador',
      departamento: 'Finanzas',
      salario: 65000,
      fechaIngreso: new Date('2021-03-10'),
      estado: 'Suspendido',
      direccion: 'Calle Duarte #789, Santiago',
      cedula: '001-3456789-0',
      fechaNacimiento: new Date('1992-03-10'),
      genero: 'Masculino',
      estadoCivil: 'Soltero',
      nacionalidad: 'Hondureña',
      motivoSuspension: 'Investigación administrativa',
      fechaSuspension: new Date('2024-10-15'),
      foto: 'https://ui-avatars.com/api/?name=Carlos+Rodriguez&background=f59e0b&color=fff&size=200',
      contactoEmergencia: {
        nombre: 'Ana Rodríguez',
        telefono: '809-555-7777',
        relacion: 'Madre'
      },
      historialLaboral: [],
      historialAcademico: [
        {
          id: 1,
          institucion: 'Universidad de Contaduría',
          titulo: 'Contaduría Pública',
          nivel: 'Universitario',
          fechaInicio: new Date('2014-01-01'),
          fechaFin: new Date('2019-12-31'),
          estado: 'Completado'
        }
      ],
      documentos: []
    },
    {
      id: 4,
      nombre: 'Ana',
      apellido: 'Martínez',
      email: 'ana.martinez@empresa.com',
      telefono: '809-555-3456',
      puesto: 'Diseñadora UX/UI',
      departamento: 'Tecnología',
      salario: 70000,
      fechaIngreso: new Date('2021-09-01'),
      estado: 'Activo',
      direccion: 'Calle El Sol #321, Santo Domingo',
      cedula: '001-4567890-1',
      fechaNacimiento: new Date('1995-11-05'),
      genero: 'Femenino',
      estadoCivil: 'Soltero',
      nacionalidad: 'Hondureña',
      foto: 'https://ui-avatars.com/api/?name=Ana+Martinez&background=10b981&color=fff&size=200',
      contactoEmergencia: {
        nombre: 'Luis Martínez',
        telefono: '809-555-6666',
        relacion: 'Hermano'
      },
      historialLaboral: [],
      historialAcademico: [
        {
          id: 1,
          institucion: 'Escuela de Diseño',
          titulo: 'Diseño Gráfico',
          nivel: 'Universitario',
          fechaInicio: new Date('2016-01-01'),
          fechaFin: new Date('2020-12-31'),
          estado: 'Completado'
        }
      ],
      documentos: []
    },
    {
      id: 5,
      nombre: 'Luis',
      apellido: 'Fernández',
      email: 'luis.fernandez@empresa.com',
      telefono: '809-555-7890',
      puesto: 'Analista de Datos',
      departamento: 'Tecnología',
      salario: 68000,
      fechaIngreso: new Date('2022-01-15'),
      estado: 'Retirado',
      direccion: 'Av. Independencia #654, Santo Domingo',
      cedula: '001-5678901-2',
      fechaNacimiento: new Date('1988-07-20'),
      genero: 'Masculino',
      estadoCivil: 'Divorciado',
      nacionalidad: 'Hondureña',
      fechaRetiro: new Date('2024-09-30'),
      motivoRetiro: 'Renuncia voluntaria - Mejor oferta laboral',
      foto: 'https://ui-avatars.com/api/?name=Luis+Fernandez&background=ef4444&color=fff&size=200',
      contactoEmergencia: {
        nombre: 'Carmen Fernández',
        telefono: '809-555-5555',
        relacion: 'Hermana'
      },
      historialLaboral: [],
      historialAcademico: [
        {
          id: 1,
          institucion: 'Universidad Tecnológica',
          titulo: 'Ingeniería Industrial',
          nivel: 'Universitario',
          fechaInicio: new Date('2010-01-01'),
          fechaFin: new Date('2015-12-31'),
          estado: 'Completado'
        }
      ],
      documentos: []
    }
  ]);

  private nextId = 6;
  private nextWorkHistoryId = 100;
  private nextAcademicHistoryId = 200;
  private nextDocumentId = 300;

  /**
   * Obtiene todos los empleados
   */
  getEmployees() {
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
    const newEmployee: Employee = {
      ...employee,
      id: this.nextId++,
      historialLaboral: employee.historialLaboral || [],
      historialAcademico: employee.historialAcademico || [],
      documentos: employee.documentos || []
    };
    this.employees.update(emps => [...emps, newEmployee]);
    return newEmployee;
  }

  /**
   * Actualiza un empleado existente
   */
  updateEmployee(id: number, employee: Partial<Employee>): boolean {
    const index = this.employees().findIndex(emp => emp.id === id);
    if (index !== -1) {
      this.employees.update(emps => {
        const updated = [...emps];
        updated[index] = { ...updated[index], ...employee };
        return updated;
      });
      return true;
    }
    return false;
  }

  /**
   * Elimina un empleado
   */
  deleteEmployee(id: number): boolean {
    const initialLength = this.employees().length;
    this.employees.update(emps => emps.filter(emp => emp.id !== id));
    return this.employees().length < initialLength;
  }

  /**
   * Agrega historial laboral a un empleado
   */
  addWorkHistory(employeeId: number, workHistory: Omit<WorkHistory, 'id'>): boolean {
    const index = this.employees().findIndex(emp => emp.id === employeeId);
    if (index !== -1) {
      const newWorkHistory: WorkHistory = {
        ...workHistory,
        id: this.nextWorkHistoryId++
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
        id: this.nextAcademicHistoryId++
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
        id: this.nextDocumentId++
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
    const index = this.employees().findIndex(emp => emp.id === employeeId);
    if (index !== -1) {
      this.employees.update(emps => {
        const updated = [...emps];
        updated[index].estado = status;
        
        if (status === 'Suspendido') {
          updated[index].motivoSuspension = reason;
          updated[index].fechaSuspension = date || new Date();
        } else if (status === 'Retirado') {
          updated[index].motivoRetiro = reason;
          updated[index].fechaRetiro = date || new Date();
        }
        
        return updated;
      });
      return true;
    }
    return false;
  }
}
