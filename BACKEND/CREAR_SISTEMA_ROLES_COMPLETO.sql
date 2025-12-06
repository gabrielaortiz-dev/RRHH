-- =====================================================================
-- SISTEMA DE GESTIÓN DE ROLES Y PERMISOS - RRHH
-- Script SQL Completo para DB Browser for SQLite
-- =====================================================================
-- Este script crea todas las tablas necesarias para el sistema de roles
-- y permisos, incluyendo datos iniciales.
--
-- INSTRUCCIONES:
-- 1. Abre DB Browser for SQLite
-- 2. Abre la base de datos rrhh.db
-- 3. Ve a la pestaña "Execute SQL"
-- 4. Copia y pega todo este script
-- 5. Click en "Execute SQL" (F5)
-- =====================================================================

-- Desactivar foreign keys temporalmente
PRAGMA foreign_keys = OFF;

-- =====================================================================
-- 1. CREAR TABLAS
-- =====================================================================

-- Tabla de Roles del Sistema
CREATE TABLE IF NOT EXISTS Roles (
    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    id_puesto INTEGER,
    nivel_acceso INTEGER DEFAULT 1,
    es_sistema BOOLEAN DEFAULT 0,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME,
    FOREIGN KEY (id_puesto) REFERENCES Puestos(id_puesto)
);

-- Tabla de Permisos
CREATE TABLE IF NOT EXISTS Permisos (
    id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Relación Roles-Permisos (muchos a muchos)
CREATE TABLE IF NOT EXISTS Roles_Permisos (
    id_rol_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_rol INTEGER NOT NULL,
    id_permiso INTEGER NOT NULL,
    concedido BOOLEAN DEFAULT 1,
    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso) ON DELETE CASCADE,
    UNIQUE(id_rol, id_permiso)
);

-- Tabla de Relación Usuarios-Roles (muchos a muchos)
CREATE TABLE IF NOT EXISTS Usuarios_Roles (
    id_usuario_rol INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    id_rol INTEGER NOT NULL,
    es_principal BOOLEAN DEFAULT 0,
    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME,
    activo BOOLEAN DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE,
    UNIQUE(usuario_id, id_rol)
);

-- Tabla de Permisos Especiales por Usuario
CREATE TABLE IF NOT EXISTS Usuarios_Permisos (
    id_usuario_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    id_permiso INTEGER NOT NULL,
    concedido BOOLEAN DEFAULT 1,
    razon TEXT,
    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME,
    asignado_por INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso) ON DELETE CASCADE,
    FOREIGN KEY (asignado_por) REFERENCES usuarios(id),
    UNIQUE(usuario_id, id_permiso)
);

-- Tabla de Historial de Cambios de Roles
CREATE TABLE IF NOT EXISTS Historial_Roles (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    id_rol_anterior INTEGER,
    id_rol_nuevo INTEGER,
    motivo TEXT,
    realizado_por INTEGER,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (id_rol_anterior) REFERENCES Roles(id_rol),
    FOREIGN KEY (id_rol_nuevo) REFERENCES Roles(id_rol),
    FOREIGN KEY (realizado_por) REFERENCES usuarios(id)
);

-- =====================================================================
-- 2. MODIFICAR TABLA PUESTOS (si existe)
-- =====================================================================

-- Verificar si Puestos necesita la columna id_rol
-- Si la tabla existe sin id_rol, necesitas ejecutar el script Python
-- o recrear la tabla manualmente

-- =====================================================================
-- 3. INSERTAR ROLES DEL SISTEMA
-- =====================================================================

-- Limpiar roles existentes (opcional - descomentar si quieres empezar de cero)
-- DELETE FROM Roles;
-- DELETE FROM sqlite_sequence WHERE name='Roles';

