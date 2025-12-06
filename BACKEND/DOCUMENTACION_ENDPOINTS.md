# 📚 Documentación Completa de Endpoints - Sistema RRHH

Este documento contiene la lista completa de todos los endpoints disponibles en el sistema de Recursos Humanos.

**URL Base:** `http://localhost:8000`

**Documentación Interactiva:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📋 Índice

1. [Guía Rápida: ¿Qué Endpoint Usar?](#guía-rápida-qué-endpoint-usar)
2. [Endpoints Principales](#endpoints-principales)
3. [Usuarios](#usuarios)
4. [Autenticación](#autenticación)
5. [Roles y Permisos](#roles-y-permisos)
6. [Departamentos](#departamentos)
7. [Empleados](#empleados)
8. [Puestos](#puestos)
9. [Contratos](#contratos)
10. [Asistencias](#asistencias)
11. [Nómina](#nómina)
12. [Vacaciones y Permisos](#vacaciones-y-permisos)
13. [Documentos](#documentos)
14. [Capacitaciones](#capacitaciones)
15. [Evaluaciones](#evaluaciones)
16. [Notificaciones](#notificaciones)
17. [Reportes y Exportaciones](#reportes-y-exportaciones)

---

## 🎯 Guía Rápida: ¿Qué Endpoint Usar?

Esta sección te ayuda a encontrar rápidamente el endpoint correcto según lo que necesites hacer.

### 🔐 Autenticación y Acceso

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Iniciar sesión y obtener token | `/api/usuarios/login` | `POST` |
| Verificar que el servidor está funcionando | `/api/health` | `GET` |

---

### 👥 Gestión de Usuarios

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los usuarios del sistema | `/api/usuarios` | `GET` |
| Ver un usuario específico | `/api/usuarios/{usuario_id}` | `GET` |
| Crear un nuevo usuario | `/api/usuarios` | `POST` |
| Actualizar datos de un usuario | `/api/usuarios/{usuario_id}` | `PUT` |
| Desactivar (eliminar) un usuario | `/api/usuarios/{usuario_id}` | `DELETE` |
| Activar/Desactivar un usuario rápidamente | `/api/usuarios/{usuario_id}/toggle-status` | `PATCH` |

**Ejemplo práctico:**
- Crear usuario: `POST /api/usuarios` con body: `{"nombre": "Juan Pérez", "email": "juan@empresa.com", "password": "pass123"}`
- Cambiar email: `PUT /api/usuarios/5` con body: `{"email": "juan.nuevo@empresa.com"}`

---

### 👤 Gestión de Empleados

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los empleados | `/api/empleados` | `GET` |
| Ver empleados de un departamento | `/api/empleados?departamento_id=1` | `GET` |
| Ver un empleado específico | `/api/empleados/{empleado_id}` | `GET` |
| Registrar un nuevo empleado | `/api/empleados` | `POST` |
| Actualizar datos de un empleado | `/api/empleados/{empleado_id}` | `PUT` |
| Desactivar un empleado | `/api/empleados/{empleado_id}` | `DELETE` |
| Vincular empleado con usuario del sistema | `/api/empleados/{empleado_id}/sincronizar-usuario` | `POST` |

**Ejemplo práctico:**
- Ver empleados de Tecnología: `GET /api/empleados?departamento_id=2`
- Crear empleado: `POST /api/empleados` con body: `{"nombre": "María", "apellido": "García", "email": "maria@empresa.com", ...}`

---

### 🏢 Gestión de Departamentos

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los departamentos | `/api/departamentos` | `GET` |
| Ver un departamento específico | `/api/departamentos/{departamento_id}` | `GET` |
| Crear un nuevo departamento | `/api/departamentos` | `POST` |

---

### 💼 Gestión de Puestos

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los puestos disponibles | `/api/puestos` | `GET` |
| Ver solo los nombres de puestos | `/api/puestos/nombres` | `GET` |
| Ver un puesto específico | `/api/puestos/{puesto_id}` | `GET` |
| Crear un nuevo puesto | `/api/puestos` | `POST` |
| Actualizar un puesto (ej: cambiar salario) | `/api/puestos/{puesto_id}` | `PUT` |
| Eliminar un puesto | `/api/puestos/{puesto_id}` | `DELETE` |

**Ejemplo práctico:**
- Crear puesto: `POST /api/puestos` con body: `{"nombre_puesto": "Desarrollador Senior", "nivel": "Senior", "salario_base": 50000}`
- Aumentar salario: `PUT /api/puestos/3` con body: `{"salario_base": 55000}`

---

### 📝 Gestión de Contratos

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los contratos | `/api/contratos` | `GET` |
| Ver contratos de un empleado | `/api/contratos?id_empleado=5` | `GET` |
| Ver un contrato específico | `/api/contratos/{contrato_id}` | `GET` |
| Crear un nuevo contrato | `/api/contratos` | `POST` |
| Actualizar un contrato | `/api/contratos/{contrato_id}` | `PUT` |
| Eliminar un contrato | `/api/contratos/{contrato_id}` | `DELETE` |
| Ver contratos próximos a vencer (alertas) | `/api/contratos/alertas/vencimiento?dias=30` | `GET` |

**Ejemplo práctico:**
- Contratos que vencen en 30 días: `GET /api/contratos/alertas/vencimiento?dias=30`
- Crear contrato: `POST /api/contratos` con body completo del contrato

---

### ⏰ Gestión de Asistencias

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todas las asistencias | `/api/asistencias` | `GET` |
| Ver asistencias de un empleado | `/api/asistencias?id_empleado=5` | `GET` |
| Ver asistencias en un rango de fechas | `/api/asistencias?fecha_inicio=2025-01-01&fecha_fin=2025-01-31` | `GET` |
| Ver una asistencia específica | `/api/asistencias/{asistencia_id}` | `GET` |
| Registrar una nueva asistencia | `/api/asistencias` | `POST` |
| Actualizar una asistencia (corregir hora) | `/api/asistencias/{asistencia_id}` | `PUT` |
| Eliminar una asistencia | `/api/asistencias/{asistencia_id}` | `DELETE` |
| Generar reporte de asistencias | `/api/asistencias/reporte` | `POST` |

**Ejemplo práctico:**
- Registrar entrada: `POST /api/asistencias` con body: `{"id_empleado": 5, "fecha": "2025-01-15", "hora_entrada": "08:00:00"}`
- Reporte mensual: `POST /api/asistencias/reporte` con body: `{"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"}`

---

### 💰 Gestión de Nómina

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todas las nóminas | `/api/nomina` | `GET` |
| Ver nóminas de un empleado | `/api/nomina?id_empleado=5` | `GET` |
| Ver nóminas de un mes específico | `/api/nomina?mes=1&anio=2025` | `GET` |
| Ver una nómina específica con detalles | `/api/nomina/{nomina_id}` | `GET` |
| Crear una nueva nómina | `/api/nomina` | `POST` |
| Ver historial de nóminas de un empleado | `/api/nomina/empleado/{empleado_id}/historial` | `GET` |

**Ejemplo práctico:**
- Crear nómina de enero: `POST /api/nomina` con body: `{"id_empleado": 5, "mes": 1, "anio": 2025, "salario_base": 50000, ...}`
- Ver todas las nóminas de enero 2025: `GET /api/nomina?mes=1&anio=2025`

---

### 🏖️ Gestión de Vacaciones y Permisos

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todas las solicitudes de vacaciones | `/api/vacaciones` | `GET` |
| Ver vacaciones de un empleado | `/api/vacaciones?id_empleado=5` | `GET` |
| Ver solo pendientes | `/api/vacaciones?estado=pendiente` | `GET` |
| Crear una solicitud de vacaciones | `/api/vacaciones` | `POST` |

**Ejemplo práctico:**
- Solicitar vacaciones: `POST /api/vacaciones` con body: `{"id_empleado": 5, "tipo": "vacaciones", "fecha_inicio": "2025-06-01", "fecha_fin": "2025-06-15", "motivo": "Vacaciones familiares"}`
- Ver pendientes: `GET /api/vacaciones?estado=pendiente`

---

### 📄 Gestión de Documentos

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los documentos | `/api/documentos` | `GET` |
| Ver documentos de un empleado | `/api/documentos?id_empleado=5` | `GET` |
| Ver documentos por tipo | `/api/documentos?tipo_documento=contrato` | `GET` |
| Subir un nuevo documento | `/api/documentos` | `POST` |

---

### 🎓 Gestión de Capacitaciones

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todas las capacitaciones | `/api/capacitaciones` | `GET` |
| Ver capacitaciones de un empleado | `/api/capacitaciones?id_empleado=5` | `GET` |
| Ver una capacitación específica | `/api/capacitaciones/{capacitacion_id}` | `GET` |
| Registrar una nueva capacitación | `/api/capacitaciones` | `POST` |
| Actualizar una capacitación | `/api/capacitaciones/{capacitacion_id}` | `PUT` |
| Eliminar una capacitación | `/api/capacitaciones/{capacitacion_id}` | `DELETE` |

**Ejemplo práctico:**
- Registrar curso: `POST /api/capacitaciones` con body: `{"id_empleado": 5, "nombre_curso": "Python Avanzado", "institucion": "Platzi", "fecha_inicio": "2025-01-01"}`

---

### ⭐ Gestión de Evaluaciones

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todas las evaluaciones | `/api/evaluaciones` | `GET` |
| Ver evaluaciones de un empleado | `/api/evaluaciones?id_empleado=5` | `GET` |
| Ver evaluaciones en un período | `/api/evaluaciones?fecha_inicio=2025-01-01&fecha_fin=2025-12-31` | `GET` |
| Ver una evaluación específica | `/api/evaluaciones/{evaluacion_id}` | `GET` |
| Crear una nueva evaluación | `/api/evaluaciones` | `POST` |
| Actualizar una evaluación | `/api/evaluaciones/{evaluacion_id}` | `PUT` |
| Eliminar una evaluación | `/api/evaluaciones/{evaluacion_id}` | `DELETE` |

**Ejemplo práctico:**
- Evaluar desempeño: `POST /api/evaluaciones` con body: `{"id_empleado": 5, "fecha": "2025-01-15", "evaluador": "Carlos Gómez", "puntaje": 85, "observaciones": "Excelente desempeño"}`

---

### 🔔 Gestión de Notificaciones

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todas las notificaciones | `/api/notificaciones` | `GET` |
| Ver notificaciones de un usuario | `/api/notificaciones?usuario_id=5` | `GET` |
| Ver notificaciones no leídas | `/api/notificaciones/usuario/{usuario_id}/no-leidas` | `GET` |
| Contar notificaciones no leídas | `/api/notificaciones/usuario/{usuario_id}/count` | `GET` |
| Ver una notificación específica | `/api/notificaciones/{notificacion_id}` | `GET` |
| Crear una notificación | `/api/notificaciones` | `POST` |
| Marcar como leída | `PATCH /api/notificaciones/{notificacion_id}` | `PATCH` |
| Marcar todas como leídas | `POST /api/notificaciones/marcar-todas-leidas/{usuario_id}` | `POST` |
| Eliminar una notificación | `/api/notificaciones/{notificacion_id}` | `DELETE` |
| Eliminar todas las leídas | `/api/notificaciones/usuario/{usuario_id}/leidas` | `DELETE` |

**Ejemplo práctico:**
- Ver cuántas notificaciones tengo: `GET /api/notificaciones/usuario/5/count`
- Marcar todas como leídas: `POST /api/notificaciones/marcar-todas-leidas/5`

---

### 🎭 Gestión de Roles y Permisos

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver todos los roles | `/api/roles` | `GET` |
| Ver un rol específico | `/api/roles/{rol_id}` | `GET` |
| Crear un nuevo rol | `/api/roles` | `POST` |
| Actualizar un rol | `/api/roles/{rol_id}` | `PUT` |
| Eliminar un rol | `/api/roles/{rol_id}` | `DELETE` |
| Asignar permisos a un rol | `/api/roles/{rol_id}/permisos` | `POST` |
| Ver todos los permisos disponibles | `/api/permisos` | `GET` |
| Crear un nuevo permiso | `/api/permisos` | `POST` |
| Ver permisos de un usuario | `/api/usuarios/{usuario_id}/permisos` | `GET` |
| Asignar rol a un usuario | `/api/usuarios/{usuario_id}/roles` | `POST` |

**Ejemplo práctico:**
- Ver permisos de un usuario: `GET /api/usuarios/5/permisos`
- Asignar permisos a un rol: `POST /api/roles/2/permisos` con body: `{"permisos": [1, 2, 3, 5]}`

---

### 📊 Reportes y Exportaciones

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Exportar empleados a PDF | `/api/reportes/empleados/export/pdf` | `GET` |
| Exportar empleados a Excel | `/api/reportes/empleados/export/excel` | `GET` |
| Exportar asistencias a PDF | `/api/reportes/asistencias/export/pdf` | `POST` |
| Exportar asistencias a Excel | `/api/reportes/asistencias/export/excel` | `POST` |
| Exportar nómina a PDF | `/api/reportes/nomina/export/pdf?mes=1&anio=2025` | `GET` |
| Exportar nómina a Excel | `/api/reportes/nomina/export/excel?mes=1&anio=2025` | `GET` |
| Exportar vacaciones a PDF | `/api/reportes/vacaciones/export/pdf` | `GET` |
| Exportar vacaciones a Excel | `/api/reportes/vacaciones/export/excel` | `GET` |

**Ejemplo práctico:**
- Descargar reporte de asistencias: `POST /api/reportes/asistencias/export/pdf` con body: `{"fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-31"}`

---

### 📋 Auditoría

| **Quiero...** | **Endpoint** | **Método** |
|--------------|-------------|-----------|
| Ver registros de auditoría | `/api/usuarios/auditoria` | `GET` |
| Ver auditoría de un usuario | `/api/usuarios/auditoria?usuario_id=5` | `GET` |
| Ver auditoría por acción | `/api/usuarios/auditoria?accion=LOGIN` | `GET` |
| Ver auditoría en un período | `/api/usuarios/auditoria?fecha_inicio=2025-01-01&fecha_fin=2025-01-31` | `GET` |
| Crear registro de auditoría | `/api/usuarios/auditoria` | `POST` |

---

## 🔄 Flujos Comunes

### Flujo 1: Registrar un nuevo empleado completo
1. `GET /api/departamentos` - Ver departamentos disponibles
2. `GET /api/puestos` - Ver puestos disponibles
3. `POST /api/empleados` - Crear el empleado
4. `POST /api/contratos` - Crear su contrato
5. `POST /api/empleados/{id}/sincronizar-usuario` - Crear usuario del sistema
6. `POST /api/usuarios/login` - El empleado inicia sesión

### Flujo 2: Procesar nómina mensual
1. `GET /api/empleados` - Ver todos los empleados activos
2. `GET /api/asistencias?fecha_inicio=...&fecha_fin=...` - Revisar asistencias del mes
3. `POST /api/nomina` - Crear nómina para cada empleado
4. `GET /api/reportes/nomina/export/pdf?mes=X&anio=2025` - Generar reporte PDF

### Flujo 3: Gestionar solicitud de vacaciones
1. `POST /api/vacaciones` - Empleado crea solicitud (genera notificación automática)
2. `GET /api/notificaciones/usuario/{id}/no-leidas` - Supervisor ve notificación
3. `GET /api/vacaciones/{id}` - Supervisor revisa solicitud
4. `PUT /api/vacaciones/{id}` - Supervisor aprueba/rechaza
5. `PATCH /api/notificaciones/{id}` - Marcar notificación como leída

### Flujo 4: Reporte completo de un empleado
1. `GET /api/empleados/{id}` - Datos del empleado
2. `GET /api/contratos?id_empleado={id}` - Sus contratos
3. `GET /api/asistencias?id_empleado={id}` - Sus asistencias
4. `GET /api/nomina/empleado/{id}/historial` - Historial de nóminas
5. `GET /api/vacaciones?id_empleado={id}` - Sus vacaciones
6. `GET /api/capacitaciones?id_empleado={id}` - Sus capacitaciones
7. `GET /api/evaluaciones?id_empleado={id}` - Sus evaluaciones

---

## 💡 Tips Rápidos

- **Siempre primero:** `POST /api/usuarios/login` para obtener el token de autenticación
- **Para listar con filtros:** Agrega parámetros query string, ej: `?id_empleado=5&estado=activo`
- **Para crear:** Usa `POST` con body JSON completo
- **Para actualizar parcial:** Usa `PUT` solo con los campos que quieres cambiar
- **Para eliminar:** Usa `DELETE` (en este sistema es "soft delete", desactiva el registro)
- **Para exportar:** Los endpoints de exportación devuelven archivos descargables

---

## 🔧 Endpoints Principales

### GET `/`
**Descripción:** Endpoint principal de la API  
**Respuesta:**
```json
{
  "mensaje": "Bienvenido a la API del Sistema de RRHH",
  "version": "1.0.0",
  "status": "activo",
  "documentacion": "/docs"
}
```

### GET `/api/health`
**Descripción:** Verificar estado del servidor y base de datos  
**Respuesta:**
```json
{
  "status": "ok",
  "database": "conectada",
  "mensaje": "Sistema funcionando correctamente"
}
```

---

## 👥 Usuarios

### GET `/api/usuarios`
**Descripción:** Listar todos los usuarios (activos e inactivos)  
**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Admin",
      "email": "admin@rrhh.com",
      "rol": "administrador",
      "fecha_creacion": "2025-01-01 10:00:00",
      "activo": 1
    }
  ],
  "count": 1
}
```

### GET `/api/usuarios/{usuario_id}`
**Descripción:** Obtener un usuario por ID  
**Parámetros:**
- `usuario_id` (int): ID del usuario

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Admin",
    "email": "admin@rrhh.com",
    "rol": "administrador",
    "fecha_creacion": "2025-01-01 10:00:00",
    "activo": 1
  }
}
```

### POST `/api/usuarios`
**Descripción:** Crear un nuevo usuario  
**Campos requeridos:**
- `nombre` (string): Nombre completo del usuario (mínimo 2 caracteres)
- `email` (string): Email único del usuario (formato email válido)
- `password` (string): Contraseña (mínimo 6 caracteres)

**Campos opcionales:**
- `rol` (string): Rol del usuario. Valores: `administrador`, `supervisor`, `empleado`. Default: `empleado`

**Body de ejemplo:**
```json
{
  "nombre": "Omar Nuñez",
  "email": "omar.nuñez@empresa.com",
  "password": "password123",
  "rol": "empleado"
}
```

**Ejemplo con cURL:**
```bash
curl -X POST http://localhost:8000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Omar Nuñez",
    "email": "omar.nuñez@empresa.com",
    "password": "password123",
    "rol": "empleado"
  }'
```

**Respuesta:** `201 Created`
```json
{
  "success": true,
  "message": "Usuario creado exitosamente",
  "data": {
    "id": 1,
    "nombre": "Omar Nuñez",
    "email": "omar.nuñez@empresa.com",
    "rol": "empleado",
    "fecha_creacion": "2025-01-15 10:00:00",
    "activo": 1
  }
}
```

**Errores comunes:**
- `400 Bad Request`: Email ya está registrado
- `422 Unprocessable Entity`: Validación fallida (campos requeridos faltantes, formato inválido)

### PUT `/api/usuarios/{usuario_id}`
**Descripción:** Actualizar un usuario existente  
**Parámetros:**
- `usuario_id` (int): ID del usuario

**Todos los campos son opcionales** (solo se actualizan los campos enviados):
- `nombre` (string): Nombre completo del usuario
- `email` (string): Email único del usuario
- `password` (string): Nueva contraseña
- `rol` (string): Rol del usuario
- `activo` (boolean): Estado activo/inactivo

**Body de ejemplo (actualizar solo email):**
```json
{
  "email": "omar.nunez.nuevo@empresa.com"
}
```

**Body de ejemplo (actualizar múltiples campos):**
```json
{
  "nombre": "Omar Nuñez Actualizado",
  "email": "omar.nuevo@empresa.com",
  "rol": "supervisor"
}
```

**Ejemplo con cURL:**
```bash
curl -X PUT http://localhost:8000/api/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "omar.nuevo@empresa.com",
    "rol": "supervisor"
  }'
```

**Respuesta:** `200 OK`
```json
{
  "success": true,
  "message": "Usuario actualizado exitosamente",
  "data": {
    "id": 1,
    "nombre": "Omar Nuñez",
    "email": "omar.nuevo@empresa.com",
    "rol": "supervisor",
    "fecha_creacion": "2025-01-15 10:00:00",
    "activo": 1
  }
}
```

**⚠️ Nota Importante:** 
- El modelo de usuarios **NO tiene** campo `apellido` separado. Solo tiene `nombre` que debe contener el nombre completo.
- Si envías campos que no existen en el modelo (como `apellido`), serán ignorados por FastAPI.
- Para crear un usuario, **debes incluir** `nombre`, `email` y `password` como mínimo.
- Si intentas crear un usuario solo con `email` y `apellido`, recibirás un error de validación.

### DELETE `/api/usuarios/{usuario_id}`
**Descripción:** Eliminar (desactivar) un usuario  
**Parámetros:**
- `usuario_id` (int): ID del usuario

### PATCH `/api/usuarios/{usuario_id}/toggle-status`
**Descripción:** Activar/Desactivar un usuario  
**Parámetros:**
- `usuario_id` (int): ID del usuario

---

## 🔐 Autenticación

### POST `/api/usuarios/login`
**Descripción:** Autenticar un usuario y generar token JWT  
**Body:**
```json
{
  "email": "admin@rrhh.com",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nombre": "Admin",
    "email": "admin@rrhh.com",
    "rol": "administrador"
  }
}
```

---

## 🎭 Roles y Permisos

### GET `/api/roles`
**Descripción:** Listar todos los roles  
**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_rol": 1,
      "nombre_rol": "administrador",
      "descripcion": "Acceso completo al sistema"
    }
  ],
  "count": 1
}
```

### GET `/api/roles/{rol_id}`
**Descripción:** Obtener un rol específico por ID  
**Parámetros:**
- `rol_id` (int): ID del rol

### POST `/api/roles`
**Descripción:** Crear un nuevo rol  
**Body:**
```json
{
  "nombre_rol": "supervisor",
  "descripcion": "Supervisor de departamento"
}
```

### PUT `/api/roles/{rol_id}`
**Descripción:** Actualizar un rol existente  
**Parámetros:**
- `rol_id` (int): ID del rol

**Body:**
```json
{
  "nombre_rol": "supervisor_actualizado",
  "descripcion": "Nueva descripción"
}
```

### DELETE `/api/roles/{rol_id}`
**Descripción:** Eliminar un rol  
**Parámetros:**
- `rol_id` (int): ID del rol

### POST `/api/roles/{rol_id}/permisos`
**Descripción:** Asignar permisos a un rol  
**Parámetros:**
- `rol_id` (int): ID del rol

**Body:**
```json
{
  "permisos": [1, 2, 3]
}
```

### GET `/api/permisos`
**Descripción:** Listar todos los permisos disponibles

### POST `/api/permisos`
**Descripción:** Crear un nuevo permiso  
**Body:**
```json
{
  "nombre_permiso": "crear_empleados",
  "descripcion": "Permiso para crear empleados"
}
```

### GET `/api/usuarios/{usuario_id}/permisos`
**Descripción:** Obtener permisos de un usuario específico  
**Parámetros:**
- `usuario_id` (int): ID del usuario

### POST `/api/usuarios/{usuario_id}/roles`
**Descripción:** Asignar roles a un usuario  
**Parámetros:**
- `usuario_id` (int): ID del usuario

**Body:**
```json
{
  "id_rol": 2
}
```

---

## 📊 Auditoría

### GET `/api/usuarios/auditoria`
**Descripción:** Obtener registros de auditoría de usuarios  
**Parámetros opcionales:**
- `usuario_id` (int): Filtrar por usuario
- `accion` (str): Filtrar por acción
- `fecha_inicio` (str): Fecha inicial (YYYY-MM-DD)
- `fecha_fin` (str): Fecha final (YYYY-MM-DD)

### POST `/api/usuarios/auditoria`
**Descripción:** Crear un registro de auditoría  
**Body:**
```json
{
  "usuario_id": 1,
  "accion": "LOGIN",
  "detalles": "Inicio de sesión exitoso"
}
```

---

## 🏢 Departamentos

### GET `/api/departamentos`
**Descripción:** Listar todos los departamentos  
**Respuesta:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "nombre": "Recursos Humanos",
      "descripcion": "Departamento de RRHH"
    }
  ],
  "count": 1
}
```

### GET `/api/departamentos/{departamento_id}`
**Descripción:** Obtener un departamento por ID  
**Parámetros:**
- `departamento_id` (int): ID del departamento

### POST `/api/departamentos`
**Descripción:** Crear un nuevo departamento  
**Body:**
```json
{
  "nombre": "Tecnología",
  "descripcion": "Departamento de Tecnología"
}
```

---

## 👤 Empleados

### GET `/api/empleados`
**Descripción:** Listar todos los empleados con información de departamento  
**Parámetros opcionales:**
- `departamento_id` (int): Filtrar por departamento
- `activo` (bool): Filtrar por estado activo/inactivo

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_empleado": 1,
      "nombre": "Juan",
      "apellido": "Pérez",
      "email": "juan@example.com",
      "departamento": "Tecnología",
      "puesto": "Desarrollador",
      "salario": 50000,
      "fecha_ingreso": "2025-01-01",
      "activo": 1
    }
  ],
  "count": 1
}
```

### GET `/api/empleados/{empleado_id}`
**Descripción:** Obtener un empleado por ID  
**Parámetros:**
- `empleado_id` (int): ID del empleado

### POST `/api/empleados`
**Descripción:** Crear un nuevo empleado  
**Body:**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan@example.com",
  "telefono": "1234567890",
  "fecha_nacimiento": "1990-01-01",
  "direccion": "Calle 123",
  "id_departamento": 1,
  "id_puesto": 1,
  "salario": 50000,
  "fecha_ingreso": "2025-01-01"
}
```

### PUT `/api/empleados/{empleado_id}`
**Descripción:** Actualizar un empleado existente  
**Parámetros:**
- `empleado_id` (int): ID del empleado

### DELETE `/api/empleados/{empleado_id}`
**Descripción:** Eliminar (desactivar) un empleado  
**Parámetros:**
- `empleado_id` (int): ID del empleado

### POST `/api/empleados/{empleado_id}/sincronizar-usuario`
**Descripción:** Sincronizar un empleado con un usuario del sistema  
**Parámetros:**
- `empleado_id` (int): ID del empleado

**Body:**
```json
{
  "usuario_id": 1
}
```

---

## 💼 Puestos

### GET `/api/puestos`
**Descripción:** Listar todos los puestos  
**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_puesto": 1,
      "nombre_puesto": "Desarrollador Senior",
      "nivel": "Senior",
      "salario_base": 45000.00
    }
  ],
  "count": 1
}
```

### GET `/api/puestos/nombres`
**Descripción:** Listar solo los nombres de los puestos (endpoint legacy)

### GET `/api/puestos/{puesto_id}`
**Descripción:** Obtener un puesto específico por ID  
**Parámetros:**
- `puesto_id` (int): ID del puesto

### POST `/api/puestos`
**Descripción:** Crear un nuevo puesto  
**Body:**
```json
{
  "nombre_puesto": "Desarrollador Senior",
  "nivel": "Senior",
  "salario_base": 45000.00
}
```

### PUT `/api/puestos/{puesto_id}`
**Descripción:** Actualizar un puesto existente  
**Parámetros:**
- `puesto_id` (int): ID del puesto

### DELETE `/api/puestos/{puesto_id}`
**Descripción:** Eliminar un puesto (no permite si hay empleados asignados)  
**Parámetros:**
- `puesto_id` (int): ID del puesto

---

## 📝 Contratos

### GET `/api/contratos`
**Descripción:** Listar contratos, opcionalmente filtrados por empleado  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_contrato": 1,
      "id_empleado": 1,
      "tipo_contrato": "Indefinido",
      "fecha_inicio": "2025-01-01",
      "fecha_fin": null,
      "salario": 50000,
      "empleado_nombre": "Juan Pérez"
    }
  ],
  "count": 1
}
```

### GET `/api/contratos/{contrato_id}`
**Descripción:** Obtener un contrato por ID  
**Parámetros:**
- `contrato_id` (int): ID del contrato

### POST `/api/contratos`
**Descripción:** Crear un nuevo contrato  
**Body:**
```json
{
  "id_empleado": 1,
  "tipo_contrato": "Indefinido",
  "fecha_inicio": "2025-01-01",
  "fecha_fin": null,
  "salario": 50000,
  "descripcion": "Contrato de trabajo"
}
```

### PUT `/api/contratos/{contrato_id}`
**Descripción:** Actualizar un contrato existente  
**Parámetros:**
- `contrato_id` (int): ID del contrato

### DELETE `/api/contratos/{contrato_id}`
**Descripción:** Eliminar un contrato  
**Parámetros:**
- `contrato_id` (int): ID del contrato

### GET `/api/contratos/alertas/vencimiento`
**Descripción:** Obtener alertas de contratos próximos a vencer  
**Parámetros opcionales:**
- `dias` (int): Días de anticipación para alertas (default: 30)

---

## ⏰ Asistencias

### GET `/api/asistencias`
**Descripción:** Listar registros de asistencia  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado
- `fecha_inicio` (str): Fecha inicial (YYYY-MM-DD)
- `fecha_fin` (str): Fecha final (YYYY-MM-DD)

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_asistencia": 1,
      "id_empleado": 1,
      "fecha": "2025-01-15",
      "hora_entrada": "08:00:00",
      "hora_salida": "17:00:00",
      "estado": "presente",
      "nombre_empleado": "Juan Pérez"
    }
  ],
  "count": 1
}
```

### GET `/api/asistencias/{asistencia_id}`
**Descripción:** Obtener un registro de asistencia por ID  
**Parámetros:**
- `asistencia_id` (int): ID de la asistencia

### POST `/api/asistencias`
**Descripción:** Registrar una nueva asistencia  
**Body:**
```json
{
  "id_empleado": 1,
  "fecha": "2025-01-15",
  "hora_entrada": "08:00:00",
  "hora_salida": "17:00:00",
  "estado": "presente"
}
```

### PUT `/api/asistencias/{asistencia_id}`
**Descripción:** Actualizar un registro de asistencia  
**Parámetros:**
- `asistencia_id` (int): ID de la asistencia

### DELETE `/api/asistencias/{asistencia_id}`
**Descripción:** Eliminar un registro de asistencia  
**Parámetros:**
- `asistencia_id` (int): ID de la asistencia

### POST `/api/asistencias/reporte`
**Descripción:** Generar reporte de asistencias  
**Body:**
```json
{
  "id_empleado": 1,
  "fecha_inicio": "2025-01-01",
  "fecha_fin": "2025-01-31"
}
```

---

## 💰 Nómina

### GET `/api/nomina`
**Descripción:** Listar nóminas con filtros opcionales  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado
- `mes` (int): Filtrar por mes (1-12)
- `anio` (int): Filtrar por año

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_nomina": 1,
      "id_empleado": 1,
      "mes": 1,
      "anio": 2025,
      "periodo": "01/2025",
      "salario_base": 50000,
      "bonificaciones_total": 5000,
      "deducciones_total": 2500,
      "salario_neto": 52500,
      "estado": "pagado",
      "nombre_empleado": "Juan Pérez"
    }
  ],
  "count": 1
}
```

### GET `/api/nomina/{nomina_id}`
**Descripción:** Obtener una nómina por ID con detalles de bonificaciones y deducciones  
**Parámetros:**
- `nomina_id` (int): ID de la nómina

### POST `/api/nomina`
**Descripción:** Crear una nueva nómina  
**Body:**
```json
{
  "id_empleado": 1,
  "mes": 1,
  "anio": 2025,
  "salario_base": 50000,
  "fecha_pago": "2025-01-31",
  "observaciones": "Nómina de enero",
  "bonificaciones": [
    {
      "concepto": "Bono por desempeño",
      "tipo": "bonificacion",
      "monto": 5000,
      "descripcion": "Bono trimestral"
    }
  ],
  "deducciones": [
    {
      "concepto": "ISR",
      "tipo": "deduccion",
      "monto": 2500,
      "descripcion": "Impuesto sobre la renta"
    }
  ]
}
```

### GET `/api/nomina/empleado/{empleado_id}/historial`
**Descripción:** Obtener historial de nóminas de un empleado  
**Parámetros:**
- `empleado_id` (int): ID del empleado

---

## 🏖️ Vacaciones y Permisos

### GET `/api/vacaciones`
**Descripción:** Listar vacaciones y permisos  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado
- `estado` (str): Filtrar por estado (pendiente, aprobado, rechazado)

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_permiso": 1,
      "id_empleado": 1,
      "tipo": "vacaciones",
      "fecha_inicio": "2025-06-01",
      "fecha_fin": "2025-06-15",
      "dias_solicitados": 15,
      "motivo": "Vacaciones de verano",
      "estado": "pendiente",
      "nombre_empleado": "Juan Pérez"
    }
  ],
  "count": 1
}
```

### POST `/api/vacaciones`
**Descripción:** Crear una solicitud de vacaciones o permiso  
**Body:**
```json
{
  "id_empleado": 1,
  "tipo": "vacaciones",
  "fecha_inicio": "2025-06-01",
  "fecha_fin": "2025-06-15",
  "dias_solicitados": 15,
  "motivo": "Vacaciones de verano"
}
```

**Nota:** Este endpoint crea notificaciones automáticas para supervisores y administradores.

---

## 📄 Documentos

### GET `/api/documentos`
**Descripción:** Listar documentos  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado
- `tipo_documento` (str): Filtrar por tipo de documento

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_documento": 1,
      "id_empleado": 1,
      "tipo_documento": "contrato",
      "nombre_archivo": "contrato_juan.pdf",
      "ruta_archivo": "/uploads/documents/contrato_juan.pdf",
      "fecha_subida": "2025-01-01",
      "nombre_empleado": "Juan Pérez"
    }
  ],
  "count": 1
}
```

