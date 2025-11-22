import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Payroll {
  id_nomina: number;
  id_empleado: number;
  nombre_empleado: string;
  mes: number;
  anio: number;
  periodo: string;
  salario_base: number;
  total_bonificaciones: number;
  total_deducciones: number;
  salario_neto: number;
  fecha_pago: string | null;
  estado: string;
  observaciones?: string;
  bonificaciones_detalle?: BonificacionItem[];
  deducciones_detalle?: DeduccionItem[];
}

export interface BonificacionItem {
  concepto: string;
  tipo?: string;
  monto: number;
  descripcion?: string;
}

export interface DeduccionItem {
  concepto: string;
  tipo?: string;
  monto: number;
  descripcion?: string;
}

export interface PayrollCreate {
  id_empleado: number;
  mes: number;
  anio: number;
  salario_base: number;
  bonificaciones?: BonificacionItem[];
  deducciones?: DeduccionItem[];
  fecha_pago?: string;
  observaciones?: string;
}

export interface ConfigImpuesto {
  id_impuesto: number;
  nombre: string;
  tipo: string;
  porcentaje?: number;
  monto_fijo?: number;
  rango_minimo?: number;
  rango_maximo?: number;
  activo: boolean;
}

export interface ConfigDeduccion {
  id_deduccion_config: number;
  nombre: string;
  tipo: string;
  porcentaje?: number;
  monto_fijo?: number;
  aplica_a_todos: boolean;
  activo: boolean;
}

export interface ConfigBeneficio {
  id_beneficio: number;
  nombre: string;
  tipo: string;
  porcentaje?: number;
  monto_fijo?: number;
  aplica_a_todos: boolean;
  activo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class PayrollService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';

  // Signals para datos
  payrolls = signal<Payroll[]>([]);
  configImpuestos = signal<ConfigImpuesto[]>([]);
  configDeducciones = signal<ConfigDeduccion[]>([]);
  configBeneficios = signal<ConfigBeneficio[]>([]);

  // Obtener todas las nóminas
  getPayrolls(filters?: { id_empleado?: number; mes?: number; anio?: number }): Observable<Payroll[]> {
    let url = `${this.apiUrl}/nomina`;
    const params: string[] = [];
    
    if (filters?.id_empleado) params.push(`id_empleado=${filters.id_empleado}`);
    if (filters?.mes) params.push(`mes=${filters.mes}`);
    if (filters?.anio) params.push(`anio=${filters.anio}`);
    
    if (params.length > 0) url += '?' + params.join('&');
    
    return this.http.get<{ success: boolean; data: Payroll[] }>(url).pipe(
      map(response => {
        this.payrolls.set(response.data);
        return response.data;
      })
    );
  }

  // Obtener nómina por ID
  getPayrollById(id: number): Observable<Payroll> {
    return this.http.get<{ success: boolean; data: Payroll }>(`${this.apiUrl}/nomina/${id}`).pipe(
      map(response => response.data)
    );
  }

  // Crear nómina
  createPayroll(payroll: PayrollCreate): Observable<Payroll> {
    return this.http.post<{ success: boolean; message: string; data: Payroll }>(
      `${this.apiUrl}/nomina`,
      payroll
    ).pipe(
      map(response => {
        this.payrolls.update(list => [response.data, ...list]);
        return response.data;
      })
    );
  }

  // Actualizar nómina
  updatePayroll(id: number, payroll: Partial<PayrollCreate>): Observable<Payroll> {
    return this.http.put<{ success: boolean; message: string; data: Payroll }>(
      `${this.apiUrl}/nomina/${id}`,
      payroll
    ).pipe(
      map(response => {
        this.payrolls.update(list => 
          list.map(p => p.id_nomina === id ? response.data : p)
        );
        return response.data;
      })
    );
  }

  // Obtener historial de un empleado
  getEmployeeHistory(empleadoId: number): Observable<Payroll[]> {
    return this.http.get<{ success: boolean; data: Payroll[] }>(
      `${this.apiUrl}/nomina/empleado/${empleadoId}/historial`
    ).pipe(
      map(response => response.data)
    );
  }

  // Obtener historial de modificaciones
  getPayrollHistory(nominaId: number): Observable<any[]> {
    return this.http.get<{ success: boolean; data: any[] }>(
      `${this.apiUrl}/nomina/${nominaId}/historial`
    ).pipe(
      map(response => response.data)
    );
  }

  // Configuración de Impuestos
  getConfigImpuestos(): Observable<ConfigImpuesto[]> {
    return this.http.get<{ success: boolean; data: ConfigImpuesto[] }>(
      `${this.apiUrl}/nomina/config/impuestos`
    ).pipe(
      map(response => {
        this.configImpuestos.set(response.data);
        return response.data;
      })
    );
  }

