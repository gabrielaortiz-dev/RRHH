# 🔐 Guía de Autenticación para Postman

## Problema: Error 403 "Not authenticated"

Cuando intentas acceder a `GET /api/usuarios` sin autenticación, recibes este error porque el endpoint requiere:
- ✅ Token JWT válido
- ✅ Usuario con rol "super admin"

---

## 📋 Pasos para Solucionarlo

### Paso 1: Hacer Login y Obtener el Token

1. **Crear una nueva petición en Postman:**
   - Método: `POST`
   - URL: `http://localhost:8000/api/usuarios/login`
   - Pestaña **Body** → selecciona **raw** → selecciona **JSON**
   - Ingresa las credenciales:
   ```json
   {
     "email": "admin@rrhh.com",
     "password": "tu_password_aqui"
   }
   ```

2. **Enviar la petición** (botón "Send")

3. **Copiar el `access_token` de la respuesta:**
   ```json
   {
     "success": true,
     "message": "Login exitoso",
     "data": {...},
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

### Paso 2: Configurar la Autenticación en tu Petición GET

Tienes **dos opciones** para agregar el token:

#### Opción A: Usar la pestaña Authorization (Recomendado)

1. En tu petición `GET /api/usuarios`
2. Ve a la pestaña **Authorization**
3. En **Type**, selecciona **Bearer Token**
4. En **Token**, pega el `access_token` que copiaste del login
5. ¡Listo! Ya puedes enviar la petición

#### Opción B: Agregar Header Manualmente

1. En tu petición `GET /api/usuarios`
2. Ve a la pestaña **Headers**
3. Agrega un nuevo header:
   - **Key**: `Authorization`
   - **Value**: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (tu token completo)
4. Envía la petición

---

## 🔄 Configurar Variables de Entorno (Opcional pero Recomendado)

Para no copiar y pegar el token manualmente cada vez:

### 1. Crear un Environment en Postman

1. Click en el icono de engranaje (⚙️) arriba a la derecha
2. Click en **"Add"** o **"+"**
3. Nombre: `RRHH Local`
4. Agrega variables:
   - `base_url`: `http://localhost:8000`
   - `token`: (deja vacío por ahora)
5. Click en **Save**

### 2. Configurar el Login para Guardar el Token Automáticamente

1. En tu petición de **Login** (`POST /api/usuarios/login`)
2. Ve a la pestaña **Tests**
3. Agrega este script:
   ```javascript
   if (pm.response.code === 200) {
       var jsonData = pm.response.json();
       pm.environment.set("token", jsonData.access_token);
       console.log("Token guardado:", jsonData.access_token);
   }
   ```
4. Ahora cada vez que hagas login, el token se guardará automáticamente

### 3. Usar Variables en tus Peticiones

1. En la URL de tus peticiones, usa: `{{base_url}}/api/usuarios`
2. En Authorization → Bearer Token, usa: `{{token}}`
3. Postman reemplazará automáticamente las variables

---

## ✅ Verificación

Después de configurar el token, tu petición `GET /api/usuarios` debería:

- ✅ Devolver status **200 OK**
- ✅ Mostrar la lista de usuarios en el body de la respuesta
- ✅ No mostrar más el error 403

---

## 📝 Notas Importantes

1. **Token Expira**: Los tokens expiran después de 24 horas. Si recibes 401 después de un tiempo, vuelve a hacer login.

2. **Rol Requerido**: El endpoint `/api/usuarios` requiere que el usuario tenga rol **"super admin"**. Si tu usuario tiene otro rol, recibirás un error 403 aunque tengas el token válido.

3. **Body en GET**: Las peticiones GET normalmente no llevan body. Si estás enviando datos JSON en un GET, probablemente estás usando el endpoint incorrecto.

4. **Testing**: Puedes usar el endpoint `/api/usuarios/me` (con token) para verificar tu información de usuario actual.

---

## 🆘 Solución de Problemas

### Error 401 "Token inválido o expirado"
- El token expiró (24 horas). Haz login nuevamente.

### Error 403 "Se requiere uno de los siguientes roles: super_admin"
- Tu usuario no tiene el rol necesario. Contacta a un administrador para cambiar tu rol.

### Error 403 "Usuario inactivo"
- Tu cuenta está desactivada. Contacta a un administrador.

---

## 📚 Endpoints Públicos vs Protegidos

### Públicos (No requieren token):
- `POST /api/usuarios/login` - Login

### Protegidos (Requieren token):
- `GET /api/usuarios` - Listar usuarios (requiere super admin)
- `GET /api/usuarios/me` - Obtener mi usuario actual
- `GET /api/usuarios/{id}` - Obtener usuario específico (requiere super admin)
- Todos los demás endpoints del sistema