---

## 🎓 Capacitaciones

### GET `/api/capacitaciones`
**Descripción:** Listar todas las capacitaciones  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_capacitacion": 1,
      "id_empleado": 1,
      "nombre_curso": "Python Avanzado",
      "institucion": "Platzi",
      "fecha_inicio": "2025-01-01",
      "fecha_fin": "2025-03-01",
      "certificado": true,
      "nombre_empleado": "Juan Pérez"
    }
  ],
  "count": 1
}
```

### GET `/api/capacitaciones/{capacitacion_id}`
**Descripción:** Obtener una capacitación específica  
**Parámetros:**
- `capacitacion_id` (int): ID de la capacitación

### POST `/api/capacitaciones`
**Descripción:** Registrar una nueva capacitación  
**Body:**
```json
{
  "id_empleado": 1,
  "nombre_curso": "Python Avanzado",
  "institucion": "Platzi",
  "fecha_inicio": "2025-01-01",
  "fecha_fin": "2025-03-01",
  "certificado": true
}
```

### PUT `/api/capacitaciones/{capacitacion_id}`
**Descripción:** Actualizar una capacitación existente  
**Parámetros:**
- `capacitacion_id` (int): ID de la capacitación

### DELETE `/api/capacitaciones/{capacitacion_id}`
**Descripción:** Eliminar una capacitación  
**Parámetros:**
- `capacitacion_id` (int): ID de la capacitación

---

## ⭐ Evaluaciones

### GET `/api/evaluaciones`
**Descripción:** Listar todas las evaluaciones  
**Parámetros opcionales:**
- `id_empleado` (int): Filtrar por empleado
- `fecha_inicio` (str): Filtrar desde fecha (YYYY-MM-DD)
- `fecha_fin` (str): Filtrar hasta fecha (YYYY-MM-DD)

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_evaluacion": 1,
      "id_empleado": 1,
      "fecha": "2025-01-15",
      "evaluador": "Carlos Gómez",
      "puntaje": 85,
      "observaciones": "Excelente desempeño",
      "nombre_empleado": "Juan Pérez"
    }
  ],
  "count": 1
}
```

