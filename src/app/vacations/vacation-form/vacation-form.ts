import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { TextareaModule } from 'primeng/textarea';

@Component({
  selector: 'app-vacation-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CardModule,
    InputTextModule,
    SelectModule,
    DatePickerModule,
    ButtonModule,
    ToastModule,
    TextareaModule
  ],
  providers: [MessageService],
  templateUrl: './vacation-form.html',
  styleUrl: './vacation-form.css'
})
export class VacationForm implements OnInit {
  private fb = inject(FormBuilder);
  private messageService = inject(MessageService);
  private router = inject(Router);

  vacationForm!: FormGroup;
  submitted = false;

  employees = [
    { label: 'Juan Pérez', value: 1, availableDays: 15 },
    { label: 'María González', value: 2, availableDays: 20 },
    { label: 'Carlos Rodríguez', value: 3, availableDays: 10 }
  ];

  vacationTypes = [
    { label: 'Vacaciones', value: 'Vacaciones' },
    { label: 'Permiso Personal', value: 'Permiso Personal' },
    { label: 'Permiso Médico', value: 'Permiso Médico' },
    { label: 'Ausencia Justificada', value: 'Ausencia Justificada' },
    { label: 'Permiso por Duelo', value: 'Permiso por Duelo' },
    { label: 'Permiso por Matrimonio', value: 'Permiso por Matrimonio' },
    { label: 'Permiso por Nacimiento', value: 'Permiso por Nacimiento' }
  ];

  selectedEmployee = signal<any>(null);
  availableDays = signal(0);
  calculatedDays = signal(0);

  ngOnInit() {
    this.vacationForm = this.fb.group({
      employeeId: ['', Validators.required],
      type: ['', Validators.required],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      reason: ['', Validators.required]
    });

    // Calcular días cuando cambian las fechas
    this.vacationForm.get('startDate')?.valueChanges.subscribe(() => this.calculateDays());
    this.vacationForm.get('endDate')?.valueChanges.subscribe(() => this.calculateDays());
    this.vacationForm.get('employeeId')?.valueChanges.subscribe((id) => {
      const employee = this.employees.find(e => e.value === id);
      if (employee) {
        this.selectedEmployee.set(employee);
        this.availableDays.set(employee.availableDays);
      }
    });
  }

  calculateDays() {
    const startDate = this.vacationForm.get('startDate')?.value;
    const endDate = this.vacationForm.get('endDate')?.value;
    
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      const diffTime = Math.abs(end.getTime() - start.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      this.calculatedDays.set(diffDays);
    }
  }

  onSubmit() {
    this.submitted = true;
    
    if (this.vacationForm.valid) {
      if (this.calculatedDays() > this.availableDays()) {
        this.messageService.add({
          severity: 'warn',
          summary: 'Advertencia',
          detail: `Los días solicitados (${this.calculatedDays()}) exceden los días disponibles (${this.availableDays()})`
        });
        return;
      }

      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Solicitud de vacaciones creada exitosamente'
      });
      
      setTimeout(() => {
        this.router.navigate(['/vacaciones']);
      }, 1500);
    } else {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Por favor complete todos los campos requeridos'
      });
    }
  }

  onCancel() {
    this.router.navigate(['/vacaciones']);
  }
}