-- Insertar los 5 roles principales
INSERT OR IGNORE INTO Roles (nombre, descripcion, nivel_acceso, es_sistema, activo)
VALUES 
    ('Super Admin', 
     'Control total del sistema, configuraciones, seguridad y creación de usuarios. Puede gestionar todo el sistema sin restricciones.',
     100, 1, 1),
    
    ('Gerente / Alta Gerencia',
     'Decisiones estratégicas, aprobación de solicitudes y acceso a reportes completos. Supervisa operaciones sin acceso a configuraciones técnicas.',
     80, 1, 1),
    
    ('Supervisor / Jefe de Área',
     'Gestión de equipos y departamentos. Puede crear, editar y aprobar solo dentro de su área de responsabilidad.',
     60, 1, 1),
    
    ('Operativo',
     'Trabajo diario en el sistema. Puede registrar información, subir documentos y modificar su propia información.',
     30, 1, 1),
    
    ('Consulta / Solo Visualización',
     'Acceso de solo lectura. Puede visualizar información del sistema sin poder modificar, crear, eliminar o aprobar.',
     10, 1, 1);

-- =====================================================================
-- 4. INSERTAR PERMISOS DEL SISTEMA
-- =====================================================================

-- Limpiar permisos existentes (opcional)
-- DELETE FROM Permisos;
-- DELETE FROM sqlite_sequence WHERE name='Permisos';

INSERT OR IGNORE INTO Permisos (nombre, descripcion, modulo, accion, codigo, activo)
VALUES 
    -- USUARIOS
    ('Ver usuarios', 'Visualizar lista de usuarios', 'usuarios', 'ver', 'usuarios.ver', 1),
    ('Crear usuarios', 'Crear nuevos usuarios', 'usuarios', 'crear', 'usuarios.crear', 1),
    ('Editar usuarios', 'Modificar usuarios existentes', 'usuarios', 'editar', 'usuarios.editar', 1),
    ('Eliminar usuarios', 'Desactivar o eliminar usuarios', 'usuarios', 'eliminar', 'usuarios.eliminar', 1),
    ('Gestionar roles', 'Asignar y gestionar roles de usuarios', 'usuarios', 'roles', 'usuarios.roles', 1),
    
    -- EMPLEADOS
    ('Ver empleados', 'Visualizar lista de empleados', 'empleados', 'ver', 'empleados.ver', 1),
    ('Crear empleados', 'Registrar nuevos empleados', 'empleados', 'crear', 'empleados.crear', 1),
    ('Editar empleados', 'Modificar información de empleados', 'empleados', 'editar', 'empleados.editar', 1),
    ('Eliminar empleados', 'Desactivar empleados', 'empleados', 'eliminar', 'empleados.eliminar', 1),
    ('Ver empleados propios', 'Ver solo información propia', 'empleados', 'ver_propio', 'empleados.ver_propio', 1),
    
    -- DEPARTAMENTOS
    ('Ver departamentos', 'Visualizar departamentos', 'departamentos', 'ver', 'departamentos.ver', 1),
    ('Gestionar departamentos', 'Crear y editar departamentos', 'departamentos', 'gestionar', 'departamentos.gestionar', 1),
    
    -- NÓMINA
    ('Ver nómina', 'Visualizar nóminas', 'nomina', 'ver', 'nomina.ver', 1),
    ('Crear nómina', 'Generar nóminas', 'nomina', 'crear', 'nomina.crear', 1),
    ('Aprobar nómina', 'Aprobar nóminas para pago', 'nomina', 'aprobar', 'nomina.aprobar', 1),
    ('Ver nómina propia', 'Ver solo recibos propios', 'nomina', 'ver_propio', 'nomina.ver_propio', 1),
    
    -- ASISTENCIA
    ('Ver asistencia', 'Visualizar asistencias', 'asistencia', 'ver', 'asistencia.ver', 1),
    ('Marcar asistencia', 'Registrar entrada/salida', 'asistencia', 'marcar', 'asistencia.marcar', 1),
    ('Gestionar asistencia', 'Modificar asistencias de empleados', 'asistencia', 'gestionar', 'asistencia.gestionar', 1),
    
    -- VACACIONES Y PERMISOS
    ('Ver solicitudes', 'Visualizar solicitudes de vacaciones/permisos', 'vacaciones', 'ver', 'vacaciones.ver', 1),
    ('Crear solicitud', 'Solicitar vacaciones o permisos', 'vacaciones', 'crear', 'vacaciones.crear', 1),
    ('Aprobar solicitudes', 'Aprobar o rechazar solicitudes', 'vacaciones', 'aprobar', 'vacaciones.aprobar', 1),
    
    -- REPORTES
    ('Ver reportes generales', 'Acceso a reportes de toda la empresa', 'reportes', 'ver_generales', 'reportes.ver_generales', 1),
    ('Ver reportes departamentales', 'Acceso a reportes del departamento', 'reportes', 'ver_departamentales', 'reportes.ver_departamentales', 1),
    ('Ver reportes personales', 'Acceso solo a reportes propios', 'reportes', 'ver_personales', 'reportes.ver_personales', 1),
    ('Exportar reportes', 'Descargar reportes en PDF/Excel', 'reportes', 'exportar', 'reportes.exportar', 1),
    
    -- CONFIGURACIÓN
    ('Configurar sistema', 'Modificar configuraciones del sistema', 'sistema', 'configurar', 'sistema.configurar', 1),
    ('Ver logs', 'Acceso a logs y auditoría', 'sistema', 'logs', 'sistema.logs', 1),
    
    -- EVALUACIONES
    ('Ver evaluaciones', 'Visualizar evaluaciones de desempeño', 'evaluaciones', 'ver', 'evaluaciones.ver', 1),
    ('Crear evaluaciones', 'Crear evaluaciones de desempeño', 'evaluaciones', 'crear', 'evaluaciones.crear', 1),
    ('Ver evaluación propia', 'Ver solo evaluación personal', 'evaluaciones', 'ver_propia', 'evaluaciones.ver_propia', 1),
    
    -- CAPACITACIONES
    ('Ver capacitaciones', 'Visualizar capacitaciones', 'capacitaciones', 'ver', 'capacitaciones.ver', 1),
    ('Gestionar capacitaciones', 'Crear y asignar capacitaciones', 'capacitaciones', 'gestionar', 'capacitaciones.gestionar', 1),
    ('Ver capacitaciones propias', 'Ver solo capacitaciones asignadas', 'capacitaciones', 'ver_propias', 'capacitaciones.ver_propias', 1),
    
    -- DOCUMENTOS
    ('Ver documentos', 'Visualizar documentos corporativos', 'documentos', 'ver', 'documentos.ver', 1),
    ('Subir documentos', 'Subir documentos al sistema', 'documentos', 'subir', 'documentos.subir', 1),
    ('Eliminar documentos', 'Eliminar documentos del sistema', 'documentos', 'eliminar', 'documentos.eliminar', 1);

