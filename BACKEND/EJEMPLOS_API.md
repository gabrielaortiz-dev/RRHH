# 📚 Ejemplos de Uso de la API

Esta guía muestra ejemplos prácticos de cómo usar los endpoints de la API.

---

## 🌐 URL Base

```
http://localhost:8000
```

---

## 📋 Endpoints Disponibles

### 1. Endpoint Principal

**Request:**
```http
GET http://localhost:8000/
```

**Response:**
```json
{
  "mensaje": "Bienvenido a la API del Sistema de RRHH",
  "version": "1.0.0",
  "status": "activo"
}
```

---

### 2. Health Check

Verifica el estado del servidor y la conexión a la base de datos.

**Request:**
```http
GET http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "ok",
  "database": "conectada",
  "mensaje": "Sistema funcionando correctamente"
}
```

---

### 3. Listar Departamentos

Obtiene todos los departamentos activos.

**Request:**
```http
GET http://localhost:8000/api/departamentos
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "nombre": "Recursos Humanos",
      "descripcion": "Departamento encargado de la gestión del personal",
      "fecha_creacion": "2025-11-15 14:53:12",
      "activo": 1
    },
    {
      "id": 2,
      "nombre": "Tecnología",
      "descripcion": "Departamento de desarrollo y sistemas",
      "fecha_creacion": "2025-11-15 14:53:12",
      "activo": 1
    }
    // ... más departamentos
  ]
}
```

---

### 4. Listar Empleados

Obtiene todos los empleados con información de su departamento.

**Request:**
```http
GET http://localhost:8000/api/empleados
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "nombre": "Carlos",
      "apellido": "Rodriguez",
      "email": "carlos.rodriguez@empresa.com",
      "telefono": "555-0101",
      "departamento_id": 1,
      "puesto": "Gerente de RRHH",
      "fecha_ingreso": "2020-01-15",
      "salario": 50000,
      "fecha_creacion": "2025-11-15 14:53:12",
      "activo": 1,
      "departamento_nombre": "Recursos Humanos"
    },
    {
      "id": 2,
      "nombre": "Ana",
      "apellido": "Martinez",
      "email": "ana.martinez@empresa.com",
      "telefono": "555-0102",
      "departamento_id": 2,
      "puesto": "Desarrollador Senior",
      "fecha_ingreso": "2019-03-20",
      "salario": 45000,
      "fecha_creacion": "2025-11-15 14:53:12",
      "activo": 1,
      "departamento_nombre": "Tecnología"
    }
    // ... más empleados
  ]
}
```

---

### 5. Listar Notificaciones de un Usuario

Obtiene las notificaciones de un usuario específico.

**Request:**
```http
GET http://localhost:8000/api/notificaciones/1
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "usuario_id": 1,
      "titulo": "Bienvenido al Sistema",
      "mensaje": "Bienvenido al sistema de gestión de RRHH",
      "tipo": "info",
      "leido": 0,
      "fecha_creacion": "2025-11-15 14:53:12"
    }
    // ... más notificaciones
  ]
}
```

---

## 💻 Ejemplos con diferentes herramientas

### PowerShell (Windows)

```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get

# Listar departamentos
Invoke-RestMethod -Uri "http://localhost:8000/api/departamentos" -Method Get

# Listar empleados
Invoke-RestMethod -Uri "http://localhost:8000/api/empleados" -Method Get

# Obtener notificaciones del usuario 1
Invoke-RestMethod -Uri "http://localhost:8000/api/notificaciones/1" -Method Get
```

### cURL (Linux/Mac/Windows)

```bash
# Health Check
curl http://localhost:8000/api/health

# Listar departamentos
curl http://localhost:8000/api/departamentos

# Listar empleados
curl http://localhost:8000/api/empleados

# Obtener notificaciones del usuario 1
curl http://localhost:8000/api/notificaciones/1
```

### JavaScript (Fetch API)

```javascript
// Health Check
fetch('http://localhost:8000/api/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Listar departamentos
fetch('http://localhost:8000/api/departamentos')
  .then(response => response.json())
  .then(data => console.log(data));

// Listar empleados
fetch('http://localhost:8000/api/empleados')
  .then(response => response.json())
  .then(data => console.log(data));

// Obtener notificaciones del usuario 1
fetch('http://localhost:8000/api/notificaciones/1')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python (requests)

```python
import requests

