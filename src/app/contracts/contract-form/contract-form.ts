import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { TextareaModule } from 'primeng/textarea';
import { DatePickerModule } from 'primeng/datepicker';
import { MessageService } from 'primeng/api';
import { ContractService, Contrato } from '../../services/contract.service';
import { EmployeeService } from '../../services/employee.service';

@Component({
  selector: 'app-contract-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CardModule,
    InputTextModule,
    InputNumberModule,
    SelectModule,
    ButtonModule,
    ToastModule,
    TextareaModule,
    DatePickerModule
  ],
  providers: [MessageService],
  templateUrl: './contract-form.html',
  styleUrl: './contract-form.css'
})
export class ContractForm implements OnInit {
  private fb = inject(FormBuilder);
  private contractService = inject(ContractService);
  private employeeService = inject(EmployeeService);
  private messageService = inject(MessageService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  contractForm!: FormGroup;
  empleados = signal<any[]>([]);
  loading = signal(false);
  isEdit = signal(false);
  contratoId = signal<number | null>(null);
  
  // Secciones colapsables
  showPrincipal = signal(true);
  showFechas = signal(true);
  showSalarial = signal(true);
  showCondiciones = signal(true);
  
  tiposContrato = [
    { label: 'Temporal', value: 'temporal' },
    { label: 'Permanente', value: 'permanente' },
    { label: 'Honorarios', value: 'honorarios' }
  ];

  ngOnInit() {
    this.initForm();
    this.cargarEmpleados();
    
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEdit.set(true);
      this.contratoId.set(+id);
      this.cargarContrato(+id);
    }
  }

  initForm() {
    this.contractForm = this.fb.group({
      id_empleado: ['', Validators.required],
      tipo_contrato: ['', Validators.required],
      fecha_inicio: ['', Validators.required],
      fecha_fin: [''],
      salario: ['', [Validators.required, Validators.min(0)]],
      condiciones: ['']
    });
  }

  cargarEmpleados() {
    const employeesSignal = this.employeeService.getEmployees();
    this.empleados.set(employeesSignal());
  }

  cargarContrato(id: number) {
    this.loading.set(true);
    this.contractService.getContrato(id).subscribe({
      next: (response) => {
        if (response.success && response.data && !Array.isArray(response.data)) {
          const contrato = response.data as Contrato;
          this.contractForm.patchValue({
            id_empleado: contrato.id_empleado,
            tipo_contrato: contrato.tipo_contrato,
            fecha_inicio: new Date(contrato.fecha_inicio),
            fecha_fin: contrato.fecha_fin ? new Date(contrato.fecha_fin) : null,
            salario: contrato.salario,
            condiciones: contrato.condiciones || ''
          });
        }
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo cargar el contrato'
        });
      }
    });
  }

  onSubmit() {
    if (this.contractForm.valid) {
      this.loading.set(true);
      const formValue = this.contractForm.value;
      
      const contratoData = {
        id_empleado: formValue.id_empleado,
        tipo_contrato: formValue.tipo_contrato,
        fecha_inicio: formValue.fecha_inicio.toISOString().split('T')[0],
        fecha_fin: formValue.fecha_fin ? formValue.fecha_fin.toISOString().split('T')[0] : undefined,
        salario: formValue.salario,
        condiciones: formValue.condiciones || undefined
      };

      if (this.isEdit() && this.contratoId()) {
        this.contractService.updateContrato(this.contratoId()!, contratoData).subscribe({
          next: (response) => {
            if (response.success) {
              this.messageService.add({
                severity: 'success',
                summary: 'Éxito',
                detail: 'Contrato actualizado exitosamente'
              });
              this.router.navigate(['/contratos']);
            } else {
              this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: response.message || 'Error al actualizar el contrato'
              });
            }
            this.loading.set(false);
          },
          error: () => {
            this.loading.set(false);
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Error al actualizar el contrato'
            });
          }
        });
      } else {
        this.contractService.createContrato(contratoData).subscribe({
          next: (response) => {
            if (response.success) {
              this.messageService.add({
                severity: 'success',
                summary: 'Éxito',
                detail: 'Contrato creado exitosamente'
              });
              this.router.navigate(['/contratos']);
            } else {
              this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: response.message || 'Error al crear el contrato'
              });
            }
            this.loading.set(false);
          },
          error: () => {
            this.loading.set(false);
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Error al crear el contrato'
            });
          }
        });
      }
    } else {
      this.markFormGroupTouched();
      this.messageService.add({
        severity: 'warn',
        summary: 'Validación',
        detail: 'Por favor complete todos los campos requeridos'
      });
    }
  }

  markFormGroupTouched() {
    Object.keys(this.contractForm.controls).forEach(key => {
      const control = this.contractForm.get(key);
      control?.markAsTouched();
    });
  }

  cancel() {
    this.router.navigate(['/contratos']);
  }
}

