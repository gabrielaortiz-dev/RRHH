import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { CardModule } from 'primeng/card';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';

interface PaymentHistory {
  id: number;
  employeeId: number;
  employeeName: string;
  period: string;
  netSalary: number;
  paymentDate: Date;
  paymentMethod: string;
  receiptNumber: string;
  status: string;
}

@Component({
  selector: 'app-payroll-history',
  standalone: true,
  imports: [
    CommonModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    TagModule,
    TooltipModule,
    CardModule,
    SelectModule,
    DatePickerModule
  ],
  templateUrl: './payroll-history.html',
  styleUrl: './payroll-history.css'
})
export class PayrollHistory {
  paymentHistory = signal<PaymentHistory[]>([
    {
      id: 1,
      employeeId: 1,
      employeeName: 'Juan Pérez',
      period: 'Enero 2024',
      netSalary: 24000,
      paymentDate: new Date('2024-01-31'),
      paymentMethod: 'Transferencia',
      receiptNumber: 'REC-2024-001',
      status: 'Pagado'
    },
    {
      id: 2,
      employeeId: 1,
      employeeName: 'Juan Pérez',
      period: 'Febrero 2024',
      netSalary: 24000,
      paymentDate: new Date('2024-02-29'),
      paymentMethod: 'Transferencia',
      receiptNumber: 'REC-2024-002',
      status: 'Pagado'
    }
  ]);

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('es-DO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  getSeverity(status: string): 'success' | 'warn' | 'danger' {
    switch (status) {
      case 'Pagado':
        return 'success';
      case 'Pendiente':
        return 'warn';
      case 'Cancelado':
        return 'danger';
      default:
        return 'warn';
    }
  }

  downloadReceipt(receipt: PaymentHistory) {
    // Implementar descarga de recibo PDF
    console.log('Descargando recibo:', receipt.receiptNumber);
  }
}

