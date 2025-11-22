import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, map, of, Observable } from 'rxjs';

export interface Asistencia {
  id_asistencia: number;
  id_empleado: number;
  fecha: string;
  hora_entrada?: string;
  hora_salida?: string;
  observaciones?: string;
  nombre_empleado?: string;
  estado_asistencia?: 'Completa' | 'Incompleta' | 'Falta';
}

export interface AsistenciaCreate {
  id_empleado: number;
  fecha: string;
  hora_entrada?: string;
  hora_salida?: string;
  observaciones?: string;
  metodo_registro?: 'manual' | 'biometrico';
}

export interface AsistenciaUpdate {
  hora_entrada?: string;
  hora_salida?: string;
  observaciones?: string;
}

export interface AsistenciaReporteRequest {
  id_empleado?: number;
  fecha_inicio: string;
  fecha_fin: string;
}

export interface AsistenciaReporteResponse {
  success: boolean;
  message?: string;
  data?: Asistencia[];
  estadisticas?: {
    total_registros: number;
    completas: number;
    incompletas: number;
    faltas: number;
    fecha_inicio: string;
    fecha_fin: string;
  };
  count?: number;
}

export interface AsistenciaResponse {
  success: boolean;
  message?: string;
  data?: Asistencia | Asistencia[];
  count?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AttendanceService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';
  
  private asistencias = signal<Asistencia[]>([]);

  /**
   * Obtener asistencias con filtros opcionales
   */
  getAsistencias(filters?: {
    id_empleado?: number;
    fecha_inicio?: string;
    fecha_fin?: string;
  }): Observable<AsistenciaResponse> {
    let url = `${this.apiUrl}/asistencias?`;
    const params: string[] = [];
    
    if (filters?.id_empleado) {
      params.push(`id_empleado=${filters.id_empleado}`);
    }
    if (filters?.fecha_inicio) {
      params.push(`fecha_inicio=${filters.fecha_inicio}`);
    }
    if (filters?.fecha_fin) {
      params.push(`fecha_fin=${filters.fecha_fin}`);
    }
    
    url += params.join('&');
    
    return this.http.get<AsistenciaResponse>(url).pipe(
      map(response => {
        if (response.success && Array.isArray(response.data)) {
          this.asistencias.set(response.data);
        }
        return response;
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error al obtener asistencias:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al obtener asistencias'
        } as AsistenciaResponse);
      })
    );
  }

  /**
   * Obtener una asistencia por ID
   */
  getAsistencia(id: number): Observable<AsistenciaResponse> {
    return this.http.get<AsistenciaResponse>(`${this.apiUrl}/asistencias/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al obtener asistencia:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al obtener asistencia'
        } as AsistenciaResponse);
      })
    );
  }

  /**
   * Registrar una nueva asistencia (manual o biométrico)
   */
  registrarAsistencia(asistencia: AsistenciaCreate): Observable<AsistenciaResponse> {
    return this.http.post<AsistenciaResponse>(`${this.apiUrl}/asistencias`, asistencia).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al registrar asistencia:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al registrar asistencia'
        } as AsistenciaResponse);
      })
    );
  }

  /**
   * Actualizar una asistencia (para justificaciones y observaciones)
   */
  updateAsistencia(id: number, asistencia: AsistenciaUpdate): Observable<AsistenciaResponse> {
    return this.http.put<AsistenciaResponse>(`${this.apiUrl}/asistencias/${id}`, asistencia).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al actualizar asistencia:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al actualizar asistencia'
        } as AsistenciaResponse);
      })
    );
  }

  /**
   * Eliminar una asistencia
   */
  deleteAsistencia(id: number): Observable<AsistenciaResponse> {
    return this.http.delete<AsistenciaResponse>(`${this.apiUrl}/asistencias/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error al eliminar asistencia:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al eliminar asistencia'
        } as AsistenciaResponse);
      })
    );
  }

  /**
   * Generar reporte de asistencias por rango de fechas
   */
  generarReporte(reporte: AsistenciaReporteRequest): Observable<AsistenciaReporteResponse> {
    return this.http.post<AsistenciaReporteResponse>(`${this.apiUrl}/asistencias/reporte`, reporte).pipe(
      map(response => {
        if (response.success && Array.isArray(response.data)) {
          this.asistencias.set(response.data);
        }
        return response;
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Error al generar reporte:', error);
        return of({
          success: false,
          message: error.error?.detail || 'Error al generar reporte'
        } as AsistenciaReporteResponse);
      })
    );
  }

  /**
   * Registrar entrada (marcar entrada)
   */
  registrarEntrada(idEmpleado: number, metodo: 'manual' | 'biometrico' = 'manual'): Observable<AsistenciaResponse> {
    const hoy = new Date().toISOString().split('T')[0];
    const horaActual = new Date().toTimeString().split(' ')[0].substring(0, 5) + ':00';
    
    return this.registrarAsistencia({
      id_empleado: idEmpleado,
      fecha: hoy,
      hora_entrada: horaActual,
      metodo_registro: metodo
    });
  }

  /**
   * Registrar salida (marcar salida)
   */
  registrarSalida(idAsistencia: number): Observable<AsistenciaResponse> {
    const horaActual = new Date().toTimeString().split(' ')[0].substring(0, 5) + ':00';
    
    return this.updateAsistencia(idAsistencia, {
      hora_salida: horaActual
    });
  }

  /**
   * Señales reactivas
   */
  getAsistenciasSignal() {
    return this.asistencias.asReadonly();
  }
}

