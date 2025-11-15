# 🔍 Guía: Abrir Base de Datos en DB Browser for SQLite

## ✅ **VERIFICACIÓN COMPLETADA**

La conexión a la base de datos SQLite se realizó **exitosamente**. 

### 📊 **Resumen de la Base de Datos:**

- **Archivo:** `rrhh.db`
- **Ubicación:** `C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND\rrhh.db`
- **Tamaño:** 36 KB
- **Versión SQLite:** 3.50.4
- **Estado:** ✅ Integridad OK, Sin errores de Foreign Keys

### 📋 **Tablas Creadas:**

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| **usuarios** | 4 | Usuarios del sistema |
| **departamentos** | 5 | Departamentos de la empresa |
| **empleados** | 8 | Información de empleados |
| **asistencias** | 5 | Registros de asistencia |
| **notificaciones** | 3 | Notificaciones del sistema |
| **sqlite_sequence** | 5 | Tabla del sistema (auto-incrementos) |

**Total:** 30 registros en 6 tablas

---

## 🚀 **Cómo Abrir en DB Browser for SQLite**

### **Paso 1: Abrir DB Browser**

1. Abre **DB Browser for SQLite** desde el menú de inicio o escritorio

### **Paso 2: Abrir la Base de Datos**

1. Click en el botón **"Abrir Base de Datos"** (Open Database)
   - O usa el menú: `Archivo > Abrir Base de Datos`
   - O presiona `Ctrl + O`

### **Paso 3: Navegar al Archivo**

1. En el explorador de archivos, navega a:
   ```
   C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND\
   ```

2. Selecciona el archivo: **`rrhh.db`**

3. Click en **"Abrir"**

---

## 📖 **Qué Verás en DB Browser**

Una vez abierto, verás la interfaz con:

### **1. Pestaña "Estructura de Base de Datos" (Database Structure)**

Aquí verás todas las tablas:
- ✅ usuarios
- ✅ departamentos
- ✅ empleados
- ✅ asistencias
- ✅ notificaciones

**Para ver la estructura de una tabla:**
- Click en el nombre de la tabla (ej: `usuarios`)
- Verás todas las columnas con sus tipos de datos

### **2. Pestaña "Datos del Navegador" (Browse Data)**

**Para ver los datos de una tabla:**
1. Selecciona una tabla del menú desplegable (ej: `usuarios`)
2. Verás todos los registros en formato de tabla
3. Puedes editar, agregar o eliminar registros directamente

**Ejemplo - Tabla usuarios:**
```
id | nombre          | email                  | password  | rol           | fecha_creacion      | activo
---|-----------------|------------------------|-----------|---------------|---------------------|-------
1  | Admin Sistema   | admin@rrhh.com        | admin123  | administrador  | 2025-11-15 14:53:12| 1
2  | Juan Perez      | juan.perez@rrhh.com   | pass123   | empleado       | 2025-11-15 14:53:12| 1
3  | Maria Garcia    | maria.garcia@rrhh.com | pass123   | supervisor     | 2025-11-15 14:53:12| 1
4  | Test Usuario    | test@empresa.com      | test123   | empleado       | 2025-11-15 15:00:49| 1
```

### **3. Pestaña "Ejecutar SQL" (Execute SQL)**

Aquí puedes ejecutar consultas SQL directamente:

**Ejemplos de consultas:**

```sql
-- Ver todos los usuarios
SELECT * FROM usuarios;

-- Ver usuarios activos
SELECT id, nombre, email, rol FROM usuarios WHERE activo = 1;

-- Ver empleados con su departamento
SELECT e.nombre, e.apellido, e.puesto, d.nombre as departamento
FROM empleados e
LEFT JOIN departamentos d ON e.departamento_id = d.id
WHERE e.activo = 1;

-- Contar registros por tabla
SELECT 'usuarios' as tabla, COUNT(*) as total FROM usuarios
UNION ALL
SELECT 'departamentos', COUNT(*) FROM departamentos
UNION ALL
SELECT 'empleados', COUNT(*) FROM empleados
UNION ALL
SELECT 'asistencias', COUNT(*) FROM asistencias
UNION ALL
SELECT 'notificaciones', COUNT(*) FROM notificaciones;
```

---

## 🔍 **Verificar la Conexión desde Python**

Si quieres verificar la conexión desde Python, ejecuta:

```bash
cd BACKEND
python verificar_bd.py
```

Este script mostrará:
- ✅ Estado de la conexión
- ✅ Lista de todas las tablas
- ✅ Estructura de cada tabla
- ✅ Cantidad de registros
- ✅ Ejemplos de datos
- ✅ Verificación de integridad

