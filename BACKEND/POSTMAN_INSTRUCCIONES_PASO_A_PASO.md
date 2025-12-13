# 🔐 Instrucciones PASO A PASO para Postman

## ⚠️ PROBLEMA: Error 403 "Not authenticated"

Tu petición `GET /api/usuarios` está fallando porque **necesitas un token de autenticación**.

---

## ✅ SOLUCIÓN PASO A PASO

### PASO 1: Hacer Login para Obtener el Token

1. **En Postman, crea una nueva petición:**
   - Click en "New" → "HTTP Request"
   - O usa una petición existente y cambia el método

2. **Configura la petición de LOGIN:**
   ```
   Método: POST
   URL: http://localhost:8000/api/usuarios/login
   ```

3. **Configura el Body:**
   - Ve a la pestaña **"Body"**
   - Selecciona **"raw"** (radio button)
   - En el dropdown de la derecha, selecciona **"JSON"**
   - Pega este contenido:
   ```json
   {
     "email": "admin@rrhh.com",
     "password": "admin123"
   }
   ```

4. **Envía la petición:**
   - Click en el botón azul **"Send"**
   - Deberías ver una respuesta como esta:
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
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBycmhoLmNvbSIsInJvbCI6ImFkbWluaXN0cmFkb3IiLCJleHAiOjE3MzUwODg4MDAsImlhdCI6MTczNTAwMjQwMH0.abcdefghijklmnopqrstuvwxyz",
     "token_type": "bearer"
   }
   ```

5. **Copia el `access_token`:**
   - Busca el campo `"access_token"` en la respuesta
   - Copia TODO el valor (es muy largo, empieza con "eyJ...")
   - Guárdalo, lo necesitarás en el siguiente paso

---

### PASO 2: Agregar el Token a tu Petición GET /api/usuarios

Ahora que tienes el token, debes agregarlo a tu petición original.

#### OPCIÓN A: Usar la pestaña Authorization (MÁS FÁCIL) ⭐

1. **En tu petición `GET /api/usuarios`:**
   - Asegúrate de que el método sea **GET**
   - Asegúrate de que la URL sea: `http://localhost:8000/api/usuarios`

2. **Ve a la pestaña "Authorization"** (está en la misma fila que Params, Headers, Body, etc.)

3. **Configura la autorización:**
   - En **"Type"**, selecciona: **"Bearer Token"** del dropdown
   - En el campo **"Token"**, pega el `access_token` que copiaste del login
   - Deberías ver algo como:
     ```
     Type: Bearer Token
     Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     ```

4. **¡Listo!** Ahora envía la petición con el botón "Send"

#### OPCIÓN B: Agregar Header Manualmente

1. **En tu petición `GET /api/usuarios`:**
   - Ve a la pestaña **"Headers"**

2. **Agrega un nuevo header:**
   - Click en el botón **"Add Header"** o simplemente escribe en la última fila vacía
   - **Key:** `Authorization`
   - **Value:** `Bearer TU_TOKEN_AQUI` (reemplaza TU_TOKEN_AQUI con el token que copiaste)
   - Ejemplo:
     ```
     Key: Authorization
     Value: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBycmhoLmNvbSIsInJvbCI6ImFkbWluaXN0cmFkb3IiLCJleHAiOjE3MzUwODg4MDAsImlhdCI6MTczNTAwMjQwMH0.abcdefghijklmnopqrstuvwxyz
     ```
   - ⚠️ **IMPORTANTE:** Debe decir `Bearer ` (con espacio) seguido del token

3. **Envía la petición**

---

### PASO 3: Verificar que Funciona

Si todo está correcto, deberías recibir:

- **Status:** `200 OK` (en verde)
- **Body:** Un JSON con la lista de usuarios:
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
    ...
  ],
  "count": 3
}
```

---

## 🔄 AUTOMATIZAR: Guardar el Token Automáticamente

Para no tener que copiar y pegar el token cada vez:

### 1. Crear una Variable de Entorno

1. En Postman, click en el icono del ojo (👁️) arriba a la derecha
2. Click en **"Add"** o **"+"**
3. Crea una variable:
   - **Variable:** `token`
   - **Initial Value:** (déjalo vacío)
   - **Current Value:** (déjalo vacío)
4. Click en **"Save"**

### 2. Configurar el Login para Guardar el Token

1. En tu petición de **LOGIN** (`POST /api/usuarios/login`)
2. Ve a la pestaña **"Tests"** (al lado de "Body")
3. Pega este código:
   ```javascript
   if (pm.response.code === 200) {
       var jsonData = pm.response.json();
       pm.collectionVariables.set("token", jsonData.access_token);
       console.log("Token guardado:", jsonData.access_token);
   }
   ```
4. Ahora cada vez que hagas login, el token se guardará automáticamente

### 3. Usar la Variable en tus Peticiones

1. En tu petición `GET /api/usuarios`
2. En **Authorization** → **Bearer Token** → **Token**
3. Escribe: `{{token}}`
4. Postman reemplazará `{{token}}` con el valor guardado automáticamente

---

## 🆘 PROBLEMAS COMUNES

### ❌ Error 401 "Token inválido o expirado"
- **Causa:** El token expiró (expiran después de 24 horas)
- **Solución:** Haz login nuevamente para obtener un nuevo token

### ❌ Error 403 "Se requiere rol de Super Admin"
- **Causa:** Tu usuario no tiene el rol "administrador" o "super admin"
- **Solución:** Usa las credenciales: `admin@rrhh.com` / `admin123`

### ❌ Error 403 "Not authenticated"
- **Causa:** No estás enviando el token o está mal formateado
- **Solución:** 
  - Verifica que en Authorization → Type sea "Bearer Token"
  - Verifica que el token esté completo (no cortado)
  - Si usas Headers, verifica que diga `Bearer ` (con espacio) seguido del token

### ❌ Error "Connection refused" o "No connection"
- **Causa:** El servidor no está corriendo
- **Solución:** 
  - Ve a la carpeta BACKEND
  - Ejecuta `iniciar-servidor.bat` o `python main.py`
  - Espera a ver "Application startup complete"

### ❌ El token no se guarda
- **Causa:** Estás usando `pm.collectionVariables` pero no estás en una Collection
- **Solución:** 
  - Crea una Collection en Postman (New → Collection)
  - Mueve tus peticiones a esa Collection
  - Usa `pm.collectionVariables.set()` como en el ejemplo

---

## 📝 RESUMEN RÁPIDO

1. **Login:** POST `/api/usuarios/login` con email y password → Obtener `access_token`
2. **Usar token:** En tu GET `/api/usuarios`, agregar el token en Authorization → Bearer Token
3. **¡Listo!** Ya puedes hacer peticiones autenticadas

---

## 🎯 NOTA IMPORTANTE

Las peticiones **GET** normalmente **NO llevan Body**. 

Si estás intentando enviar datos JSON en un GET, probablemente estés usando el endpoint incorrecto. 

Para crear/modificar datos, usa:
- **POST** para crear
- **PUT** o **PATCH** para actualizar

