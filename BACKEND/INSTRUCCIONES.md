# 📚 INSTRUCCIONES DE USO - Backend RRHH

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

Abre una terminal en la carpeta `BACKEND` y ejecuta:

```bash
pip install -r requirements.txt
```

### 2. Inicializar la Base de Datos

La base de datos SQLite se crea automáticamente al iniciar el servidor por primera vez.

Si deseas crear la base de datos manualmente:

```bash
python -c "import database; database.init_db()"
```

### 3. Insertar Datos de Ejemplo (Opcional)

Para probar el sistema con datos de ejemplo:

```bash
python insert_sample_data.py
```

Esto creará:
- 3 usuarios de prueba
- 5 departamentos
- 8 empleados
- 5 registros de asistencia
- 3 notificaciones

**Credenciales de prueba:**
- Email: `admin@rrhh.com`
- Password: `admin123`

---

## ▶️ Iniciar el Servidor

### Opción 1: Usando el script .bat (Recomendado para Windows)

Simplemente haz doble clic en:
```
iniciar-servidor.bat
```

### Opción 2: Desde la terminal

```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: **http://localhost:8000**

---

## 📊 Base de Datos SQLite

### Ubicación
- Archivo: `rrhh.db` (en la carpeta BACKEND)
- Tipo: SQLite3 (incluido en Python por defecto)

### Tablas Creadas

1. **usuarios**
   - Gestión de usuarios del sistema
   - Campos: id, nombre, email, password, rol, fecha_creacion, activo

2. **departamentos**
   - Departamentos de la empresa
   - Campos: id, nombre, descripcion, fecha_creacion, activo

3. **empleados**
   - Información de empleados
   - Campos: id, nombre, apellido, email, telefono, departamento_id, puesto, fecha_ingreso, salario, fecha_creacion, activo

4. **asistencias**
   - Registro de asistencias
   - Campos: id, empleado_id, fecha, hora_entrada, hora_salida, estado, observaciones

5. **notificaciones**
   - Sistema de notificaciones
   - Campos: id, usuario_id, titulo, mensaje, tipo, leido, fecha_creacion

### Probar la Conexión

Para verificar que la base de datos funciona correctamente:

```bash
python test_connection.py
```

---

## 🔗 Endpoints de la API

### Principal
- `GET /` - Página principal de la API

### Health Check
- `GET /api/health` - Verificar estado del servidor y base de datos

### Departamentos
- `GET /api/departamentos` - Obtener todos los departamentos

### Empleados
- `GET /api/empleados` - Obtener todos los empleados (con información de departamento)

### Notificaciones
- `GET /api/notificaciones/{usuario_id}` - Obtener notificaciones de un usuario

---

## 📖 Documentación Interactiva

FastAPI genera documentación automática e interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Puedes probar todos los endpoints directamente desde estas interfaces.

---

## 🧪 Ejemplos de Uso

### 1. Verificar el estado del servidor

```bash
curl http://localhost:8000/api/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "database": "conectada",
  "mensaje": "Sistema funcionando correctamente"
}
```

### 2. Obtener departamentos

```bash
curl http://localhost:8000/api/departamentos
```

### 3. Obtener empleados

```bash
curl http://localhost:8000/api/empleados
```

### 4. Obtener notificaciones de un usuario

```bash
curl http://localhost:8000/api/notificaciones/1
```

---

## 🔧 Tecnologías Utilizadas

- **Python 3.14** - Lenguaje de programación
- **FastAPI** - Framework web moderno y rápido
- **SQLite3** - Base de datos ligera (incluida en Python)
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validación de datos

---

## 📝 Estructura de Archivos

```
BACKEND/
├── database.py              # Conexión y gestión de la base de datos
├── main.py                  # Servidor FastAPI y endpoints
├── requirements.txt         # Dependencias de Python
├── iniciar-servidor.bat     # Script para iniciar el servidor (Windows)
├── test_connection.py       # Script de prueba de conexión
├── insert_sample_data.py    # Script para insertar datos de ejemplo
├── README.md                # Documentación general
├── INSTRUCCIONES.md         # Este archivo (instrucciones detalladas)
└── rrhh.db                  # Base de datos SQLite (se crea automáticamente)
```

---

## ❗ Solución de Problemas

### Error: "Module not found"
Asegúrate de haber instalado las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"
El puerto 8000 está ocupado. Puedes cambiar el puerto en `main.py` o detener el proceso que lo está usando.

### Error: "Database is locked"
Cierra todas las conexiones a la base de datos e intenta nuevamente.

### Resetear la base de datos
Si necesitas empezar de cero:
1. Detén el servidor
2. Elimina el archivo `rrhh.db`
3. Inicia el servidor nuevamente (se creará una nueva base de datos)
4. Ejecuta `python insert_sample_data.py` para agregar datos de ejemplo

---

## 🌐 Conectar con el Frontend Angular

El backend está configurado con CORS para permitir conexiones desde:
- http://localhost:4200
- http://localhost:4201

Si tu frontend usa otro puerto, modifica la configuración en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:TU_PUERTO"],
    ...
)
```

---

## 📞 Soporte

Si tienes problemas o preguntas:
1. Verifica que Python esté instalado correctamente
2. Asegúrate de estar en la carpeta BACKEND al ejecutar los comandos
3. Revisa los logs del servidor para identificar errores

---

## ✅ Checklist de Verificación

- [ ] Python instalado y funcionando
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos creada (archivo `rrhh.db` existe)
- [ ] Datos de ejemplo insertados (opcional)
- [ ] Servidor iniciado sin errores
- [ ] Endpoints responden correctamente
- [ ] Documentación interactiva accesible

---

**¡Listo! Tu backend con SQLite y Python está funcionando correctamente.** 🎉