---

## 📊 **Estructura de las Tablas**

### **Tabla: usuarios**
```
id (INTEGER, PRIMARY KEY)
nombre (VARCHAR(100), NOT NULL)
email (VARCHAR(100), UNIQUE, NOT NULL)
password (VARCHAR(255), NOT NULL)
rol (VARCHAR(50), DEFAULT 'empleado')
fecha_creacion (DATETIME, DEFAULT CURRENT_TIMESTAMP)
activo (BOOLEAN, DEFAULT 1)
```

### **Tabla: departamentos**
```
id (INTEGER, PRIMARY KEY)
nombre (VARCHAR(100), NOT NULL)
descripcion (TEXT)
fecha_creacion (DATETIME, DEFAULT CURRENT_TIMESTAMP)
activo (BOOLEAN, DEFAULT 1)
```

### **Tabla: empleados**
```
id (INTEGER, PRIMARY KEY)
nombre (VARCHAR(100), NOT NULL)
apellido (VARCHAR(100), NOT NULL)
email (VARCHAR(100), UNIQUE, NOT NULL)
telefono (VARCHAR(20))
departamento_id (INTEGER, FOREIGN KEY -> departamentos.id)
puesto (VARCHAR(100))
fecha_ingreso (DATE)
salario (DECIMAL(10, 2))
fecha_creacion (DATETIME, DEFAULT CURRENT_TIMESTAMP)
activo (BOOLEAN, DEFAULT 1)
```

### **Tabla: asistencias**
```
id (INTEGER, PRIMARY KEY)
empleado_id (INTEGER, NOT NULL, FOREIGN KEY -> empleados.id)
fecha (DATE, NOT NULL)
hora_entrada (TIME)
hora_salida (TIME)
estado (VARCHAR(50), DEFAULT 'presente')
observaciones (TEXT)
```

### **Tabla: notificaciones**
```
id (INTEGER, PRIMARY KEY)
usuario_id (INTEGER, FOREIGN KEY -> usuarios.id)
titulo (VARCHAR(200), NOT NULL)
mensaje (TEXT, NOT NULL)
tipo (VARCHAR(50), DEFAULT 'info')
leido (BOOLEAN, DEFAULT 0)
fecha_creacion (DATETIME, DEFAULT CURRENT_TIMESTAMP)
```

---

## ✅ **Verificación de Integridad**

La base de datos ha sido verificada y está en perfecto estado:

- ✅ **Integridad:** OK
- ✅ **Foreign Keys:** Sin errores
- ✅ **Conexión:** Exitosa
- ✅ **Datos:** Presentes y correctos

---

## 🎯 **Operaciones Comunes en DB Browser**

### **Ver Datos:**
1. Click en pestaña "Browse Data"
2. Selecciona la tabla del menú desplegable
3. Verás todos los registros

### **Editar Registro:**
1. En "Browse Data", haz doble click en una celda
2. Edita el valor
3. Presiona Enter
4. Click en "Escribir Cambios" (Write Changes)

### **Agregar Registro:**
1. En "Browse Data", click en "Nuevo Registro" (New Record)
2. Completa los campos
3. Click en "Escribir Cambios"

### **Eliminar Registro:**
1. Selecciona la fila
2. Click derecho > "Eliminar Registro" (Delete Record)
3. Click en "Escribir Cambios"

### **Ejecutar Consulta SQL:**
1. Click en pestaña "Execute SQL"
2. Escribe tu consulta SQL
3. Click en "Ejecutar SQL" (Execute SQL) o presiona `F5`

---

## 🔒 **Importante**

⚠️ **Nota de Seguridad:**
- Si editas datos directamente en DB Browser, asegúrate de guardar los cambios
- Los cambios se reflejarán inmediatamente en la base de datos
- La API de Python usará los datos actualizados automáticamente

---

## 📝 **Ruta Completa del Archivo**

```
C:\Users\GABRIELAORTIZ\Desktop\PROYECTO RRHH\BACKEND\rrhh.db
```

**Copia esta ruta y úsala en DB Browser para abrir la base de datos.**

---

## ✅ **Confirmación**

La conexión a la base de datos SQLite está **100% funcional** y lista para usar tanto desde:
- ✅ Python/FastAPI (tu API)
- ✅ DB Browser for SQLite (gestor visual)
- ✅ Cualquier otra herramienta compatible con SQLite

**¡Todo está funcionando correctamente!** 🎉

