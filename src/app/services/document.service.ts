import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Document {
  id_documento: number;
  id_empleado: number;
  nombre_empleado: string;
  nombre_archivo: string;
  nombre_original: string;
  tipo_documento: string;
  categoria?: string;
  ruta_archivo: string;
  tamano_bytes: number;
  mime_type: string;
  fecha_subida: string;
  fecha_expiracion?: string;
  estado: string;
  descripcion?: string;
  expirado?: boolean;
  dias_para_expiracion?: number;
}

export interface DocumentCreate {
  id_empleado: number;
  tipo_documento: string;
  categoria?: string;
  descripcion?: string;
  fecha_expiracion?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';

  documents = signal<Document[]>([]);

  getDocuments(filters?: { id_empleado?: number; tipo?: string; categoria?: string; buscar?: string }): Observable<Document[]> {
    let url = `${this.apiUrl}/documentos`;
    const params: string[] = [];
    
    if (filters?.id_empleado) params.push(`id_empleado=${filters.id_empleado}`);
    if (filters?.tipo) params.push(`tipo=${filters.tipo}`);
    if (filters?.categoria) params.push(`categoria=${filters.categoria}`);
    if (filters?.buscar) params.push(`buscar=${filters.buscar}`);
    
    if (params.length > 0) url += '?' + params.join('&');
    
    return this.http.get<{ success: boolean; data: Document[] }>(url).pipe(
      map(response => {
        this.documents.set(response.data);
        return response.data;
      })
    );
  }

  uploadDocument(file: File, documentData: DocumentCreate, usuarioId?: number): Observable<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_empleado', documentData.id_empleado.toString());
    formData.append('tipo_documento', documentData.tipo_documento);
    if (documentData.categoria) formData.append('categoria', documentData.categoria);
    if (documentData.descripcion) formData.append('descripcion', documentData.descripcion);
    if (documentData.fecha_expiracion) formData.append('fecha_expiracion', documentData.fecha_expiracion);
    if (usuarioId) formData.append('usuario_id', usuarioId.toString());

    return this.http.post<{ success: boolean; message: string; data: Document }>(
      `${this.apiUrl}/documentos/upload`,
      formData
    ).pipe(
      map(response => {
        this.documents.update(list => [response.data, ...list]);
        return response.data;
      })
    );
  }

  downloadDocument(documentId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/documentos/${documentId}/download`, {
      responseType: 'blob'
    });
  }

  deleteDocument(documentId: number): Observable<void> {
    return this.http.delete<{ success: boolean; message: string }>(
      `${this.apiUrl}/documentos/${documentId}`
    ).pipe(
      map(() => {
        this.documents.update(list => list.filter(d => d.id_documento !== documentId));
      })
    );
  }

  getExpiredDocuments(): Observable<Document[]> {
    return this.http.get<{ success: boolean; data: Document[] }>(
      `${this.apiUrl}/documentos/vencidos`
    ).pipe(
      map(response => response.data)
    );
  }

  previewDocument(document: Document): string {
    // Retornar URL para vista previa
    return `${this.apiUrl}/documentos/${document.id_documento}/download`;
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}

