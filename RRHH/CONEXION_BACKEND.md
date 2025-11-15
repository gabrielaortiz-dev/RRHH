# Conexión Frontend Angular con Backend Flask

Este documento explica cómo está configurada la conexión entre el frontend Angular y el backend Flask.

## 📋 Configuración Realizada

### 1. Archivos de Environment

Se crearon archivos de configuración para diferentes entornos:

- **`src/environments/environment.ts`** - Configuración de desarrollo
  - `apiUrl: 'http://localhost:5000/api'`

- **`src/environments/environment.prod.ts`** - Configuración de producción
  - `apiUrl: 'https://api.tudominio.com/api'` (cambiar según tu dominio)

### 2. Configuración de HttpClient

Se configuró `HttpClient` en `app.config.ts` para permitir peticiones HTTP al backend:

```typescript
provideHttpClient(withInterceptorsFromDi())
```

### 3. Servicios Actualizados

#### AuthService (`src/app/services/auth.service.ts`)

- ✅ **Login**: Conectado al endpoint `/api/users` para autenticación
- ✅ **Register**: Conectado al endpoint `POST /api/users` para registro
- ✅ Usa `HttpClient` y `Observables` para comunicación asíncrona
- ✅ Manejo de errores implementado

**Endpoints utilizados:**
- `GET /api/users` - Para buscar usuario en login
- `POST /api/users` - Para registrar nuevo usuario

#### EmployeeService (`src/app/services/employee.service.ts`)

- ✅ **Cargar empleados**: `GET /api/empleados`
- ✅ **Obtener por ID**: `GET /api/empleados/{id}`
- ✅ **Crear empleado**: `POST /api/empleados`
- ✅ **Actualizar empleado**: `PUT /api/empleados/{id}`
- ✅ **Eliminar empleado**: `DELETE /api/empleados/{id}`
- ✅ Normalización de datos entre formato backend y frontend

### 4. Componentes Actualizados

#### Login Component (`src/app/login/login.ts`)

- ✅ Actualizado para usar `Observables` en lugar de `Promises`
- ✅ Manejo de errores mejorado
- ✅ Mensajes de error más descriptivos

#### Register Component (`src/app/register/register.ts`)

- ✅ Conectado al servicio de autenticación
- ✅ Envía datos al backend para registro
- ✅ Redirige al login después de registro exitoso

---

## 🚀 Cómo Usar

### 1. Iniciar el Backend

```bash
cd backend
python app.py
# O usar el script
.\iniciar-api.ps1
```

El backend estará disponible en: `http://localhost:5000`

### 2. Iniciar el Frontend

```bash
cd RRHH
npm start
# O usar el script
.\iniciar-servidor.ps1
```

El frontend estará disponible en: `http://localhost:4200`

### 3. Verificar la Conexión

1. Abre el navegador en `http://localhost:4200`
2. Intenta hacer login o registro
3. Revisa la consola del navegador (F12) para ver las peticiones HTTP
4. Revisa la consola del backend para ver las peticiones recibidas

---

## 🔧 Configuración de CORS

El backend ya está configurado para aceptar peticiones desde `http://localhost:4200`.

Si necesitas cambiar el origen permitido, edita `backend/.env`:

```env
CORS_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
```

---

## 📡 Endpoints Utilizados

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users` | Listar usuarios (usado en login) |
| POST | `/api/users` | Registrar nuevo usuario |

### Empleados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/empleados` | Listar todos los empleados |
| GET | `/api/empleados/{id}` | Obtener empleado por ID |
| POST | `/api/empleados` | Crear nuevo empleado |
| PUT | `/api/empleados/{id}` | Actualizar empleado |
| DELETE | `/api/empleados/{id}` | Eliminar empleado |

---

## 🐛 Solución de Problemas

### Error: "Error al conectar con el servidor"

**Causa**: El backend no está ejecutándose o no está accesible.

**Solución**:
1. Verifica que el backend esté corriendo en `http://localhost:5000`
2. Prueba acceder a `http://localhost:5000/api/health` en el navegador
3. Verifica que no haya errores en la consola del backend

### Error de CORS

**Causa**: El backend no permite peticiones desde el origen del frontend.

**Solución**:
1. Verifica `backend/.env` que `CORS_ORIGINS` incluya `http://localhost:4200`
2. Reinicia el backend después de cambiar `.env`

### Error 404 en las peticiones

**Causa**: La URL del API no es correcta.

**Solución**:
1. Verifica `src/environments/environment.ts` que `apiUrl` sea `http://localhost:5000/api`
2. Verifica que el backend esté usando el puerto 5000

### Los datos no se muestran

**Causa**: El formato de datos del backend no coincide con el esperado por el frontend.

**Solución**:
1. Revisa la consola del navegador para ver la respuesta del backend
2. Verifica que el backend esté retornando datos en el formato correcto:
   ```json
   {
     "status": "success",
     "data": [...]
   }
   ```

---

## 📝 Notas Importantes

1. **Login Actual**: El login actual busca usuarios por email. En producción, deberías implementar un endpoint específico de login que valide credenciales.

2. **Normalización de Datos**: El `EmployeeService` normaliza los datos del backend (que usa `correo`, `fecha_nacimiento`, etc.) al formato del frontend (que usa `email`, `fechaNacimiento`, etc.).

3. **Manejo de Errores**: Todos los servicios incluyen manejo de errores con mensajes descriptivos.

4. **Observables**: Los servicios usan `Observables` de RxJS para manejar peticiones asíncronas. Asegúrate de suscribirte correctamente en los componentes.

---

## 🔄 Próximos Pasos

1. **Implementar endpoint de login real** en el backend que valide credenciales
2. **Agregar autenticación JWT** para sesiones seguras
3. **Implementar guards** en Angular para proteger rutas
4. **Agregar interceptors** para incluir tokens en las peticiones
5. **Conectar otros servicios** (departamentos, asistencias, etc.)

---

## 📚 Referencias

- [Angular HttpClient](https://angular.dev/guide/http)
- [RxJS Observables](https://rxjs.dev/guide/observable)
- [Flask CORS](https://flask-cors.readthedocs.io/)

