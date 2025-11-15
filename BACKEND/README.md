# Backend - Sistema de RRHH con Python y SQLite

Backend desarrollado con **Python 3**, **FastAPI** y **SQLite** para el sistema de Recursos Humanos.

---

## ✅ Estado de Instalación

- ✅ SQLite instalado y configurado
- ✅ Base de datos `rrhh.db` creada
- ✅ 5 tablas creadas con datos de ejemplo
- ✅ Servidor FastAPI funcionando
- ✅ Endpoints respondiendo correctamente

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias (si aún no lo has hecho)

```bash
pip install -r requirements.txt
```

### 2. Iniciar el servidor

**Opción recomendada (Windows):**
```
Hacer doble clic en: iniciar-servidor.bat
```

**Desde la terminal:**
```bash
python main.py
```

### 3. Verificar que funciona

Abre tu navegador en: **http://localhost:8000/docs**

---

## 📊 Base de Datos SQLite

El sistema utiliza SQLite3 (incluido en Python por defecto).

### Ubicación
- Archivo: `rrhh.db` (en esta carpeta)

### Tablas creadas automáticamente:
- **usuarios** (3 registros) - Gestión de usuarios del sistema
- **departamentos** (5 registros) - Departamentos de la empresa
- **empleados** (8 registros) - Información de empleados
- **asistencias** (5 registros) - Registro de asistencias
- **notificaciones** (3 registros) - Sistema de notificaciones

### Datos de prueba incluidos

Credenciales:
- Email: `admin@rrhh.com`
- Password: `admin123`

---

## 🔗 Endpoints de la API

### Principales
- `GET /` - Información de la API
- `GET /api/health` - Verificar estado del sistema

### 👥 Usuarios (NUEVO)
- `GET /api/usuarios` - Listar todos los usuarios
- `GET /api/usuarios/{id}` - Obtener usuario por ID
- `POST /api/usuarios` - Crear nuevo usuario
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar (desactivar) usuario
- `POST /api/usuarios/login` - Autenticar usuario

### Otros Recursos
- `GET /api/departamentos` - Listar todos los departamentos
- `GET /api/empleados` - Listar todos los empleados (con info de departamento)
- `GET /api/notificaciones/{usuario_id}` - Obtener notificaciones de un usuario

---

## 📝 Documentación Interactiva

FastAPI genera documentación automática donde puedes probar los endpoints:

- **Swagger UI**: http://localhost:8000/docs (Recomendado)
- **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ Tecnologías

- **Python 3.14** - Lenguaje de programación
- **FastAPI** - Framework web moderno y rápido
- **SQLite3** - Base de datos ligera (incluida en Python)
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **Pydantic** - Validación de datos

---

## 📁 Archivos del Proyecto

```
BACKEND/
├── database.py                 # Conexión a SQLite
├── main.py                     # Servidor FastAPI con todos los endpoints
├── models.py                   # Modelos Pydantic para validación
├── requirements.txt            # Dependencias
├── iniciar-servidor.bat        # Script de inicio (Windows)
├── insert_sample_data.py       # Datos de ejemplo
├── README.md                   # Este archivo
├── INSTRUCCIONES.md            # Guía detallada
├── EJEMPLOS_API.md             # Ejemplos de uso
├── USUARIOS_API.md             # Documentación de API de usuarios
├── RESUMEN_INSTALACION.txt     # Resumen de instalación
└── rrhh.db                     # Base de datos SQLite
```

---

## 🔧 Scripts Útiles

### Insertar datos de ejemplo
```bash
python insert_sample_data.py
```

### Reiniciar la base de datos
1. Detén el servidor
2. Elimina el archivo `rrhh.db`
3. Inicia el servidor (se creará nueva BD)
4. Ejecuta `python insert_sample_data.py`

---

## 🌐 Conectar con Angular

El backend está configurado con CORS para:
- http://localhost:4200
- http://localhost:4201

Para cambiar los puertos permitidos, edita `main.py`:
```python
allow_origins=["http://localhost:4200", "http://localhost:TU_PUERTO"]
```

---

## 📖 Más Información

Para instrucciones detalladas, consulta:
- **INSTRUCCIONES.md** - Guía completa de uso
- **USUARIOS_API.md** - Documentación completa de API de usuarios
- **EJEMPLOS_API.md** - Ejemplos de uso en varios lenguajes
- **RESUMEN_INSTALACION.txt** - Resumen de la instalación

---

## ✨ ¡Listo para usar!

El servidor está funcionando en: **http://localhost:8000**

Documentación interactiva: **http://localhost:8000/docs**

