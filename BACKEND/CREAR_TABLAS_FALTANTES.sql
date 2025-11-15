-- EJECUTA ESTE SQL EN DB BROWSER
-- Ve a la pestaña "Execute SQL" y ejecuta este script completo

-- Crear tabla Departamentos (si no existe)
CREATE TABLE IF NOT EXISTS "Departamentos" (
    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_departamento VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Crear tabla Empleados (si no existe)
CREATE TABLE IF NOT EXISTS "Empleados" (
    id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    genero VARCHAR(10),
    estado_civil VARCHAR(20),
    direccion TEXT,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    fecha_ingreso DATE,
    estado VARCHAR(20),
    id_departamento INTEGER,
    id_puesto INTEGER,
    FOREIGN KEY (id_departamento) REFERENCES "Departamentos"(id_departamento),
    FOREIGN KEY (id_puesto) REFERENCES "Puestos"(id_puesto)
);

-- Crear tabla Asistencias (si no existe)
CREATE TABLE IF NOT EXISTS "Asistencias" (
    id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado INTEGER,
    fecha DATE,
    hora_entrada TIME,
    hora_salida TIME,
    observaciones TEXT,
    FOREIGN KEY (id_empleado) REFERENCES "Empleados"(id_empleado)
);

-- Verificar que se crearon
SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Departamentos', 'Empleados', 'Asistencias');

