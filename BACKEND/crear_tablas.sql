-- Script SQL para crear las tablas Departamentos y Puestos
-- Ejecuta este script en DB Browser for SQLite:
-- 1. Abre DB Browser for SQLite
-- 2. Abre la base de datos: rrhh.db
-- 3. Ve a la pestaña "Execute SQL"
-- 4. Copia y pega este script
-- 5. Click en "Execute SQL" (F5)

-- Crear tabla Departamentos (si no existe)
CREATE TABLE IF NOT EXISTS Departamentos (
    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_departamento VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Crear tabla Puestos (si no existe)
CREATE TABLE IF NOT EXISTS Puestos (
    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_puesto VARCHAR(100) NOT NULL,
    nivel VARCHAR(50),
    salario_base DECIMAL(10,2)
);

-- Verificar que se crearon correctamente
SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Departamentos', 'Puestos');

