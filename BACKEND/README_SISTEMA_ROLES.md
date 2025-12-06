# 🚀 Sistema de Roles y Permisos - Guía de Implementación

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Requisitos](#requisitos)
3. [Instalación Rápida](#instalación-rápida)
4. [Instalación Paso a Paso](#instalación-paso-a-paso)
5. [Uso del Sistema](#uso-del-sistema)
6. [Verificación](#verificación)
7. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

Este sistema implementa un modelo de permisos basado en **roles**, donde:

- ✅ Los usuarios tienen permisos según su **ROL** (no por puesto)
- ✅ Los **puestos** están vinculados a roles específicos
- ✅ Hay **5 roles principales** con niveles de acceso del 10 al 100
- ✅ **25 puestos** distribuidos en los roles

### Los 5 Roles del Sistema:
1. **Super Admin** (100) - Control total
2. **Gerente / Alta Gerencia** (80) - Decisiones estratégicas
3. **Supervisor / Jefe de Área** (60) - Gestión departamental
4. **Operativo** (30) - Trabajo diario
5. **Consulta / Solo Visualización** (10) - Solo lectura

---

## 📦 Requisitos

### Software Necesario:
- ✅ Python 3.8 o superior
- ✅ SQLite 3
- ✅ DB Browser for SQLite (opcional pero recomendado)

### Librerías Python:
```bash
pip install sqlite3  # Ya viene con Python
pip install bcrypt   # Para hashear contraseñas
```

---

## ⚡ Instalación Rápida (5 minutos)

### Opción A: Script Automático (Recomendado)

```bash
# Paso 1: Ir al directorio BACKEND
cd BACKEND

# Paso 2: Ejecutar actualización de estructura
python actualizar_estructura_roles.py

# Paso 3: Configurar roles y puestos
python configurar_roles_y_puestos.py

# ¡Listo! El sistema está configurado
```

### Opción B: SQL Directo (Solo roles y permisos)

```bash
# Paso 1: Abrir DB Browser for SQLite
# Paso 2: Abrir rrhh.db
# Paso 3: Ve a "Execute SQL"
# Paso 4: Abrir y ejecutar: CREAR_SISTEMA_ROLES_COMPLETO.sql
# Paso 5: Ejecutar: python configurar_roles_y_puestos.py
```

---

## 📖 Instalación Paso a Paso

### Paso 1: Preparar el Entorno

```bash
# Asegúrate de estar en el directorio BACKEND
cd BACKEND

# Verifica que exista la base de datos
ls rrhh.db  # En Linux/Mac
dir rrhh.db  # En Windows
```

### Paso 2: Actualizar Estructura de la Base de Datos

Este script crea todas las tablas necesarias:

```bash
python actualizar_estructura_roles.py
```

**¿Qué hace este script?**
- ✅ Crea tabla `Roles`
- ✅ Crea tabla `Permisos`
- ✅ Crea tabla `Roles_Permisos`
- ✅ Crea tabla `Usuarios_Roles`
- ✅ Crea tabla `Usuarios_Permisos`
- ✅ Crea tabla `Historial_Roles`
- ✅ Agrega columna `id_rol` a `Puestos`

**Salida Esperada:**
```
====================================================================
ACTUALIZACIÓN DE ESTRUCTURA DE ROLES
====================================================================

[OK] Tabla Roles verificada
[OK] Tabla Permisos verificada
[OK] Tabla Roles_Permisos verificada
...
====================================================================
ACTUALIZACIÓN COMPLETADA EXITOSAMENTE
====================================================================
```

### Paso 3: Configurar Roles y Puestos

Este script crea los 5 roles y los 25 puestos:

```bash
python configurar_roles_y_puestos.py
```

**¿Qué hace este script?**
- ✅ Crea los 5 roles del sistema con sus descripciones
- ✅ Crea los 25 puestos de trabajo
- ✅ Vincula cada puesto con su rol correspondiente
- ✅ Genera un reporte completo

**Pregunta Interactiva:**
```
¿Desea limpiar roles y puestos existentes? (s/n):
```

- Responde **s** si quieres empezar desde cero
- Responde **n** si quieres mantener datos existentes

**Salida Esperada:**
```
====================================================================
CREANDO ROLES DEL SISTEMA
====================================================================

[OK] Rol: Super Admin
     Nivel de acceso: 100
     Permisos:
       • Control total
       • Gestionar usuarios y roles
       ...

====================================================================
CREANDO PUESTOS Y VINCULÁNDOLOS CON ROLES
====================================================================

ROL: Super Admin (ID: 1)
-----------------------------------------------------------
  ✓ Gerente General........................ Executive  $95,000.00
  ✓ Director de Tecnología (CTO)........... Executive  $90,000.00
  ✓ Gerente de Proyectos................... Executive  $85,000.00
  
...

[OK] 25 puestos creados y vinculados a roles

====================================================================
CONFIGURACIÓN COMPLETADA EXITOSAMENTE
====================================================================
```

### Paso 4: (Opcional) Ejecutar SQL Adicional

Si quieres crear también los permisos, ejecuta el SQL:

```bash
# En DB Browser:
# 1. Abre rrhh.db
# 2. Ve a "Execute SQL"
# 3. Abre: CREAR_SISTEMA_ROLES_COMPLETO.sql
# 4. Ejecuta (F5)
```

---

## 💻 Uso del Sistema

### 1. Asignar un Rol a un Usuario

#### En Python:

```python
import sqlite3

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

# Asignar rol "Operativo" (id_rol=4) al usuario con ID 10
cursor.execute("""
    INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
    VALUES (10, 4, 1, 1)
""")

conn.commit()
conn.close()

print("Rol asignado exitosamente")
```

#### En SQL Directo:

```sql
-- Asignar rol "Gerente / Alta Gerencia" al usuario ID 5
INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
VALUES (5, 2, 1, 1);

-- Verificar asignación
SELECT u.nombre, r.nombre as rol, r.nivel_acceso
FROM usuarios u
INNER JOIN Usuarios_Roles ur ON u.id = ur.usuario_id
INNER JOIN Roles r ON ur.id_rol = r.id_rol
WHERE u.id = 5;
```

### 2. Verificar Permisos de un Usuario

#### Función Python:

```python
def verificar_permiso(usuario_id, codigo_permiso):
    """
    Verifica si un usuario tiene un permiso específico
    
    Args:
        usuario_id: ID del usuario
        codigo_permiso: Código del permiso (ej: 'empleados.crear')
    
    Returns:
        bool: True si tiene el permiso, False si no
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM Permisos p
        INNER JOIN Roles_Permisos rp ON p.id_permiso = rp.id_permiso
        INNER JOIN Usuarios_Roles ur ON rp.id_rol = ur.id_rol
        WHERE ur.usuario_id = ? 
          AND p.codigo = ? 
          AND ur.activo = 1
          AND rp.concedido = 1
    """, (usuario_id, codigo_permiso))
    
    tiene_permiso = cursor.fetchone()[0] > 0
    conn.close()
    
    return tiene_permiso

# Uso:
if verificar_permiso(10, 'empleados.crear'):
    print("✅ Usuario puede crear empleados")
else:
    print("❌ Usuario NO puede crear empleados")
```

### 3. Obtener Todos los Permisos de un Usuario

```python
def obtener_permisos_usuario(usuario_id):
    """Retorna lista de todos los permisos del usuario"""
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT p.codigo, p.nombre, p.modulo
        FROM Permisos p
        INNER JOIN Roles_Permisos rp ON p.id_permiso = rp.id_permiso
        INNER JOIN Usuarios_Roles ur ON rp.id_rol = ur.id_rol
        WHERE ur.usuario_id = ? AND ur.activo = 1
        ORDER BY p.modulo, p.nombre
    """, (usuario_id,))
    
    permisos = cursor.fetchall()
    conn.close()
    
    return permisos

# Uso:
permisos = obtener_permisos_usuario(10)
print(f"Usuario tiene {len(permisos)} permisos:")
for codigo, nombre, modulo in permisos:
    print(f"  • [{modulo}] {nombre} ({codigo})")
```

### 4. Cambiar Rol de un Usuario

```python
def cambiar_rol_usuario(usuario_id, nuevo_rol_id, motivo, admin_id):
    """
    Cambia el rol principal de un usuario
    
    Args:
        usuario_id: ID del usuario a modificar
        nuevo_rol_id: ID del nuevo rol
        motivo: Razón del cambio
        admin_id: ID del administrador que hace el cambio
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # 1. Obtener rol actual
        cursor.execute("""
            SELECT id_rol FROM Usuarios_Roles
            WHERE usuario_id = ? AND es_principal = 1 AND activo = 1
        """, (usuario_id,))
        
        resultado = cursor.fetchone()
        rol_anterior_id = resultado[0] if resultado else None
        
        # 2. Desactivar rol anterior
        if rol_anterior_id:
            cursor.execute("""
                UPDATE Usuarios_Roles
                SET activo = 0
                WHERE usuario_id = ? AND es_principal = 1
            """, (usuario_id,))
        
        # 3. Asignar nuevo rol
        cursor.execute("""
            INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
            VALUES (?, ?, 1, 1)
        """, (usuario_id, nuevo_rol_id))
        
        # 4. Registrar en historial
        cursor.execute("""
            INSERT INTO Historial_Roles 
            (usuario_id, id_rol_anterior, id_rol_nuevo, motivo, realizado_por)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, rol_anterior_id, nuevo_rol_id, motivo, admin_id))
        
        conn.commit()
        print("✅ Rol cambiado exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al cambiar rol: {e}")
    finally:
        conn.close()

# Uso:
cambiar_rol_usuario(
    usuario_id=10,
    nuevo_rol_id=3,  # Supervisor
    motivo="Promoción a jefe de área",
    admin_id=1
)
```

### 5. Crear un Empleado con su Rol Automático

```python
def crear_empleado_completo(datos_empleado, puesto_id):
    """
    Crea un empleado y le asigna automáticamente el rol según su puesto
    
    Args:
        datos_empleado: dict con datos del empleado
        puesto_id: ID del puesto a asignar
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # 1. Crear empleado
        cursor.execute("""
            INSERT INTO empleados 
            (nombre, apellido, email, telefono, departamento_id, puesto, 
             fecha_ingreso, salario, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            datos_empleado['nombre'],
            datos_empleado['apellido'],
            datos_empleado['email'],
            datos_empleado['telefono'],
            datos_empleado['departamento_id'],
            puesto_id,
            datos_empleado['fecha_ingreso'],
            datos_empleado['salario']
        ))
        
        empleado_id = cursor.lastrowid
        
        # 2. Crear usuario
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, activo)
            VALUES (?, ?, ?, 1)
        """, (
            f"{datos_empleado['nombre']} {datos_empleado['apellido']}",
            datos_empleado['email'],
            datos_empleado['password_hash']
        ))
        
        usuario_id = cursor.lastrowid
        
        # 3. Obtener rol del puesto
        cursor.execute("""
            SELECT id_rol FROM Puestos WHERE id_puesto = ?
        """, (puesto_id,))
        
        resultado = cursor.fetchone()
        
        if resultado and resultado[0]:
            rol_id = resultado[0]
            
            # 4. Asignar rol al usuario
            cursor.execute("""
                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                VALUES (?, ?, 1, 1)
            """, (usuario_id, rol_id))
            
            print(f"✅ Empleado creado con rol asignado automáticamente")
        else:
            print("⚠️  Empleado creado pero puesto sin rol asignado")
        
        conn.commit()
        return empleado_id, usuario_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return None, None
    finally:
        conn.close()

# Uso:
empleado_nuevo = {
    'nombre': 'Carlos',
    'apellido': 'Martínez',
    'email': 'carlos.martinez@empresa.com',
    'telefono': '+504 9999-8888',
    'departamento_id': 2,
    'fecha_ingreso': '2025-01-15',
    'salario': 38000,
    'password_hash': 'hash_bcrypt_aqui'
}

crear_empleado_completo(empleado_nuevo, puesto_id=16)  # Ejecutivo de Ventas
```

---

## ✅ Verificación

### Verificar que Todo Está Correcto

```bash
# Opción 1: En Python
python -c "
import sqlite3
conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

print('ROLES:')
cursor.execute('SELECT nombre, nivel_acceso FROM Roles ORDER BY nivel_acceso DESC')
for nombre, nivel in cursor.fetchall():
    print(f'  • {nombre}: {nivel}')

print('\nPUESTOS:')
cursor.execute('SELECT COUNT(*) FROM Puestos')
print(f'  Total: {cursor.fetchone()[0]}')

conn.close()
"
```

```sql
-- Opción 2: En DB Browser (Execute SQL)

-- Ver todos los roles
SELECT * FROM Roles ORDER BY nivel_acceso DESC;

-- Ver distribución de puestos por rol
SELECT r.nombre as rol, COUNT(p.id_puesto) as cantidad_puestos
FROM Roles r
LEFT JOIN Puestos p ON r.id_rol = p.id_rol
GROUP BY r.nombre
ORDER BY r.nivel_acceso DESC;

-- Ver usuarios con roles asignados
SELECT u.nombre, r.nombre as rol, r.nivel_acceso
FROM usuarios u
INNER JOIN Usuarios_Roles ur ON u.id = ur.usuario_id
INNER JOIN Roles r ON ur.id_rol = r.id_rol
WHERE ur.activo = 1;
```

---

## 🔧 Solución de Problemas

### Problema 1: "Table Puestos has no column named id_rol"

**Solución:**
```bash
python actualizar_estructura_roles.py
```

Este script agregará la columna faltante.

### Problema 2: "UNIQUE constraint failed"

**Causa:** Estás intentando crear un rol o puesto que ya existe.

**Solución:**
```bash
# Ejecutar el script con limpieza
python configurar_roles_y_puestos.py
# Responder 's' cuando pregunte si quiere limpiar
```

### Problema 3: Los puestos no tienen rol asignado

**Solución:**
```bash
# Re-ejecutar la configuración
python configurar_roles_y_puestos.py
```

### Problema 4: Usuario no tiene permisos después de asignar rol

**Verificar:**
```sql
-- 1. ¿El usuario tiene el rol asignado?
SELECT * FROM Usuarios_Roles WHERE usuario_id = TU_USUARIO_ID;

-- 2. ¿El rol está activo?
SELECT * FROM Roles WHERE id_rol = TU_ROL_ID;

-- 3. ¿El rol tiene permisos asignados?
SELECT * FROM Roles_Permisos WHERE id_rol = TU_ROL_ID;
```

### Problema 5: Base de datos bloqueada

**Solución:**
```bash
# Cerrar DB Browser for SQLite si está abierto
# Luego ejecutar el script de nuevo
```

---

## 📚 Archivos del Sistema

| Archivo | Descripción |
|---------|-------------|
| `configurar_roles_y_puestos.py` | Script principal para crear roles y puestos |
| `actualizar_estructura_roles.py` | Actualiza estructura de la BD |
| `CREAR_SISTEMA_ROLES_COMPLETO.sql` | SQL para crear roles y permisos |
| `DOCUMENTACION_SISTEMA_ROLES.md` | Documentación completa del sistema |
| `README_SISTEMA_ROLES.md` | Esta guía de instalación |
| `verificador_permisos.py` | Módulo para verificar permisos |

---

## 🎓 Próximos Pasos

1. ✅ **Implementar en el Backend**: Usa el módulo `verificador_permisos.py`
2. ✅ **Implementar en el Frontend**: Muestra/oculta botones según permisos
3. ✅ **Capacitar Usuarios**: Usa `DOCUMENTACION_SISTEMA_ROLES.md`
4. ✅ **Asignar Roles**: Asigna roles a usuarios existentes
5. ✅ **Probar Sistema**: Verifica que los permisos funcionen correctamente

---

## 📞 Soporte

Para más información, consulta:
- `DOCUMENTACION_SISTEMA_ROLES.md` - Documentación completa
- Los scripts incluyen comentarios detallados
- Revisa los ejemplos en esta guía

---

**Versión:** 1.0  
**Fecha:** Diciembre 2025  
**Sistema:** RRHH - Gestión de Roles y Permisos

