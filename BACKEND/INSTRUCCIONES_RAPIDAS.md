# 🚀 INSTRUCCIONES RÁPIDAS - Acceso Total Sin Restricciones

## ✅ SOLUCIÓN IMPLEMENTADA

He creado un sistema de **ACCESO TOTAL SIN RESTRICCIONES** para tu usuario específico.

---

## 🔧 CÓMO CONFIGURAR TU USUARIO

### Opción 1: Usar el Script (MÁS FÁCIL)

```bash
cd BACKEND
python CONFIGURAR_MI_USUARIO.py
```

Solo ingresa tu email y listo.

### Opción 2: Editar Manualmente

1. Abre: `BACKEND/auth.py`
2. Busca la línea 19 (aproximadamente):
   ```python
   USUARIOS_ACCESO_TOTAL = [
       "admin@rrhh.com",
       # AGREGA TU EMAIL AQUI
   ]
   ```
3. Agrega tu email:
   ```python
   USUARIOS_ACCESO_TOTAL = [
       "admin@rrhh.com",
       "tu-email@ejemplo.com",  # <-- Tu email aquí
   ]
   ```
4. Guarda el archivo

---

## ⚠️ IMPORTANTE: REINICIA EL SERVIDOR

Después de agregar tu email, **REINICIA el servidor**:

1. Detén el servidor (Ctrl+C)
2. Inicia de nuevo: `python main.py` o ejecuta `iniciar-servidor.bat`
3. Haz login nuevamente con tu email

---

## ✅ QUÉ HACE ESTO

Una vez que agregues tu email:

- ✅ **Acceso TOTAL a TODO** sin restricciones
- ✅ **NO más errores de "Acceso Denegado"**
- ✅ **Puedes hacer CUALQUIER acción** en el sistema
- ✅ **Funciona en Postman y en la aplicación web**
- ✅ **No importa tu rol**, tendrás acceso total

---

## 🧪 PROBAR EN POSTMAN

### 1. Login
```
POST http://localhost:8000/api/usuarios/login
Body:
{
  "email": "tu-email@ejemplo.com",
  "password": "tu-password"
}
```

### 2. Copiar el token
Del campo `access_token` en la respuesta

### 3. Usar en tus peticiones
En la pestaña **Authorization** → **Bearer Token** → Pega el token

### 4. Hacer peticiones
```
GET http://localhost:8000/api/usuarios
```

**¡Ya no deberías recibir error 403!**

---

## 📝 ENDPOINTS QUE AHORA FUNCIONAN

Con tu email en la lista, estos endpoints funcionarán sin restricciones:

- ✅ `GET /api/usuarios` - Listar todos los usuarios
- ✅ `GET /api/usuarios/{id}` - Ver cualquier usuario
- ✅ `POST /api/usuarios` - Crear usuarios
- ✅ `PUT /api/usuarios/{id}` - Actualizar usuarios
- ✅ `DELETE /api/usuarios/{id}` - Eliminar usuarios
- ✅ Y TODOS los demás endpoints del sistema

---

## 🆘 SI AÚN NO FUNCIONA

1. **Verifica que agregaste tu email correctamente** en `auth.py`
2. **Reinicia el servidor** (muy importante)
3. **Haz login nuevamente** para obtener un nuevo token
4. **Limpia el cache del navegador** (Ctrl+Shift+Delete)
5. **Verifica que el email sea exactamente el mismo** (case-insensitive pero debe coincidir)

---

## 📞 RESumen

1. ✅ Ejecuta: `python CONFIGURAR_MI_USUARIO.py`
2. ✅ Ingresa tu email
3. ✅ Reinicia el servidor
4. ✅ Haz login
5. ✅ ¡Listo! Ya no más errores

