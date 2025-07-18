CREATE DATABASE IF NOT EXISTS inventario_uniformes;
USE inventario_uniformes;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin','user') NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    referencia VARCHAR(100) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    colegio VARCHAR(100) NOT NULL,
    genero VARCHAR(20) NOT NULL,
    talla VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    cliente_id INT NOT NULL,
    cantidad INT NOT NULL,
    fecha DATETIME NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS colegios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    telefono VARCHAR(20),
    contacto VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(50) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS configuracion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100),
    direccion VARCHAR(200),
    telefono VARCHAR(50),
    email VARCHAR(100),
    logo VARCHAR(200),
    color_primario VARCHAR(20) DEFAULT '#dc3545',
    color_secundario VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS gastos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200),
    cantidad INT NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    fecha DATETIME NOT NULL
);

-- Datos iniciales
INSERT INTO usuarios (username, password, email, role) VALUES
  ('admin', 'admin', 'admin@example.com', 'admin');

INSERT INTO colegios (nombre, direccion, telefono, contacto) VALUES
  ('Colegio Central', 'Calle 123', '123456789', 'Contacto');

INSERT INTO productos (referencia, nombre, colegio, genero, talla, cantidad, precio) VALUES
  ('REF001', 'Camiseta', 'Colegio Central', 'Unisex', 'M', 10, 25000.00);

INSERT INTO clientes (nombre, apellido, cedula, telefono, email) VALUES
  ('Juan', 'Perez', '11111111', '555-1234', 'juan@example.com');

INSERT INTO configuracion (nombre_empresa, direccion, telefono, email) VALUES
  ('Mi Empresa', 'Direccion 123', '555-1234', 'empresa@example.com');
