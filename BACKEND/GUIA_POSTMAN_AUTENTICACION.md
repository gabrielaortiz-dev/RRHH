# 🔐 Guía de Autenticación en Postman

## ❌ Error que estás viendo

```
403 Forbidden
{
  "detail": "Not authenticated"
}
```

**Significado:** El endpoint `GET /api/usuarios` requiere autenticación con un token JWT, pero no estás enviando el token en la petición.

---

## ✅ Solución: Autenticarte en Postman

### **PASO 1: Hacer Login para obtener el token**

1. **Crea una nueva petición en Postman:**
   - Método: `POST`
   - URL: `http://localhost:8000/api/usuarios/login`

2. **Ve a la pestaña "Body":**
   - Selecciona `raw`
   - Selecciona `JSON` en el dropdown
   - Ingresa el siguiente JSON:
   ```json
   {
     "email": "admin@rrhh.com",
     "password": "tu_contraseña"
   }
   ```
   > **Nota:** Usa el email y contraseña de un usuario que tenga rol "SUPER ADMIN" o esté en la lista de acceso total.

3. **Haz clic en "Send"**

4. **Copia el token de la respuesta:**
   La respuesta será algo como:
   ```json
   {
     "success": true,
     "message": "Login exitoso",
     "data": { ... },
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
   **Copia el valor de `access_token`** (es un string largo que empieza con `eyJ...`)

---

### **PASO 2: Usar el token en tu petición GET /api/usuarios**

1. **En tu petición `GET /api/usuarios`:**
   - Asegúrate de que la URL sea: `http://localhost:8000/api/usuarios`

2. **Ve a la pestaña "Authorization":**
   - En "Type", selecciona: `Bearer Token`
   - En "Token", pega el `access_token` que copiaste del login

3. **Haz clic en "Send"**

4. **¡Deberías recibir la lista de usuarios!** ✅

---

## 📋 Resumen Visual

```
┌─────────────────────────────────────────┐
│  PASO 1: LOGIN                          │
│  POST /api/usuarios/login               │
│  Body: { "email": "...", "password": "..." } │
│  → Obtener: access_token                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  PASO 2: USAR EL TOKEN                  │
│  GET /api/usuarios                      │
│  Authorization: Bearer {access_token}   │
│  → Obtener: Lista de usuarios          │
└─────────────────────────────────────────┘
```

---

## ⚠️ Requisitos Importantes

1. **Usuario con permisos:** El usuario con el que haces login debe tener:
   - Rol `"SUPER ADMIN"` o `"administrador"`, O
   - Estar en la lista de usuarios con acceso total (como `admin@rrhh.com`)

2. **Token válido:** El token expira después de 24 horas. Si recibes un error después de un tiempo, vuelve a hacer login.

3. **Usuario activo:** El usuario debe estar activo (`activo = 1` en la base de datos).

---

## 🔍 Verificar tu Usuario Actual

Puedes usar el endpoint `/api/usuarios/me` para verificar tu información:

- **Método:** `GET`
- **URL:** `http://localhost:8000/api/usuarios/me`
- **Authorization:** Bearer Token (el mismo token del login)

Esto te mostrará tu información de usuario actual, incluyendo tu rol.

---

## 🐛 Si sigues teniendo problemas

1. **Verifica que el servidor esté corriendo:**
   - Debe estar en `http://localhost:8000`

2. **Verifica que el token esté completo:**
   - El token es muy largo (cientos de caracteres)
   - Asegúrate de copiarlo completo

3. **Verifica el formato del header:**
   - En Postman, cuando seleccionas "Bearer Token", automáticamente agrega el header correcto
   - No necesitas agregar "Bearer " manualmente, Postman lo hace por ti

4. **Verifica el rol del usuario:**
   - Si recibes un error diferente como "Se requiere rol de Super Admin", significa que tu token es válido pero tu usuario no tiene los permisos necesarios.

---

## 📝 Ejemplo Completo en Postman

### Request 1: Login
```
POST http://localhost:8000/api/usuarios/login
Content-Type: application/json

{
  "email": "admin@rrhh.com",
  "password": "admin123"
}
```

### Request 2: Obtener Usuarios
```
GET http://localhost:8000/api/usuarios
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBycmhoLmNvbSIsInJvbCI6InN1cGVyIGFkbWluIiwiZXhwIjoxNzM0MDk2ODAwLCJpYXQiOjE3MzQwMTE2MDB9.xxxxx
```

---

¡Con esto deberías poder usar el endpoint sin problemas! 🎉

