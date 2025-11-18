import { Injectable, signal, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError, firstValueFrom } from 'rxjs';

export interface User {
  email: string;
  name: string;
  role: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  message?: string;
  data?: {
    id: number;
    nombre: string;
    email: string;
    rol: string;
    fecha_creacion: string;
    activo: number;
  };
}

interface LoginResult {
  success: boolean;
  message?: string;
  user?: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api';
  
  private currentUser = signal<User | null>(null);
  private isAuthenticated = signal<boolean>(false);

  /**
   * Intenta autenticar al usuario con las credenciales proporcionadas
   */
  async login(credentials: LoginCredentials): Promise<LoginResult> {
    try {
      const response = await firstValueFrom(
        this.http.post<LoginResponse>(
          `${this.apiUrl}/usuarios/login`,
          credentials
        ).pipe(
          catchError((error: HttpErrorResponse) => {
            let message = 'Error al conectar con el servidor';
            
            if (error.error) {
              message = error.error.detail || error.error.message || message;
            }
            
            const errorResult: LoginResult = {
              success: false,
              message: message
            };
            
            return throwError(() => errorResult);
          })
        )
      );

      if (response.success && response.data) {
        const authenticatedUser: User = {
          email: response.data.email,
          name: response.data.nombre,
          role: response.data.rol
        };
        
        this.currentUser.set(authenticatedUser);
        this.isAuthenticated.set(true);
        
        // Guardar en localStorage para persistencia
        localStorage.setItem('currentUser', JSON.stringify(authenticatedUser));
        localStorage.setItem('isAuthenticated', 'true');
        
        return {
          success: true,
          user: authenticatedUser
        };
      } else {
        return {
          success: false,
          message: response.message || 'Credenciales incorrectas'
        };
      }
    } catch (error: unknown) {
      // Manejar el error que viene del throwError
      if (error && typeof error === 'object' && 'success' in error) {
        return error as LoginResult;
      } else {
        return {
          success: false,
          message: 'Error desconocido al intentar iniciar sesión'
        };
      }
    }
  }

  /**
   * Cierra la sesión del usuario actual
   */
  logout(): void {
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
    localStorage.removeItem('currentUser');
    localStorage.removeItem('isAuthenticated');
    console.log('Sesión cerrada exitosamente');
  }

  /**
   * Obtiene el usuario actual
   */
  getCurrentUser() {
    return this.currentUser.asReadonly();
  }

  /**
   * Verifica si el usuario está autenticado
   */
  getIsAuthenticated() {
    return this.isAuthenticated.asReadonly();
  }

  /**
   * Restaura la sesión desde localStorage
   */
  restoreSession(): boolean {
    const userStr = localStorage.getItem('currentUser');
    const isAuth = localStorage.getItem('isAuthenticated');

    if (userStr && isAuth === 'true') {
      try {
        const user = JSON.parse(userStr);
        this.currentUser.set(user);
        this.isAuthenticated.set(true);
        return true;
      } catch (e) {
        this.logout();
        return false;
      }
    }
    return false;
  }

  /**
   * Obtiene todos los usuarios disponibles (solo para demo)
   */
  getAvailableUsers() {
    return [];
  }
}
