-- COPIAR Y PEGAR ESTE SQL EN DB BROWSER
-- Pestaña "Execute SQL" -> Pegar -> F5

CREATE TABLE Puestos (
    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_puesto VARCHAR(100) NOT NULL,
    nivel VARCHAR(50),
    salario_base DECIMAL(10,2)
);

