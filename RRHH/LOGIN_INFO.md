# Sistema de Autenticación - RRHH

## 📋 Información General

Este sistema cuenta con un proceso de autenticación completo con múltiples usuarios y roles.

## 👥 Usuarios Disponibles

### 1. Administrador
- **Email:** `admin@rrhh.com`
- **Contraseña:** `Admin123`
- **Rol:** `admin`
- **Nombre:** Administrador
- **Permisos:** Acceso completo al sistema

### 2. Usuario Regular
- **Email:** `usuario@rrhh.com`
- **Contraseña:** `Usuario123`
- **Rol:** `user`
- **Nombre:** Usuario Regular
- **Permisos:** Acceso limitado al sistema

## 🔐 Características del Sistema de Login

### Validaciones Implementadas
- ✅ Validación de formato de email
- ✅ Validación de contraseña (mínimo 6 caracteres)
- ✅ Mensajes de error personalizados
- ✅ Indicador de carga durante la autenticación
- ✅ Manejo de errores de credenciales incorrectas

### Funcionalidades
- **Autenticación:** Validación de credenciales contra base de datos local
- **Sesión persistente:** Los datos de sesión se guardan en localStorage
- **Logout:** Cierre de sesión completo con limpieza de datos
- **Navegación:** Redirección automática al menú tras login exitoso
- **Información de usuario:** Almacenamiento de nombre, email y rol

## 🎨 Diseño

- **Estilo:** Minimalista con tema azul Material Design
- **Colores principales:**
  - Azul primario: `#1976d2`
  - Azul hover: `#1565c0`
  - Fondo: Degradado azul claro
- **Responsive:** Adaptable a dispositivos móviles y desktop

## 🔧 Arquitectura Técnica

### Servicio de Autenticación (`auth.service.ts`)
```typescript
- login(credentials): Promise<{success, message?, user?}>
- logout(): void
- getCurrentUser(): Signal<User | null>
- getIsAuthenticated(): Signal<boolean>
- restoreSession(): boolean
```

### Componente de Login (`login.ts`)
- Formulario reactivo con validaciones
- Integración con AuthService
- Manejo de estados (loading, error)
- Navegación automática tras login exitoso

### Componente de Menú (`menu.ts`)
- Barra de navegación con PrimeNG
- Opción de logout integrada
- Diseño responsive con tarjetas informativas

## 📝 Notas de Desarrollo

### Para agregar más usuarios:
Edita el archivo `src/app/services/auth.service.ts` y agrega nuevos usuarios al array `users`:

```typescript
{
  email: 'nuevo@rrhh.com',
  password: 'Password123',
  name: 'Nuevo Usuario',
  role: 'role_name'
}
```

### Para conectar con un backend real:
Reemplaza el método `login()` en `auth.service.ts` con una llamada HTTP a tu API:

```typescript
login(credentials: LoginCredentials): Promise<any> {
  return this.http.post('/api/auth/login', credentials).toPromise();
}
```

## 🚀 Uso

1. Inicia el servidor: `ng serve`
2. Abre el navegador en: `http://localhost:4200`
3. Usa cualquiera de las credenciales listadas arriba
4. El sistema te redirigirá automáticamente al menú principal

## 🔒 Seguridad

**IMPORTANTE:** Este es un sistema de demostración. En producción:
- ❌ NO almacenes contraseñas en texto plano
- ❌ NO uses localStorage para tokens sensibles
- ✅ Implementa JWT o similar
- ✅ Usa HTTPS
- ✅ Implementa rate limiting
- ✅ Hash de contraseñas en el backend
- ✅ Validación en servidor, no solo cliente

