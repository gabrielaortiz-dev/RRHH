# Guía de Configuración de Entornos

Este documento explica cómo configurar y usar los diferentes entornos en el backend del sistema de RRHH.

## 📋 Índice

1. [Configuración de Entornos](#configuración-de-entornos)
2. [Variables de Entorno](#variables-de-entorno)
3. [Entornos Disponibles](#entornos-disponibles)
4. [Uso](#uso)
5. [Ejemplos](#ejemplos)

---

## 🔧 Configuración de Entornos

El sistema utiliza el patrón de configuración por entornos de Flask, permitiendo diferentes configuraciones para desarrollo, producción y testing.

### Estructura de Archivos

```
backend/
├── config.py          # Configuraciones por entorno
├── .env               # Variables de entorno (NO subir a Git)
├── .env.example       # Plantilla de variables de entorno
└── .gitignore        # Protege archivos sensibles
```

---

## 🔐 Variables de Entorno

### Configuración Inicial

1. **Copia el archivo de ejemplo:**
   ```bash
   cp .env.example .env
   ```

2. **Edita el archivo `.env`** con tus valores específicos.

### Variables Disponibles

| Variable | Descripción | Valor por Defecto | Requerido en Producción |
|----------|-------------|-------------------|------------------------|
| `FLASK_ENV` | Entorno de ejecución (`development`, `production`, `testing`) | `development` | ✅ |
| `SECRET_KEY` | Clave secreta para sesiones y tokens | `dev-secret-key...` | ✅ |
| `DATABASE_NAME` | Nombre del archivo de base de datos | `rrhh.db` | ❌ |
| `HOST` | Dirección IP del servidor | `127.0.0.1` | ❌ |
| `PORT` | Puerto del servidor | `5000` | ❌ |
| `DEBUG` | Modo debug (`true`/`false`) | `false` | ❌ |
| `CORS_ORIGINS` | Orígenes permitidos (separados por comas) | `http://localhost:4200` | ✅ |
| `LOG_LEVEL` | Nivel de logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` | ❌ |
| `LOG_FILE` | Archivo de logs | `app.log` | ❌ |
| `JWT_SECRET_KEY` | Clave secreta para JWT | (usa SECRET_KEY) | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRES` | Tiempo de expiración del token (segundos) | `3600` | ❌ |
| `ITEMS_PER_PAGE` | Elementos por página en paginación | `10` | ❌ |

---

## 🌍 Entornos Disponibles

### 1. Development (Desarrollo)

**Configuración:** `FLASK_ENV=development`

**Características:**
- ✅ Modo debug activado
- ✅ Logging detallado (DEBUG)
- ✅ CORS permisivo para localhost
- ✅ Base de datos local

**Uso:**
```bash
# En .env
FLASK_ENV=development
DEBUG=true
```

### 2. Production (Producción)

**Configuración:** `FLASK_ENV=production`

**Características:**
- ❌ Modo debug desactivado
- ⚠️ Logging reducido (WARNING)
- 🔒 CORS restrictivo (solo orígenes permitidos)
- ✅ Validación de SECRET_KEY obligatoria
- ✅ Validación de CORS_ORIGINS obligatoria

**Uso:**
```bash
# En .env
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-super-segura-aqui
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com
DEBUG=false
```

### 3. Testing (Pruebas)

**Configuración:** `FLASK_ENV=testing`

**Características:**
- ✅ Modo debug activado
- ✅ Base de datos de prueba (temporal)
- ✅ CORS completamente permisivo
- ✅ Configuración optimizada para tests

**Uso:**
```bash
# En .env
FLASK_ENV=testing
```

---

## 🚀 Uso

### Iniciar el Servidor

El servidor detecta automáticamente el entorno según la variable `FLASK_ENV`:

```bash
# Desarrollo
python app.py

# O usando Flask CLI
flask run
```

### Cambiar de Entorno

1. **Edita el archivo `.env`:**
   ```env
   FLASK_ENV=production
   ```

2. **O establece la variable de entorno directamente:**
   ```bash
   # Windows PowerShell
   $env:FLASK_ENV="production"
   python app.py
   
   # Linux/Mac
   export FLASK_ENV=production
   python app.py
   ```

---

## 📝 Ejemplos

### Ejemplo 1: Desarrollo Local

**Archivo `.env`:**
```env
FLASK_ENV=development
SECRET_KEY=mi-clave-secreta-desarrollo
DATABASE_NAME=rrhh.db
HOST=127.0.0.1
PORT=5000
DEBUG=true
CORS_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
LOG_LEVEL=DEBUG
```

### Ejemplo 2: Producción

**Archivo `.env`:**
```env
FLASK_ENV=production
SECRET_KEY=clave-super-segura-generada-aleatoriamente
DATABASE_NAME=rrhh_prod.db
HOST=0.0.0.0
PORT=5000
DEBUG=false
CORS_ORIGINS=https://app.midominio.com,https://www.midominio.com
LOG_LEVEL=WARNING
LOG_FILE=/var/log/rrhh/app.log
```

### Ejemplo 3: Testing

**Archivo `.env`:**
```env
FLASK_ENV=testing
SECRET_KEY=test-secret-key
DATABASE_NAME=test_rrhh.db
```

---

## 🔒 Seguridad

### ⚠️ Importante

1. **NUNCA subas el archivo `.env` a Git**
   - Ya está incluido en `.gitignore`
   - Usa `.env.example` como plantilla

2. **En Producción:**
   - Genera una `SECRET_KEY` segura y única
   - Limita `CORS_ORIGINS` solo a tus dominios
   - Desactiva `DEBUG`
   - Usa variables de entorno del sistema en lugar de archivos `.env`

3. **Generar SECRET_KEY segura:**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

---

## 🐛 Solución de Problemas

### Error: "SECRET_KEY debe estar configurada en producción"

**Solución:** Establece `SECRET_KEY` en tu archivo `.env` o como variable de entorno del sistema.

### Error: "CORS_ORIGINS debe estar configurada en producción"

**Solución:** Establece `CORS_ORIGINS` con los dominios permitidos separados por comas.

### El servidor no detecta los cambios en `.env`

**Solución:** Reinicia el servidor después de modificar `.env`.

---

## 📚 Referencias

- [Flask Configuration](https://flask.palletsprojects.com/en/latest/config/)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

