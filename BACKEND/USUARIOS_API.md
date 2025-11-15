# 👥 API de Gestión de Usuarios

Documentación completa de los endpoints para gestionar usuarios en el sistema de RRHH.

---

## 📋 Tabla de Contenidos

1. [Listar Usuarios](#1-listar-usuarios)
2. [Obtener Usuario por ID](#2-obtener-usuario-por-id)
3. [Crear Usuario](#3-crear-usuario)
4. [Actualizar Usuario](#4-actualizar-usuario)
5. [Eliminar Usuario](#5-eliminar-usuario)
6. [Login de Usuario](#6-login-de-usuario)

---

## 1. Listar Usuarios

Obtiene todos los usuarios activos del sistema (sin passwords).

**Endpoint:** `GET /api/usuarios`

### Request

```http
GET http://localhost:8000/api/usuarios
```

### Response (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Admin Sistema",
      "email": "admin@rrhh.com",
      "rol": "administrador",
      "fecha_creacion": "2025-11-15 14:53:12",
      "activo": 1
    },
    {
      "id": 2,
      "nombre": "Juan Perez",
      "email": "juan.perez@rrhh.com",
      "rol": "empleado",
      "fecha_creacion": "2025-11-15 14:53:12",
      "activo": 1
    }
  ],
  "count": 2
}
```

### Ejemplo en Angular/TypeScript

```typescript
this.http.get('http://localhost:8000/api/usuarios')
  .subscribe((response: any) => {
    console.log('Usuarios:', response.data);
    console.log('Total:', response.count);
  });
```

---

## 2. Obtener Usuario por ID

Obtiene un usuario específico por su ID (sin password).

**Endpoint:** `GET /api/usuarios/{usuario_id}`

### Request

```http
GET http://localhost:8000/api/usuarios/1
```

### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Admin Sistema",
    "email": "admin@rrhh.com",
    "rol": "administrador",
    "fecha_creacion": "2025-11-15 14:53:12",
    "activo": 1
  }
}
```

### Response (404 Not Found)

```json
{
  "detail": "Usuario con ID 999 no encontrado"
}
```

### Ejemplo en Angular/TypeScript

```typescript
const usuarioId = 1;
this.http.get(`http://localhost:8000/api/usuarios/${usuarioId}`)
  .subscribe(
    (response: any) => {
      console.log('Usuario:', response.data);
    },
    (error) => {
      console.error('Error:', error.error.detail);
    }
  );
```

---

## 3. Crear Usuario

Crea un nuevo usuario en el sistema.

**Endpoint:** `POST /api/usuarios`

### Request

```http
POST http://localhost:8000/api/usuarios
Content-Type: application/json

{
  "nombre": "Nuevo Usuario",
  "email": "nuevo@empresa.com",
  "password": "password123",
  "rol": "empleado"
}
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| nombre | string | Sí | Nombre completo (min: 2, max: 100) |
| email | string | Sí | Email único válido |
| password | string | Sí | Contraseña (min: 6, max: 255) |
| rol | string | No | Rol del usuario (default: "empleado") |

**Roles válidos:** `administrador`, `supervisor`, `empleado`

### Response (201 Created)

```json
{
  "success": true,
  "message": "Usuario creado exitosamente",
  "data": {
    "id": 4,
    "nombre": "Nuevo Usuario",
    "email": "nuevo@empresa.com",
    "rol": "empleado",
    "fecha_creacion": "2025-11-15 15:00:49",
    "activo": 1
  }
}
```

### Response (400 Bad Request)

```json
{
  "detail": "El email nuevo@empresa.com ya está registrado"
}
```

### Ejemplo en Angular/TypeScript

```typescript
const nuevoUsuario = {
  nombre: "María López",
  email: "maria.lopez@empresa.com",
  password: "pass123456",
  rol: "supervisor"
};

this.http.post('http://localhost:8000/api/usuarios', nuevoUsuario)
  .subscribe(
    (response: any) => {
      console.log('Usuario creado:', response.data);
      alert(response.message);
    },
    (error) => {
      console.error('Error:', error.error.detail);
    }
  );
```

---

## 4. Actualizar Usuario

Actualiza los datos de un usuario existente.

**Endpoint:** `PUT /api/usuarios/{usuario_id}`

### Request

```http
PUT http://localhost:8000/api/usuarios/2
Content-Type: application/json

{
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.nuevo@empresa.com",
  "rol": "supervisor"
}
```

### Campos

Todos los campos son opcionales. Solo se actualizarán los campos proporcionados.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre | string | Nombre completo |
| email | string | Email único válido |
| password | string | Nueva contraseña |
| rol | string | Nuevo rol |
| activo | boolean | Estado del usuario |

### Response (200 OK)

```json
{
  "success": true,
  "message": "Usuario actualizado exitosamente",
  "data": {
    "id": 2,
    "nombre": "Juan Pérez Actualizado",
    "email": "juan.nuevo@empresa.com",
    "rol": "supervisor",
    "fecha_creacion": "2025-11-15 14:53:12",
    "activo": 1
  }
}
```

### Response (404 Not Found)

```json
{
  "detail": "Usuario con ID 999 no encontrado"
}
```

### Response (400 Bad Request)

```json
{
  "detail": "El email juan.nuevo@empresa.com ya está en uso"
}
```

### Ejemplo en Angular/TypeScript

```typescript
const usuarioId = 2;
const datosActualizar = {
  nombre: "Juan Pérez Actualizado",
  rol: "supervisor"
};

this.http.put(`http://localhost:8000/api/usuarios/${usuarioId}`, datosActualizar)
  .subscribe(
    (response: any) => {
      console.log('Usuario actualizado:', response.data);
      alert(response.message);
    },
    (error) => {
      console.error('Error:', error.error.detail);
    }
  );
```

---

## 5. Eliminar Usuario

Desactiva un usuario (no lo elimina de la base de datos).

**Endpoint:** `DELETE /api/usuarios/{usuario_id}`

### Request

```http
DELETE http://localhost:8000/api/usuarios/2
```

### Response (200 OK)

```json
{
  "success": true,
  "message": "Usuario 'Juan Perez' desactivado exitosamente"
}
```

### Response (404 Not Found)

```json
{
  "detail": "Usuario con ID 999 no encontrado"
}
```

### Ejemplo en Angular/TypeScript

```typescript
const usuarioId = 2;

if (confirm('¿Estás seguro de eliminar este usuario?')) {
  this.http.delete(`http://localhost:8000/api/usuarios/${usuarioId}`)
    .subscribe(
      (response: any) => {
        console.log(response.message);
        alert('Usuario eliminado correctamente');
      },
      (error) => {
        console.error('Error:', error.error.detail);
      }
    );
}
```

---

## 6. Login de Usuario

Autentica un usuario en el sistema.

**Endpoint:** `POST /api/usuarios/login`

### Request

```http
POST http://localhost:8000/api/usuarios/login
Content-Type: application/json

{
  "email": "admin@rrhh.com",
  "password": "admin123"
}
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| email | string | Sí | Email del usuario |
| password | string | Sí | Contraseña |

### Response (200 OK)

```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "id": 1,
    "nombre": "Admin Sistema",
    "email": "admin@rrhh.com",
    "rol": "administrador",
    "fecha_creacion": "2025-11-15 14:53:12",
    "activo": 1
  }
}
```

### Response (401 Unauthorized)

```json
{
  "detail": "Credenciales inválidas"
}
```

### Ejemplo en Angular/TypeScript

```typescript
const credentials = {
  email: this.loginForm.value.email,
  password: this.loginForm.value.password
};

this.http.post('http://localhost:8000/api/usuarios/login', credentials)
  .subscribe(
    (response: any) => {
      console.log('Login exitoso:', response.data);
      // Guardar datos del usuario en localStorage o sessionStorage
      localStorage.setItem('usuario', JSON.stringify(response.data));
      // Redirigir al dashboard
      this.router.navigate(['/dashboard']);
    },
    (error) => {
      console.error('Error de login:', error.error.detail);
      alert('Credenciales incorrectas');
    }
  );
```

---

## 🧪 Pruebas con PowerShell

```powershell
# 1. Listar usuarios
Invoke-RestMethod -Uri "http://localhost:8000/api/usuarios" -Method Get

# 2. Obtener usuario específico
Invoke-RestMethod -Uri "http://localhost:8000/api/usuarios/1" -Method Get

# 3. Crear usuario
$body = @{
    nombre = "Test Usuario"
    email = "test@empresa.com"
    password = "test123"
    rol = "empleado"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/usuarios" `
    -Method Post -Body $body -ContentType "application/json"

# 4. Actualizar usuario
$body = @{
    nombre = "Test Actualizado"
    rol = "supervisor"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/usuarios/4" `
    -Method Put -Body $body -ContentType "application/json"

# 5. Login
$body = @{
    email = "admin@rrhh.com"
    password = "admin123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/usuarios/login" `
    -Method Post -Body $body -ContentType "application/json"

# 6. Eliminar usuario
Invoke-RestMethod -Uri "http://localhost:8000/api/usuarios/4" -Method Delete
```

---

## 🔒 Notas de Seguridad

⚠️ **IMPORTANTE:** Esta implementación es básica y para propósitos de demostración.

Para producción, considera:

1. **Hashear las contraseñas:** No guardes contraseñas en texto plano. Usa `bcrypt` o `passlib`.
2. **Implementar JWT:** Para autenticación basada en tokens.
3. **Validación adicional:** Validar roles, permisos, etc.
4. **Rate limiting:** Prevenir ataques de fuerza bruta en el login.
5. **HTTPS:** Usar siempre HTTPS en producción.

---

## 📊 Estructura de la Tabla Usuarios

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) DEFAULT 'empleado',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
)
```

---

## 🎯 Servicio Angular Completo

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Usuario {
  id?: number;
  nombre: string;
  email: string;
  password?: string;
  rol: string;
  fecha_creacion?: string;
  activo?: number;
}

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private apiUrl = 'http://localhost:8000/api/usuarios';

  constructor(private http: HttpClient) {}

  // Listar todos los usuarios
  getUsuarios(): Observable<any> {
    return this.http.get(this.apiUrl);
  }

  // Obtener un usuario por ID
  getUsuario(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`);
  }

  // Crear nuevo usuario
  crearUsuario(usuario: Usuario): Observable<any> {
    return this.http.post(this.apiUrl, usuario);
  }

  // Actualizar usuario
  actualizarUsuario(id: number, usuario: Partial<Usuario>): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, usuario);
  }

  // Eliminar usuario
  eliminarUsuario(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  // Login
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { email, password });
  }
}
```

---

## ✅ Verificación

Para verificar que todos los endpoints funcionan, abre:

**Documentación interactiva Swagger:**
```
http://localhost:8000/docs
```

Allí podrás probar todos los endpoints directamente desde el navegador.

---

**¡La API de usuarios está completamente funcional!** 🎉

