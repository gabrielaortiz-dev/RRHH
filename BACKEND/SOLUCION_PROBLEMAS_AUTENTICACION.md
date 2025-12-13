# 🔧 Solución a Problemas de Autenticación y Permisos

## ✅ Mejoras Implementadas

He corregido y mejorado el sistema de autenticación y permisos con las siguientes mejoras:

### 1. **Manejo Mejorado de Errores de Autenticación**
   - Mensajes de error más claros
   - Manejo robusto de tokens inválidos
   - Validación mejorada de credenciales

### 2. **Sistema de Acceso Total por Email**
   - Ahora puedes dar acceso total a usuarios específicos sin cambiar su rol
   - Se configuró en `BACKEND/auth.py` con la lista `USUARIOS_ACCESO_TOTAL`

### 3. **Función `is_super_admin` Mejorada**
   - Reconoce usuarios con acceso total por email
   - Reconoce roles "super admin" y "administrador"
   - Evita problemas de importación circular

### 4. **Login Mejorado**
   - Normalización de emails (case-insensitive)
   - Actualización automática de contraseñas en texto plano
   - Mejor manejo de errores y logging

---

## 🚀 Cómo Dar Acceso Total a Tu Usuario

Tienes **DOS opciones** para dar acceso total a tu usuario:

### OPCIÓN 1: Agregar tu Email a la Lista de Acceso Total (RECOMENDADO)

1. Abre el archivo: `BACKEND/auth.py`

2. Busca esta línea (alrededor de la línea 18):
   ```python
   USUARIOS_ACCESO_TOTAL = [
       "admin@rrhh.com",  # Usuario admin por defecto
       # Agrega aquí tu email para acceso total
   ]
   ```

3. Agrega tu email en la lista:
   ```python
   USUARIOS_ACCESO_TOTAL = [
       "admin@rrhh.com",  # Usuario admin por defecto
       "tu-email@ejemplo.com",  # <-- Agrega tu email aquí
   ]
   ```

4. Guarda el archivo y reinicia el servidor

### OPCIÓN 2: Cambiar el Rol a "super admin"

Ejecuta el script de configuración:

```bash
cd BACKEND
python configurar_acceso_total.py
```

Este script te permitirá:
- Ver todos los usuarios disponibles
- Ver quién tiene acceso total actualmente
- Actualizar el rol de un usuario a "super admin"

---

## 🔍 Solución al Error 403 "Not authenticated"

Este error ocurre cuando intentas acceder a un endpoint protegido sin token.

### Pasos para Solucionarlo:

1. **Hacer Login primero:**
   ```
   POST http://localhost:8000/api/usuarios/login
   Body (JSON):
   {
     "email": "tu-email@ejemplo.com",
     "password": "tu-password"
   }
   ```

2. **Copiar el `access_token` de la respuesta**

3. **Agregar el token a tus peticiones:**
   - En Postman: Pestaña "Authorization" → Type: "Bearer Token" → Pega el token
   - O en Headers: `Authorization: Bearer TU_TOKEN_AQUI`

---

## 🧪 Verificar que Todo Funciona

### 1. Verificar Login

```bash
# En Postman o con curl:
POST http://localhost:8000/api/usuarios/login
Content-Type: application/json

{
  "email": "admin@rrhh.com",
  "password": "admin123"
}
```

Deberías recibir:
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "id": 1,
    "nombre": "Admin Sistema",
    "email": "admin@rrhh.com",
    "rol": "administrador",
    "activo": 1
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Probar Endpoint Protegido

Usando el token del paso anterior:

```bash
GET http://localhost:8000/api/usuarios
Authorization: Bearer TU_TOKEN_AQUI
```

Deberías recibir la lista de usuarios sin error 403.

---

## 📝 Notas Importantes

1. **Los tokens expiran después de 24 horas**. Si recibes error 401, haz login nuevamente.

2. **Reinicia el servidor** después de cambiar `USUARIOS_ACCESO_TOTAL` en `auth.py`.

3. **Los usuarios con acceso total** tienen permisos de super admin sin importar su rol en la base de datos.

4. **El login ahora normaliza emails** (minúsculas), así que puedes escribir el email en mayúsculas o minúsculas.

5. **Las contraseñas en texto plano se actualizan automáticamente** a bcrypt cuando haces login.

---

## 🔧 Solución de Problemas

### Error: "Credenciales inválidas"
- Verifica que el email y contraseña sean correctos
- Verifica que el usuario esté activo en la base de datos

### Error: "Usuario inactivo"
- El usuario está desactivado en la base de datos
- Ejecuta: `python configurar_acceso_total.py` para ver usuarios activos

### Error: "Token inválido o expirado"
- El token expiró (24 horas)
- Haz login nuevamente para obtener un nuevo token

### Error: 403 "Not authenticated" en Postman
- No estás enviando el token correctamente
- Verifica que en Authorization → Bearer Token tengas el token completo
- O verifica que en Headers tengas: `Authorization: Bearer TU_TOKEN_COMPLETO`

### El usuario sigue sin tener acceso total
- Verifica que agregaste el email correcto en `USUARIOS_ACCESO_TOTAL`
- Verifica que reiniciaste el servidor después de hacer cambios
- Verifica que el email en la lista coincida exactamente (case-insensitive)

---

## 📚 Archivos Modificados

- ✅ `BACKEND/auth.py` - Mejorado manejo de autenticación y lista de acceso total
- ✅ `BACKEND/permissions.py` - Función `is_super_admin` mejorada
- ✅ `BACKEND/main.py` - Endpoint de login mejorado
- ✅ `BACKEND/configurar_acceso_total.py` - Nuevo script de configuración

---

## ✅ Próximos Pasos

1. **Agrega tu email** a `USUARIOS_ACCESO_TOTAL` en `auth.py`
2. **Reinicia el servidor**
3. **Haz login** con tus credenciales
4. **Prueba los endpoints** protegidos con el token

¡Todo debería funcionar correctamente ahora! 🎉

