# Backend - Sistema de RRHH

Backend desarrollado en Python con Flask y SQLite para el sistema de gestión de recursos humanos.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
```

2. Activar el entorno virtual:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

La base de datos SQLite se creará automáticamente en la carpeta `database/` cuando se ejecute la aplicación por primera vez.

## Ejecución

### Opción 1: Usando el script de inicio (Windows)
Doble clic en `iniciar-api.bat` o ejecuta desde la terminal:
```bash
.\iniciar-api.bat
```

### Opción 2: Usando PowerShell (Windows)
```bash
.\iniciar-api.ps1
```

### Opción 3: Manualmente
```bash
cd backend
python app.py
```

El servidor se ejecutará en `http://localhost:5000`

## Verificar que la API está funcionando

Una vez iniciado el servidor, abre tu navegador o usa curl:

```bash
# Verificar estado del servidor
curl http://localhost:5000/api/health

# O abre en tu navegador:
# http://localhost:5000/api/health
```

## Endpoints disponibles

### Endpoints del Sistema
- `GET /api/health` - Verificar el estado del servidor
- `GET /api/database/test` - Probar la conexión a la base de datos
- `POST /api/database/init` - Inicializar la base de datos

### Endpoints de Usuarios
- `GET /api/users` - Obtener todos los usuarios
- `GET /api/users/<id>` - Obtener un usuario por ID
- `POST /api/users` - Crear un nuevo usuario
- `PUT /api/users/<id>` - Actualizar un usuario
- `DELETE /api/users/<id>` - Eliminar un usuario

Para más detalles sobre la API de usuarios, consulta `USERS_API.md`

## Estructura de la base de datos

- **users**: Usuarios del sistema
- **departments**: Departamentos de la empresa
- **employees**: Empleados
- **attendance**: Registro de asistencia

## Notas

- SQLite viene incluido con Python, no requiere instalación adicional
- La base de datos se crea automáticamente en `database/rrhh.db`
- Para producción, cambiar la SECRET_KEY en las variables de entorno