### GET `/api/evaluaciones/{evaluacion_id}`
**Descripción:** Obtener una evaluación específica  
**Parámetros:**
- `evaluacion_id` (int): ID de la evaluación

### POST `/api/evaluaciones`
**Descripción:** Crear una nueva evaluación de desempeño  
**Body:**
```json
{
  "id_empleado": 1,
  "fecha": "2025-01-15",
  "evaluador": "Carlos Gómez",
  "puntaje": 85,
  "observaciones": "Excelente desempeño en el último trimestre"
}
```

**Validaciones:**
- Puntaje debe estar entre 0 y 100
- Verifica que el empleado exista

### PUT `/api/evaluaciones/{evaluacion_id}`
**Descripción:** Actualizar una evaluación existente  
**Parámetros:**
- `evaluacion_id` (int): ID de la evaluación

### DELETE `/api/evaluaciones/{evaluacion_id}`
**Descripción:** Eliminar una evaluación  
**Parámetros:**
- `evaluacion_id` (int): ID de la evaluación

---

## 🔔 Notificaciones

### GET `/api/notificaciones`
**Descripción:** Listar todas las notificaciones  
**Parámetros opcionales:**
- `usuario_id` (int): Filtrar por usuario
- `leido` (bool): Filtrar por estado de lectura
- `tipo` (str): Filtrar por tipo de notificación

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_notificacion": 1,
      "usuario_id": 1,
      "titulo": "Nueva solicitud de vacaciones",
      "mensaje": "Juan Pérez ha solicitado vacaciones",
      "tipo": "vacaciones",
      "leido": false,
      "fecha_creacion": "2025-01-15 10:00:00"
    }
  ],
  "count": 1
}
```

### GET `/api/notificaciones/{notificacion_id}`
**Descripción:** Obtener una notificación específica  
**Parámetros:**
- `notificacion_id` (int): ID de la notificación

### GET `/api/notificaciones/usuario/{usuario_id}/no-leidas`
**Descripción:** Obtener notificaciones no leídas de un usuario  
**Parámetros:**
- `usuario_id` (int): ID del usuario

### GET `/api/notificaciones/usuario/{usuario_id}/count`
**Descripción:** Obtener contador de notificaciones no leídas  
**Parámetros:**
- `usuario_id` (int): ID del usuario

**Respuesta:**
```json
{
  "success": true,
  "count": 5
}
```

### GET `/api/notificaciones/{usuario_id}`
**Descripción:** Obtener notificaciones de un usuario (endpoint legacy)  
**Parámetros:**
- `usuario_id` (int): ID del usuario

### POST `/api/notificaciones`
**Descripción:** Crear una nueva notificación  
**Body:**
```json
{
  "usuario_id": 1,
  "titulo": "Nueva solicitud",
  "mensaje": "Tienes una nueva solicitud pendiente",
  "tipo": "sistema"
}
```

### PATCH `/api/notificaciones/{notificacion_id}`
**Descripción:** Actualizar una notificación (generalmente para marcarla como leída)  
**Parámetros:**
- `notificacion_id` (int): ID de la notificación

**Body:**
```json
{
  "leido": true
}
```

### POST `/api/notificaciones/marcar-todas-leidas/{usuario_id}`
**Descripción:** Marcar todas las notificaciones de un usuario como leídas  
**Parámetros:**
- `usuario_id` (int): ID del usuario

### DELETE `/api/notificaciones/{notificacion_id}`
**Descripción:** Eliminar una notificación  
**Parámetros:**
- `notificacion_id` (int): ID de la notificación

### DELETE `/api/notificaciones/usuario/{usuario_id}/leidas`
**Descripción:** Eliminar todas las notificaciones leídas de un usuario  
**Parámetros:**
- `usuario_id` (int): ID del usuario

---

## 📊 Reportes y Exportaciones

### GET `/api/reportes/empleados/export/pdf`
**Descripción:** Exportar reporte de empleados a PDF  
**Respuesta:** Archivo PDF descargable

**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename=reporte_empleados_YYYYMMDD.pdf
```

