# API Endpoints - Sistema de RRHH

Documentación completa de todos los endpoints disponibles en el sistema de Recursos Humanos.

**Base URL:** `http://localhost:5000`

---

## 📋 Índice

1. [Endpoints del Sistema](#endpoints-del-sistema)
2. [Usuarios](#usuarios)
3. [Empleados (estructura antigua)](#empleados-estructura-antigua)
4. [Empleados (nueva estructura)](#empleados-nueva-estructura)
5. [Contratos](#contratos)
6. [Asistencias](#asistencias)
7. [Capacitaciones](#capacitaciones)
8. [Evaluaciones](#evaluaciones)
9. [Nómina](#nómina)
10. [Vacaciones y Permisos](#vacaciones-y-permisos)

---

## 🔧 Endpoints del Sistema

### Health Check
**GET** `/api/health`

Verifica el estado del servidor.

**Respuesta (200):**
```json
{
  "status": "ok",
  "message": "Backend funcionando correctamente"
}
```

---

### Inicializar Base de Datos
**POST** `/api/database/init`

Inicializa todas las tablas de la base de datos.

**Respuesta (200):**
```json
{
  "status": "success",
  "message": "Base de datos inicializada correctamente"
}
```

---

### Probar Conexión a Base de Datos
**GET** `/api/database/test`

Prueba la conexión a la base de datos y lista las tablas existentes.

**Respuesta (200):**
```json
{
  "status": "success",
  "message": "Conexión a la base de datos exitosa",
  "tables": ["users", "Empleados", "Contratos", ...]
}
```

---

## 👥 Usuarios

### Listar Todos los Usuarios
**GET** `/api/users`

Obtiene todos los usuarios registrados en el sistema.

**Respuesta (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "username": "juan_perez",
      "email": "juan@example.com",
      "created_at": "2024-01-15 10:30:00"
    }
  ],
  "count": 1
}
```

---

### Obtener Usuario por ID
**GET** `/api/users/<user_id>`

Obtiene un usuario específico por su ID.

**Parámetros:**
- `user_id` (int): ID del usuario

**Respuesta (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "juan_perez",
    "email": "juan@example.com",
    "created_at": "2024-01-15 10:30:00"
  }
}
```

---

### Crear Usuario
**POST** `/api/users`

Crea un nuevo usuario en el sistema.

**Body (JSON):**
```json
{
  "username": "maria_garcia",
  "email": "maria@example.com",
  "password": "contraseña123"
}
```

**Campos requeridos:**
- `username` (string): Nombre de usuario único
- `email` (string): Email único
- `password` (string): Contraseña en texto plano

**Respuesta (201):**
```json
{
  "status": "success",
  "message": "Usuario creado correctamente",
  "data": {
    "id": 2,
    "username": "maria_garcia",
    "email": "maria@example.com",
    "created_at": "2024-01-15 11:00:00"
  }
}
```

---

### Actualizar Usuario
**PUT** `/api/users/<user_id>`

Actualiza los datos de un usuario existente.

**Parámetros:**
- `user_id` (int): ID del usuario

**Body (JSON):** Todos los campos son opcionales
```json
{
  "username": "maria_garcia_nuevo",
  "email": "maria.nueva@example.com",
  "password": "nueva_contraseña123"
}
```

**Respuesta (200):**
```json
{
  "status": "success",
  "message": "Usuario actualizado correctamente",
  "data": {
    "id": 2,
    "username": "maria_garcia_nuevo",
    "email": "maria.nueva@example.com",
    "created_at": "2024-01-15 11:00:00"
  }
}
```

---

### Eliminar Usuario
**DELETE** `/api/users/<user_id>`

Elimina un usuario del sistema.

**Parámetros:**
- `user_id` (int): ID del usuario

**Respuesta (200):**
```json
{
  "status": "success",
  "message": "Usuario eliminado correctamente"
}
```

---

## 👤 Empleados (Estructura Antigua)

### Crear Empleado
**POST** `/api/employees`

Crea un nuevo empleado (tabla `employees`).

**Body (JSON):**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan.perez@example.com",
  "phone": "1234567890",
  "department_id": 1,
  "position": "Desarrollador Senior",
  "hire_date": "2024-01-15"
}
```

**Campos requeridos:**
- `first_name` (string): Nombre
- `last_name` (string): Apellido
- `email` (string): Email único

**Campos opcionales:**
- `phone` (string): Teléfono
- `department_id` (integer): ID del departamento
- `position` (string): Puesto
- `hire_date` (string): Fecha de contratación (YYYY-MM-DD)

---

### Listar Todos los Empleados
**GET** `/api/employees`

Obtiene todos los empleados de la tabla `employees`.

---

### Obtener Empleado por ID
**GET** `/api/employees/<employee_id>`

Obtiene un empleado específico por su ID.

---

### Actualizar Empleado
**PUT** `/api/employees/<employee_id>`

Actualiza los datos de un empleado existente.

---

### Eliminar Empleado
**DELETE** `/api/employees/<employee_id>`

Elimina un empleado de la tabla `employees`.

---

## 👔 Empleados (Nueva Estructura)

### Crear Empleado
**POST** `/api/empleados`

Crea un nuevo empleado en la tabla `Empleados`.

**Body (JSON):**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "fecha_nacimiento": "1990-05-15",
  "genero": "Masculino",
  "estado_civil": "Soltero",
  "direccion": "Calle 123, Ciudad",
  "telefono": "1234567890",
  "correo": "juan.perez@example.com",
  "fecha_ingreso": "2024-01-15",
  "estado": "Activo",
  "id_departamento": 1,
  "id_puesto": 1
}
```

**Campos requeridos:**
- `nombre` (string): Nombre del empleado
- `apellido` (string): Apellido del empleado

**Campos opcionales:**
- `fecha_nacimiento` (string): Fecha de nacimiento (YYYY-MM-DD)
- `genero` (string): Género
- `estado_civil` (string): Estado civil
- `direccion` (string): Dirección
- `telefono` (string): Teléfono
- `correo` (string): Correo electrónico
- `fecha_ingreso` (string): Fecha de ingreso (YYYY-MM-DD)
- `estado` (string): Estado (Activo, Suspendido, Retirado)
- `id_departamento` (integer): ID del departamento
- `id_puesto` (integer): ID del puesto

**Respuesta (201):**
```json
{
  "status": "success",
  "message": "Empleado creado correctamente",
  "data": {
    "id_empleado": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    ...
  }
}
```

---

### Listar Todos los Empleados
**GET** `/api/empleados`

Obtiene todos los empleados de la tabla `Empleados`.

---

### Obtener Empleado por ID
**GET** `/api/empleados/<empleado_id>`

Obtiene un empleado específico por su ID.

---

### Actualizar Empleado
**PUT** `/api/empleados/<empleado_id>`

Actualiza los datos de un empleado existente.

---

### Eliminar Empleado
**DELETE** `/api/empleados/<empleado_id>`

Elimina un empleado de la tabla `Empleados`.

---

## 📄 Contratos

### Crear Contrato
**POST** `/api/contratos`

Crea un nuevo contrato para un empleado.

**Body (JSON):**
```json
{
  "id_empleado": 1,
  "tipo_contrato": "Permanente",
  "fecha_inicio": "2024-01-15",
  "fecha_fin": null,
  "salario": 50000.00,
  "condiciones": "Contrato indefinido con beneficios completos"
}
```

**Campos requeridos:**
- `id_empleado` (integer): ID del empleado

**Campos opcionales:**
- `tipo_contrato` (string): Tipo (Permanente, Temporal, Honorarios)
- `fecha_inicio` (string): Fecha de inicio (YYYY-MM-DD)
- `fecha_fin` (string): Fecha de fin (YYYY-MM-DD)
- `salario` (float): Salario del contrato
- `condiciones` (string): Condiciones del contrato

**Respuesta (201):**
```json
{
  "status": "success",
  "message": "Contrato creado correctamente",
  "data": {
    "id_contrato": 1,
    "id_empleado": 1,
    "tipo_contrato": "Permanente",
    ...
  }
}
```

---

### Listar Todos los Contratos
**GET** `/api/contratos`

Obtiene todos los contratos registrados.

---

### Obtener Contrato por ID
**GET** `/api/contratos/<contrato_id>`

Obtiene un contrato específico por su ID.

---

### Obtener Contratos de un Empleado
**GET** `/api/contratos/empleado/<empleado_id>`

Obtiene todos los contratos asociados a un empleado específico.

**Respuesta (200):**
```json
{
  "status": "success",
  "data": [...],
  "count": 2
}
```

---

### Actualizar Contrato
**PUT** `/api/contratos/<contrato_id>`

Actualiza los datos de un contrato existente.

---

### Eliminar Contrato
**DELETE** `/api/contratos/<contrato_id>`

Elimina un contrato del sistema.

---

## ✅ Asistencias

### Crear Asistencia
**POST** `/api/asistencias`

Registra una nueva asistencia de un empleado.

**Body (JSON):**
```json
{
  "id_empleado": 1,
  "fecha": "2024-01-15",
  "hora_entrada": "09:00:00",
  "hora_salida": "18:00:00",
  "observaciones": "Asistencia normal"
}
```

**Campos requeridos:**
- `id_empleado` (integer): ID del empleado

**Campos opcionales:**
- `fecha` (string): Fecha de la asistencia (YYYY-MM-DD)
- `hora_entrada` (string): Hora de entrada (HH:MM:SS)
- `hora_salida` (string): Hora de salida (HH:MM:SS)
- `observaciones` (string): Observaciones

---

### Listar Todas las Asistencias
**GET** `/api/asistencias`

Obtiene todas las asistencias registradas.

---

### Obtener Asistencia por ID
**GET** `/api/asistencias/<asistencia_id>`

Obtiene una asistencia específica por su ID.

---

### Obtener Asistencias de un Empleado
**GET** `/api/asistencias/empleado/<empleado_id>`

Obtiene todas las asistencias de un empleado específico.

---

### Actualizar Asistencia
**PUT** `/api/asistencias/<asistencia_id>`

Actualiza los datos de una asistencia existente.

---

### Eliminar Asistencia
**DELETE** `/api/asistencias/<asistencia_id>`

Elimina una asistencia del sistema.

---

## 🎓 Capacitaciones

### Crear Capacitación
**POST** `/api/capacitaciones`

Registra una nueva capacitación para un empleado.

**Body (JSON):**
```json
{
  "id_empleado": 1,
  "nombre_curso": "Desarrollo Web Moderno",
  "institucion": "Universidad XYZ",
  "fecha_inicio": "2024-01-01",
  "fecha_fin": "2024-03-31",
  "certificado": true
}
```

**Campos requeridos:**
- `id_empleado` (integer): ID del empleado

**Campos opcionales:**
- `nombre_curso` (string): Nombre del curso
- `institucion` (string): Institución que imparte el curso
- `fecha_inicio` (string): Fecha de inicio (YYYY-MM-DD)
- `fecha_fin` (string): Fecha de fin (YYYY-MM-DD)
- `certificado` (boolean): Si tiene certificado (true/false)

---

### Listar Todas las Capacitaciones
**GET** `/api/capacitaciones`

Obtiene todas las capacitaciones registradas.

---

### Obtener Capacitación por ID
**GET** `/api/capacitaciones/<capacitacion_id>`

Obtiene una capacitación específica por su ID.

---

### Obtener Capacitaciones de un Empleado
**GET** `/api/capacitaciones/empleado/<empleado_id>`

Obtiene todas las capacitaciones de un empleado específico.

---

### Actualizar Capacitación
**PUT** `/api/capacitaciones/<capacitacion_id>`

Actualiza los datos de una capacitación existente.

---

### Eliminar Capacitación
**DELETE** `/api/capacitaciones/<capacitacion_id>`

Elimina una capacitación del sistema.

---

## 📊 Evaluaciones

### Crear Evaluación
**POST** `/api/evaluaciones`

Registra una nueva evaluación de desempeño para un empleado.

**Body (JSON):**
```json
{
  "id_empleado": 1,
  "fecha": "2024-01-15",
  "evaluador": "María García",
  "puntaje": 85,
  "observaciones": "Desempeño excelente"
}
```

**Campos requeridos:**
- `id_empleado` (integer): ID del empleado

**Campos opcionales:**
- `fecha` (string): Fecha de la evaluación (YYYY-MM-DD)
- `evaluador` (string): Nombre del evaluador
- `puntaje` (integer): Puntaje de la evaluación
- `observaciones` (string): Observaciones sobre la evaluación

---

### Listar Todas las Evaluaciones
**GET** `/api/evaluaciones`

Obtiene todas las evaluaciones registradas.

---

### Obtener Evaluación por ID
**GET** `/api/evaluaciones/<evaluacion_id>`

Obtiene una evaluación específica por su ID.

---

### Obtener Evaluaciones de un Empleado
**GET** `/api/evaluaciones/empleado/<empleado_id>`

Obtiene todas las evaluaciones de un empleado específico.

---

### Actualizar Evaluación
**PUT** `/api/evaluaciones/<evaluacion_id>`

Actualiza los datos de una evaluación existente.

---

### Eliminar Evaluación
**DELETE** `/api/evaluaciones/<evaluacion_id>`

Elimina una evaluación del sistema.

---

## 💰 Nómina

### Crear Registro de Nómina
**POST** `/api/nomina`

Registra un nuevo pago de nómina para un empleado.

**Body (JSON):**
```json
{
  "id_empleado": 1,
  "mes": 1,
  "anio": 2024,
  "salario_base": 50000.00,
  "bonificaciones": 5000.00,
  "deducciones": 10000.00,
  "salario_neto": 45000.00,
  "fecha_pago": "2024-01-31"
}
```

**Campos requeridos:**
- `id_empleado` (integer): ID del empleado

**Campos opcionales:**
- `mes` (integer): Mes del pago (1-12)
- `anio` (integer): Año del pago
- `salario_base` (float): Salario base
- `bonificaciones` (float): Bonificaciones
- `deducciones` (float): Deducciones
- `salario_neto` (float): Salario neto (total a pagar)
- `fecha_pago` (string): Fecha de pago (YYYY-MM-DD)

---

### Listar Todos los Registros de Nómina
**GET** `/api/nomina`

Obtiene todos los registros de nómina.

---

### Obtener Registro de Nómina por ID
**GET** `/api/nomina/<nomina_id>`

Obtiene un registro de nómina específico por su ID.

---

### Obtener Nómina de un Empleado
**GET** `/api/nomina/empleado/<empleado_id>`

Obtiene todos los registros de nómina de un empleado específico.

---

### Actualizar Registro de Nómina
**PUT** `/api/nomina/<nomina_id>`

Actualiza los datos de un registro de nómina existente.

---

### Eliminar Registro de Nómina
**DELETE** `/api/nomina/<nomina_id>`

Elimina un registro de nómina del sistema.

---

## 🏖️ Vacaciones y Permisos

### Crear Vacación/Permiso
**POST** `/api/vacaciones-permisos`

Registra una nueva solicitud de vacación o permiso.

**Body (JSON):**
```json
{
  "id_empleado": 1,
  "tipo": "Vacación",
  "fecha_solicitud": "2024-01-15",
  "fecha_inicio": "2024-02-01",
  "fecha_fin": "2024-02-07",
  "estado": "Pendiente",
  "observaciones": "Vacaciones programadas"
}
```

**Campos requeridos:**
- `id_empleado` (integer): ID del empleado

**Campos opcionales:**
- `tipo` (string): Tipo (Vacación, Permiso, Licencia)
- `fecha_solicitud` (string): Fecha de solicitud (YYYY-MM-DD)
- `fecha_inicio` (string): Fecha de inicio (YYYY-MM-DD)
- `fecha_fin` (string): Fecha de fin (YYYY-MM-DD)
- `estado` (string): Estado (Aprobado, Pendiente, Rechazado)
- `observaciones` (string): Observaciones

**Respuesta (201):**
```json
{
  "status": "success",
  "message": "Vacación/Permiso creado correctamente",
  "data": {
    "id_permiso": 1,
    "id_empleado": 1,
    "tipo": "Vacación",
    ...
  }
}
```

---

### Listar Todas las Vacaciones y Permisos
**GET** `/api/vacaciones-permisos`

Obtiene todas las solicitudes de vacaciones y permisos.

---

### Obtener Vacación/Permiso por ID
**GET** `/api/vacaciones-permisos/<permiso_id>`

Obtiene una solicitud específica por su ID.

---

### Obtener Vacaciones/Permisos de un Empleado
**GET** `/api/vacaciones-permisos/empleado/<empleado_id>`

Obtiene todas las solicitudes de vacaciones/permisos de un empleado específico.

---

### Actualizar Vacación/Permiso
**PUT** `/api/vacaciones-permisos/<permiso_id>`

Actualiza los datos de una solicitud existente (útil para cambiar el estado a Aprobado/Rechazado).

---

### Eliminar Vacación/Permiso
**DELETE** `/api/vacaciones-permisos/<permiso_id>`

Elimina una solicitud de vacación/permiso del sistema.

---

## 🔐 Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Error de validación o datos incorrectos
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

---

## 📝 Notas Importantes

1. **Autenticación**: Actualmente los endpoints no requieren autenticación. Se recomienda implementar JWT o tokens de sesión para producción.

2. **Validaciones**: Todos los endpoints validan los datos requeridos y retornan mensajes de error descriptivos.

3. **CORS**: El CORS está habilitado para permitir peticiones desde el frontend Angular.

4. **Formato de Fechas**: Todas las fechas deben estar en formato `YYYY-MM-DD` y las horas en formato `HH:MM:SS`.

5. **IDs**: Todos los IDs en las rutas son números enteros (integer).

6. **Respuestas JSON**: Todas las respuestas siguen el formato:
   ```json
   {
     "status": "success|error",
     "message": "Mensaje descriptivo",
     "data": {...}
   }
   ```

---

## 📚 Ejemplos con cURL

### Crear un Empleado
```bash
curl -X POST http://localhost:5000/api/empleados \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo": "juan@example.com",
    "estado": "Activo"
  }'
```

### Obtener todos los empleados
```bash
curl http://localhost:5000/api/empleados
```

### Crear una asistencia
```bash
curl -X POST http://localhost:5000/api/asistencias \
  -H "Content-Type: application/json" \
  -d '{
    "id_empleado": 1,
    "fecha": "2024-01-15",
    "hora_entrada": "09:00:00",
    "hora_salida": "18:00:00"
  }'
```

### Actualizar estado de vacación
```bash
curl -X PUT http://localhost:5000/api/vacaciones-permisos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "Aprobado"
  }'
```

---

## 🔗 Tablas Relacionadas

- **Empleados** → Departamentos (id_departamento)
- **Empleados** → Puestos (id_puesto)
- **Contratos** → Empleados (id_empleado)
- **Asistencias** → Empleados (id_empleado)
- **Capacitaciones** → Empleados (id_empleado)
- **Evaluaciones** → Empleados (id_empleado)
- **Nomina** → Empleados (id_empleado)
- **Vacaciones_Permisos** → Empleados (id_empleado)

---

**Última actualización:** 2024-01-15
**Versión de la API:** 1.0.0