# Health Check
response = requests.get('http://localhost:8000/api/health')
print(response.json())

# Listar departamentos
response = requests.get('http://localhost:8000/api/departamentos')
print(response.json())

# Listar empleados
response = requests.get('http://localhost:8000/api/empleados')
print(response.json())

# Obtener notificaciones del usuario 1
response = requests.get('http://localhost:8000/api/notificaciones/1')
print(response.json())
```

### TypeScript/Angular (HttpClient)

```typescript
import { HttpClient } from '@angular/common/http';

// En tu servicio
private apiUrl = 'http://localhost:8000/api';

// Health Check
this.http.get(`${this.apiUrl}/health`)
  .subscribe(data => console.log(data));

// Listar departamentos
this.http.get(`${this.apiUrl}/departamentos`)
  .subscribe(data => console.log(data));

// Listar empleados
this.http.get(`${this.apiUrl}/empleados`)
  .subscribe(data => console.log(data));

// Obtener notificaciones del usuario 1
this.http.get(`${this.apiUrl}/notificaciones/1`)
  .subscribe(data => console.log(data));
```

---

## 🔍 Probar en el Navegador

Simplemente abre estas URLs en tu navegador:

1. **Health Check:**
   ```
   http://localhost:8000/api/health
   ```

2. **Departamentos:**
   ```
   http://localhost:8000/api/departamentos
   ```

3. **Empleados:**
   ```
   http://localhost:8000/api/empleados
   ```

4. **Notificaciones (usuario 1):**
   ```
   http://localhost:8000/api/notificaciones/1
   ```

---

## 📱 Documentación Interactiva (Swagger)

La forma más fácil de probar la API es usando la documentación interactiva:

**URL:** http://localhost:8000/docs

Características:
- ✅ Interfaz visual para probar endpoints
- ✅ Visualización de request/response
- ✅ Validación automática de datos
- ✅ Ejemplos de uso
- ✅ Descarga de esquemas OpenAPI

---

## 🎯 Casos de Uso Comunes

### 1. Obtener lista de empleados por departamento

```typescript
// Angular/TypeScript
getEmpleadosPorDepartamento(departamentoId: number) {
  this.http.get('http://localhost:8000/api/empleados')
    .subscribe((response: any) => {
      const empleados = response.data.filter(
        (emp: any) => emp.departamento_id === departamentoId
      );
      console.log(empleados);
    });
}
```

### 2. Contar empleados por departamento

```typescript
// Angular/TypeScript
contarEmpleadosPorDepartamento() {
  this.http.get('http://localhost:8000/api/empleados')
    .subscribe((response: any) => {
      const contador: any = {};
      response.data.forEach((emp: any) => {
        const dept = emp.departamento_nombre;
        contador[dept] = (contador[dept] || 0) + 1;
      });
      console.log(contador);
    });
}
```

### 3. Obtener notificaciones no leídas

```typescript
// Angular/TypeScript
getNotificacionesNoLeidas(usuarioId: number) {
  this.http.get(`http://localhost:8000/api/notificaciones/${usuarioId}`)
    .subscribe((response: any) => {
      const noLeidas = response.data.filter(
        (notif: any) => notif.leido === 0
      );
      console.log(`Notificaciones no leídas: ${noLeidas.length}`);
    });
}
```

---

## 🛠️ Manejo de Errores

### Error 404 - Not Found

```json
{
  "detail": "Not Found"
}
```

**Solución:** Verifica que la URL sea correcta.

### Error 500 - Internal Server Error

```json
{
  "detail": "Error en la base de datos: ..."
}
```

**Solución:** Verifica que la base de datos exista y esté funcionando.

### Error de CORS

**Error:** `Access to fetch... from origin... has been blocked by CORS policy`

**Solución:** 
1. Verifica que tu frontend esté en http://localhost:4200 o http://localhost:4201
2. Si usas otro puerto, agrégalo en `main.py`:
   ```python
   allow_origins=["http://localhost:TU_PUERTO"]
   ```

---

## 📞 Soporte

Para más información, consulta:
- **README.md** - Información general
- **INSTRUCCIONES.md** - Guía detallada
- **Documentación interactiva:** http://localhost:8000/docs

---

**¡Listo para integrar con tu aplicación!** 🚀

