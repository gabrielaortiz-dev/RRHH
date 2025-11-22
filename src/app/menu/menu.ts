import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { MenuItem } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { Navigation } from '../navigation';
import { AuthService } from '../services/auth.service';
import { NotificationPanel } from '../notifications/notification-panel';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-menu',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, ButtonModule, TooltipModule, NotificationPanel],
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
    // Inicializar items del menú
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
        label: 'Contratos',
        icon: 'pi pi-file',
        expanded: false,
        items: [
          {
            label: 'Lista de Contratos',
            icon: 'pi pi-list',
            routerLink: '/contratos'
          },
          {
            label: 'Nuevo Contrato',
            icon: 'pi pi-plus',
            routerLink: '/contratos/nuevo'
          }
        ]
      },
      {
        label: 'Asistencias',
        icon: 'pi pi-calendar-check',
        expanded: false,
        items: [
          {
            label: 'Registro de Asistencias',
            icon: 'pi pi-list',
            routerLink: '/asistencias'
          },
          {
            label: 'Registrar Asistencia',
            icon: 'pi pi-plus',
            routerLink: '/asistencias/registrar'
          },
          {
            label: 'Reportes de Asistencias',
            icon: 'pi pi-file-pdf',
            routerLink: '/asistencias/reportes'
          }
        ]
      },
      {
        label: 'Nómina',
        icon: 'pi pi-money-bill',
        expanded: false,
        items: [
          {
            label: 'Lista de Nóminas',
            icon: 'pi pi-list',
            routerLink: '/nomina'
          },
          {
            label: 'Calcular Nómina',
            icon: 'pi pi-calculator',
            routerLink: '/nomina/calcular'
          },
          {
            label: 'Historial de Pagos',
            icon: 'pi pi-history',
            routerLink: '/nomina/historial'
          },
          {
            label: 'Generar Recibos PDF',
            icon: 'pi pi-file-pdf',
            routerLink: '/nomina/recibos'
          }
        ]
      },
      {
        label: 'Vacaciones y Permisos',
        icon: 'pi pi-calendar-times',
        expanded: false,
        items: [
          {
            label: 'Lista de Solicitudes',
            icon: 'pi pi-list',
            routerLink: '/vacaciones'
          },
          {
            label: 'Nueva Solicitud',
            icon: 'pi pi-plus',
            routerLink: '/vacaciones/solicitar'
          },
          {
            label: 'Registro de Ausencias',
            icon: 'pi pi-calendar-minus',
            routerLink: '/vacaciones/ausencias'
          },
          {
            label: 'Cálculo de Días Disponibles',
            icon: 'pi pi-calculator',
            routerLink: '/vacaciones/calculo'
          },
          {
            label: 'Alertas y Seguimiento',
            icon: 'pi pi-bell',
            routerLink: '/vacaciones/alertas'
          }
        ]
      },
      {
        label: 'Documentación',
        icon: 'pi pi-file',
        expanded: false,
        items: [
          {
            label: 'Gestión de Documentos',
            icon: 'pi pi-folder-open',
            routerLink: '/documentos'
          },
          {
            label: 'Subir Documentos',
            icon: 'pi pi-upload',
            routerLink: '/documentos/subir'
          },
          {
            label: 'Clasificación por Tipo',
            icon: 'pi pi-tags',
            routerLink: '/documentos/clasificacion'
          }
        ]
      },
      {
        label: 'Usuarios y Roles',
        icon: 'pi pi-shield',
        expanded: false,
        items: [
          {
            label: 'Gestión de Usuarios',
            icon: 'pi pi-users',
            routerLink: '/usuarios'
          },
          {
            label: 'Gestión de Roles',
            icon: 'pi pi-key',
            routerLink: '/usuarios/roles'
          },
          {
            label: 'Permisos por Módulo',
            icon: 'pi pi-lock',
            routerLink: '/usuarios/permisos'
          },
          {
            label: 'Auditoría y Seguridad',
            icon: 'pi pi-shield',
            routerLink: '/usuarios/auditoria'
          }
        ]
      },
      {
        label: 'Reportes',
        icon: 'pi pi-chart-bar',
        expanded: false,
        items: [
          {
            label: 'Dashboard Principal',
            icon: 'pi pi-chart-line',
            routerLink: '/reportes/dashboard'
          },
          {
            label: 'Reporte General',
            icon: 'pi pi-file-pdf',
            routerLink: '/reportes/general'
          },
          {
            label: 'Reporte de Asistencias',
            icon: 'pi pi-calendar',
            routerLink: '/reportes/asistencias'
          },
          {
            label: 'Indicadores Clave (KPI)',
            icon: 'pi pi-chart-pie',
            routerLink: '/reportes/kpi'
          },
          {
            label: 'Gráficas Interactivas',
            icon: 'pi pi-chart-bar',
            routerLink: '/reportes/graficas'
          },
          {
            label: 'Exportar a Excel/PDF',
            icon: 'pi pi-download',
            routerLink: '/reportes/exportar'
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
            label: 'Notificaciones',
            icon: 'pi pi-bell',
            routerLink: '/config/notificaciones'
          },
          {
            label: 'Configuración General',
            icon: 'pi pi-wrench',
            routerLink: '/config/general'
          },
          {
            label: 'Parámetros del Sistema',
            icon: 'pi pi-sliders-h',
            routerLink: '/config/parametros'
          },
          {
            label: 'Personalización de Interfaz',
            icon: 'pi pi-palette',
            routerLink: '/config/interfaz'
          },
          {
            label: 'Integraciones',
            icon: 'pi pi-link',
            routerLink: '/config/integraciones'
          }
        ]
      }
    ];

    // Verificar que todos los items estén cargados
    console.log('Items del menú cargados:', this.items.length);
    console.log('Módulos disponibles:', this.items.map(i => i.label));

    // Actualizar título de página según la ruta
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.updatePageTitle();
    });
    
    this.updatePageTitle();
  }

  toggleSidebar() {
    const wasCollapsed = this.sidebarCollapsed();
    this.sidebarCollapsed.update(val => !val);
    
    // Si se está colapsando, mantener los submenús abiertos para mostrarlos como flotantes
    // Si se está expandiendo, mantener el estado actual
    if (wasCollapsed) {
      // Al expandir, mantener el estado actual de los submenús
      return;
    }
    // Al colapsar, mantener los submenús expandidos si estaban abiertos
  }

  toggleSubmenu(item: MenuItem) {
    item.expanded = !item.expanded;
    // Si el sidebar está colapsado, mantener abierto solo este submenú
    // Si está expandido, cerrar otros submenús
    if (!this.sidebarCollapsed()) {
      this.items.forEach(i => {
        if (i !== item && i.items) {
          i.expanded = false;
        }
      });
    } else {
      // Cuando está colapsado, permitir que solo un submenú esté abierto a la vez
      this.items.forEach(i => {
        if (i !== item && i.items && i.expanded) {
          i.expanded = false;
        }
      });
    }
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
      '/contratos': 'Gestión de Contratos',
      '/contratos/nuevo': 'Nuevo Contrato',
      '/contratos/editar': 'Editar Contrato',
      '/asistencias': 'Registro de Asistencias',
      '/asistencias/registrar': 'Registrar Asistencia',
      '/asistencias/editar': 'Editar Asistencia',
      '/asistencias/reportes': 'Reportes de Asistencias',
      '/nomina': 'Gestión de Nómina',
      '/nomina/calcular': 'Calcular Nómina',
      '/nomina/historial': 'Historial de Pagos',
      '/nomina/recibos': 'Generar Recibos PDF',
      '/vacaciones': 'Vacaciones y Permisos',
      '/vacaciones/solicitar': 'Solicitar Vacaciones',
      '/vacaciones/ausencias': 'Registro de Ausencias',
      '/vacaciones/calculo': 'Cálculo de Días Disponibles',
      '/vacaciones/alertas': 'Alertas y Seguimiento',
      '/documentos': 'Gestión de Documentación',
      '/documentos/subir': 'Subir Documentos',
      '/documentos/clasificacion': 'Clasificación por Tipo',
      '/usuarios': 'Usuarios y Roles',
      '/usuarios/roles': 'Gestión de Roles',
      '/usuarios/permisos': 'Permisos por Módulo',
      '/usuarios/auditoria': 'Auditoría y Seguridad',
      '/reportes/dashboard': 'Dashboard Principal',
      '/reportes/general': 'Reporte General',
      '/reportes/asistencias': 'Reporte de Asistencias',
      '/reportes/kpi': 'Indicadores Clave (KPI)',
      '/reportes/graficas': 'Gráficas Interactivas',
      '/reportes/exportar': 'Exportar a Excel/PDF',
      '/config/perfil': 'Mi Perfil',
      '/config/notificaciones': 'Configuración de Notificaciones',
      '/config/general': 'Configuración General',
      '/config/parametros': 'Parámetros del Sistema',
      '/config/interfaz': 'Personalización de Interfaz',
      '/config/integraciones': 'Integraciones'
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