-- =====================================================================
-- 5. ASIGNAR PERMISOS A ROLES
-- =====================================================================

-- Limpiar asignaciones existentes (opcional)
-- DELETE FROM Roles_Permisos;

-- SUPER ADMIN (Nivel 100) - TODOS LOS PERMISOS
INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso, concedido)
SELECT 
    (SELECT id_rol FROM Roles WHERE nombre = 'Super Admin'),
    id_permiso,
    1
FROM Permisos;

-- GERENTE / ALTA GERENCIA (Nivel 80) - Permisos de gestión (sin configuración del sistema)
INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso, concedido)
SELECT 
    (SELECT id_rol FROM Roles WHERE nombre = 'Gerente / Alta Gerencia'),
    id_permiso,
    1
FROM Permisos
WHERE codigo IN (
    'usuarios.ver',
    'empleados.ver', 'empleados.editar',
    'departamentos.ver',
    'nomina.ver', 'nomina.aprobar',
    'asistencia.ver',
    'vacaciones.ver', 'vacaciones.aprobar',
    'reportes.ver_generales', 'reportes.exportar',
    'evaluaciones.ver', 'evaluaciones.crear',
    'capacitaciones.ver', 'capacitaciones.gestionar',
    'documentos.ver', 'documentos.subir'
);

