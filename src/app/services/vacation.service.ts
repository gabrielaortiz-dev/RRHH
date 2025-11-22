import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface VacationRequest {
  id_permiso: number;
  id_empleado: number;
  nombre_empleado: string;
  tipo: string;
  fecha_solicitud: string;
  fecha_inicio: string;
  fecha_fin: string;
  dias_solicitados: number;
  dias_disponibles: number;
  motivo?: string;
  estado: string;
  aprobado_por_jefe?: number;
  aprobado_por_rrhh?: number;
  fecha_aprobacion_jefe?: string;
  fecha_aprobacion_rrhh?: string;
  motivo_rechazo?: string;
}

export interface VacationCreate {
  id_empleado: number;
  tipo: string;
  fecha_inicio: string;
  fecha_fin: string;
  motivo?: string;
  observaciones?: string;
}

export interface VacationBalance {
  id_balance: number;
  id_empleado: number;
  anio: number;
  dias_totales: number;
  dias_usados: number;
  dias_disponibles: number;
  dias_acumulados: number;
}

@Injectable({
  providedIn: 'root'
})
export class VacationService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';

  vacations = signal<VacationRequest[]>([]);

  getVacations(filters?: { id_empleado?: number; estado?: string }): Observable<VacationRequest[]> {
    let url = `${this.apiUrl}/vacaciones`;
    const params: string[] = [];
    
    if (filters?.id_empleado) params.push(`id_empleado=${filters.id_empleado}`);
    if (filters?.estado) params.push(`estado=${filters.estado}`);
    
    if (params.length > 0) url += '?' + params.join('&');
    
    return this.http.get<{ success: boolean; data: VacationRequest[] }>(url).pipe(
      map(response => {
        this.vacations.set(response.data);
        return response.data;
      })
    );
  }

  createVacation(vacation: VacationCreate): Observable<VacationRequest> {
    return this.http.post<{ success: boolean; message: string; data: VacationRequest }>(
      `${this.apiUrl}/vacaciones`,
      vacation
    ).pipe(
      map(response => {
        this.vacations.update(list => [response.data, ...list]);
        return response.data;
      })
    );
  }

  approveRejectVacation(permisoId: number, aprobar: boolean, nivel: 'jefe' | 'rrhh', motivo?: string, usuarioId?: number): Observable<VacationRequest> {
    return this.http.put<{ success: boolean; message: string; data: VacationRequest }>(
      `${this.apiUrl}/vacaciones/${permisoId}/aprobar`,
      { aprobar, nivel, motivo },
      { params: usuarioId ? { usuario_id: usuarioId.toString() } : {} }
    ).pipe(
      map(response => {
        this.vacations.update(list => 
          list.map(v => v.id_permiso === permisoId ? response.data : v)
        );
        return response.data;
      })
    );
  }

  getBalance(empleadoId: number, anio?: number): Observable<VacationBalance> {
    let url = `${this.apiUrl}/vacaciones/empleado/${empleadoId}/balance`;
    if (anio) url += `?anio=${anio}`;
    
    return this.http.get<{ success: boolean; data: VacationBalance }>(url).pipe(
      map(response => response.data)
    );
  }

  getCalendar(mes: number, anio: number): Observable<VacationRequest[]> {
    return this.http.get<{ success: boolean; data: VacationRequest[] }>(
      `${this.apiUrl}/vacaciones/calendario?mes=${mes}&anio=${anio}`
    ).pipe(
      map(response => response.data)
    );
  }
}

