import { Injectable, signal } from '@angular/core';

export interface User {
  email: string;
  name: string;
  role: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUser = signal<User | null>(null);
  private isAuthenticated = signal<boolean>(false);

  // Base de datos de usuarios (en producción esto vendría de un backend)
  private readonly users = [
    {
      email: 'admin@rrhh.com',
      password: 'Admin123',
      name: 'Administrador',
      role: 'admin'
    },
    {
      email: 'usuario@rrhh.com',
      password: 'Usuario123',
      name: 'Usuario Regular',
      role: 'user'
    }
  ];

  /**
   * Intenta autenticar al usuario con las credenciales proporcionadas
   */
  login(credentials: LoginCredentials): Promise<{ success: boolean; message?: string; user?: User }> {
    return new Promise((resolve) => {
      // Simular delay de red
      setTimeout(() => {
        const user = this.users.find(
          u => u.email === credentials.email && u.password === credentials.password
        );

        if (user) {
          const authenticatedUser: User = {
            email: user.email,
            name: user.name,
            role: user.role
          };

          this.currentUser.set(authenticatedUser);
          this.isAuthenticated.set(true);

          // Guardar en localStorage para persistencia
          localStorage.setItem('currentUser', JSON.stringify(authenticatedUser));
          localStorage.setItem('isAuthenticated', 'true');

          resolve({
            success: true,
            user: authenticatedUser
          });
        } else {
          resolve({
            success: false,
            message: 'Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.'
          });
        }
      }, 1000);
    });
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
    return this.users.map(u => ({
      email: u.email,
      name: u.name,
      role: u.role
    }));
  }
}

