import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { FileUploadModule } from 'primeng/fileupload';
import { TableModule } from 'primeng/table';
import { DialogModule } from 'primeng/dialog';
import { TextareaModule } from 'primeng/textarea';
import { MessageService } from 'primeng/api';
import { PasswordModule } from 'primeng/password';
import { EmployeeService } from '../../services/employee.service';

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
    ToastModule,
    FileUploadModule,
    TableModule,
    DialogModule,
    TextareaModule,
    PasswordModule
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

  // Formularios por sección
  personalForm!: FormGroup;
  laboralForm!: FormGroup;
  documentosForm!: FormGroup;
  bancariaForm!: FormGroup;
  academicaForm!: FormGroup;
  habilidadesForm!: FormGroup;
  emergenciaForm!: FormGroup;
  opcionalesForm!: FormGroup;
  sistemaForm!: FormGroup;

  // Signals para secciones colapsables
  showPersonal = signal(true);
  showLaboral = signal(false);
  showDocumentos = signal(false);
  showBancaria = signal(false);
  showAcademica = signal(false);
  showHabilidades = signal(false);
  showEmergencia = signal(false);
  showOpcionales = signal(false);
  showSistema = signal(false);

  employeePhoto = signal<string>('');
  submitted = false;

  // Opciones de Select
  generos = [
    { label: 'Masculino', value: 'Masculino' },
    { label: 'Femenino', value: 'Femenino' },
    { label: 'Otro', value: 'Otro' }
  ];

  estadosCiviles = [
    { label: 'Soltero/a', value: 'Soltero' },
    { label: 'Casado/a', value: 'Casado' },
    { label: 'Divorciado/a', value: 'Divorciado' },
    { label: 'Viudo/a', value: 'Viudo' },
    { label: 'Unión Libre', value: 'Union Libre' }
  ];

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

  tiposContrato = [
    { label: 'Indefinido', value: 'Indefinido' },
    { label: 'Temporal', value: 'Temporal' },
    { label: 'Por Proyecto', value: 'Por Proyecto' },
    { label: 'Por Servicios', value: 'Por Servicios' },
    { label: 'Prácticas', value: 'Prácticas' }
  ];

  jornadas = [
    { label: 'Tiempo Completo', value: 'Tiempo Completo' },
    { label: 'Medio Tiempo', value: 'Medio Tiempo' },
    { label: 'Por Horas', value: 'Por Horas' },
    { label: 'Mixta', value: 'Mixta' }
  ];

  formasPago = [
    { label: 'Semanal', value: 'Semanal' },
    { label: 'Quincenal', value: 'Quincenal' },
    { label: 'Mensual', value: 'Mensual' },
    { label: 'Por Hora', value: 'Por Hora' }
  ];

  tiposCuenta = [
    { label: 'Ahorros', value: 'Ahorros' },
    { label: 'Corriente', value: 'Corriente' },
    { label: 'Nómina', value: 'Nómina' }
  ];

  nivelesEstudio = [
    { label: 'Primaria', value: 'Primaria' },
    { label: 'Secundaria', value: 'Secundaria' },
    { label: 'Técnico', value: 'Técnico' },
    { label: 'Universitario', value: 'Universitario' },
    { label: 'Maestría', value: 'Maestría' },
    { label: 'Doctorado', value: 'Doctorado' }
  ];

  roles = [
    { label: 'Empleado', value: 'Empleado' },
    { label: 'Supervisor', value: 'Supervisor' },
    { label: 'RRHH', value: 'RRHH' },
    { label: 'Admin', value: 'Admin' }
  ];

  constructor() {
    // 1. Información Personal
    this.personalForm = this.fb.group({
      nombreCompleto: ['', [Validators.required, Validators.minLength(3)]],
      numeroIdentidad: ['', Validators.required],
      fechaNacimiento: [null],
      genero: [''],
      estadoCivil: [''],
      nacionalidad: ['Hondureña'],
      direccion: [''],
      telefonoPersonal: ['', Validators.required],
      telefonoCasa: [''],
      telefonoOficina: [''],
      correoPersonal: ['', [Validators.required, Validators.email]],
      foto: ['']
    });

    // 2. Información Laboral
    this.laboralForm = this.fb.group({
      cargo: ['', Validators.required],
      departamento: ['', Validators.required],
      fechaIngreso: [new Date(), Validators.required],
      tipoContrato: ['', Validators.required],
      jornadaLaboral: ['', Validators.required],
      jefeInmediato: [''],
      numeroEmpleado: [''],
      salarioBase: [null, [Validators.required, Validators.min(0)]],
      formaPago: ['', Validators.required],
      centroTrabajo: ['']
    });

    // 3. Documentos y Datos Legales
    this.documentosForm = this.fb.group({
      copiaIdentidad: [''],
      numeroSeguroSocial: [''],
      numeroRTN: [''],
      documentosContrato: [''],
      firmasDigitales: [''],
      permisosLaborales: ['']
    });

    // 4. Información Bancaria
    this.bancariaForm = this.fb.group({
      nombreBanco: [''],
      tipoCuenta: [''],
      numeroCuenta: [''],
      nombreTitular: ['']
    });

    // 5. Información Académica
    this.academicaForm = this.fb.group({
      nivelEstudios: [''],
      titulosObtenidos: [''],
      certificaciones: [''],
      cursosCapacitaciones: ['']
    });

    // 6. Habilidades y Experiencia
    this.habilidadesForm = this.fb.group({
      añosExperiencia: [null],
      idiomas: [''],
      habilidadesTecnicas: [''],
      habilidadesBlandas: ['']
    });

    // 7. Información de Emergencia
    this.emergenciaForm = this.fb.group({
      nombreContacto: [''],
      relacionContacto: [''],
      telefonoContacto: [''],
      direccionContacto: ['']
    });

    // 8. Datos Opcionales
    this.opcionalesForm = this.fb.group({
      numeroUniforme: [''],
      talla: [''],
      observaciones: [''],
      beneficiosAsignados: [''],
      politicasFirmadas: [''],
      tipoTransporte: ['']
    });

    // 9. Información del Sistema
    this.sistemaForm = this.fb.group({
      usuario: ['', Validators.required],
      contrasena: ['', [Validators.required, Validators.minLength(6)]],
      rol: ['Empleado', Validators.required]
    });
  }

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
        detail: 'La foto se ha cargado correctamente'
      });
    }
  }

  onSubmit() {
    this.submitted = true;

    if (this.personalForm.valid && this.laboralForm.valid && this.sistemaForm.valid) {
      const employeeData = {
        ...this.personalForm.value,
        ...this.laboralForm.value,
        ...this.documentosForm.value,
        ...this.bancariaForm.value,
        ...this.academicaForm.value,
        ...this.habilidadesForm.value,
        ...this.emergenciaForm.value,
        ...this.opcionalesForm.value,
        ...this.sistemaForm.value,
        foto: this.employeePhoto()
      };

      console.log('Datos del empleado:', employeeData);

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Empleado creado correctamente',
        life: 3000
      });

      setTimeout(() => {
        this.router.navigate(['/empleados']);
      }, 1500);
    } else {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Complete todos los campos requeridos',
        life: 4000
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
