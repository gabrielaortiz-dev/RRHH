import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { MenuItem } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { Navigation } from '../navigation';
import { AuthService } from '../services/auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-menu',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, ButtonModule, TooltipModule],
  templateUrl: './menu.html',
  styleUrl: './menu.css'
})
export class Menu implements OnInit {
  items: MenuItem[] = [];
  private navigation = inject(Navigation);
  private authService = inject(AuthService);
  private router = inject(Router);
  
  sidebarCollapsed = signal(false);
  currentPageTitle = signal('Dashboard');
  currentUser = this.authService.getCurrentUser();

  ngOnInit() {
    this.items = [
      {
        label: 'Inicio',
        icon: 'pi pi-home',
        routerLink: '/dashboard'
      },
      {
        label: 'Empleados',
        icon: 'pi pi-users',
        expanded: false,
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
        expanded: false,
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
        expanded: false,
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
        expanded: false,
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
          }
        ]
      }
    ];

    // Actualizar título de página según la ruta
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.updatePageTitle();
    });
    
    this.updatePageTitle();
  }

  toggleSidebar() {
    this.sidebarCollapsed.update(val => !val);
  }

  toggleSubmenu(item: MenuItem) {
    item.expanded = !item.expanded;
    // Cerrar otros submenús
    this.items.forEach(i => {
      if (i !== item && i.items) {
        i.expanded = false;
      }
    });
  }

  isActive(item: MenuItem): boolean {
    const currentUrl = this.router.url;
    if (item.routerLink && currentUrl.includes(item.routerLink.toString())) {
      return true;
    }
    if (item.items) {
      return item.items.some(subitem => 
        subitem.routerLink && currentUrl.includes(subitem.routerLink.toString())
      );
    }
    return false;
  }

  updatePageTitle() {
    const currentUrl = this.router.url;
    const titles: { [key: string]: string } = {
      '/dashboard': 'Dashboard',
      '/empleados': 'Lista de Empleados',
      '/empleados/nuevo': 'Nuevo Empleado',
      '/departamentos': 'Departamentos',
      '/departamentos/nuevo': 'Nuevo Departamento',
      '/reportes/general': 'Reporte General',
      '/reportes/asistencias': 'Reporte de Asistencias',
      '/config/perfil': 'Mi Perfil',
      '/config/general': 'Configuración General'
    };

    const title = Object.entries(titles).find(([path]) => 
      currentUrl.includes(path)
    )?.[1] || 'Dashboard';
    
    this.currentPageTitle.set(title);
  }

  executeCommand(item: MenuItem) {
    if (item.command) {
      item.command({});
    }
  }

  logout() {
    console.log('Cerrando sesión...');
    this.authService.logout();
    this.navigation.showLogin();
  }
}
