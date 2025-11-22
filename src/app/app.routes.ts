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
import { ContractList } from './contracts/contract-list/contract-list';
import { ContractForm } from './contracts/contract-form/contract-form';
import { AttendanceList } from './attendance/attendance-list/attendance-list';
import { AttendanceRegister } from './attendance/attendance-register/attendance-register';
import { PayrollList } from './payroll/payroll-list/payroll-list';
import { PayrollForm } from './payroll/payroll-form/payroll-form';
import { PayrollHistory } from './payroll/payroll-history/payroll-history';
import { VacationList } from './vacations/vacation-list/vacation-list';
import { VacationForm } from './vacations/vacation-form/vacation-form';
import { DocumentList } from './documents/document-list/document-list';
import { UserList } from './users/user-list/user-list';

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
  },
  {
    path: 'contratos',
    component: ContractList
  },
  {
    path: 'contratos/nuevo',
    component: ContractForm
  },
  {
    path: 'contratos/editar/:id',
    component: ContractForm
  },
  {
    path: 'asistencias',
    component: AttendanceList
  },
  {
    path: 'asistencias/registrar',
    component: AttendanceRegister
  },
  {
    path: 'asistencias/editar/:id',
    component: AttendanceRegister
  },
  {
    path: 'asistencias/reportes',
    component: AttendanceReport
  },
  {
    path: 'nomina',
    component: PayrollList
  },
  {
    path: 'nomina/calcular',
    component: PayrollForm
  },
  {
    path: 'nomina/historial',
    component: PayrollHistory
  },
  {
    path: 'nomina/recibos',
    component: PayrollList
  },
  {
    path: 'vacaciones',
    component: VacationList
  },
  {
    path: 'vacaciones/solicitar',
    component: VacationForm
  },
  {
    path: 'vacaciones/ausencias',
    component: VacationList
  },
  {
    path: 'vacaciones/calculo',
    component: VacationForm
  },
  {
    path: 'vacaciones/alertas',
    component: VacationList
  },
  {
    path: 'documentos',
    component: DocumentList
  },
  {
    path: 'documentos/subir',
    component: DocumentList
  },
  {
    path: 'documentos/clasificacion',
    component: DocumentList
  },
  {
    path: 'usuarios',
    component: UserList
  },
  {
    path: 'usuarios/roles',
    component: UserList
  },
  {
    path: 'usuarios/permisos',
    component: UserList
  },
  {
    path: 'usuarios/auditoria',
    component: UserList
  },
  {
    path: 'reportes/dashboard',
    component: Dashboard
  },
  {
    path: 'reportes/kpi',
    component: GeneralReport
  },
  {
    path: 'reportes/graficas',
    component: GeneralReport
  },
  {
    path: 'reportes/exportar',
    component: GeneralReport
  },
  {
    path: 'config/parametros',
    component: GeneralSettings
  },
  {
    path: 'config/interfaz',
    component: GeneralSettings
  },
  {
    path: 'config/integraciones',
    component: GeneralSettings
  }
];
