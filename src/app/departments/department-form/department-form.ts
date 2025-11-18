import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { DepartmentService } from '../../services/department.service';

@Component({
  selector: 'app-department-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CardModule,
    InputTextModule,
    TextareaModule,
    InputNumberModule,
    SelectModule,
    DatePickerModule,
    ButtonModule,
    MessageModule,
    ToastModule
  ],
  providers: [MessageService],
  templateUrl: './department-form.html',
  styleUrl: './department-form.css'
})
export class DepartmentForm {
  private fb = inject(FormBuilder);
  private departmentService = inject(DepartmentService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  departmentForm: FormGroup;
  submitted = false;

  estados = [
    { label: 'Activo', value: 'Activo' },
    { label: 'Inactivo', value: 'Inactivo' }
  ];

  constructor() {
    this.departmentForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      descripcion: ['', [Validators.required, Validators.minLength(10)]],
      gerente: ['', [Validators.required]],
      numeroEmpleados: [0, [Validators.required, Validators.min(0)]],
      presupuesto: [null, [Validators.required, Validators.min(0)]],
      fechaCreacion: [new Date(), Validators.required],
      estado: ['Activo', Validators.required]
    });
  }

  onSubmit() {
    this.submitted = true;

    if (this.departmentForm.valid) {
      const formValue = this.departmentForm.value;
      
      this.departmentService.addDepartment(formValue);

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: `Departamento "${formValue.nombre}" creado correctamente`,
        life: 3000
      });

      setTimeout(() => {
        this.router.navigate(['/departamentos']);
      }, 1500);
    } else {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Por favor complete todos los campos requeridos correctamente',
        life: 3000
      });

      Object.keys(this.departmentForm.controls).forEach(key => {
        this.departmentForm.get(key)?.markAsTouched();
      });
    }
  }

  onCancel() {
    this.router.navigate(['/departamentos']);
  }

  hasError(field: string): boolean {
    const control = this.departmentForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched || this.submitted));
  }

  getErrorMessage(field: string): string {
    const control = this.departmentForm.get(field);
    if (!control || !control.errors) return '';

    if (control.errors['required']) return 'Este campo es requerido';
    if (control.errors['minlength']) {
      return `Mínimo ${control.errors['minlength'].requiredLength} caracteres`;
    }
    if (control.errors['min']) return 'El valor debe ser mayor o igual a 0';

    return 'Campo inválido';
  }
}