-- SUPERVISOR / JEFE DE ÁREA (Nivel 60) - Permisos departamentales
INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso, concedido)
SELECT 
    (SELECT id_rol FROM Roles WHERE nombre = 'Supervisor / Jefe de Área'),
    id_permiso,
    1
FROM Permisos
WHERE codigo IN (
    'empleados.ver', 'empleados.editar',
    'departamentos.ver',
    'nomina.ver',
    'asistencia.ver', 'asistencia.gestionar',
    'vacaciones.ver', 'vacaciones.aprobar',
    'reportes.ver_departamentales', 'reportes.exportar',
    'evaluaciones.ver', 'evaluaciones.crear',
    'capacitaciones.ver', 'capacitaciones.gestionar',
    'documentos.ver', 'documentos.subir'
);

-- OPERATIVO (Nivel 30) - Permisos básicos de trabajo
INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso, concedido)
SELECT 
    (SELECT id_rol FROM Roles WHERE nombre = 'Operativo'),
    id_permiso,
    1
FROM Permisos
WHERE codigo IN (
    'empleados.ver_propio',
    'nomina.ver_propio',
    'asistencia.marcar',
    'vacaciones.crear', 'vacaciones.ver',
    'reportes.ver_personales',
    'evaluaciones.ver_propia',
    'capacitaciones.ver_propias',
    'documentos.ver', 'documentos.subir'
);

-- CONSULTA / SOLO VISUALIZACIÓN (Nivel 10) - Solo lectura
INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso, concedido)
SELECT 
    (SELECT id_rol FROM Roles WHERE nombre = 'Consulta / Solo Visualización'),
    id_permiso,
    1
FROM Permisos
WHERE codigo IN (
    'empleados.ver',
    'departamentos.ver',
    'asistencia.ver',
    'vacaciones.ver',
    'reportes.ver_generales',
    'evaluaciones.ver',
    'capacitaciones.ver',
    'documentos.ver'
);

-- =====================================================================
-- 6. CREAR ÍNDICES PARA MEJOR RENDIMIENTO
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_usuarios_roles_usuario ON Usuarios_Roles(usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_roles_rol ON Usuarios_Roles(id_rol);
CREATE INDEX IF NOT EXISTS idx_roles_permisos_rol ON Roles_Permisos(id_rol);
CREATE INDEX IF NOT EXISTS idx_roles_permisos_permiso ON Roles_Permisos(id_permiso);
CREATE INDEX IF NOT EXISTS idx_historial_roles_usuario ON Historial_Roles(usuario_id);
CREATE INDEX IF NOT EXISTS idx_roles_nivel_acceso ON Roles(nivel_acceso);
CREATE INDEX IF NOT EXISTS idx_permisos_codigo ON Permisos(codigo);

-- =====================================================================
-- 7. REACTIVAR FOREIGN KEYS
-- =====================================================================

PRAGMA foreign_keys = ON;

-- =====================================================================
-- 8. VERIFICACIÓN
-- =====================================================================

-- Ver todos los roles creados
SELECT 'ROLES CREADOS:' as resultado;
SELECT id_rol, nombre, nivel_acceso, es_sistema FROM Roles ORDER BY nivel_acceso DESC;

-- Ver total de permisos
SELECT 'TOTAL DE PERMISOS:' as resultado;
SELECT COUNT(*) as total_permisos FROM Permisos;

-- Ver asignaciones de permisos por rol
SELECT 'PERMISOS POR ROL:' as resultado;
SELECT r.nombre as rol, COUNT(rp.id_permiso) as total_permisos
FROM Roles r
LEFT JOIN Roles_Permisos rp ON r.id_rol = rp.id_rol
GROUP BY r.nombre
ORDER BY r.nivel_acceso DESC;

-- =====================================================================
-- SCRIPT COMPLETADO
-- =====================================================================
-- Ahora debes ejecutar el script Python para crear los puestos:
-- python configurar_roles_y_puestos.py
-- =====================================================================

