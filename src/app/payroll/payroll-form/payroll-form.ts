import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { TableModule } from 'primeng/table';

@Component({
  selector: 'app-payroll-form',
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
    TableModule
  ],
  providers: [MessageService],
  templateUrl: './payroll-form.html',
  styleUrl: './payroll-form.css'
})
export class PayrollForm implements OnInit {
  private fb = inject(FormBuilder);
  private messageService = inject(MessageService);
  private router = inject(Router);

  payrollForm!: FormGroup;
  submitted = false;

  // Bonificaciones y deducciones
  bonuses = signal<Array<{description: string, amount: number}>>([]);
  deductions = signal<Array<{description: string, amount: number}>>([]);

  // Cálculos
  totalBonuses = signal(0);
  totalDeductions = signal(0);
  netSalary = signal(0);

  employees = [
    { label: 'Juan Pérez', value: 1 },
    { label: 'María González', value: 2 },
    { label: 'Carlos Rodríguez', value: 3 }
  ];

  bonusTypes = [
    { label: 'Bono de Productividad', value: 'productividad' },
    { label: 'Bono de Asistencia', value: 'asistencia' },
    { label: 'Bono Extraordinario', value: 'extraordinario' },
    { label: 'Otro', value: 'otro' }
  ];

  deductionTypes = [
    { label: 'ISR (Impuesto sobre la Renta)', value: 'isr' },
    { label: 'Seguro Social', value: 'seguro' },
    { label: 'Préstamo', value: 'prestamo' },
    { label: 'Otro', value: 'otro' }
  ];

  ngOnInit() {
    this.payrollForm = this.fb.group({
      employeeId: ['', Validators.required],
      period: ['', Validators.required],
      baseSalary: [0, [Validators.required, Validators.min(0)]],
      bonusDescription: [''],
      bonusAmount: [0, [Validators.min(0)]],
      deductionDescription: [''],
      deductionAmount: [0, [Validators.min(0)]]
    });

    // Calcular salario neto cuando cambian los valores
    this.payrollForm.get('baseSalary')?.valueChanges.subscribe(() => this.calculateNetSalary());
  }

  addBonus() {
    const description = this.payrollForm.get('bonusDescription')?.value;
    const amount = this.payrollForm.get('bonusAmount')?.value;
    
    if (description && amount > 0) {
      this.bonuses.update(list => [...list, { description, amount }]);
      this.payrollForm.patchValue({ bonusDescription: '', bonusAmount: 0 });
      this.calculateNetSalary();
    }
  }

  removeBonus(index: number) {
    this.bonuses.update(list => list.filter((_, i) => i !== index));
    this.calculateNetSalary();
  }

  addDeduction() {
    const description = this.payrollForm.get('deductionDescription')?.value;
    const amount = this.payrollForm.get('deductionAmount')?.value;
    
    if (description && amount > 0) {
      this.deductions.update(list => [...list, { description, amount }]);
      this.payrollForm.patchValue({ deductionDescription: '', deductionAmount: 0 });
      this.calculateNetSalary();
    }
  }

  removeDeduction(index: number) {
    this.deductions.update(list => list.filter((_, i) => i !== index));
    this.calculateNetSalary();
  }

  calculateNetSalary() {
    const baseSalary = this.payrollForm.get('baseSalary')?.value || 0;
    const totalBonuses = this.bonuses().reduce((sum, b) => sum + b.amount, 0);
    const totalDeductions = this.deductions().reduce((sum, d) => sum + d.amount, 0);
    
    this.totalBonuses.set(totalBonuses);
    this.totalDeductions.set(totalDeductions);
    this.netSalary.set(baseSalary + totalBonuses - totalDeductions);
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  onSubmit() {
    this.submitted = true;
    
    if (this.payrollForm.valid) {
      this.messageService.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Nómina calculada exitosamente'
      });
      
      setTimeout(() => {
        this.router.navigate(['/nomina']);
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
    this.router.navigate(['/nomina']);
  }
}

