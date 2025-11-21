-- Eliminar base de datos si existe
DROP DATABASE IF EXISTS demo_db;

-- Crear base de datos y usuario
CREATE DATABASE IF NOT EXISTS demo_db;
CREATE USER IF NOT EXISTS 'demo_user'@'%' IDENTIFIED BY 'demo_pass';
GRANT ALL PRIVILEGES ON demo_db.* TO 'demo_user'@'%';
FLUSH PRIVILEGES;

-- Crear tabla y datos de ejemplo
USE demo_db;
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    sueldo DECIMAL(10,2),
    puesto VARCHAR(100)
);
INSERT INTO usuarios (nombre, email, sueldo, puesto) VALUES
('Juan Perez', 'juan@example.com', 55000.00, 'Desarrollador'),
('Ana Gomez', 'ana@example.com', 60000.00, 'Analista'),
('Carlos Ruiz', 'carlos.ruiz@example.com', 48000.00, 'Tester'),
('Maria Lopez', 'maria.lopez@example.com', 70000.00, 'Lider de Proyecto'),
('Sofia Torres', 'sofia.torres@example.com', 52000.00, 'Soporte'),
('Luis Fernandez', 'luis.fernandez@example.com', 58000.00, 'DevOps'),
('Valentina Diaz', 'valentina.diaz@example.com', 62000.00, 'Scrum Master'),
('Pedro Alvarez', 'pedro.alvarez@example.com', 54000.00, 'Backend'),
('Martina Castro', 'martina.castro@example.com', 75000.00, 'Gerente'),
('Diego Ramos', 'diego.ramos@example.com', 47000.00, 'QA');