### GET `/api/reportes/empleados/export/excel`
**Descripción:** Exportar reporte de empleados a Excel  
**Respuesta:** Archivo Excel descargable

**Headers:**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=reporte_empleados_YYYYMMDD.xlsx
```

### POST `/api/reportes/asistencias/export/pdf`
**Descripción:** Exportar reporte de asistencias a PDF  
**Body:**
```json
{
  "id_empleado": 1,
  "fecha_inicio": "2025-01-01",
  "fecha_fin": "2025-01-31"
}
```

**Respuesta:** Archivo PDF descargable

### POST `/api/reportes/asistencias/export/excel`
**Descripción:** Exportar reporte de asistencias a Excel  
**Body:**
```json
{
  "id_empleado": 1,
  "fecha_inicio": "2025-01-01",
  "fecha_fin": "2025-01-31"
}
```

**Respuesta:** Archivo Excel descargable

### GET `/api/reportes/nomina/export/pdf`
**Descripción:** Exportar reporte de nómina a PDF  
**Parámetros:**
- `mes` (int): Mes (1-12)
- `anio` (int): Año

**Ejemplo:** `/api/reportes/nomina/export/pdf?mes=1&anio=2025`

**Respuesta:** Archivo PDF descargable

### GET `/api/reportes/nomina/export/excel`
**Descripción:** Exportar reporte de nómina a Excel  
**Parámetros:**
- `mes` (int): Mes (1-12)
- `anio` (int): Año

**Ejemplo:** `/api/reportes/nomina/export/excel?mes=1&anio=2025`

**Respuesta:** Archivo Excel descargable

### GET `/api/reportes/vacaciones/export/pdf`
**Descripción:** Exportar reporte de vacaciones a PDF  
**Respuesta:** Archivo PDF descargable

### GET `/api/reportes/vacaciones/export/excel`
**Descripción:** Exportar reporte de vacaciones a Excel  
**Respuesta:** Archivo Excel descargable

---

## 📮 Ejemplos de Uso en Postman

### Configuración Inicial en Postman

1. **URL Base:** `http://localhost:8000`
2. **Headers:** Configurar `Content-Type: application/json` en los headers de la colección
3. **Authorization:** Para endpoints protegidos, agregar header `Authorization: Bearer {token}`

