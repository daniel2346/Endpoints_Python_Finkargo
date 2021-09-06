CREATE DATABASE db_finkargo_daag;

CREATE TABLE usuarios(
	idusuario int AUTO_INCREMENT not null,
	Nombres varchar(45) not null,
	Apellidos varchar(45) not null,
	Edad int not null,
	Nacionalidad varchar(45) not null,
	primary key(idusuario)
);

CREATE TABLE Ventas(
	idVenta int AUTO_INCREMENT not null,
	Fecha date not null,
	idusuario int not null,
	primary key(idVenta),
	foreign key(idusuario) references usuarios(idusuario)
);

CREATE TABLE Productos(
	idProducto int AUTO_INCREMENT not null,
	Nombre varchar(45) not null,
	Precio DECIMAL(18,2) not null,
	primary key(idProducto)
);

CREATE TABLE DetalleVentas(
	idDetalle int AUTO_INCREMENT not null,
	idVenta int not null,
	idProducto int not null,
	Cantidad int not null,
	Descuento decimal(18,2),
	primary key(idDetalle),
	foreign key(idVenta) references Ventas(idVenta),
	foreign key(idProducto) references Productos(idProducto)
);