import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmationService, MessageService } from 'primeng/api';
import { CardModule } from 'primeng/card';
import { SelectModule } from 'primeng/select';
import { DatePickerModule } from 'primeng/datepicker';

interface Payroll {
  id: number;
  employeeId: number;
  employeeName: string;
  period: string;
  baseSalary: number;
  bonuses: number;
  deductions: number;
  netSalary: number;
  status: string;
  paymentDate: Date;
}

@Component({
  selector: 'app-payroll-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    TableModule,
    ButtonModule,
    InputTextModule,
    TagModule,
    TooltipModule,
    ConfirmDialogModule,
    ToastModule,
    CardModule,
    SelectModule,
    DatePickerModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './payroll-list.html',
  styleUrl: './payroll-list.css'
})
export class PayrollList {
  private confirmationService = inject(ConfirmationService);
  private messageService = inject(MessageService);

  payrolls = signal<Payroll[]>([
    {
      id: 1,
      employeeId: 1,
      employeeName: 'Juan Pérez',
      period: 'Enero 2024',
      baseSalary: 25000,
      bonuses: 2000,
      deductions: 3000,
      netSalary: 24000,
      status: 'Pagado',
      paymentDate: new Date('2024-01-31')
    }
  ]);

  searchValue = signal('');
  selectedPeriod = signal<string>('');

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

  generateReceipt(payroll: Payroll) {
    // Simulación de generación de PDF
    const receiptData = {
      employeeName: payroll.employeeName,
      period: payroll.period,
      baseSalary: payroll.baseSalary,
      bonuses: payroll.bonuses,
      deductions: payroll.deductions,
      netSalary: payroll.netSalary,
      paymentDate: payroll.paymentDate
    };

    // Crear contenido del recibo
    const receiptContent = `
      RECIBO DE NÓMINA
      =================
      
      Empleado: ${receiptData.employeeName}
      Período: ${receiptData.period}
      Fecha de Pago: ${this.formatDate(receiptData.paymentDate)}
      
      DESGLOSE:
      ---------
      Salario Base:     ${this.formatCurrency(receiptData.baseSalary)}
      Bonificaciones:   ${this.formatCurrency(receiptData.bonuses)}
      Deducciones:      ${this.formatCurrency(receiptData.deductions)}
      -------------------------
      SALARIO NETO:     ${this.formatCurrency(receiptData.netSalary)}
      
      Estado: ${payroll.status}
    `;

    // Crear y descargar archivo (simulación)
    const blob = new Blob([receiptContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Recibo_${payroll.employeeName.replace(/\s+/g, '_')}_${payroll.period.replace(/\s+/g, '_')}.txt`;
    link.click();
    window.URL.revokeObjectURL(url);

    this.messageService.add({
      severity: 'success',
      summary: 'Recibo Generado',
      detail: `Recibo PDF generado para ${payroll.employeeName}`
    });
  }

  deletePayroll(payroll: Payroll) {
    this.confirmationService.confirm({
      message: `¿Está seguro que desea eliminar la nómina de ${payroll.employeeName}?`,
      header: 'Confirmar Eliminación',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí, eliminar',
      rejectLabel: 'Cancelar',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.payrolls.update(list => list.filter(p => p.id !== payroll.id));
        this.messageService.add({
          severity: 'success',
          summary: 'Eliminado',
          detail: 'La nómina ha sido eliminada exitosamente'
        });
      }
    });
  }
}

