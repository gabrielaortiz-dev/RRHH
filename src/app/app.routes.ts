import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { EmployeeList } from './employees/employee-list/employee-list';
import { EmployeeForm } from './employees/employee-form/employee-form';
import { DepartmentList } from './departments/department-list/department-list';
import { DepartmentForm } from './departments/department-form/department-form';
import { GeneralReport } from './reports/general-report/general-report';
import { AttendanceReport } from './reports/attendance-report/attendance-report';
import { UserProfile } from './config/user-profile/user-profile';
import { GeneralSettings } from './config/general-settings/general-settings';
import { NotificationSettings } from './config/notification-settings/notification-settings';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    component: Dashboard
  },
  {
    path: 'empleados/nuevo',
    component: EmployeeForm
  },
  {
    path: 'empleados',
    component: EmployeeList
  },
  {
    path: 'departamentos/nuevo',
    component: DepartmentForm
  },
  {
    path: 'departamentos',
    component: DepartmentList
  },
  {
    path: 'reportes/general',
    component: GeneralReport
  },
  {
    path: 'reportes/asistencias',
    component: AttendanceReport
  },
  {
    path: 'config/perfil',
    component: UserProfile
  },
  {
    path: 'config/general',
    component: GeneralSettings
  },
  {
    path: 'config/notificaciones',
    component: NotificationSettings
  }
];
