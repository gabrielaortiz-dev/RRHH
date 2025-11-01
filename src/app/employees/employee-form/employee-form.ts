import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';
import { ToastModule } from 'primeng/toast';
import { FileUploadModule } from 'primeng/fileupload';
import { ImageModule } from 'primeng/image';
import { TableModule } from 'primeng/table';
import { DialogModule } from 'primeng/dialog';
import { TextareaModule } from 'primeng/textarea';
import { MessageService, SharedModule } from 'primeng/api';
import { EmployeeService, WorkHistory, AcademicHistory, DocumentFile } from '../../services/employee.service';

@Component({
  selector: 'app-employee-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CardModule,
    InputTextModule,
    InputNumberModule,
    SelectModule,
    DatePickerModule,
    ButtonModule,
    MessageModule,
    ToastModule,
    FileUploadModule,
    ImageModule,
    TableModule,
    DialogModule,
    TextareaModule,
    SharedModule
  ],
  providers: [MessageService],
  templateUrl: './employee-form.html',
  styleUrl: './employee-form.css'
})
export class EmployeeForm {
  private fb = inject(FormBuilder);
  private employeeService = inject(EmployeeService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  // Forms
  personalForm: FormGroup;
  laboralForm: FormGroup;
  
  // Datos
  employeePhoto = signal<string>('');
  workHistoryList: WorkHistory[] = [];
  academicHistoryList: AcademicHistory[] = [];
  documentsList: DocumentFile[] = [];
  
  // Dialogs
  showWorkHistoryDialog = signal(false);
  showAcademicHistoryDialog = signal(false);
  workHistoryForm: FormGroup;
  academicHistoryForm: FormGroup;
  
  // Secciones colapsables
  showPersonalData = signal(true);
  showLaboralData = signal(false);
  showWorkHistory = signal(false);
  showAcademicHistory = signal(false);
  showDocuments = signal(false);
  
  submitted = false;

  // Opciones de Select
  departamentos = [
    { label: 'Tecnología', value: 'Tecnología' },
    { label: 'Recursos Humanos', value: 'Recursos Humanos' },
    { label: 'Finanzas', value: 'Finanzas' },
    { label: 'Ventas', value: 'Ventas' },
    { label: 'Marketing', value: 'Marketing' },
    { label: 'Operaciones', value: 'Operaciones' }
  ];

  puestos = [
    { label: 'Desarrollador Junior', value: 'Desarrollador Junior' },
    { label: 'Desarrollador Senior', value: 'Desarrollador Senior' },
    { label: 'Diseñador UX/UI', value: 'Diseñador UX/UI' },
    { label: 'Gerente de Proyecto', value: 'Gerente de Proyecto' },
    { label: 'Gerente de RRHH', value: 'Gerente de RRHH' },
    { label: 'Analista de Datos', value: 'Analista de Datos' },
    { label: 'Contador', value: 'Contador' },
    { label: 'Ejecutivo de Ventas', value: 'Ejecutivo de Ventas' }
  ];

  estados = [
    { label: 'Activo', value: 'Activo' },
    { label: 'Suspendido', value: 'Suspendido' },
    { label: 'Retirado', value: 'Retirado' }
  ];

  generos = [
    { label: 'Masculino', value: 'Masculino' },
    { label: 'Femenino', value: 'Femenino' },
    { label: 'Otro', value: 'Otro' }
  ];

  estadosCiviles = [
    { label: 'Soltero', value: 'Soltero' },
    { label: 'Casado', value: 'Casado' },
    { label: 'Divorciado', value: 'Divorciado' },
    { label: 'Viudo', value: 'Viudo' }
  ];

  nivelesAcademicos = [
    { label: 'Primaria', value: 'Primaria' },
    { label: 'Secundaria', value: 'Secundaria' },
    { label: 'Técnico', value: 'Técnico' },
    { label: 'Universitario', value: 'Universitario' },
    { label: 'Maestría', value: 'Maestría' },
    { label: 'Doctorado', value: 'Doctorado' }
  ];

  estadosAcademicos = [
    { label: 'En Curso', value: 'En Curso' },
    { label: 'Completado', value: 'Completado' },
    { label: 'Abandonado', value: 'Abandonado' }
  ];

  tiposDocumento = [
    { label: 'CV', value: 'CV' },
    { label: 'Certificado', value: 'Certificado' },
    { label: 'Diploma', value: 'Diploma' },
    { label: 'Contrato', value: 'Contrato' },
    { label: 'Identificación', value: 'Identificación' },
    { label: 'Otro', value: 'Otro' }
  ];

  constructor() {
    // Formulario de datos personales
    this.personalForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(2)]],
      apellido: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required]],
      cedula: [''],
      direccion: [''],
      fechaNacimiento: [null],
      genero: [''],
      estadoCivil: [''],
      nacionalidad: ['Hondureña'],
      contactoEmergenciaNombre: [''],
      contactoEmergenciaTelefono: [''],
      contactoEmergenciaRelacion: ['']
    });

    // Formulario laboral
    this.laboralForm = this.fb.group({
      puesto: ['', Validators.required],
      departamento: ['', Validators.required],
      salario: [null, [Validators.required, Validators.min(0)]],
      fechaIngreso: [new Date(), Validators.required],
      estado: ['Activo', Validators.required],
      motivoSuspension: [''],
      motivoRetiro: ['']
    });

    // Formulario para historial laboral
    this.workHistoryForm = this.fb.group({
      empresa: ['', Validators.required],
      puesto: ['', Validators.required],
      fechaInicio: [null, Validators.required],
      fechaFin: [null],
      descripcion: [''],
      motivoSalida: ['']
    });

    // Formulario para historial académico
    this.academicHistoryForm = this.fb.group({
      institucion: ['', Validators.required],
      titulo: ['', Validators.required],
      nivel: ['', Validators.required],
      fechaInicio: [null, Validators.required],
      fechaFin: [null],
      estado: ['Completado', Validators.required]
    });
  }

  // Manejo de foto
  onPhotoSelect(event: any) {
    const file = event.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.employeePhoto.set(e.target.result);
      };
      reader.readAsDataURL(file);
      
      this.messageService.add({
        severity: 'success',
        summary: 'Foto cargada',
        detail: 'La foto se ha cargado correctamente',
        life: 2000
      });
    }
  }

  // Historial laboral
  openWorkHistoryDialog() {
    this.workHistoryForm.reset();
    this.showWorkHistoryDialog.set(true);
  }

  addWorkHistory() {
    if (this.workHistoryForm.valid) {
      const workHistory: WorkHistory = {
        id: Date.now(),
        ...this.workHistoryForm.value
      };
      this.workHistoryList.push(workHistory);
      this.showWorkHistoryDialog.set(false);
      this.messageService.add({
        severity: 'success',
        summary: 'Agregado',
        detail: 'Historial laboral agregado',
        life: 2000
      });
    }
  }

  removeWorkHistory(id: number) {
    this.workHistoryList = this.workHistoryList.filter(w => w.id !== id);
  }

  // Historial académico
  openAcademicHistoryDialog() {
    this.academicHistoryForm.reset({ estado: 'Completado' });
    this.showAcademicHistoryDialog.set(true);
  }

  addAcademicHistory() {
    if (this.academicHistoryForm.valid) {
      const academicHistory: AcademicHistory = {
        id: Date.now(),
        ...this.academicHistoryForm.value
      };
      this.academicHistoryList.push(academicHistory);
      this.showAcademicHistoryDialog.set(false);
      this.messageService.add({
        severity: 'success',
        summary: 'Agregado',
        detail: 'Historial académico agregado',
        life: 2000
      });
    }
  }

  removeAcademicHistory(id: number) {
    this.academicHistoryList = this.academicHistoryList.filter(a => a.id !== id);
  }

  // Documentos
  onDocumentSelect(event: any) {
    for (let file of event.files) {
      const document: DocumentFile = {
        id: Date.now() + Math.random(),
        nombre: file.name,
        tipo: 'Otro',
        url: '#',
        fechaSubida: new Date(),
        tamano: file.size
      };
      this.documentsList.push(document);
    }
    
    this.messageService.add({
      severity: 'success',
      summary: 'Documentos cargados',
      detail: `${event.files.length} documento(s) cargado(s)`,
      life: 2000
    });
  }

  removeDocument(id: number) {
    this.documentsList = this.documentsList.filter(d => d.id !== id);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  // Submit final
  onSubmit() {
    this.submitted = true;

    if (this.personalForm.valid && this.laboralForm.valid) {
      const personalData = this.personalForm.value;
      const laboralData = this.laboralForm.value;
      
      const contactoEmergencia = personalData.contactoEmergenciaNombre ? {
        nombre: personalData.contactoEmergenciaNombre,
        telefono: personalData.contactoEmergenciaTelefono,
        relacion: personalData.contactoEmergenciaRelacion
      } : undefined;

      const employeeData = {
        ...personalData,
        ...laboralData,
        foto: this.employeePhoto() || undefined,
        contactoEmergencia,
        historialLaboral: this.workHistoryList,
        historialAcademico: this.academicHistoryList,
        documentos: this.documentsList
      };

      // Eliminar campos del contacto de emergencia del objeto principal
      delete employeeData.contactoEmergenciaNombre;
      delete employeeData.contactoEmergenciaTelefono;
      delete employeeData.contactoEmergenciaRelacion;

      this.employeeService.addEmployee(employeeData);

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: `Empleado ${personalData.nombre} ${personalData.apellido} creado correctamente`,
        life: 3000
      });

      setTimeout(() => {
        this.router.navigate(['/empleados']);
      }, 1500);
    } else {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Complete todos los campos requeridos en Datos Personales e Información Laboral',
        life: 4000
      });

      // Marcar todos los campos como tocados
      Object.keys(this.personalForm.controls).forEach(key => {
        this.personalForm.get(key)?.markAsTouched();
      });
      Object.keys(this.laboralForm.controls).forEach(key => {
        this.laboralForm.get(key)?.markAsTouched();
      });
    }
  }

  onCancel() {
    this.router.navigate(['/empleados']);
  }

  hasError(form: FormGroup, field: string): boolean {
    const control = form.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched || this.submitted));
  }

  getErrorMessage(form: FormGroup, field: string): string {
    const control = form.get(field);
    if (!control || !control.errors) return '';

    if (control.errors['required']) return 'Este campo es requerido';
    if (control.errors['email']) return 'Email inválido';
    if (control.errors['minlength']) {
      return `Mínimo ${control.errors['minlength'].requiredLength} caracteres`;
    }
    if (control.errors['min']) return 'El valor debe ser mayor a 0';

    return 'Campo inválido';
  }
}
