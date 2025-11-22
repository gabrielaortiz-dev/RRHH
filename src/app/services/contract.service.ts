import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, map, of, Observable } from 'rxjs';

export interface Contrato {
  id_contrato: number;
  id_empleado: number;
  tipo_contrato: 'temporal' | 'permanente' | 'honorarios';
  fecha_inicio: string;
  fecha_fin?: string;
  salario: number;
  condiciones?: string;
  nombre_empleado?: string;
  estado_vencimiento?: 'vencido' | 'por_vencer' | 'vigente';
  dias_restantes?: number;
}

export interface ContratoCreate {
  id_empleado: number;
  tipo_contrato: 'temporal' | 'permanente' | 'honorarios';
  fecha_inicio: string;
  fecha_fin?: string;
  salario: number;
  condiciones?: string;
}

export interface ContratoUpdate {
  tipo_contrato?: 'temporal' | 'permanente' | 'honorarios';
  fecha_inicio?: string;
  fecha_fin?: string;
  salario?: number;
  condiciones?: string;
}

export interface ContratoResponse {
  success: boolean;
  message?: string;
  data?: Contrato | Contrato[];
  count?: number;
  dias_consulta?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ContractService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';
  
  private contratos = signal<Contrato[]>([]);
  private alertasVencimiento = signal<Contrato[]>([]);

  /**
   * Obtener todos los contratos o los de un empleado específico
   */
  getContratos(idEmpleado?: number): Observable<ContratoResponse> {
    const url = idEmpleado 
      ? `${this.apiUrl}/contratos?id_empleado=${idEmpleado}`
      : `${this.apiUrl}/contratos`;
    
    return this.http.get<ContratoResponse>(url).pipe(
      map(response => {
        if (response.success && Array.isArray(response.data)) {
          this.contratos.set(response.data);
        }
        return response;
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error al obtener contratos:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al obtener contratos'
        } as ContratoResponse);
      })
    );
  }

  /**
   * Obtener un contrato por ID
   */
  getContrato(id: number): Observable<ContratoResponse> {
    return this.http.get<ContratoResponse>(`${this.apiUrl}/contratos/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al obtener contrato:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al obtener contrato'
        } as ContratoResponse);
      })
    );
  }

  /**
   * Crear un nuevo contrato
   */
  createContrato(contrato: ContratoCreate): Observable<ContratoResponse> {
    return this.http.post<ContratoResponse>(`${this.apiUrl}/contratos`, contrato).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al crear contrato:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al crear contrato'
        } as ContratoResponse);
      })
    );
  }

  /**
   * Actualizar un contrato
   */
  updateContrato(id: number, contrato: ContratoUpdate): Observable<ContratoResponse> {
    return this.http.put<ContratoResponse>(`${this.apiUrl}/contratos/${id}`, contrato).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al actualizar contrato:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al actualizar contrato'
        } as ContratoResponse);
      })
    );
  }

  /**
   * Eliminar un contrato
   */
  deleteContrato(id: number): Observable<ContratoResponse> {
    return this.http.delete<ContratoResponse>(`${this.apiUrl}/contratos/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al eliminar contrato:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al eliminar contrato'
        } as ContratoResponse);
      })
    );
  }

  /**
   * Obtener alertas de contratos próximos a vencer
   */
  getAlertasVencimiento(dias: number = 30): Observable<ContratoResponse> {
    return this.http.get<ContratoResponse>(`${this.apiUrl}/contratos/alertas/vencimiento?dias=${dias}`).pipe(
      map(response => {
        if (response.success && Array.isArray(response.data)) {
          this.alertasVencimiento.set(response.data);
        }
        return response;
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error al obtener alertas:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al obtener alertas de vencimiento'
        } as ContratoResponse);
      })
    );
  }

  /**
   * Obtener historial de contratos de un empleado
   */
  getHistorialContratos(idEmpleado: number): Observable<ContratoResponse> {
    return this.getContratos(idEmpleado);
  }

  /**
   * Señales reactivas
   */
  getContratosSignal() {
    return this.contratos.asReadonly();
  }

  getAlertasVencimientoSignal() {
    return this.alertasVencimiento.asReadonly();
  }
}

