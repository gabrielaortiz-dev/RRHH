import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MenuItem } from 'primeng/api';
import { MenubarModule } from 'primeng/menubar';
import { Navigation } from '../navigation';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-menu',
  imports: [CommonModule, MenubarModule],
  templateUrl: './menu.html',
  styleUrl: './menu.css'
})
export class Menu implements OnInit {
  items: MenuItem[] = [];
  private navigation = inject(Navigation);
  private authService = inject(AuthService);

  ngOnInit() {
    this.items = [
      {
        label: 'Inicio',
        icon: 'pi pi-home',
        routerLink: '/'
      },
      {
        label: 'Empleados',
        icon: 'pi pi-users',
        items: [
          {
            label: 'Lista de Empleados',
            icon: 'pi pi-list',
            routerLink: '/empleados'
          },
          {
            label: 'Nuevo Empleado',
            icon: 'pi pi-user-plus',
            routerLink: '/empleados/nuevo'
          }
        ]
      },
      {
        label: 'Departamentos',
        icon: 'pi pi-building',
        items: [
          {
            label: 'Ver Departamentos',
            icon: 'pi pi-sitemap',
            routerLink: '/departamentos'
          },
          {
            label: 'Crear Departamento',
            icon: 'pi pi-plus-circle',
            routerLink: '/departamentos/nuevo'
          }
        ]
      },
      {
        label: 'Reportes',
        icon: 'pi pi-chart-bar',
        items: [
          {
            label: 'Reporte General',
            icon: 'pi pi-file-pdf',
            routerLink: '/reportes/general'
          },
          {
            label: 'Reporte de Asistencias',
            icon: 'pi pi-calendar',
            routerLink: '/reportes/asistencias'
          }
        ]
      },
      {
        label: 'Configuración',
        icon: 'pi pi-cog',
        items: [
          {
            label: 'Perfil',
            icon: 'pi pi-user',
            routerLink: '/config/perfil'
          },
          {
            label: 'Configuración General',
            icon: 'pi pi-wrench',
            routerLink: '/config/general'
          },
          {
            separator: true
          },
          {
            label: 'Cerrar Sesión',
            icon: 'pi pi-sign-out',
            command: () => {
              this.logout();
            }
          }
        ]
      }
    ];
  }

  logout() {
    console.log('Cerrando sesión...');
    // Cerrar sesión en el servicio de autenticación
    this.authService.logout();
    // Regresar al login
    this.navigation.showLogin();
  }
}
