# API de Usuarios - Documentación

Documentación de los endpoints para manejar usuarios en el sistema de RRHH.

## Base URL
```
http://localhost:5000/api/users
```

## Endpoints Disponibles

### 1. Obtener todos los usuarios
**GET** `/api/users`

**Respuesta exitosa (200):**
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

### 2. Obtener un usuario por ID
**GET** `/api/users/<user_id>`

**Parámetros:**
- `user_id` (int): ID del usuario

**Ejemplo:**
```
GET /api/users/1
```

**Respuesta exitosa (200):**
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

**Respuesta de error (404):**
```json
{
  "status": "error",
  "message": "Usuario no encontrado"
}
```

---

### 3. Crear un nuevo usuario
**POST** `/api/users`

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
- `email` (string): Email único del usuario
- `password` (string): Contraseña en texto plano

**Respuesta exitosa (201):**
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

**Respuesta de error (400):**
```json
{
  "status": "error",
  "message": "El usuario 'maria_garcia' ya existe"
}
```

---

### 4. Actualizar un usuario
**PUT** `/api/users/<user_id>`

**Parámetros:**
- `user_id` (int): ID del usuario a actualizar

**Body (JSON):**
```json
{
  "username": "maria_garcia_nuevo",
  "email": "maria.nueva@example.com",
  "password": "nueva_contraseña123"
}
```

**Nota:** Todos los campos son opcionales. Solo incluye los campos que deseas actualizar.

**Ejemplo - Solo actualizar email:**
```json
{
  "email": "nuevo_email@example.com"
}
```

**Respuesta exitosa (200):**
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

**Respuesta de error (404):**
```json
{
  "status": "error",
  "message": "Usuario no encontrado"
}
```

---

### 5. Eliminar un usuario
**DELETE** `/api/users/<user_id>`

**Parámetros:**
- `user_id` (int): ID del usuario a eliminar

**Ejemplo:**
```
DELETE /api/users/1
```

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "message": "Usuario eliminado correctamente"
}
```

**Respuesta de error (404):**
```json
{
  "status": "error",
  "message": "Usuario no encontrado"
}
```

---

## Ejemplos con cURL

### Crear un usuario
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Obtener todos los usuarios
```bash
curl http://localhost:5000/api/users
```

### Obtener un usuario específico
```bash
curl http://localhost:5000/api/users/1
```

### Actualizar un usuario
```bash
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo_email@example.com"
  }'
```

### Eliminar un usuario
```bash
curl -X DELETE http://localhost:5000/api/users/1
```

---

## Seguridad

- Las contraseñas se almacenan con hash usando `werkzeug.security`
- Nunca se retorna la contraseña en las respuestas de la API
- Los usuarios y emails deben ser únicos en la base de datos

## Notas

- Todos los endpoints retornan JSON
- Los códigos de estado HTTP siguen estándares REST:
  - `200`: Operación exitosa
  - `201`: Recurso creado exitosamente
  - `400`: Error de validación
  - `404`: Recurso no encontrado
  - `500`: Error del servidor