### Ejemplo: Crear Usuario (POST)

**Configuración:**
- **Método:** `POST`
- **URL:** `http://localhost:8000/api/usuarios`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw, JSON):**
```json
{
  "nombre": "Omar Nuñez",
  "email": "omar.nuñez@empresa.com",
  "password": "password123",
  "rol": "empleado"
}
```

**⚠️ Importante:** 
- El campo `nombre` es **requerido** y debe contener el nombre completo (no existe campo `apellido` separado en el modelo de usuarios)
- Si envías solo `email` sin `nombre` y `password`, recibirás un error `422 Unprocessable Entity`
- Para actualizar un usuario existente, usa `PUT /api/usuarios/{usuario_id}`

### Ejemplo: Actualizar Usuario (PUT)

**Configuración:**
- **Método:** `PUT`
- **URL:** `http://localhost:8000/api/usuarios/1`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw, JSON):**
```json
{
  "email": "omar.nuñez.nuevo@empresa.com"
}
```
O para actualizar múltiples campos:
```json
{
  "nombre": "Omar Nuñez Actualizado",
  "email": "omar.nuevo@empresa.com",
  "rol": "supervisor"
}
```

### Ejemplo: Login (POST)

**Configuración:**
- **Método:** `POST`
- **URL:** `http://localhost:8000/api/usuarios/login`
- **Body (raw, JSON):**
```json
{
  "email": "omar.nuñez@empresa.com",
  "password": "password123"
}
```