  createConfigImpuesto(impuesto: Partial<ConfigImpuesto>): Observable<ConfigImpuesto> {
    return this.http.post<{ success: boolean; data: ConfigImpuesto }>(
      `${this.apiUrl}/nomina/config/impuestos`,
      impuesto
    ).pipe(
      map(response => {
        this.configImpuestos.update(list => [...list, response.data]);
        return response.data;
      })
    );
  }

  // Configuración de Deducciones
  getConfigDeducciones(): Observable<ConfigDeduccion[]> {
    return this.http.get<{ success: boolean; data: ConfigDeduccion[] }>(
      `${this.apiUrl}/nomina/config/deducciones`
    ).pipe(
      map(response => {
        this.configDeducciones.set(response.data);
        return response.data;
      })
    );
  }

  createConfigDeduccion(deduccion: Partial<ConfigDeduccion>): Observable<ConfigDeduccion> {
    return this.http.post<{ success: boolean; data: ConfigDeduccion }>(
      `${this.apiUrl}/nomina/config/deducciones`,
      deduccion
    ).pipe(
      map(response => {
        this.configDeducciones.update(list => [...list, response.data]);
        return response.data;
      })
    );
  }

  // Configuración de Beneficios
  getConfigBeneficios(): Observable<ConfigBeneficio[]> {
    return this.http.get<{ success: boolean; data: ConfigBeneficio[] }>(
      `${this.apiUrl}/nomina/config/beneficios`
    ).pipe(
      map(response => {
        this.configBeneficios.set(response.data);
        return response.data;
      })
    );
  }

  createConfigBeneficio(beneficio: Partial<ConfigBeneficio>): Observable<ConfigBeneficio> {
    return this.http.post<{ success: boolean; data: ConfigBeneficio }>(
      `${this.apiUrl}/nomina/config/beneficios`,
      beneficio
    ).pipe(
      map(response => {
        this.configBeneficios.update(list => [...list, response.data]);
        return response.data;
      })
    );
  }

  // Generar PDF de recibo (simulado - en producción usar librería como jsPDF)
  generateReceiptPDF(payroll: Payroll): void {
    const content = this.generateReceiptContent(payroll);
    const blob = new Blob([content], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Recibo_${payroll.nombre_empleado.replace(/\s+/g, '_')}_${payroll.periodo}.html`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  private generateReceiptContent(payroll: Payroll): string {
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Recibo de Nómina - ${payroll.nombre_empleado}</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    .header { text-align: center; margin-bottom: 30px; }
    .receipt-info { margin-bottom: 20px; }
    .receipt-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .receipt-table th, .receipt-table td { padding: 10px; border: 1px solid #ddd; text-align: left; }
    .receipt-table th { background-color: #f2f2f2; }
    .total-row { font-weight: bold; background-color: #e8f5e9; }
    .signature-section { margin-top: 50px; display: flex; justify-content: space-between; }
    .signature-box { width: 200px; border-top: 1px solid #000; padding-top: 10px; text-align: center; }
  </style>
</head>
<body>
  <div class="header">
    <h1>RECIBO DE NÓMINA</h1>
    <p>Período: ${payroll.periodo}</p>
  </div>
  
  <div class="receipt-info">
    <p><strong>Empleado:</strong> ${payroll.nombre_empleado}</p>
    <p><strong>Fecha de Pago:</strong> ${payroll.fecha_pago || 'Pendiente'}</p>
    <p><strong>Estado:</strong> ${payroll.estado}</p>
  </div>
  
  <table class="receipt-table">
    <thead>
      <tr>
        <th>Concepto</th>
        <th>Descripción</th>
        <th>Monto</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Salario Base</td>
        <td>-</td>
        <td>${this.formatCurrency(payroll.salario_base)}</td>
      </tr>
      ${payroll.bonificaciones_detalle?.map(b => `
        <tr>
          <td>Bonificación</td>
          <td>${b.concepto}</td>
          <td>${this.formatCurrency(b.monto)}</td>
        </tr>
      `).join('') || ''}
      ${payroll.deducciones_detalle?.map(d => `
        <tr>
          <td>Deducción</td>
          <td>${d.concepto}</td>
          <td>-${this.formatCurrency(d.monto)}</td>
        </tr>
      `).join('') || ''}
      <tr class="total-row">
        <td colspan="2"><strong>SALARIO NETO</strong></td>
        <td><strong>${this.formatCurrency(payroll.salario_neto)}</strong></td>
      </tr>
    </tbody>
  </table>
  
  <div class="signature-section">
    <div class="signature-box">
      <p>Firma del Empleado</p>
    </div>
    <div class="signature-box">
      <p>Firma de RRHH</p>
    </div>
  </div>
  
  <p style="margin-top: 30px; font-size: 12px; color: #666;">
    Fecha de generación: ${new Date().toLocaleString('es-DO')}
  </p>
</body>
</html>
    `;
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-HN', {
      style: 'currency',
      currency: 'HNL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }
}

