import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { SelectModule } from 'primeng/select';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { DatePickerModule } from 'primeng/datepicker';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { MessageService } from 'primeng/api';
import { AttendanceService } from '../../services/attendance.service';
import { EmployeeService } from '../../services/employee.service';

@Component({
  selector: 'app-attendance-register',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    SelectModule,
    ButtonModule,
    ToastModule,
    DatePickerModule,
    InputTextModule,
    TextareaModule
  ],
  providers: [MessageService],
  templateUrl: './attendance-register.html',
  styleUrl: './attendance-register.css'
})
export class AttendanceRegister implements OnInit {
  private fb = inject(FormBuilder);
  private attendanceService = inject(AttendanceService);
  private employeeService = inject(EmployeeService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  attendanceForm!: FormGroup;
  empleados = signal<any[]>([]);
  loading = signal(false);
  metodoRegistro = signal<'manual' | 'biometrico'>('manual');

  ngOnInit() {
    this.initForm();
    this.cargarEmpleados();
  }

  initForm() {
    const hoy = new Date();
    this.attendanceForm = this.fb.group({
      id_empleado: ['', Validators.required],
      fecha: [hoy, Validators.required],
      hora_entrada: [''],
      hora_salida: [''],
      observaciones: ['']
    });
  }

  cargarEmpleados() {
    const employeesSignal = this.employeeService.getEmployees();
    this.empleados.set(employeesSignal());
  }

  onSubmit() {
    if (this.attendanceForm.valid) {
      this.loading.set(true);
      const formValue = this.attendanceForm.value;
      
      const asistenciaData = {
        id_empleado: formValue.id_empleado,
        fecha: formValue.fecha.toISOString().split('T')[0],
        hora_entrada: formValue.hora_entrada || undefined,
        hora_salida: formValue.hora_salida || undefined,
        observaciones: formValue.observaciones || undefined,
        metodo_registro: this.metodoRegistro()
      };

      this.attendanceService.registrarAsistencia(asistenciaData).subscribe({
        next: (response) => {
          if (response.success) {
            this.messageService.add({
              severity: 'success',
              summary: 'Éxito',
              detail: response.message || 'Asistencia registrada exitosamente'
            });
            this.router.navigate(['/asistencias']);
          } else {
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: response.message || 'Error al registrar la asistencia'
            });
          }
          this.loading.set(false);
        },
        error: () => {
          this.loading.set(false);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Error al registrar la asistencia'
          });
        }
      });
    } else {
      this.markFormGroupTouched();
      this.messageService.add({
        severity: 'warn',
        summary: 'Validación',
        detail: 'Por favor complete todos los campos requeridos'
      });
    }
  }

  marcarEntrada() {
    const horaActual = new Date().toTimeString().split(' ')[0].substring(0, 5) + ':00';
    this.attendanceForm.patchValue({ hora_entrada: horaActual });
  }

  marcarSalida() {
    const horaActual = new Date().toTimeString().split(' ')[0].substring(0, 5) + ':00';
    this.attendanceForm.patchValue({ hora_salida: horaActual });
  }

  markFormGroupTouched() {
    Object.keys(this.attendanceForm.controls).forEach(key => {
      const control = this.attendanceForm.get(key);
      control?.markAsTouched();
    });
  }

  cancel() {
    this.router.navigate(['/asistencias']);
  }
}

