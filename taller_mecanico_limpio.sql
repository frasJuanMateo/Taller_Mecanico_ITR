
DROP DATABASE IF EXISTS taller_mecanico;
CREATE DATABASE IF NOT EXISTS taller_mecanico DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE taller_mecanico;

DROP TABLE IF EXISTS persona;
CREATE TABLE persona (
  dni VARCHAR(20) NOT NULL,
  apellido VARCHAR(40) NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  direccion VARCHAR(50) DEFAULT NULL,
  telefono VARCHAR(12) DEFAULT NULL,
  PRIMARY KEY (dni)
);

DROP TABLE IF EXISTS empleado;
CREATE TABLE empleado (
  legajo INT NOT NULL,
  dni VARCHAR(20) NOT NULL,
  PRIMARY KEY (legajo),
  KEY FK_dni_empleado (dni),
  CONSTRAINT FK_dni_empleado FOREIGN KEY (dni) REFERENCES persona (dni) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS marca;
CREATE TABLE marca (
  cod_marca INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (cod_marca)
);

DROP TABLE IF EXISTS tipo_vehiculo;
CREATE TABLE tipo_vehiculo (
  cod_tipo_vehiculo VARCHAR(5) NOT NULL,
  descripcion VARCHAR(15) DEFAULT NULL,
  PRIMARY KEY (cod_tipo_vehiculo)
);

DROP TABLE IF EXISTS repuestos;
CREATE TABLE repuestos (
  cod_repuesto VARCHAR(50) NOT NULL,
  descripcion VARCHAR(50) DEFAULT NULL,
  ingreso DATETIME,
  egreso DATETIME,
  pcio_unit FLOAT DEFAULT NULL,
  PRIMARY KEY (cod_repuesto)
);

DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
  email VARCHAR(50) NOT NULL,
  usuario VARCHAR(20) NOT NULL,
  contraseña VARCHAR(20) NOT NULL,
  #legajo INT NOT NULL,
  PRIMARY KEY (email)
  #,CONSTRAINT FK_legajo_usuario FOREIGN KEY (legajo) REFERENCES empleado (legajo) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS cliente;
CREATE TABLE cliente (
  cod_cliente VARCHAR(20) NOT NULL,
  dni VARCHAR(20) NOT NULL,
  PRIMARY KEY (cod_cliente),
  KEY FK_dni_cliente (dni),
  CONSTRAINT FK_dni_cliente FOREIGN KEY (dni) REFERENCES persona (dni) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS customer_vehiculo;
CREATE TABLE customer_vehiculo (
  id_customer INT NOT NULL AUTO_INCREMENT,
  cod_cliente VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY (id_customer),
  KEY Fk_Customer_cliente (cod_cliente),
  CONSTRAINT Fk_Customer_cliente FOREIGN KEY (cod_cliente) REFERENCES cliente (cod_cliente) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS customer_detalle;
CREATE TABLE customer_detalle (
  id_detalle_customer INT NOT NULL,
  id_customer INT NOT NULL,
  cod_cliente VARCHAR(20) NOT NULL,
  patente VARCHAR(10) NOT NULL,
  cod_tipo_vehiculo VARCHAR(5) NOT NULL,
  cod_marca INT DEFAULT NULL,
  PRIMARY KEY (id_detalle_customer),
  KEY FK_cod_tipo_vehiculo (cod_tipo_vehiculo),
  KEY FK_cod_cliente (cod_cliente),
  KEY FK_cod_marca (cod_marca),
  CONSTRAINT FK_cod_cliente FOREIGN KEY (cod_cliente) REFERENCES cliente (cod_cliente) ON UPDATE CASCADE,
  CONSTRAINT FK_cod_marca FOREIGN KEY (cod_marca) REFERENCES marca (cod_marca) ON UPDATE CASCADE,
  CONSTRAINT FK_cod_tipo_vehiculo FOREIGN KEY (cod_tipo_vehiculo) REFERENCES tipo_vehiculo (cod_tipo_vehiculo) ON UPDATE CASCADE,
  CONSTRAINT FK_idCustomer FOREIGN KEY (id_customer) REFERENCES customer_vehiculo (id_customer) ON UPDATE CASCADE
);



DROP TABLE IF EXISTS ficha_tecnica;
CREATE TABLE ficha_tecnica (
  nro_ficha INT NOT NULL,
  cod_cliente VARCHAR(20) DEFAULT NULL,
  vehiculo VARCHAR(12) NOT NULL,
  subtotal FLOAT DEFAULT NULL,
  mano_obra FLOAT DEFAULT NULL,
  total_general FLOAT DEFAULT NULL,
  PRIMARY KEY (nro_ficha),
  KEY FK_CodCliente (cod_cliente),
  CONSTRAINT FK_CodCliente FOREIGN KEY (cod_cliente) REFERENCES cliente (cod_cliente) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS detalle_empleado_fechatec;
CREATE TABLE detalle_empleado_fechatec (
  id_detalle_empleado_FT INT NOT NULL AUTO_INCREMENT,
  nro_ficha INT NOT NULL,
  legajo INT NOT NULL,
  horas_trabajadas FLOAT DEFAULT NULL,
  PRIMARY KEY (id_detalle_empleado_FT),
  KEY FKnro_ficha (nro_ficha),
  KEY FK_codLegajo (legajo),
  CONSTRAINT FK_codLegajo FOREIGN KEY (legajo) REFERENCES empleado (legajo) ON UPDATE CASCADE,
  CONSTRAINT FKnro_ficha FOREIGN KEY (nro_ficha) REFERENCES ficha_tecnica (nro_ficha) ON UPDATE CASCADE
);

DROP TABLE IF EXISTS detalle_ficha;
CREATE TABLE detalle_ficha (
  id_detalle_ficha INT NOT NULL AUTO_INCREMENT,
  nro_ficha INT NOT NULL,
  fecha DATE NOT NULL,
  cod_respuesto VARCHAR(30) NOT NULL,
  descripcion VARCHAR(50) DEFAULT NULL,
  cantidad FLOAT NOT NULL,
  precio FLOAT NOT NULL,
  importe FLOAT NOT NULL,
  PRIMARY KEY (id_detalle_ficha),
  KEY FK_nro_ficha (nro_ficha),
  KEY FKcod_respuesto (cod_respuesto),
  CONSTRAINT FK_nro_ficha FOREIGN KEY (nro_ficha) REFERENCES ficha_tecnica (nro_ficha) ON UPDATE CASCADE,
  CONSTRAINT FKcod_respuesto FOREIGN KEY (cod_respuesto) REFERENCES repuestos (cod_repuesto) ON UPDATE CASCADE
);

CREATE TABLE proveedor (
  cod_proveedor INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(50) DEFAULT NULL,
  telefono VARCHAR(15) DEFAULT NULL,
  email VARCHAR(50) DEFAULT NULL,
  direccion VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (cod_proveedor)
);
