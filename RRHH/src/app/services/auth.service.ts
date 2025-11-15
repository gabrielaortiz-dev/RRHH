import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

export interface User {
  id?: number;
  email: string;
  username?: string;
  name?: string;
  role?: string;
  created_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  phone?: string;
}

interface ApiResponse<T> {
  status: string;
  data?: T;
  message?: string;
  count?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUser = signal<User | null>(null);
  private isAuthenticated = signal<boolean>(false);
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  /**
   * Intenta autenticar al usuario con las credenciales proporcionadas
   */
  login(credentials: LoginCredentials): Observable<{ success: boolean; message?: string; user?: User }> {
    // Buscar usuario por email en el backend
    return this.http.get<ApiResponse<User[]>>(`${this.apiUrl}/users`).pipe(
      map(response => {
        if (response.status === 'success' && response.data) {
          // Buscar usuario por email (en producción esto debería ser un endpoint de login)
          const user = response.data.find(u => u.email === credentials.email);
          
          if (user) {
            // En producción, el backend debería validar la contraseña
            // Por ahora, asumimos que el usuario existe
            const authenticatedUser: User = {
              id: user.id,
              email: user.email,
              username: user.username,
              name: user.name || user.username || user.email,
              role: user.role || 'user',
              created_at: user.created_at
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
              message: 'Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.'
            };
          }
        }
        return {
          success: false,
          message: 'Error al conectar con el servidor'
        };
      }),
      catchError(error => {
        console.error('Error en login:', error);
        return throwError(() => ({
          success: false,
          message: 'Error al conectar con el servidor. Verifica que el backend esté ejecutándose.'
        }));
      })
    );
  }

  /**
   * Registra un nuevo usuario
   */
  register(data: RegisterData): Observable<{ success: boolean; message?: string; user?: User }> {
    const userData = {
      username: data.username || data.email.split('@')[0],
      email: data.email,
      password: data.password
    };

    return this.http.post<ApiResponse<User>>(`${this.apiUrl}/users`, userData).pipe(
      map(response => {
        if (response.status === 'success' && response.data) {
          const newUser: User = {
            id: response.data.id,
            email: response.data.email,
            username: response.data.username,
            name: response.data.name || response.data.username || response.data.email,
            role: response.data.role || 'user',
            created_at: response.data.created_at
          };

          return {
            success: true,
            message: response.message || 'Usuario registrado exitosamente',
            user: newUser
          };
        }
        return {
          success: false,
          message: response.message || 'Error al registrar usuario'
        };
      }),
      catchError(error => {
        console.error('Error en registro:', error);
        const errorMessage = error.error?.message || 'Error al conectar con el servidor';
        return throwError(() => ({
          success: false,
          message: errorMessage
        }));
      })
    );
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
   * Obtiene todos los usuarios (solo para desarrollo/admin)
   */
  getUsers(): Observable<User[]> {
    return this.http.get<ApiResponse<User[]>>(`${this.apiUrl}/users`).pipe(
      map(response => response.data || []),
      catchError(error => {
        console.error('Error al obtener usuarios:', error);
        return throwError(() => error);
      })
    );
  }
}