**Respuesta:** Guarda el `access_token` de la respuesta para usar en otros endpoints protegidos.

---

## 📝 Notas Generales

### Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en la solicitud (validación, datos inválidos)
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No autorizado
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

### Estructura de Respuesta Estándar

**Respuestas Exitosas:**
```json
{
  "success": true,
  "message": "Mensaje opcional",
  "data": { /* objeto o array */ },
  "count": 1  // solo en listas
}
```

**Respuestas de Error:**
```json
{
  "detail": "Mensaje de error descriptivo"
}
```

### Autenticación

La mayoría de los endpoints requieren autenticación mediante JWT. Para obtener un token:

1. POST a `/api/usuarios/login` con credenciales
2. Incluir el token en el header: `Authorization: Bearer {token}`

### Validaciones Comunes

- **IDs**: Deben ser enteros positivos
- **Fechas**: Formato YYYY-MM-DD
- **Emails**: Formato de email válido
- **Contraseñas**: Mínimo de caracteres según configuración del sistema

### Manejo de Errores

Todos los endpoints incluyen manejo robusto de errores:
- Validación de existencia de recursos
- Verificación de foreign keys
- Prevención de duplicados
- Mensajes de error descriptivos
- Logging detallado

---

## 🔗 Referencias

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/health`

---

**Última actualización:** Diciembre 2025  
**Versión de la API:** 1.0.0

